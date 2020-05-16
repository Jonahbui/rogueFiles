# mfs.py
A program that can read a fat32 image programmed in python
## Author
Jonah Bui
## Files included
- mfs.py: the main program that runs reads and manipulates the fat32 image
- directory.py: provides functions and classes that allow mfs.py to read in data from the fat32 image

## Functions
open 'file_name'
    Opens a filesystem passed in as an input argument.
close
    Closes the current filesystem open if there is one.
quit
    Closes the program.
ls
    Displays the contents of the current working directory of the filesystem.
cd 'dir_path'
    Changes the cwd in the filesystem. Works with absolute and relative addresses.
info
    Displays the information about the filesystem currently open
stat 'file_name"
    Displays info about the file
get 'file_name"
    Finds the filename passed in and places it in the cwd
read 'file_name' 'start_offset' 'bytes_to_read' 'format'
    Reads the file passed in at the given byte start_offset and up to bytes_to_read. Specifying 'ascii' in 'format' will print ascii. Default is hex values.
rm 'file_name'
    Deletes a file.
