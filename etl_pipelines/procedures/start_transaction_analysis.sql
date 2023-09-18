
/**
* 
* This process starts the analysis of transactions of the records
* in the database that have monitoring status is null
* 
**/

-- please note this strings that as used as default, should tally with the initial rules
-- as defined in the seed_rules file in the etl_pipelines/management/commands/seed_rules.py
CREATE OR REPLACE PROCEDURE public.start_transaction_analysis()
 LANGUAGE plpgsql
AS $procedure$
DECLARE
p_rule record;
p_transaction_type varchar(200);
P_EXCEED_DAILY_LIMIT varchar(200) default 'exceeded daily limit';
P_EXCEED_CARD_DAILY_LIMIT varchar(200) default 'exceeded card daily limit';
P_EXCEED_ACCT_DAILY_LIMIT varchar(200) default 'exceeded account daily limit';
P_EXCEED_LIMIT varchar(200) default 'exceeded limit';
P_EXCEED_BALANCE varchar(200) default 'exceeded balance';
P_EXCEED_SINGLE_TRANSACTION_LIMIT varchar(200) default 'exceeded single transaction limit';
P_FLAG_DUPLICATE varchar(200) default 'flag duplicate transaction';
P_NUMBER_OF_DAILY_TRANSACTIONS varchar(200) default 'exceeded number of daily transaction';
P_NUMBER_OF_CARD_DAILY_TRANSACTIONS varchar(200) default 'exceeded number of daily transaction on card';
P_NUMBER_OF_ACCT_DAILY_TRANSACTIONS varchar(200) default 'exceeded number of daily transaction on account';
P_TRANSACTION_TIME varchar(200) default 'transaction time';
begin
    
      -- fire this procedure to label transactions
    CALL label_transactions();

    -- loop over all the rules in the table 
    FOR p_rule IN (SELECT * FROM etl_pipelines_rule WHERE active = TRUE) LOOP

        IF lower(p_rule.condition) = P_TRANSACTION_TIME THEN
            CALL check_transaction_time(p_rule.id, p_rule.value::varchar, p_rule.value2::varchar, p_rule.product_type);
        END IF;

        -- classify the rules based on the product type
        IF lower(p_rule.product_type) LIKE '%withdraw%' THEN
            
            -- based on the p_rule.condition fire on stored procedure to 
            -- classify the transactions accordingly

            IF lower(p_rule.condition) = P_EXCEED_DAILY_LIMIT THEN 
                CALL flag_daily_withdrawal_limit(p_rule.id, p_rule.value::integer);
            ELSIF lower(p_rule.condition) = P_EXCEED_LIMIT THEN
            -- yet to be defined

            ELSIF lower(p_rule.condition) = P_EXCEED_BALANCE THEN
            -- yet to be defined

            ELSIF lower(p_rule.condition) = P_EXCEED_CARD_DAILY_LIMIT THEN
                CALL flag_daily_withdrawal_limit_on_card(p_rule.id, p_rule.value::integer);
            ELSIF lower(p_rule.condition) = P_EXCEED_SINGLE_TRANSACTION_LIMIT THEN
                CALL flag_single_withdrawal_limit(p_rule.id, p_rule.value::integer);
            ELSIF lower(p_rule.condition) = P_FLAG_DUPLICATE THEN
                CALL flag_duplicate_withdrawal_transactions(p_rule.id, p_rule.value::integer);
            ELSIF lower(p_rule.condition) = P_NUMBER_OF_DAILY_TRANSACTIONS THEN
                CALL flag_number_of_daily_withdrawal_transactions(p_rule.id, p_rule.value::integer);
            ELSIF lower(p_rule.condition) = P_NUMBER_OF_CARD_DAILY_TRANSACTIONS THEN
                CALL flag_max_withdrawals_on_card(p_rule.id, p_rule.value::integer);
            END IF;
        ELSIF lower(p_rule.product_type) LIKE '%transfer%' THEN

            IF lower(p_rule.condition) = P_EXCEED_DAILY_LIMIT THEN 
                CALL flag_daily_transfer_limit(p_rule.id, p_rule.value::integer);
            ELSIF lower(p_rule.condition) = P_EXCEED_LIMIT THEN
                CALL flag_user_transfer_above_limit(p_rule.id, p_rule.value::integer);
            ELSIF lower(p_rule.condition) = P_EXCEED_BALANCE THEN
                CALL flag_user_transfer_above_wallet_balance(p_rule.id, p_rule.value::integer);
            ELSIF lower(p_rule.condition) = P_EXCEED_SINGLE_TRANSACTION_LIMIT THEN
                CALL flag_single_transfer_limit(p_rule.id, p_rule.value::integer);
            ELSIF lower(p_rule.condition) = P_FLAG_DUPLICATE THEN
                CALL flag_duplicate_transfer_transactions(p_rule.id, p_rule.value::integer);
            ELSIF lower(p_rule.condition) = P_NUMBER_OF_DAILY_TRANSACTIONS THEN
                CALL flag_daily_number_of_transfer_transactions(p_rule.id, p_rule.value::integer);
            ELSIF lower(p_rule.condition) = P_NUMBER_OF_ACCT_DAILY_TRANSACTIONS THEN
                CALL flag_max_transfers_on_acct(p_rule.id, p_rule.value::integer);
            ELSIF lower(p_rule.condition) = P_EXCEED_ACCT_DAILY_LIMIT THEN
                CALL flag_daily_transfer_limit_on_acct(p_rule.id, p_rule.value::integer);
            END IF;
        ELSE
                      IF lower(p_rule.condition) = P_EXCEED_DAILY_LIMIT THEN 
        CALL flag_daily_vas_transaction_limit(
            p_rule.id,
            p_rule.product_type,
            p_rule.value::integer
        );
    ELSIF lower(p_rule.condition) = P_EXCEED_LIMIT THEN

    ELSIF lower(p_rule.condition) = P_EXCEED_BALANCE THEN

    ELSIF lower(p_rule.condition) = P_EXCEED_SINGLE_TRANSACTION_LIMIT THEN
        CALL flag_single_vas_transaction_limit(
            p_rule.id,
            p_rule.product_type,
            p_rule.value::integer
        );
    ELSIF lower(p_rule.condition) = P_FLAG_DUPLICATE THEN
        CALL flag_duplicate_vas_transaction(
            p_rule.id,
            p_rule.product_type,
            p_rule.value::integer
        );
    ELSIF lower(p_rule.condition) = P_NUMBER_OF_DAILY_TRANSACTIONS THEN
        CALL flag_vas_transfer_above_wallet_balance(
            p_rule.id,
            p_rule.product_type,
            p_rule.value::integer
        );
    END IF;
        end if;
    end loop;

    -- call this function to label transactions that are more than
    -- 2 days olds and have no entry in the monitoring comments column as Cleared
    UPDATE etl_pipelines_etftransaction 
    SET monitoring_status = 'Cleared'
    WHERE (
        transaction_created_at < NOW() - INTERVAL '2 DAYS'
        AND (monitoring_comments = '' OR monitoring_comments IS NULL)
    );  

    UPDATE etl_pipelines_etftransaction 
    SET monitoring_status = 'Suspected'
    WHERE (
        transaction_created_at < NOW() - INTERVAL '2 DAYS'
        AND (monitoring_comments is not null)
    );

end;$procedure$
