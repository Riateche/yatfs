#!/usr/bin/env python
import fuse

fuse.fuse_python_api = (0, 2)

class YatFS(fuse.Fuse):
    """
    """

    def __init__(self, *args, **kw):
        fuse.Fuse.__init__(self, *args, **kw)
        self.README = 'This is YatFS\n'
        self.source_path = '/'
    def readdir(self, path, offset):
        # 
        yield fuse.Direntry('.')
        yield fuse.Direntry('..')
        if path == '/':
            # 
            yield fuse.Direntry('README')
            yield fuse.Direntry('simple')


    
def main():
    usage = """
        Yatfs

    """ + fuse.Fuse.fusage

  
    server = YatFS(version="%prog " + fuse.__version__,
                 usage=usage,
                 dash_s_do='setsingle')

    server.parser.add_option(mountopt="source", metavar="PATH", default='/',
                             help="source folder")
    server.parse(values=server, errex=1)
    server.main()

if __name__ == '__main__':
    main()
