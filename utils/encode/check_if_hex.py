import re

def are_keys_hexadecimal(d):
    hex_pattern = re.compile(r'^[0-9a-fA-F]+$')
    return all(hex_pattern.match(key) for key in d.keys())