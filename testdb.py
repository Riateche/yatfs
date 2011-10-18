#!/usr/bin/env python

import os
from optparse import OptionParser
from yatfscore import YatfsCore

def path_to_tags(path, case_sensitive):
    if not case_sensitive:
        path = path.lower()
    tags = path.split(os.sep)
    tags = filter(lambda x: len(x)>0, tags) #remove empty strings
    tags = list(set(tags)) #remove duplicates
    return tags

def get_yatfs(folder, case_sensitive):
    db = YatfsCore("", True) 
    prefix_length = len(folder) + 1

    for root, dirs, files in os.walk(folder): #@UnusedVariable
        path = root[prefix_length:]
        tags = path_to_tags(path, case_sensitive)
        for file in files:
            file_tag, dot, file_extension = file.rpartition(".")
            if not case_sensitive:
                file_tag = file_tag.lower()
            file_path =  root + os.sep + file
            db.add_file(tags, file_tag, file_path, file, file_extension) 
    return db

def output_file_list(file_list):
    for file in file_list:
        if file["type"] == "folder":
            print file["name"] + "\\"
        else:
            if file["type"] == "extension":
                print "+\\"
            else:
                print file["name"]

def print_folder_contents(db, folder, case_sensitive):
    tags = path_to_tags(folder, case_sensitive)
    if tags.count('+') > 0:
        tags.remove('+')
        output_file_list(db.get_file_list_full(tags))
    else:
        output_file_list(db.get_file_list_short(tags))
def get_text_attr(db, path, case_sensitive):
    if path[-1] == '+':
        return "extension"
    tags = path_to_tags(folder, case_sensitive)
    
    return "unknown"
    
def print_folder_contents2(db, folder, case_sensitive):
    tags = path_to_tags(folder, case_sensitive)
    if tags.count('+') > 0:
        tags.remove('+')
        file_list = db.get_file_list_full(tags)
    else:
        file_list = db.get_file_list_short(tags)
    
    for file in file_list:
        if file["type"] == "extension":
            file_name = "+"
        else:
            file_name = file["name"]
        file_name = folder + "/" + file_name     
        print file_name + "\t" + get_text_attr(db, file_name, case_sensitive)
         

def main():
    usage = "usage: %prog [options] arg"
    parser = OptionParser(usage)
    parser.set_defaults(case_sensitive=False)
    parser.add_option("-c", "--case-sensetive",
                      action="store_true", dest="case_sensitive")
    (options, args) = parser.parse_args()
    if len(args) != 1:
        parser.error("incorrect number of arguments")

    db = get_yatfs(args[0].decode('utf-8'), options.case_sensitive)    

    print "enter q to exit"
    while True:
        folder = raw_input("Folder path: ")
        
        if folder == "q":
            break
        print_folder_contents2(db, folder.decode('utf-8'), options.case_sensitive) 

if __name__ == '__main__':
    main()
