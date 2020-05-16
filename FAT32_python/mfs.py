# Author: Jonah Bui
# Date
# Purpose:
# Changelogs:

from directory import NextLB, LBAToOffset, GetFileSystemInfo, GetDirectory, FileMatch, PrintDirectory, DirectoryEntry
import struct

def main():
    ## Loops program until user quits
    user_quit = False

    # Use to check if a file is currently in use. Cannot open multiple files at once
    file_open = False

    file = None
    filesystem = None
    cwd = 0
    root = 0
    dir = []

    while not user_quit:
        ## Input
        user_input = input("mfs> ")
        user_input = user_input.lower()
        user_input = user_input.split(' ')

        if(len(user_input) == 0):
            continue

        # Opens a filesystem so the user can interact with it
        if(user_input[0] == "open"):
            # Open a filesystem if there is no files are currently being worked on
            if(not file_open):
                try:
                    file = open(user_input[1], 'rb+')
                    file_open = True

                    # Get information about the current filesystem
                    filesystem = GetFileSystemInfo(file)

                    # Set current working directory to root for initial file system usage
                    cwd = LBAToOffset(2, filesystem)
                    root = cwd
                    dir = GetDirectory(file, cwd)
                except OSError:
                    print("Error: file cannot be opened\n")
                except IndexError:
                    print("Error: open requires 2 parameters\n")
            else:
                print("Error: a file is currently opened. Close the current file first\n")
        # Closes a filesystem currently in use
        elif(user_input[0] == "close"):
            if(file_open):
                filesystem = None
                file.close()
                file_open = False
            else:
                print("Error: no file currently open\n")
        # Ends the program and frees necessary objects
        elif(user_input[0] == "quit"):
            user_quit = True
            if(file_open):
                filesystem = None
                file.close()
        elif(file_open):
            # Displays the contents of the current working directory
            if(user_input[0] == "ls"):
                dir = GetDirectory(file, cwd)
                PrintDirectory(dir)
            # Changes the current working directory
            elif(user_input[0] == "cd"):
                try:
                    # Delimit the directories by / to reference each individually
                    cd_token = user_input[1].strip()
                    
                    # Go to root directory if ~
                    if(user_input[1] == "~"):
                        dir = GetDirectory(file, root)
                        cwd = root
                        continue
                    
                    # Split token to determine the paths to check out
                    cd_token = cd_token.split('/')

                    # Use offset to the address to get directory info from
                    offset = 0

                    # Use index to store location of file found in the directory
                    index = -1

                    # Relative address
                    # Attempt to find each folder in path until the last one is found. If it could
                    # not be found, keep the user in the same directory when the command was called.
                    for i in range(len(cd_token)):
                        index = FileMatch(dir, cd_token[i])
                        if(index != -1):
                            if(dir[index].attr == 0x10):
                                if(dir[index].firstClusterLow == 0x0000):
                                    offset = LBAToOffset(2, filesystem)
                                else:
                                    offset = LBAToOffset(dir[index].firstClusterLow, filesystem)
                                dir = GetDirectory(file, offset)
                            else:
                                print("Error: not a directory\n")
                                index = -1
                                continue
                        else:
                            break
                    
                    # Search was succesful, update the current working directory
                    if(index != -1):
                        cwd = offset
                    # Search failed
                    else:
                        print("Search failed")
                except IndexError:
                    print("Error: cd requires 2 valid parameters\n")
            # Displays info about the current filesystem
            elif(user_input[0] == "info"):
                print(f"\nBPB_BytesPerSec: \nDec = {filesystem.BPB_BytesPerSec} "+
                f"\nHex = {hex(filesystem.BPB_BytesPerSec)}\n")
                print(f"BPB_SecPerClus: \nDec = {filesystem.BPB_SecPerClus} "+
                f"\nHex = {hex(filesystem.BPB_SecPerClus)}\n")
                print(f"BPB_RsvdSecCnt: \nDec = {filesystem.BPB_RsvdSecCnt} "+
                f"\nHex = {hex(filesystem.BPB_RsvdSecCnt)}\n")
                print(f"BPB_NumFATS: \nDec = {filesystem.BPB_NumFATS} "+
                f"\nHex = {hex(filesystem.BPB_NumFATS)}\n")
                print(f"BPB_FATSz32: \nDec = {filesystem.BPB_FATSz32} "+
                f"\nHex = {hex(filesystem.BPB_FATSz32)}\n")
            # Displays info about a file
            elif(user_input[0] == "stat"):
                try:
                    index = FileMatch(dir, user_input[1])
                    if(index != -1):
                        print(f"   | Attributes:\tFile Size:\tStarting Cluster Number:")
                        print(f"----------------------------------------------------------------")
                        print(f"Dec: {dir[index].attr : <11d}\t{dir[index].filesize: <11d}\t"+
                        f"{dir[index].firstClusterLow : <24d}")
                        print(f"Hex: {dir[index].attr : <11x}\t{dir[index].filesize: <11x}\t"+
                        f"{dir[index].firstClusterLow : <24x}\n")
                    else:
                        print("Error: file not found\n")
                except IndexError:
                    print(f"Error: stat requires 2 valid parameters\n")
            # Retrieves a file from the system and places in the cwd
            elif(user_input[0] == "get"):
                try:
                    ## Ignore files that are already in the cwd
                    # Get file if not in cwd
                    index = FileMatch(dir, user_input[1])
                    if( index == -1):
                        # Create queue to perform BPS at root directory to search for file
                        queue = []
                        file_found = -1

                        # Enqueue root directory to start BFS
                        queue.append(root)

                        ## BFS
                        while( len(queue) != 0 and file_found == -1):
                            dequeued_address = queue.pop(0)
                            dir = GetDirectory(file, dequeued_address)
                            file_found = FileMatch(dir, user_input[1])

                            ## File found, place it the cwd
                            if( file_found != -1 ):
                                file.seek(dequeued_address+32*file_found)
                                dir_to_write = file.read(32)
                                ## Find free entry to place file into in cwd
                                file.seek(cwd)
                                for j in range(16):
                                    check_name = struct.unpack("<B", file.read(1))[0]
                                    if(check_name == 0x00 or check_name == 0xe5):
                                        file.seek(cwd+j*32)
                                        file.write(dir_to_write)

                                        ## Mark original file as deleted
                                        file.seek(dequeued_address+file_found*32)
                                        file.write(bytes([0xe5]))
                                        break
                                    else:
                                        file.seek(31, 1)
                            else:
                                ## File not found; enqueue directories in the cwd to be searched
                                for i in range(16):
                                    if(dir[i].attr == 0x10 and dir[i].name[0] != 0xe5 and dir[i].name[0] != 0x00 ):
                                        validating_address = dir[i].firstClusterLow
                                        if(validating_address != root and validating_address != dequeued_address and
                                        dir[i].name[0] != 0x2e and dir[i].name[1] != 0x2e):
                                            queue.append(LBAToOffset(validating_address, filesystem))
                    if( file_found == -1 ):
                        print("Error: file not found\n")
                except:
                    print("Error: get needs 2 valid arguments\n")
            # Prints out the file's contents
            elif(user_input[0] == "read"):
                try:
                    # Use to determine where to read data
                    offset = 0

                    bytes_to_read = 0
                    # Find file to read
                    index = FileMatch(dir, user_input[1])
                    if(index != -1 and dir[index].attr != 0x10 and dir[index].name[0] != 0xe5 and
                    (dir[index].attr == 0x01 or dir[index].attr == 0x20)):
                        # Use to store posiion to offset from
                        offset_start = int(user_input[2])
                       
                        # Set the number of bytes to read in
                        if(user_input[3] == "max"):
                            bytes_to_read = dir[index].filesize
                        else:
                            bytes_to_read = int(user_input[3])

                        # Use to track number of bytes to print
                        bytes_to_read_temp = bytes_to_read

                        # Determine max number of bytes readable due to offset in the file
                        num_readable_bytes = dir[index].filesize - offset_start

                        # Don't allow starting offsets to exceed file size
                        if(offset_start >= dir[index].filesize):
                            print("Error: initial offset is greater than file size")

                        # Adjust readable file size for position offset into file; need to calculate
                        # appropriate number of bytes to read
                        lb = dir[index].firstClusterLow
                        offset = LBAToOffset(lb, filesystem)+offset_start

                        # Don't allow reads greater than the adjusted filesize
                        if(bytes_to_read > num_readable_bytes):
                            bytes_to_read = num_readable_bytes
                            bytes_to_read_temp = num_readable_bytes
                        
                        # Print out contents of file
                        file.seek(offset)
                        ## NEED TO FIX PRINTING
                        while( lb != -1 ):
                            if( bytes_to_read_temp < 512):
                                to_print = struct.unpack(f"<{bytes_to_read_temp}s", file.read(bytes_to_read_temp))[0]
                                print(''.join('{:x}'.format(x) for x in to_print), end='')
                                bytes_to_read_temp = 0
                                break
                            to_print = struct.unpack("<512s", file.read(512))[0]
                            print(''.join('{:x}'.format(x) for x in to_print), end='')
                            bytes_to_read_temp-= 512

                            lb = NextLB(lb, filesystem, file)
                            if( lb != -1 ):
                                offset = LBAToOffset(lb, filesystem)
                                file.seek(offset)
                        print()
                    else:
                        print("Error: file not found or not file\n")
                except IndexError:
                    print("Error: read needs 4 valid arguments\n")
                except struct.error:
                    print("Error reading from struct\n")
            # Removes a file in the cwd
            elif( user_input[0] == "rm"):
                try:
                    index = FileMatch(dir, user_input[1])
                    print(user_input[1])
                    print(index)
                    if( index != -1 ):
                        file.seek(cwd + 32*index)
                        file.write(bytes([0xe5]))
                except:
                    print("Error: rm needs 2 valud arguments\n")
            else:
                print("Error: command not found\n")

        else:
            print("Error: file system must be opened first\n")

if __name__ == "__main__":
    main()