/*
* This file contains all possible withdrawal procedures that can be run on transactions 
* of type withdrawal. This include logic that can flag
* -> Withdrawal Transactions that exceed the maximum limit.
* -> Multiple withdrawal transactions on a single card etc.
*
*/
CREATE OR REPLACE PROCEDURE public.flag_single_withdrawal_limit(p_rule_id bigint, p_amount integer)
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
    where lower(transaction_type) like '%withdrawal%' and
    monitoring_status is null and 
    amount > p_amount;
  EXCEPTION
    WHEN others THEN
      GET STACKED DIAGNOSTICS l_error_message = MESSAGE_TEXT;
      RAISE NOTICE 'Error in flag_single_withdrawal_limit procedure: %', l_error_message;

      -- Insert the error message into the log table
      INSERT INTO log_table (error_message) VALUES (l_error_message);
  END;
END;$procedure$;


CREATE OR REPLACE PROCEDURE public.flag_daily_withdrawal_limit(p_rule_id bigint, p_amount integer)
 LANGUAGE plpgsql
AS $procedure$
DECLARE
  table_record record;
  l_error_message text;
BEGIN
    
  /**
    * flags withdrawal transactions on a wallet id, 
    * that violates the authorized daily limit
    * and put the rule id that the violate into the monitoring comments column
    */
  BEGIN
    for table_record in (
        select 
            wallet_id,
            date(transaction_created_at) as txn_date,
            sum(amount) as txn_val
        from etl_pipelines_etftransaction 
        where lower(transaction_type) like '%withdraw%'
        and monitoring_status is null
        group by wallet_id, date(transaction_created_at)
        having sum(amount) > p_amount) loop
            update etl_pipelines_etftransaction
            set monitoring_comments = check_and_concatenate(monitoring_comments, p_rule_id)
            where wallet_id = table_record.wallet_id
            and date(transaction_created_at) = table_record.txn_date
            and lower(transaction_type) like '%withdraw%'
            and monitoring_status is null;
        end loop;
  EXCEPTION
    WHEN others THEN
      GET STACKED DIAGNOSTICS l_error_message = MESSAGE_TEXT;
      RAISE NOTICE 'Error in flag_daily_withdrawal_limit procedure: %', l_error_message;

      -- Insert the error message into the log table
      INSERT INTO log_table (error_message) VALUES (l_error_message);
  END;
END;$procedure$;



CREATE OR REPLACE PROCEDURE public.flag_max_withdrawals_on_card(p_rule_id bigint, p_count integer)
 LANGUAGE plpgsql
AS $procedure$
DECLARE
  table_record record;
  v_error_message text;
BEGIN
  BEGIN
    /**
    * if a card has carried out more transactions than the authorized limit for a day, 
    * those transactions will be flagged by this procedure
    *
    */
    for table_record in (
      select 
        response->>'PAN' as CARD,
        date(transaction_created_at) as txn_date,
        count(*) as TXN_VOL 
      from etl_pipelines_etftransaction
      where lower(transaction_type) like '%withdraw%' and
      monitoring_status is null
      group by response->>'PAN', date(transaction_created_at)
      having count(*) > p_count)
    loop
      update etl_pipelines_etftransaction 
      set monitoring_comments = check_and_concatenate(monitoring_comments, p_rule_id)
      where response->>'PAN' = table_record.card 
      and date(transaction_created_at) = table_record.txn_date
      and monitoring_status is null
      and lower(transaction_type) like '%withdraw%';
    end loop;
  EXCEPTION
    WHEN OTHERS THEN
      v_error_message := SQLERRM;
  END;
  
  IF v_error_message IS NOT NULL THEN
    INSERT INTO log_table (error_message, timestamps)
    VALUES (v_error_message, NOW());
  END IF;
END;$procedure$;


CREATE OR REPLACE PROCEDURE public.flag_duplicate_withdrawal_transactions(p_rule_id bigint, p_count integer default 1)
 LANGUAGE plpgsql
AS $procedure$
DECLARE
  table_record record;
  v_error_message text;
BEGIN
  BEGIN
    for table_record in (
      WITH cte AS (
        SELECT 
          *,
          ROW_NUMBER() OVER (PARTITION BY amount, response->>'PAN', wallet_id, date_trunc('minute', transaction_created_at) ORDER BY transaction_created_at) AS rn
        FROM 
          etl_pipelines_etftransaction where lower(transaction_type) like '%withdraw%'
          and monitoring_status is null
      )
      SELECT  * FROM cte WHERE rn > p_count
    ) loop

      update etl_pipelines_etftransaction
      set monitoring_comments = check_and_concatenate(monitoring_comments, p_rule_id)
      where lower(transaction_type) like '%withdraw%'
      and wallet_id = table_record.wallet_id
      and amount = table_record.amount
      and date_trunc('minute', transaction_created_at) = date_trunc('minute', table_record.transaction_created_at)
      and monitoring_status is null;

    end loop;
  EXCEPTION
    WHEN OTHERS THEN
        v_error_message := SQLERRM;
    END;
    
    IF v_error_message IS NOT NULL THEN
        INSERT INTO log_table (error_message, timestamps)
        VALUES (v_error_message, NOW());
    END IF;
END;$procedure$;


CREATE OR REPLACE PROCEDURE public.flag_daily_withdrawal_limit_on_card(p_rule_id bigint, p_amount integer)
 LANGUAGE plpgsql
AS $procedure$
DECLARE
    table_record record;
    l_error_message text;
BEGIN
    
    /**
    * Flags withdrawal transactions on a card (PAN)
    * that violate the authorized daily limit
    * and puts the rule id of the violation into the monitoring comments column
    */
    BEGIN
        FOR table_record IN (
            SELECT 
                wallet_id,
                response->>'PAN' AS card_pan,
                date(transaction_created_at) AS txn_date,
                sum(amount) AS txn_val
            FROM etl_pipelines_etftransaction 
            WHERE lower(transaction_type) LIKE '%withdraw%'
                AND monitoring_status IS NULL
            GROUP BY wallet_id, response->>'PAN', date(transaction_created_at)
            HAVING sum(amount) > p_amount
        )
        LOOP
            UPDATE etl_pipelines_etftransaction
            SET monitoring_comments = check_and_concatenate(monitoring_comments, p_rule_id)
            WHERE wallet_id = table_record.wallet_id
                AND response->>'PAN' = table_record.card_pan
                AND date(transaction_created_at) = table_record.txn_date
                AND lower(transaction_type) LIKE '%withdraw%'
                AND monitoring_status IS NULL;
        END LOOP;
    EXCEPTION
        WHEN OTHERS THEN
            l_error_message := SQLERRM;
            RAISE NOTICE 'Error in flag_daily_withdrawal_limit_on_card procedure: %', l_error_message;

            -- Insert the error message into the log table
            INSERT INTO log_table (error_message) VALUES (l_error_message);
    END;
END;
$procedure$;


CREATE OR REPLACE PROCEDURE public.flag_number_of_daily_withdrawal_transactions(p_rule_id bigint, p_count integer)
 LANGUAGE plpgsql
AS $procedure$
DECLARE
    table_record record;
    v_error_message text;
BEGIN
    BEGIN
        /**
        * Flags withdrawal transactions on a card (PAN)
        * that exceed the authorized transaction count limit for a day
        */
        FOR table_record IN (
            SELECT 
                wallet_id ,
                date(transaction_created_at) AS txn_date,
                count(*) AS txn_vol
            FROM etl_pipelines_etftransaction
            WHERE lower(transaction_type) LIKE '%withdraw%'
                AND monitoring_status IS NULL
            GROUP BY wallet_id, date(transaction_created_at)
            HAVING count(*) > p_count
        )
        LOOP
            UPDATE etl_pipelines_etftransaction 
            SET monitoring_comments = check_and_concatenate(monitoring_comments, p_rule_id)
            WHERE wallet_id = table_record.wallet_id 
                AND date(transaction_created_at) = table_record.txn_date
                AND monitoring_status IS NULL
                AND lower(transaction_type) LIKE '%withdraw%';
        END LOOP;
    EXCEPTION
        WHEN OTHERS THEN
            v_error_message := SQLERRM;
    END;

    IF v_error_message IS NOT NULL THEN
        INSERT INTO log_table (error_message, timestamps)
        VALUES (v_error_message, NOW());
    END IF;
END;
$procedure$;



