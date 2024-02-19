import struct
import ctypes
import pymem
import os

# Parasyte's State File Name (Relative to its EXE).
STATE_FILE = "Data\\CurrentHandler.csi"


# A class to hold Parasyte State Information.
class State:
    def __init__(self, path):
        with open(path, 'rb') as f:
            self.game_id = struct.unpack("Q", f.read(8))[0]
            self.pools_address = struct.unpack("Q", f.read(8))[0]
            self.strings_address = struct.unpack("Q", f.read(8))[0]
            self.game_directory = f.read(struct.unpack("I", f.read(4))[0])
            self.game_directory = self.game_directory.decode("utf-8")


# Parasytes XAsset Structure.
class XAssetPool64(ctypes.Structure):
    _fields_ = [
        # The start of the asset chain.
        ("Root", ctypes.c_uint64),
        # The end of the asset chain.
        ("End", ctypes.c_uint64),
        # The asset hash table for this pool.
        ("LookupTable", ctypes.c_uint64),
        # Storage for asset headers for this pool.
        ("HeaderMemory", ctypes.c_uint64),
        # Storage for asset entries for this pool.
        ("AssetMemory", ctypes.c_uint64),
    ]


# Parasytes XAsset Structure.
class XAsset64(ctypes.Structure):
    _fields_ = [
        # The asset header.
        ("Header", ctypes.c_uint64),
        # Whether or not this asset is a temp slot.
        ("Temp", ctypes.c_uint64),
        # The next xasset in the list.
        ("Next",  ctypes.c_uint64),
    ]


# Parse the pool, givin the current offset and asset type
#      - The offset is where you wish to begin reading from,
#        for start of pool, aquire this from the asset pool's "FirstXAsset"
#      - The request function is for you to provide the parser with the XAsset
#        using your own internal process reading methods.
#      - The callback is provided for when a valid asset is read, this is when
#        you can add the asset to tables or process it.
def PoolParser64(offset, request, callback):
    p = request(offset)
    while True:
        if p.Header != 0:
            callback(p)
        if p.Next == 0:
            break
        p = request(p.Next)


def get_state_file_path(pm):
    for m in pm.list_modules():
        if "cordycep.cli.exe" in os.path.basename(m.filename).lower():
            return os.path.join(os.path.dirname(m.filename), STATE_FILE)


PS_PROC = pymem.Pymem("cordycep.cli.exe")
STATE = State(get_state_file_path(PS_PROC))