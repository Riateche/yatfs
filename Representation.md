# Database #
Root folder of real filesystem must contains database file naming ".yatfs.sqlite". This file can be created automatically.

# Tags #
File with name "filename" and tags "tag1", "tag2" is storing at path "/tag1/tag2/filename". To minimize the number of real directories yatfs order the directories by tag usage. For example: "filename" has "tag1", "tag2". "Tag1" used 5 times, "Tag2" - 10 times. the real path would be /tag2/tag1/filename.