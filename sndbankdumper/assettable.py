import util

# Bank asset
BANK_ASSET_HASH_TABLE = {}

def load_bank_asset_hash_table():
    util.load_asset_list("data/table/bank.csv", BANK_ASSET_HASH_TABLE)


# Sound asset
SND_ASSET_HASH_TABLE = {}

def load_snd_asset_hash_table():
    util.load_asset_list("data/table/snd.csv", SND_ASSET_HASH_TABLE)

# Alias string
STRING_HASH_TABLE = {}

def load_alias_string_hash_table():
    util.load_alias_string_list("data/table/alias.csv", STRING_HASH_TABLE)