CREATE OR REPLACE PROCEDURE check_transaction_time(p_rule_id BIGINT, p_start_time VARCHAR, p_end_time VARCHAR, p_transaction_type text)
LANGUAGE plpgsql
AS $$
DECLARE
    start_time TIME := p_start_time::TIME;
    end_time TIME := p_end_time::TIME;
    next_day_start_time TIME;
    next_day_end_time TIME;
    transaction_date DATE;
BEGIN
    -- Check if end_time overlaps into the next day
    IF end_time < start_time THEN
        -- Calculate next day's start_time and end_time
        next_day_start_time := '00:00:00'::TIME;
        next_day_end_time := end_time;
        end_time := '23:59:59'::TIME;
    ELSE
        next_day_start_time := NULL;
        next_day_end_time := NULL;
    END IF;

    -- Query transactions where monitoring_status is NULL and group by date
    FOR transaction_date IN (
        SELECT transaction_created_at::DATE AS transaction_date
        FROM etl_pipelines_etftransaction
        WHERE monitoring_status IS NULL
        AND lower(transaction_type) LIKE LOWER('%' || p_transaction_type || '%')
        GROUP BY transaction_created_at::DATE
    )
    LOOP
        -- Update monitoring_comments for transactions within the time range
        BEGIN
            UPDATE etl_pipelines_etftransaction
            SET monitoring_comments = check_and_concatenate(monitoring_comments, p_rule_id)
            WHERE (
                transaction_created_at::TIME >= start_time
                AND transaction_created_at::TIME <= end_time
            ) OR (
                next_day_start_time IS NOT NULL
                AND transaction_created_at::TIME >= next_day_start_time
                AND transaction_created_at::TIME <= next_day_end_time
            )
            AND (
                transaction_created_at::DATE = transaction_date
                OR transaction_created_at::DATE = transaction_date + INTERVAL '1 day'
            )
            AND monitoring_status IS NULL
            AND lower(transaction_type) LIKE LOWER('%' || p_transaction_type || '%');
        EXCEPTION
            WHEN OTHERS THEN
            INSERT INTO log_table (timestamps, error_message)
            VALUES (NOW(), SQLERRM);
        END;
    END LOOP;
END;
$$;
