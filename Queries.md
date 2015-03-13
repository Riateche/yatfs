# Queries used in yatfs.

## Fill temporary table ##

Fills temporary table folder\_files with file\_id

```
INSERT INTO folder_files
  SELECT *
  FROM files_tags
  WHERE tag_id IN (%tags%) 
```

%tags% - list of tags

%tag\_count% - taglist length

## List full tag contents ##

List the contents of "+" folder

```
SELECT 
   tag_id,
   COUNT(file_id) AS tag_size
FROM folder_files 
GROUP BY tag_id
ORDER BY tag_size DESC
```

## Simple list tag contents ##

Get the biggest tag

```
SELECT 
   tag_id,
   COUNT(file_id) AS tag_size
FROM folder_files 
GROUP BY tag_id
ORDER BY tag_size DESC
LIMIT 1
```

Remove tag from temporary table
```
DELET FROM folder_files
WHERE file_id in (
  SELECT DISTINCT file_id
  FROM folder_files
  WHERE tag_id = %tag_id%
)
```