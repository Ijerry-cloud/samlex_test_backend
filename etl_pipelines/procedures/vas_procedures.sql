/**
* V.A.S stands for Value Added Services, 
*
* this file contains all the db stored procedures 
* that relate to value added services transactions
*
*/

CREATE OR REPLACE PROCEDURE public.flag_single_vas_transaction_limit(p_rule_id bigint, p_transaction_type text, p_amount integer)
 LANGUAGE plpgsql
AS $procedure$
DECLARE
  l_error_message text;
BEGIN
  /**
    * flags single transactions above the stated limit
    * and put the rule id that the violate into the monitoring comments column
    */
  BEGIN
    update etl_pipelines_etftransaction 
    set monitoring_comments = check_and_concatenate(monitoring_comments, p_rule_id)
    where lower(transaction_type) like '%' || lower(p_transaction_type) || '%' and
    monitoring_status is null and 
    amount > p_amount;
  EXCEPTION
    WHEN others THEN
      GET STACKED DIAGNOSTICS l_error_message = MESSAGE_TEXT;
      RAISE NOTICE 'Error in flag_single_vas_transaction procedure: %', l_error_message;

      -- Insert the error message into the log table
      INSERT INTO log_table (error_message, timestamps) VALUES (l_error_message, NOW());
  END;
END;$procedure$;


CREATE OR REPLACE PROCEDURE public.flag_daily_vas_transaction_limit(p_rule_id bigint, p_transaction_type text, p_amount integer)
 LANGUAGE plpgsql
AS $procedure$
DECLARE
  table_record record;
  l_error_message text;
BEGIN 
  /**
    * flags daily vas transactions above the stated limit
    * and put the rule id that the violate into the monitoring comments column
    */
  BEGIN
    for table_record in (select account, date(transaction_created_at) as txn_date, sum(amount) as txn_val from etl_pipelines_etftransaction
            where lower(transaction_type) like '%' || lower(p_transaction_type) || '%'
            and monitoring_status is null
            group by account, date(transaction_created_at)
            having sum(amount) > p_amount)
        loop
            update etl_pipelines_etftransaction
            set monitoring_comments = check_and_concatenate(monitoring_comments,p_rule_id)
            where account = table_record.account
            and lower(transaction_type) like '%' || lower(p_transaction_type) || '%'
            and monitoring_status is null
            and date(transaction_created_at) = table_record.txn_date;
        end loop;
  EXCEPTION
    WHEN others THEN
      GET STACKED DIAGNOSTICS l_error_message = MESSAGE_TEXT;
      RAISE NOTICE 'Error in flag_daily_vas_transaction procedure: %', l_error_message;

      -- Insert the error message into the log table
      INSERT INTO log_table (error_message, timestamps) VALUES (l_error_message, NOW());
  END;
END;$procedure$;


CREATE OR REPLACE PROCEDURE public.flag_duplicate_vas_transaction(p_rule_id bigint, p_transaction_type text, p_amount integer)
 LANGUAGE plpgsql
AS $procedure$
DECLARE
  table_record record;
  l_error_message text;
BEGIN 
  /**
    * flag vas that are considered as duplicates
    *
    */
  BEGIN
    for table_record in (
            WITH cte AS (
            SELECT 
                *,
                ROW_NUMBER() OVER (PARTITION BY amount, account, date_trunc('minute', transaction_created_at) ORDER BY transaction_created_at) AS rn
            FROM 
                etl_pipelines_etftransaction where lower(transaction_type) like '%' || lower(p_transaction_type) || '%'
                and monitoring_status is null
            )
            SELECT  * FROM cte WHERE rn > p_amount
        ) loop

            update etl_pipelines_etftransaction
            set monitoring_comments = check_and_concatenate(monitoring_comments, p_rule_id)
            where lower(transaction_type) like '%' || lower(p_transaction_type) || '%'            
            and account = table_record.account
            and amount = table_record.amount
            and date_trunc('minute', transaction_created_at) = date_trunc('minute', table_record.transaction_created_at)
            and monitoring_status is null;

        end loop;
  EXCEPTION
    WHEN others THEN
      GET STACKED DIAGNOSTICS l_error_message = MESSAGE_TEXT;
      RAISE NOTICE 'Error in flag_duplicate_vas_transaction procedure: %', l_error_message;

      -- Insert the error message into the log table
      INSERT INTO log_table (error_message, timestamps) VALUES (l_error_message, NOW());
  END;
END;$procedure$;



CREATE OR REPLACE PROCEDURE public.flag_vas_transfer_above_wallet_balance(p_rule_id bigint, p_transaction_type text, p_amount integer)
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
                lower(transaction_type) like '%' || lower(p_transaction_type) || '%' and
                lower(debit_response->>'message') like '%insuffici%'   
             group by wallet_id, date(transaction_created_at)
             having count(*) > p_amount) loop
                update etl_pipelines_etftransaction
                set monitoring_comments = check_and_concatenate(monitoring_comments, p_rule_id)
                where wallet_id = table_record.wallet_id 
                and lower(transaction_type) like '%' || lower(p_transaction_type) || '%'
                and lower(debit_response->>'message') like '%insuffici%' 
                and date(transaction_created_at) = table_record.txn_date;
        end loop;
    EXCEPTION
        WHEN OTHERS THEN
            INSERT INTO log_table (timestamps, error_message)
            VALUES (NOW(), 'flag_vas_transfer_above_wallet_balance: ' || SQLERRM);
        END;
END;$procedure$;