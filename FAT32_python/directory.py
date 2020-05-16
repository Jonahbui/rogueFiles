import struct

def Compare(filename, input):
    '''
    Function
    -----------------------------------------------------------------------------------------------
    Compares the input to the filename encoded in the filesystem's format to see if they are 
    equivalent.
    Parameters
    -----------------------------------------------------------------------------------------------
    filename : string
        Filename presented in the filesystem to compare to.
    input : string
        Filename user enters to check against the fileystem's filename
    Returns
    -----------------------------------------------------------------------------------------------
    Returns False if not equal. True if equal.
    '''
    parse = input.upper()
    parse = parse.split('.')
    adjusted_name = parse[0]
    for i in range(8-len(parse[0])):
        adjusted_name+=' '

    try:
        adjusted_name+=parse[1]
    except IndexError:
        adjusted_name+="   "

    # Note filename is 
    if(filename.decode("ASCII") == adjusted_name):
        return True
    return False

def FileMatch(dir, match):
    '''
    Function
    -----------------------------------------------------------------------------------------------
    Finds a file name given a filename
    Parameters
    -----------------------------------------------------------------------------------------------
    dir : DirectoryEntry[]
        A list holding the directory entries
    match : string
        The name of the file to read
    Returns
    -----------------------------------------------------------------------------------------------
    Returns -1 if the file could not be found. Else it returns a number from 0 to 15 indicating the
    index of the file searched.
    '''
    for i in range(16):
        if(dir[i].name[0] == 0xe5):
            continue

        if(dir[i].name[0] != 0x2e and Compare(dir[i].name, match)):
            return i
        elif(dir[i].name[0] == 0x2e == dir[i].name[1] and match == ".."):
            return i
        elif(dir[i].name[0] == 0x2e != dir[i].name[1] and match == "."):
            return i
    return -1

def PrintDirectory(dir):
    '''
    Function
    -----------------------------------------------------------------------------------------------
    Given a directory, prints all the files in the directory that should be displayed to a user.
    Does not display deleted files, system volumes, or system files.
    Parameters
    -----------------------------------------------------------------------------------------------
    dir : DirectoryEntry[]
        A list of directory entries to print out
    Returns
    -----------------------------------------------------------------------------------------------
    Nothing
    '''
    for i in range(16):
        if(dir[i].name[0] == 0xe5):
            continue
        
        # Only print directories, modified files, and read-only files. Don't show deleted files,
        # system files, or system volume names.
        if(dir[i].attr == 0x01 or dir[i].attr == 0x10 or dir[i].attr == 0x20 or dir[i].attr == 0x30):
            # Check if first char of filename is 0x05 and replace it with 0xe5. 0x05 represents a
            # file who's original byte is actually 0xe5 but 0xe5 is reserved for a deleted file
            if(dir[i].name[0] == 0x05):
                dir[i].name[0] == 0xe5
                print(dir[i].name.decode("ASCII"))
                dir[i].name[0] = 0x05
                continue
            
            # If not 0xe5 at beginning filename, print normally
            print(dir[i].name.decode("ASCII"))
    print()

def LBAToOffset(sector, filesystem):
    '''
    Function
    -----------------------------------------------------------------------------------------------
    Finds the starting address of a block of data given the sector number corresponding to that data
    block.
    Parameters
    -----------------------------------------------------------------------------------------------
    sector : int
        A sector number.
    filesystem : FileSystem
        A class used to hold the information about a given filesystem.
    Returns
    -----------------------------------------------------------------------------------------------
    The value of the address for that block of data.
    '''
    return (((sector - 2) *  filesystem.BPB_BytesPerSec)
    +(filesystem.BPB_BytesPerSec * filesystem.BPB_RsvdSecCnt)
    +(filesystem.BPB_NumFATS * filesystem.BPB_FATSz32 * filesystem.BPB_BytesPerSec)
    )

def NextLB(sector, filesystem, file):
    '''
    Function
    -----------------------------------------------------------------------------------------------
    Given a logical block address, look up into the first FAT and return the logical block address 
    of the block in the file.
    Parameters
    -----------------------------------------------------------------------------------------------
    sector : int
        A sector number.
    filesystem: FileSystem
        A class used to hold the information about a given filesystem.
    file : File
        The filesystem that is currently opened and has the corresponding FileSystem passed in.
    Returns
    -----------------------------------------------------------------------------------------------
    Returns -1 if no further blocks. Else returns the next logical block.
    '''
    FATAddress = (filesystem.BPB_BytesPerSec * filesystem.BPB_RsvdSecCnt) + (sector * 4)
    file.seek(FATAddress, 0)
    return struct.unpack("<H",file.read(2))[0]

def GetFileSystemInfo(file):
    '''
    Function
    -----------------------------------------------------------------------------------------------
    Gets the information about the filesystem passed in through 'file'.
    Parameters
    -----------------------------------------------------------------------------------------------
    file : File
        The current filesystem opened.
    Returns
    -----------------------------------------------------------------------------------------------
    Returns a FileSystem containing all the information about the filesystem opened.
    '''
    # Bytes Per Sector
    file.seek(11, 0)
    BPB_BytesPerSec = struct.unpack("<H", file.read(2))[0]
    
    # Sectors Per Cluster
    file.seek(13, 0)
    BPB_SecPerClus = struct.unpack("<B", file.read(1))[0]

    # Reserved Sector Count
    file.seek(14, 0)
    BPB_RsvdSecCnt = struct.unpack("<H", file.read(2))[0]

    # Number FATs
    file.seek(16, 0)
    BPB_NumFATS = struct.unpack("<B", file.read(1))[0]

    # Fat Size
    file.seek(36, 0)
    BPB_FATSz32 = struct.unpack("<I", file.read(4))[0]

    return FileSystem(BPB_BytesPerSec, BPB_SecPerClus, BPB_RsvdSecCnt, 
    BPB_NumFATS, BPB_FATSz32)

def GetDirectory(file, address):
    '''
    Function
    -----------------------------------------------------------------------------------------------
    Gets files in a directory

    Parameters
    -----------------------------------------------------------------------------------------------
    dir : DirectoryEntry[16]
        A list of directory entries that will be used to hold the files in a directory.
    filesystem: FILE
        A file to read the bytes from.
    address : int
        The address of a directory to read from

    Returns
    -----------------------------------------------------------------------------------------------
    A list of DirectoryEntry that holds the information of each file in a directory
    '''
    dir = []
    # Read in current directory entry information

    # .read(number_of_bytes) function
    # number_of_bytes: number of bytes to read in
    
    #.seek(offset[, whence])
    # offset: position of the read/write pointer within the file
    # whence: 0 means absolute file position, 1 means relative to current position, 2 means relative
    # to file's end

    file.seek(address, 0)
    for i in range(16):
        # Name
        name = struct.unpack("<11s", file.read(11))[0]
        # Attributes
        attr = struct.unpack("<B", file.read(1))[0]
        # Unused1
        unused1 = struct.unpack("<8B", file.read(8))[0]
        # First Cluster High
        firstClusterHigh = struct.unpack("<H", file.read(2))[0]
        # Unused2
        unused2 = struct.unpack("<4B", file.read(4))[0]
        # First Cluster Low
        firstClusterLow = struct.unpack("<H", file.read(2))[0]
        # File Size
        filesize = struct.unpack("<I", file.read(4))[0]
        dir.append(
            DirectoryEntry(name, attr, unused1, firstClusterHigh, unused2, firstClusterLow,
            filesize)
        )
    return dir

class DirectoryEntry():
    def __init__(self, name, attr, unused1, firstClusterHigh, unused2, firstClusterLow, filesize):
        self.name = name
        self.attr = attr
        self.unused1 = unused1
        self.firstClusterHigh = firstClusterHigh
        self.unused2 = unused2
        self.firstClusterLow = firstClusterLow
        self.filesize = filesize

class FileSystem():
    def __init__(self, BPB_BytesPerSec, BPB_SecPerClus, BPB_RsvdSecCnt, BPB_NumFATS, BPB_FATSz32):
        self.BPB_BytesPerSec = BPB_BytesPerSec
        self.BPB_SecPerClus = BPB_SecPerClus
        self.BPB_RsvdSecCnt = BPB_RsvdSecCnt
        self.BPB_NumFATS = BPB_NumFATS
        self.BPB_FATSz32 = BPB_FATSz32