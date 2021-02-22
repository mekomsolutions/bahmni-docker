UPDATE report_card
SET dataset_query=REGEXP_REPLACE(dataset_query, lookup.findstr, lookup.replacestr)
FROM (
    WITH wrongref AS (
        SELECT rc.id, REGEXP_MATCHES(rc.dataset_query, '"source-table":("/databases/([^/]+)/schemas/([^/]+)/tables/([^"]+)")') AS findstr
        FROM report_card AS rc WHERE rc.dataset_query LIKE '%"source-table":"/databases/%'
    )
    SELECT
      wrongref.id,
      concat('"source-table":', wrongref.findstr[1]) AS findstr,
      concat('"source-table":', (
        SELECT mt.id::varchar FROM metabase_database AS md LEFT JOIN metabase_table AS mt ON mt.db_id=md.id WHERE md."name"=wrongref.findstr[2] AND mt."schema"=wrongref.findstr[3] AND mt."name"=wrongref.findstr[4])
      ) AS replacestr
    FROM wrongref
) AS lookup
WHERE report_card.id=lookup.id