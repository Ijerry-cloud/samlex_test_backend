CREATE OR REPLACE FUNCTION check_and_concatenate(text, bigint)
RETURNS text AS $$
DECLARE
    result text;
BEGIN
    IF $1 IS NULL THEN
        $1 = '';
    END IF;
    IF $1 LIKE '%' || $2 || '%' THEN
        result = $1;
    ELSE
        result = $1 || ',' || $2::text;
    END IF;
    IF result = ',' || $2::text THEN
        result = $2::text;
    END IF;
    RETURN result;
END;
$$ LANGUAGE plpgsql;