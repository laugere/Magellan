CREATE OR REPLACE FUNCTION s57_search_doublon(
)
RETURNS table(schemaname text, tablename text, CELLID text, LNAM text, wkb_geometry geometry, SCACEL int)
AS $$
declare
	COUNTER int;
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
			FOR LNAM, COUNTER IN EXECUTE query
				LOOP
					IF COUNTER > 1 THEN
						FOR i IN 1..COUNTER
						LOOP
							query := format('SELECT "CELLID", "LNAM", "wkb_geometry", SUBSTRING("CELLID", 3, 3) FROM %I.%I AS t WHERE "LNAM" = ''%s''',
											schemaname,
										tablename,
									  LNAM);
							EXECUTE query into CELLID, LNAM, wkb_geometry, SCACEL;
							RETURN NEXT;
						END LOOP;
				END IF;
			END LOOP;
		END IF;
	END LOOP; -- for table
END;
$$ language plpgsql;
