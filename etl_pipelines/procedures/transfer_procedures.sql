/*
* This file contains all possible transfer procedures that can be run on transactions 
* of type transfer. This include logic that can flag
* -> Transfer Transactions that exceed the maximum limit.
* -> users trying to transfer above their maximum limit etc.
*
*/
CREATE OR REPLACE PROCEDURE public.flag_single_transfer_limit(
    p_rule_id bigint,
    p_amount integer)
LANGUAGE plpgsql
AS $procedure$
DECLARE
    l_error_message text;
BEGIN
    BEGIN
        update etl_pipelines_etftransaction
        set monitoring_comments = check_and_concatenate(monitoring_comments, p_rule_id)
        where amount > p_amount and
        monitoring_status is null and
        lower(transaction_type) like '%transfer%';
        EXCEPTION
        WHEN OTHERS THEN
        l_error_message := SQLERRM;
    END;

    IF l_error_message IS NOT NULL THEN
        INSERT INTO log_table (error_message, timestamps)
        VALUES (l_error_message, NOW());
    END IF;
END;$procedure$;

CREATE OR REPLACE PROCEDURE public.flag_max_transfers_on_acct(p_rule_id bigint, p_amount integer)
LANGUAGE plpgsql
AS $procedure$
    DECLARE
        table_record record;
        l_error_message text;
    BEGIN
        BEGIN
            FOR table_record IN (
                SELECT account, date(transaction_created_at) AS txn_date, count(*) AS txn_count
                FROM etl_pipelines_etftransaction
                WHERE lower(transaction_type) LIKE '%transfer%'
                AND monitoring_status IS NULL
                GROUP BY account, date(transaction_created_at)
                HAVING count(*) > p_amount
            )
            LOOP
                UPDATE etl_pipelines_etftransaction
                SET monitoring_comments = check_and_concatenate(monitoring_comments, p_rule_id)
                WHERE account = table_record.account 
                AND date(transaction_created_at) = table_record.txn_date
                AND lower(transaction_type) LIKE '%transfer%'
                AND monitoring_status IS NULL;
            END LOOP;
        EXCEPTION
            WHEN OTHERS THEN
                l_error_message := SQLERRM;
        END;

        IF l_error_message IS NOT NULL THEN
            INSERT INTO log_table (error_message, timestamps)
            VALUES (l_error_message, NOW());
        END IF;
    END;
$procedure$;



CREATE OR REPLACE PROCEDURE public.flag_daily_transfer_limit_on_acct(p_rule_id bigint, p_amount integer)
LANGUAGE plpgsql
AS $procedure$
    DECLARE
    	table_record record;
        l_error_message text;
    BEGIN
    BEGIN
        for table_record in (select account, wallet_id, date(transaction_created_at) as txn_date, sum(amount) as txn_val from etl_pipelines_etftransaction
            where lower(transaction_type) like '%transfer%'
            and monitoring_status is null
            group by account, date(transaction_created_at)
            having sum(amount) > p_amount)
        loop
            update etl_pipelines_etftransaction
            set monitoring_comments = check_and_concatenate(monitoring_comments,p_rule_id)
            where account = table_record.account 
            and wallet_id = table_record.wallet_id
            and date(transaction_created_at) = table_record.txn_date
            and lower(transaction_type) like '%transfer%'
            and monitoring_status is null;
        end loop;
    EXCEPTION
    WHEN OTHERS THEN
        l_error_message := SQLERRM;
    END;

    IF l_error_message IS NOT NULL THEN
        INSERT INTO log_table (error_message, timestamps)
        VALUES (l_error_message, NOW());
    END IF;
END;$procedure$; 

CREATE OR REPLACE PROCEDURE public.flag_daily_transfer_limit(p_rule_id bigint, p_amount integer)
LANGUAGE plpgsql
AS $procedure$
    DECLARE
    	table_record record;
        l_error_message text;
    BEGIN
    BEGIN
        for table_record in (select wallet_id, date(transaction_created_at) as txn_date, sum(amount) as txn_val from etl_pipelines_etftransaction
            where lower(transaction_type) like '%transfer%'
            and monitoring_status is null
            group by wallet_id, date(transaction_created_at)
            having sum(amount) > p_amount)
        loop
            update etl_pipelines_etftransaction
            set monitoring_comments = check_and_concatenate(monitoring_comments,p_rule_id)
            where wallet_id = table_record.wallet_id 
            and date(transaction_created_at) = table_record.txn_date
            and lower(transaction_type) like '%transfer%'
            and monitoring_status is null;
        end loop;
    EXCEPTION
    WHEN OTHERS THEN
        l_error_message := SQLERRM;
    END;

    IF l_error_message IS NOT NULL THEN
        INSERT INTO log_table (error_message, timestamps)
        VALUES (l_error_message, NOW());
    END IF;
END;$procedure$; 

CREATE OR REPLACE PROCEDURE public.flag_duplicate_transfer_transactions(p_rule_id bigint, p_count integer default 1)
 LANGUAGE plpgsql
AS $procedure$
DECLARE
table_record record;
BEGIN
    BEGIN
        for table_record in (
            WITH cte AS (
            SELECT 
                *,
                ROW_NUMBER() OVER (PARTITION BY amount, response->>'beneficiaryAccountNumber', wallet_id, date_trunc('minute', transaction_created_at) ORDER BY transaction_created_at) AS rn
            FROM 
                etl_pipelines_etftransaction where lower(transaction_type) like '%transfer%'
                and monitoring_status is null
            )
            SELECT  * FROM cte WHERE rn > p_count
        ) loop

            update etl_pipelines_etftransaction
            set monitoring_comments = check_and_concatenate(monitoring_comments, p_rule_id)
            where lower(transaction_type) like '%transfer%'
            and wallet_id = table_record.wallet_id
            and amount = table_record.amount
            and date_trunc('minute', transaction_created_at) = date_trunc('minute', table_record.transaction_created_at)
            and monitoring_status is null;

        end loop;
    EXCEPTION
        WHEN OTHERS THEN
            INSERT INTO log_table (timestamps, error_message)
            VALUES (NOW(), SQLERRM);
    END;
END;$procedure$;

CREATE OR REPLACE PROCEDURE public.flag_user_transfer_above_limit(p_rule_id bigint, p_amount integer)
 LANGUAGE plpgsql
AS $procedure$
DECLARE
BEGIN
    BEGIN
        update etl_pipelines_etftransaction 
        set monitoring_comments = check_and_concatenate(monitoring_comments, p_rule_id)
        where amount > p_amount and 
        monitoring_status is null and
        lower(transaction_type) like '%transfer%';
    EXCEPTION
        WHEN OTHERS THEN
            INSERT INTO log_table (timestamps, error_message)
            VALUES (NOW(), SQLERRM);
    END;
END;$procedure$;


CREATE OR REPLACE PROCEDURE public.flag_user_transfer_above_wallet_balance(p_rule_id bigint, p_amount integer)
 LANGUAGE plpgsql
AS $procedure$
DECLARE
table_record record;
BEGIN
    BEGIN
        for table_record in (
            select
                wallet_id,
                date(transaction_created_at) as txn_date,
                count(*) as txn_count 
             from etl_pipelines_etftransaction 
             where monitoring_status is null and 
                lower(transaction_type) like '%transfer%' and 
                lower(debit_response->>'message') like '%insuffici%'   
             group by wallet_id, date(transaction_created_at)
             having count(*) > p_amount) loop
                update etl_pipelines_etftransaction
                set monitoring_comments = check_and_concatenate(monitoring_comments, p_rule_id)
                where wallet_id = table_record.wallet_id
                and date(transaction_created_at) = table_record.txn_date 
                and lower(transaction_type) like '%transfer%'
                and lower(debit_response->>'message') like '%insuffici%' 
                and monitoring_status is null;
        end loop;
    EXCEPTION
        WHEN OTHERS THEN
            INSERT INTO log_table (timestamps, error_message)
            VALUES (NOW(), 'flag_user_transfer_above_wallet_balance: ' || SQLERRM);
        END;
END;$procedure$;

CREATE OR REPLACE PROCEDURE public.flag_daily_number_of_transfer_transactions(p_rule_id bigint, p_amount integer)
 LANGUAGE plpgsql
AS $procedure$
DECLARE
    table_record record;
BEGIN
    BEGIN
        FOR table_record IN (
            SELECT
                wallet_id,
                date(transaction_created_at) AS txn_date,
                count(*) AS txn_count 
            FROM etl_pipelines_etftransaction 
            WHERE monitoring_status IS NULL
                AND lower(transaction_type) LIKE '%transfer%'
            GROUP BY wallet_id, date(transaction_created_at)
            HAVING count(*) > p_amount
        )
        LOOP
            UPDATE etl_pipelines_etftransaction
            SET monitoring_comments = check_and_concatenate(monitoring_comments, p_rule_id)
            WHERE wallet_id = table_record.wallet_id
                AND date(transaction_created_at) = table_record.txn_date 
                AND lower(transaction_type) LIKE '%transfer%'
                AND monitoring_status IS NULL;
        END LOOP;
    EXCEPTION
        WHEN OTHERS THEN
            INSERT INTO log_table (timestamps, error_message)
            VALUES (NOW(), 'flag_number_of_transfer_transactions: ' || SQLERRM);
    END;
END;
$procedure$;
