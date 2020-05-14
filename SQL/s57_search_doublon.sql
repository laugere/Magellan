CREATE OR REPLACE FUNCTION s57_search_doublon(
)
RETURNS table(schemaname text, tablename text, LNAM text, COUNTER int)
AS $$
declare
  query text;
  hit boolean;
begin
  FOR schemaname,tablename IN
      SELECT table_schema, table_name
      FROM information_schema.tables t
        WHERE t.table_type='BASE TABLE'
  LOOP
               IF tablename != 'spatial_ref_sys' AND schemaname = 'public' AND tablename != 'DSID' THEN
                               query := format('SELECT "LNAM",COUNT(*) FROM %I.%I AS t GROUP BY "LNAM" HAVING COUNT(*) > 1',
                                               schemaname,
                                               tablename);
                               EXECUTE query INTO LNAM, COUNTER;
                               FOR LNAM, COUNTER IN EXECUTE query
                               LOOP
                                               RETURN NEXT;
                               END LOOP;
                END IF;
  END LOOP; -- for table
END;
$$ language plpgsql;
