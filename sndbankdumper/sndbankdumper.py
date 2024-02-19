import os
import parasyte as ps
import ctypes
import util
import config
import assettable

STRING_HASH_TABLE = {}

# Type definition
class MW6XSndBank(ctypes.Structure):
    _fields_ = [
        ("Name", ctypes.c_uint64),
        ("Padding", ctypes.c_uint64 * 3),
        ("Count", ctypes.c_uint64),
        ("SndAliasList", ctypes.c_uint64),
    ]

class MW6XSndAlias(ctypes.Structure):
    _fields_ = [
        ("Padding", ctypes.c_uint64 * 4),
        ("AliasName", ctypes.c_uint64),
        ("SecondaryAliasName", ctypes.c_uint64),
        ("AssetFileName", ctypes.c_uint64),
    ]

# Check game
if ps.STATE.game_id == 0x4B4F4D41594D4159:
    CURR_GAME = "mw6"
    CURR_TYPE = MW6XSndBank
    GET_XASSET_NAME = util.get_hashed_asset_name
    SOUND_BANK_TRANSIENT_INDEX = 0x27
    SOUND_BANK_INDEX = 0x25
else:
    print("The game is unsupported.")
    exit()

# Base func
def dump_sndbank(asset: ps.XAsset64, type_name: str):
    os.makedirs(f"{type_name}_{CURR_GAME}", exist_ok=True)

    pkg_header = util.read_struct(ps.PS_PROC, asset.Header, CURR_TYPE)
    # print('Name:', hex(pkg_header.Name))

    if ((pkg_header.Count == 0) or (pkg_header.SndAliasList == 0)):
        return

    # print('SndAliasList:', hex(pkg_header.SndAliasList))
    asset_file_name = GET_XASSET_NAME(pkg_header.Name, type_name, assettable.BANK_ASSET_HASH_TABLE)
    with open(f"{type_name}_{CURR_GAME}\\{asset_file_name}.csv", "w") as f:
        f.write("name,secondary,file\n")

        for i in range(pkg_header.Count):
            sndAliasList_ptr = pkg_header.SndAliasList + (i * 8 * 6)
            sndAlias_count = ps.PS_PROC.read_ushort(sndAliasList_ptr + (8 * 3))

            sndAlias_ptr = ps.PS_PROC.read_ulonglong(sndAliasList_ptr)
            # print('sndAlias_ptr:', hex(sndAlias_ptr))

            for j in range(sndAlias_count):
                sndAlias = util.read_struct(ps.PS_PROC, sndAlias_ptr + (j * 8 * 8), MW6XSndAlias)

                aliasName = ""
                secondaryAliasName = ""
                assetFileName = ""

                if sndAlias.AliasName != 0:
                    aliasName = GET_XASSET_NAME(sndAlias.AliasName, '', STRING_HASH_TABLE)

                if sndAlias.SecondaryAliasName != 0:
                    secondaryAliasName = GET_XASSET_NAME(sndAlias.SecondaryAliasName, '', STRING_HASH_TABLE)

                if sndAlias.AssetFileName != 0:
                    file_hash = ps.PS_PROC.read_ulonglong(sndAlias.AssetFileName)
                    assetFileName = GET_XASSET_NAME(file_hash, 'xsound', assettable.SND_ASSET_HASH_TABLE)

                f.write(f"{aliasName},{secondaryAliasName},{assetFileName}\n")


def read_sndbank(asset: ps.XAsset64):
    dump_sndbank(asset, "soundbank")

def read_sndbank_tr(asset: ps.XAsset64):
    dump_sndbank(asset, "soundbanktr")


# Main func

# Load string hash table
if config.fill_string_table or config.only_export_string_table:
    util.load_string_hash_table(STRING_HASH_TABLE)
    print("string_hash_table Loaded.")

if config.only_export_string_table:
    print("only export stringtable Finished.")
    exit()

# Load sound asset hash table
if config.fill_asset_table:
    assettable.load_snd_asset_hash_table()
    util.load_hash_table("wni\\fnv1a_xsounds.csv", assettable.SND_ASSET_HASH_TABLE)
    print("snd_asset_hash_table Loaded.")

# Load bank asset hash table
if config.fill_bank_asset_table:
    assettable.load_bank_asset_hash_table()
    print("bank_asset_hash_table Loaded.")

# Sound Bank dumper
if config.dump_sndbank:
    xasset_pool_bank = util.read_struct(
    ps.PS_PROC,
    ps.STATE.pools_address,
    ps.XAssetPool64,
    SOUND_BANK_INDEX)

    ps.PoolParser64(
        xasset_pool_bank.Root,
        lambda x: util.read_struct(ps.PS_PROC, x, ps.XAsset64),
        read_sndbank)
    print("Dumped Sound Bank.")

# Sound Bank Transient dumper
if config.dump_sndbank_tr:
    xasset_pool_banktr = util.read_struct(
    ps.PS_PROC,
    ps.STATE.pools_address,
    ps.XAssetPool64,
    SOUND_BANK_TRANSIENT_INDEX)

    ps.PoolParser64(
        xasset_pool_banktr.Root,
        lambda x: util.read_struct(ps.PS_PROC, x, ps.XAsset64),
        read_sndbank_tr)
    print("Dumped Sound Bank Transient.")


# Done
print("Finished.")