# This page contains database structure of internal storage

# Introduction #

DB initialized at FS start and filled with info about tags and files.
SQLite chosen as database engine.

# Tables #

## tags ##
Colums:
  * tag\_id
  * tag\_text

SQL:
```
CREATE TABLE tags (
   id INTEGER PRIMARY KEY,
   tag_text TEXT NOT NULL UNIQUE
)  
```

## files ##
Columns:
  * file\_id
  * file\_path (real directory, for example, "multimedia/video")
  * file\_name (for example, "file.avi")

SQL:
```
CREATE TABLE files (
   id INTEGER PRIMARY KEY,
   file_path TEXT NOT NULL,
   file_name TEXT NOT NULL
)
```

## files\_tags ##
Columns:
  * file\_id
  * tag\_id

SQL:
```
CREATE TABLE files_tags (
   file_id INTEGER NOT NULL,
   tag_id INTEGER NOT NULL,
   PRIMARY KEY (file_id, tag_id)
)
```

## folder\_files ##
Temporary table for list of files in current folder

Columns:
  * file\_id
  * tag\_id

SQL:
```
CREATE TEMPORARY TABLE folder_files (
   file_id INTEGER NOT NULL,
   tag_id INTEGER NOT NULL,
   PRIMARY KEY (file_id, tag_id)
)
```