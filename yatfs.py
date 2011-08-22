#!/usr/bin/env python

import fuse
import os
from yatfscore import YatfsCore

fuse.fuse_python_api = (0, 2)

class YatFS(fuse.Fuse):
    """
    """

    def __init__(self, *args, **kw):
        fuse.Fuse.__init__(self, *args, **kw)
        self.README = 'This is YatFS\n'
        self.source_path = '/'
        self.core = None
        self.case_sensitive = False
        
    def path_to_tags(self, path):
        if not self.case_sensitive:
            path = path.lower()
        tags = path.split(os.sep)
        tags = filter(lambda x: len(x)>0, tags) #remove empty strings
        tags = list(set(tags)) #remove duplicates
        return tags

    def init_core(self):
        self.core = YatfsCore("", True) 
        self.source_path = self.source_path.decode('utf-8')
        prefix_length = len(self.source_path) + 1

        for root, dirs, files in os.walk(self.source_path): 
            path = root[prefix_length:]
            tags = self.path_to_tags(path)
            for file in files:
                file_tag, dot, file_extension = file.rpartition(".")
                if not self.case_sensitive:
                    file_tag = file_tag.lower()
                file_path =  root + os.sep + file
                self.core.add_file(tags, file_tag, file_path, file, file_extension) 

    def main(self):
        self.init_core()
#        fuse.Fuse.main(self)
    
    def readdir(self, path, offset):
        # 
        yield fuse.Direntry('.')
        yield fuse.Direntry('..')
        if path == '/':
            # 
            yield fuse.Direntry('README')
            yield fuse.Direntry('simple')


    
def main():
    usage = """Yet Another Tag Filesystem
    """ + fuse.Fuse.fusage
  
    server = YatFS(version="%prog " + fuse.__version__,
                 usage=usage,
                 dash_s_do='setsingle')

    server.parser.add_option(mountopt="source-path", metavar="PATH", dest="source_path",
                             help="source path")
    #server.parser.add_option("--case-sensitive", dest="case_sensitive", action="store_true",  default=True, 
    #                         help="should be tags case sensitive")

    server.parse(values=server, errex=1)
    print server.source_path
    server.main()

if __name__ == '__main__':
    main()
