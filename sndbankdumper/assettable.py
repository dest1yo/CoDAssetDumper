import util

# Bank asset
BANK_ASSET_TABLE = [
    # "bank_name_example1",
    # "bank_name_example2",
]

BANK_ASSET_HASH_TABLE = {}

def load_bank_asset_hash_table():
    if len(BANK_ASSET_TABLE):
        for name in BANK_ASSET_TABLE:
            hash = util.hash_asset(name) & 0xFFFFFFFFFFFFFFF
            BANK_ASSET_HASH_TABLE[hash] = name


# Sound asset
SND_ASSET_TABLE = [
    "defaultsndasset"
]

SND_ASSET_HASH_TABLE = {}

def load_snd_asset_hash_table():
    if len(SND_ASSET_TABLE):
        for name in SND_ASSET_TABLE:
            hash = util.hash_asset(name) & 0xFFFFFFFFFFFFFFF
            SND_ASSET_HASH_TABLE[hash] = name

