import sqlite3

class YatfsDb():
    def _rebuild_database(self):
        """ Ccreates the database tables """
        
        self.cur.execute('DROP TABLE IF EXISTS tags')
        self.cur.execute('CREATE TABLE tags ( \
                            id INTEGER PRIMARY KEY, \
                            tag_text TEXT NOT NULL UNIQUE)')
        
        self.cur.execute('DROP TABLE IF EXISTS files')
        self.cur.execute('CREATE TABLE files ( \
                            id INTEGER PRIMARY KEY, \
                            file_path TEXT NOT NULL, \
                            file_name TEXT NOT NULL, \
                            file_extension TEXT NOT NULL, \
                            file_tag_id INTEGER NOT NULL )')    
        
        self.cur.execute('DROP TABLE IF EXISTS files_tags')
        self.cur.execute('CREATE TABLE files_tags ( \
                            file_id INTEGER NOT NULL, \
                            tag_id INTEGER NOT NULL, \
                            PRIMARY KEY (file_id, tag_id))')      
                             
    def __init__(self, database, rebuild):
        self.con = sqlite3.connect(database)
        self.cur = self.con.cursor()
        if rebuild:
            self._rebuild_database()
    
    def _get_tag_id(self, tag, add_if_not_exists=False ):
        """ returns the tag id"""
        self.cur.execute('SELECT id FROM tags WHERE tag_text = ?', (tag, ))
        row = self.cur.fetchone()
        if row == None:
            if add_if_not_exists:
                self.cur.execute('INSERT INTO tags (tag_text) \
                                         VALUES (?)', (tag, ))
                return self.cur.lastrowid
            else:
                #raise NameError("File not found", tag)
                print 'file not found', tag
                return -1
        else:    
            return row[0]

    def _text_tag_to_ids(self, tags, add_if_not_exists=True):
        """ Converts list of tags to list of tags id's """
        return [self._get_tag_id(tag, add_if_not_exists) for tag in tags]
        
    def add_file(self, tags, filetag, filepath, name, extension):
        """ Loads file and tags into database. """
        file_tag_id = self._get_tag_id(filetag, True)
        
        self.cur.execute('INSERT INTO files (file_name, file_path, file_extension, file_tag_id) \
                                 VALUES (?, ?, ?, ?)', (name, filepath, extension, file_tag_id))
        file_id = self.cur.lastrowid
        tag_ids = self._text_tag_to_ids(tags)
        for tag_id in tag_ids + [file_tag_id]:
            self.cur.execute('INSERT OR IGNORE INTO files_tags (file_id, tag_id) \
                                     VALUES (?, ?)', (file_id, tag_id))
    
    def _delete_synonymous(self):
        self.cur.execute('SELECT tag_id, COUNT(file_id) AS tag_size, \
                          MAX(file_id) AS max_file_id \
                          FROM temp_files_tags \
                          GROUP BY tag_id ORDER BY tag_size DESC, tag_id')
        row = self.cur.fetchone()
        if row == None:
            return
        tag_size = row[1]
        file_id = row[2]
        synonymous = [row[0]]
        for row in self.cur:
            if row[1] == tag_size:
                synonymous.append(row[0])
        
        
        param = ','.join(str(tag_id) for tag_id in synonymous)
        self.cur.execute('DELETE FROM temp_files_tags \
                          WHERE tag_id IN (' + param +')')
        
        ### Check if table is empty (one file in tag)
        self.cur.execute('SELECT * FROM temp_files_tags LIMIT 1') 
        if self.cur.fetchone() == None:
            self.cur.execute('INSERT INTO temp_files_tags \
                                     SELECT id, file_tag_id \
                                     FROM files WHERE id = ?', (file_id, ))
         

        
    def _create_folder_table(self, tags):
        self.cur.execute('CREATE TABLE temp_files_tags ( \
                           file_id INTEGER NOT NULL, \
                           tag_id INTEGER NOT NULL, \
                           PRIMARY KEY (file_id, tag_id) )')
        if len(tags) != 0:
            tag_ids = self._text_tag_to_ids(tags, False)
            param = ','.join(str(tag_id) for tag_id in tag_ids)           
            query = 'INSERT INTO temp_files_tags \
                            SELECT file_id, tag_id \
                            FROM files_tags \
                            WHERE file_id IN ( \
                                SELECT file_id FROM files_tags \
                                WHERE tag_id IN (' + param +')\
                                GROUP BY file_id \
                                HAVING COUNT(tag_id) = ?)'
            self.cur.execute(query, (len(tag_ids), ))
        else:
            query = 'INSERT OR IGNORE INTO temp_files_tags \
                            SELECT file_id, tag_id \
                            FROM files_tags'
            self.cur.execute(query, )
        self._delete_synonymous()       
    
    def _drop_folder_tables(self):
        """ Drops temporary table """
        self.cur.execute('DROP TABLE IF EXISTS temp_files_tags')
    
    def print_table(self, table_name):
        print table_name
        self.cur.execute('SELECT * FROM ' + table_name)
        for row in self.cur:
            print row
                               
    def get_file_list_full(self, tags):
        self._create_folder_table(tags)

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
  
    def _get_tag_name(self, tag_id):
        """ returns the tag id"""
        cur = self.con.execute('SELECT tag_text FROM tags WHERE id = ?', (tag_id, ))
        return cur.fetchone()[0]

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
    

    def __del__(self):
        self.con.close()
        
