# Author: Jonah Bui
# Date
# Purpose:
# Changelogs:

from directory import *
import struct

def main():
    # Control variables
    # Continue the program until the user quits
    user_quit = False

    # Use to check if a file is currently in use. Cannot open multiple files at once
    file_open = False

    file = None
    filesystem = None
    cwd = 0
    root = 0
    dir = None

    while not user_quit:
        # Gets input
        user_input = input("mfs> ")
        user_input = user_input.lower()
        # Parse input
        user_input = user_input.split(' ')

        # Ignore empty inputs
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
        elif(user_input[0] == "quit"):
            user_quit = True
            if(file_open):
                filesystem = None
                file.close()
        elif(file_open):
            if(user_input[0] == "ls"):
                dir = GetDirectory(file, cwd)
                PrintDirectory(dir)
            elif(user_input[0] == "cd"):
                try:
                    # Delimit the directories by / to reference each individually
                    cd_token = user_input[1].strip()
                    cd_token = cd_token.split('/\\')

                    #
                    offset = 0
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
                        else:
                            break
                    
                    # Search was succesful, update the current working directory
                    if(index != -1):
                        cwd = offset
                        print(hex(offset))
                    # Search failed,
                    else:
                        print("Search failed")
                except IndexError:
                    print("Error: cd requires 2 valid parameters\n")
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
            elif(user_input[0] == "stat"):
                # FIXE HERE
                try:
                    index = FileMatch(dir, user_input[1])
                    print(index)
                    if(index != -1):
                        print(f"   | Attributes:\tFile Size:\tStarting Cluster Number:")
                        print(f"----------------------------------------------------------------")
                        print(f"Dec: {dir[index].attr : <11d}\t{dir[index].filesize: <11d}\t"+
                        f"{dir[index].firstClusterLow : <24d}")
                        print(f"Hex: {dir[index].attr : <11x}\t{dir[index].filesize: <11x}\t"+
                        f"{dir[index].firstClusterLow : <24x}\n")
                except IndexError:
                    print(f"Error: stat requires 2 valid parameters\n")
            elif(user_input[0] == "get"):
                pass
            else:
                print("Error: command not found\n")
        else:
            print("Error: file system must be opened first\n")


if __name__ == "__main__":
    main()