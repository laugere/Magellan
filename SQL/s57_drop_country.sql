CREATE OR REPLACE FUNCTION s57_drop_country(countryName text)
RETURNS BOOLEAN
AS $$
DECLARE
    result BOOLEAN;
    schemaname text;
    tablename text;
	query text;
BEGIN
FOR schemaname, tablename IN
    SELECT table_schema, table_name
    FROM information_schema.tables t
    WHERE t.table_type='BASE TABLE'
    LOOP
        IF tablename != 'spatial_ref_sys' AND schemaname = 'public' THEN
            query := format('DELETE FROM %I.%I AS t WHERE SUBSTRING("CELLID",1,2) LIKE ''%s''', schemaname, tablename, UPPER(countryName));
			raise notice 'Value: %', query;
            EXECUTE query;
        END IF;
    END LOOP;
	RETURN result;
END;
$$ language plpgsql;