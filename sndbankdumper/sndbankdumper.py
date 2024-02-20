import os
import parasyte as ps
import ctypes
import util
import config
import assettable

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
    # Make dir
    output_dir = f"output/{type_name}_{CURR_GAME}"
    os.makedirs(output_dir, exist_ok=True)

    # Read asset header
    pkg_header = util.read_struct(ps.PS_PROC, asset.Header, CURR_TYPE)
    # print('Name:', hex(pkg_header.Name))

    # If it has no alias, return
    if ((pkg_header.Count == 0) or (pkg_header.SndAliasList == 0)):
        return

    # print('SndAliasList:', hex(pkg_header.SndAliasList))
    asset_file_name = GET_XASSET_NAME(pkg_header.Name, type_name, assettable.BANK_ASSET_HASH_TABLE)

    # When a new bank name is hit, the old hash naming file will be deleted.
    # TODO: Not a good method but for temporary use.
    asset_hash = pkg_header.Name & 0xFFFFFFFFFFFFFFF
    file_hash_name = f"{type_name}_{asset_hash:x}"
    file_hash_path = f"{output_dir}/{file_hash_name}.csv"

    if (file_hash_name != asset_file_name) and (os.path.exists(file_hash_path)):
        os.remove(file_hash_path)
        print("Hit New Bank Name:", asset_file_name)
        print("Remove file:", file_hash_name)

    with open(f"{output_dir}/{asset_file_name}.csv", "w") as f:
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
                    aliasName = GET_XASSET_NAME(sndAlias.AliasName, '', assettable.STRING_HASH_TABLE)

                if sndAlias.SecondaryAliasName != 0:
                    secondaryAliasName = GET_XASSET_NAME(sndAlias.SecondaryAliasName, '', assettable.STRING_HASH_TABLE)

                if sndAlias.AssetFileName != 0:
                    file_hash = ps.PS_PROC.read_ulonglong(sndAlias.AssetFileName)
                    assetFileName = GET_XASSET_NAME(file_hash, 'xsound', assettable.SND_ASSET_HASH_TABLE)

                f.write(f"{aliasName},{secondaryAliasName},{assetFileName}\n")


def read_sndbank(asset: ps.XAsset64):
    dump_sndbank(asset, "soundbank")

def read_sndbank_tr(asset: ps.XAsset64):
    dump_sndbank(asset, "soundbanktr")


# Main func

# Load string hash table ingame
if config.load_string_table_ingame or config.only_export_string_table_ingame:
    util.load_string_hash_table_ingame(assettable.STRING_HASH_TABLE)
    print("Loaded string_hash_table_ingame.")

if config.only_export_string_table_ingame:
    print("Finished export stringtable(only).")
    exit()

# Load string hash table
if config.fill_string_table:
    assettable.load_alias_string_hash_table()
    print("Loaded string_hash_table.")

# Load sound asset hash table
if config.fill_snd_asset_table:
    # List
    assettable.load_snd_asset_hash_table()
    # Hash table
    util.load_hash_table("data/wni/fnv1a_xsounds.csv", assettable.SND_ASSET_HASH_TABLE)
    print("Loaded snd_asset_hash_table.")

# Load bank asset hash table
if config.fill_bank_asset_table:
    assettable.load_bank_asset_hash_table()
    print("Loaded bank_asset_hash_table.")

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