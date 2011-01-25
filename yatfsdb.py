import sqlite3

class FilesTags():
    def __init__(self):
        self.files = {}
        self.tags = {}
    
    def add(file_id, tag_id):
        self.files.setdefault(file_id, []).append(tag_id)
        self.tags.setdefault(tag_id, []).append(file_id)
        
            
class YatfsDb():
    """ Main FS object """
    
    def __init__(self, database, rebuild):
        self.con = sqlite3.connect(database)
        if rebuild:
            self._recreate_tables()
            
    def __del__(self):
        self.con.close()
        
    def _recreate_tables(self):
        """ Drop exisiting tables and create new. """
        self.con.execute("""
            DROP TABLE IF EXISTS tags;
            CREATE TABLE tags ( 
                id INTEGER PRIMARY KEY, 
                tag_name TEXT NOT NULL UNIQUE
            );
            
            DROP TABLE IF EXISTS files;
            CREATE TABLE files ( 
                id INTEGER PRIMARY KEY, 
                file_path TEXT NOT NULL, 
                file_name TEXT NOT NULL, 
                file_extension TEXT NOT NULL, 
                file_tag_id INTEGER NOT NULL
            );   
             
            DROP TABLE IF EXISTS files_tags;
            CREATE TABLE files_tags ( 
                file_id INTEGER NOT NULL, 
                tag_id INTEGER NOT NULL, 
                    PRIMARY KEY (file_id, tag_id)
            );
        """)
      
    def _add_tag(self, tag_name):
        """ Adds tag and return it's id"""
        q = "INSERT INTO tags (tag_text) VALUES (?)"
        cur = self.con.execute(q, (tag_name, ))
        return cur.lastrowid
      
    def _get_tag_id(self, tag_name, add_if_not_exists=False):
        """ Returns the id of tag with provided name. """
        q = "SELECT id FROM tags WHERE tag_name = ?"
        row = self.con.execute(q, (tag_name, )).fetchone()
        if row is not None:
            return row['id']
        ## tag not found        
        if add_if_not_exists:
            return _add_tag(tag_name)
        else:
            raise NameError("File not found", tag)

    def _get_tag_name(self, tag_id):
        """ Returns the name of tag"""
        q = "SELECT tag_name FROM tags WHERE id = ?"
        cur = self.con.execute(q, (tag_id, ))
        return cur.fetchone()['tag_name']
    
##    def _get_tag_ids(self, tag_names, add_if_not_exists=True):
##        """ Converts list of tag names to list of tags ids """
##        return 
        
    def _add_file_tags(self, file_id, tag_ids):
        for tag_id in tag_ids:
            q = """INSERT OR IGNORE INTO files_tags (file_id, tag_id)
                        VALUES (?, ?)"""
            self.con.execute(q, (file_id, tag_id))
            
    def add_file(self, tag_names, file_tag_name, path, name, extension):
        """ Loads file and it's tags into database. """
        file_tag_id = self._get_tag_id(file_tag_name, True)
        q = """ INSERT INTO files (
                   file_path, file_name, file_extension, file_tag_id
                ) VALUES (?, ?, ?, ?)"""
        cur = self.con.execute(q, (path, name, extension, file_tag_id))
        file_id = cur.lastrowid
        tag_ids = [self._get_tag_id(tag_name, True) for tag_name in tag_names]
        self._add_file_tags(file_id, tag_ids + [file_tag_id])
    
    def print_table(self, table_name):
        print table_name
        for row in self.con.execute('SELECT * FROM ?', (table_name, )):
            print row
    
    def _get_tag_files(self, tag_names):
        """ Returns the cursor with files """
        tag_ids = [self._get_tag_id(tag_name, False) for tag_name in tag_names]
        query = """SELECT file_id, tag_id FROM files_tags """
        params = ()
        if len(tag_ids) != 0:
            placeholders = ', '.join('?' for unused in tag_ids)
            query = query + """ 
                WHERE file_id IN (
                    SELECT DISTINCT file_id FROM files_tags 
                        WHERE tag_id IN (%s)
                        GROUP BY file_id 
                        HAVING COUNT(tag_id) = ?)
            """ % placeholders
            p = tag_ids + [len(tag_ids)]
        
        files_tags = FilesTags()
        cur = self.con.execute(query, params)
        for row in cur:
            files_tags.add(row['file_id'], row['tag_id'])
        
        return files_tags
                             
    def get_file_list_full(self, tag_names):
        files_tags = self._get_tag_files(tag_names)

        self.cur.execute('SELECT tag_id, COUNT(file_id) AS tag_size, \
                          MAX(file_id) AS max_file_id \
                          FROM temp_files_tags \
                          GROUP BY tag_id ORDER BY tag_size DESC, tag_id')
        file_list = []       
        for row in self.cur:
            node = self._get_node(row[0], row[1], row[2])
            file_list.append(node)
        
        self._drop_folder_tables()
        return file_list
  


    def _get_file_extension(self, file_id):
        """ returns the tag id"""
        cur = self.con.execute('SELECT file_extension FROM files WHERE id = ?', (file_id, ))
        return cur.fetchone()[0]
    
    def _get_node(self, tag_id, tag_size, max_file_id):
        node = {}
        if tag_size > 1:
            node['type'] = "folder" 
            node['name'] = self._get_tag_name(tag_id)
        else:
            node['type'] = "file"                 
            node['name'] = self._get_tag_name(tag_id) + "." + \
                           self._get_file_extension(max_file_id)
    
        return node
        
    def get_file_list_short(self, tags):   
        self._create_folder_table(tags)
        file_list = []   
         
        while True:
            self.cur.execute('SELECT tag_id, COUNT(file_id) AS tag_size, \
                              MAX(file_id) AS max_file_id \
                              FROM temp_files_tags \
                              GROUP BY tag_id ORDER BY tag_size DESC LIMIT 1')
            row = self.cur.fetchone()
            if row == None:
                break
            
            if (len(file_list) == 0) and (row[1] > 1):
                file_list.append({"type": "extension"})
                
            node = self._get_node(row[0], row[1], row[2])
            file_list.append(node)
            
            self.cur.execute('DELETE FROM temp_files_tags WHERE file_id in (\
                                SELECT DISTINCT file_id FROM temp_files_tags \
                                WHERE tag_id = ?)', (row[0], ))
                              
        self._drop_folder_tables()
        return file_list
    


        
