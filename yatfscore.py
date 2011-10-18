import sqlite3

class FilesTags():
    """
    Class for storing pairs (file_id, tag_id). The data can be retrieved by:
    FilesTags.files[file_id] - list of file_id tags
    FilesTags.tags[tag_id] - list of files with tag_id

    """
    
    def __init__(self):
        self.files = {}
        self.tags = {}
        self.tag_items = []
    
    def add(self, file_id, tag_id):
        self.files.setdefault(file_id, []).append(tag_id)
        self.tags.setdefault(tag_id, []).append(file_id)
    
    def remove_tag(self, tag_id):
        tag_files = self.tags[tag_id]
        for file_id in tag_files[:]:
            self.files[file_id].remove(tag_id)
        del self.tags[tag_id]
        
    def remove_file(self, file_id):
        file_tags = self.files[file_id]
        for tag_id in file_tags[:]:
            self.tags[tag_id].remove(file_id)
        del self.files[file_id]
        
    def remove_tag_and_files(self, tag_id):
        tag_files = self.tags[tag_id]
        for file_id in tag_files[:]:
            self.remove_file(file_id)
        del self.tags[tag_id]       

    def sort_tag_items(self):
        self.tag_items = [item for item in self.tags.items() if len(item[1]) > 0] 
        self.tag_items.sort(key=lambda x: len(x[1]), reverse=True)
        
    def finalize(self):
        self.tag_items = self.tags.items()
        file_count = len(self.files)
        for k, v in self.tag_items:
            if len(v) == file_count:
                self.remove_tag(k)
        self.sort_tag_items()
            
class YatfsCore():
    """ Main FS object """
    
    def __init__(self, database, rebuild):
        self.con = sqlite3.connect(database)
        if rebuild:
            self._recreate_tables()
            
    def __del__(self):
        self.con.close()
        
    def _recreate_tables(self):
        """ Drop existing tables and create new. """
        self.con.executescript("""
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
        """ Add tag and return it's id"""
        q = "INSERT INTO tags (tag_name) VALUES (?)"
        cur = self.con.execute(q, (tag_name, ))
        return cur.lastrowid
      
    def _get_tag_id(self, tag_name, add_if_not_exists=False):
        """ Returns the id of tag with provided name. """
        q = "SELECT id FROM tags WHERE tag_name = ?"
        row = self.con.execute(q, (tag_name, )).fetchone()
        if row is not None:
            return row[0]
        ## tag not found        
        if add_if_not_exists:
            return self._add_tag(tag_name)
        else:
            raise NameError("File not found", tag_name)

    def _get_tag_name(self, tag_id):
        """ Returns the name of tag"""
        q = "SELECT tag_name FROM tags WHERE id = ?"
        cur = self.con.execute(q, (tag_id, ))
        return cur.fetchone()[0]
    
        
    def _add_file_tags(self, file_id, tag_ids):
        """ Add file with tags to files_tags table"""
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
        for row in self.con.execute('SELECT * FROM ' + table_name):
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
            params = tag_ids + [len(tag_ids)]
        
        files_tags = FilesTags()
        cur = self.con.execute(query, params)
        for row in cur:
            files_tags.add(row[0], row[1])
        
        files_tags.finalize()
        return files_tags
                             
    def _get_file_extension(self, file_id):
        """ Get the file extension"""
        cur = self.con.execute('SELECT file_extension FROM files WHERE id = ?', (file_id, ))
        return cur.fetchone()[0]
    
    def _get_file_tag_id(self, file_id):
        """ Get the file_tag id (filename tag)"""
        cur = self.con.execute('SELECT file_tag_id FROM files WHERE id = ?', (file_id, ))
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
    
    def get_files_without_tags(self, files_tags):
        file_list = []
        for file_id, tags in files_tags.files.items():
            if len(tags) == 0:
               node = self._get_node(self._get_file_tag_id(file_id), 1, file_id)
               file_list.append(node) 
        return file_list                
        
    def get_file_list_short(self, tag_names):
        files_tags = self._get_tag_files(tag_names)
        file_list = []
        while True:
            if len(files_tags.tag_items) == 0:
                break
            tag, files = files_tags.tag_items[0]
            if (len(file_list) == 0) and (len(files) > 1):
                file_list.append({"type": "extension"})
                
            node = self._get_node(tag, len(files), files[0])
            file_list.append(node)
            
            files_tags.remove_tag_and_files(tag)
            files_tags.sort_tag_items()
            
        file_list.extend(self.get_files_without_tags(files_tags))
        return file_list
    
    def get_file_item(self, tag_names):
        files_tags = self._get_tag_files(tag_names)
        file_list = []       
    
    def get_file_list_full(self, tag_names):
        files_tags = self._get_tag_files(tag_names)
        file_list = []
        for tag, files in files_tags.tag_items:
            node = self._get_node(tag, len(files), files[0])
            file_list.append(node)
        file_list.extend(self.get_files_without_tags(files_tags))
        return file_list         
   
    


        
