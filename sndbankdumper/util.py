import ctypes
import parasyte as ps
import config

def hash_asset(data: str):
	result = 0x47F5817A5EF961BA

	for i in range(len(data)):
		value = data[i].lower()
		if (value == '\\'):
			value = '/'

		result = 0x100000001B3 * (ord(value) ^ result)

	return result & 0x7FFFFFFFFFFFFFFF

def hash_sound_string(data: str):
	result = 0xCBF29CE484222325

	for i in range(len(data)):
		value = data[i].lower()
		if (value == '\\'):
			value = '/'

		result = 0x100000001B3 * (ord(value) ^ result)

	return result & 0x7FFFFFFFFFFFFFFF

def load_hash_table(file_path: str, hash_table: dict):
    with open(file_path, "r") as f:
        for line in f:
            line = line.strip('\n')
            line_split = line.strip().split(",")
            hash_table[int(line_split[0], 16)] = line_split[-1]

def load_alias_string_list(file_path: str, hash_table: dict):
    with open(file_path, "r") as f:
        for line in f:
            line = line.strip('\n')
            hash = hash_sound_string(line) & 0xFFFFFFFFFFFFFFF
            hash_table[hash] = line

def load_asset_list(file_path: str, hash_table: dict):
    with open(file_path, "r") as f:
        for line in f:
            line = line.strip('\n')
            hash = hash_asset(line) & 0xFFFFFFFFFFFFFFF
            hash_table[hash] = line

def read_struct(pm, address, structType, index=0):
    size = ctypes.sizeof(structType)
    buf = pm.read_bytes(address + index * size, size)
    result = structType()
    ctypes.memmove(ctypes.pointer(result), buf, size)
    return result

def get_hashed_asset_name(asset_hash: int, asset_type: str, hash_table: dict):
    asset_hash = asset_hash & 0xFFFFFFFFFFFFFFF

    if asset_hash in hash_table:
        if config.debug_mode:
            print(hash_table[asset_hash])

        return hash_table[asset_hash]

    if asset_type == "":
        return f"{asset_hash:x}"

    return f"{asset_type}_{asset_hash:x}"

def get_normal_asset_name(asset_name: int):
    return ps.PS_PROC.read_string(asset_name, 256)

def load_string_hash_table_ingame(hash_table: dict):
    with open(f"output/stringtable_dumped.csv", "w") as f:
        address = ps.STATE.strings_address

        while True:
            str = get_normal_asset_name(address)

            # Return if no more string
            if len(str) == 0:
                break

            address += len(str) + 1

            f.write(f"{str}\n")

            if "," in str and str.split(",")[0] != "":
                str = str.split(",")[0]
                # print(str)

            if str in hash_table:
                continue

            hash = hash_sound_string(str) & 0xFFFFFFFFFFFFFFF
            hash_table[hash] = str

            if str.startswith("ps_"):
                str = str.replace("ps_", "")
                hash = hash_sound_string(str) & 0xFFFFFFFFFFFFFFF
                hash_table[hash] = str

            # print(hash, ":", str)
