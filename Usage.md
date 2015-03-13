`yatfs [options] source destination`

| destination | Path for mounted file system. If not exists, will be created. |
|:------------|:--------------------------------------------------------------|
| source | Path containing real files of partition. If source is block device, yatfs will try to mount it to temporary directory and use. |
| options | One of options described above: |
| --check | Rebuild database |
| --normalize | Optimize tags tree |
| --case-insensitive | Tags are case insensitive|
| --db-path `[path]` | Path to database. If not specified, yatfs creates temporary database, that removed on exit.|