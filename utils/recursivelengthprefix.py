import rlp as recursive_length_prefix

enc = recursive_length_prefix.encode([b'cat', b'dog'])
enc = recursive_length_prefix.encode([b'cat', [b'dog', b'woof', 2]])

print(enc)

dec = recursive_length_prefix.decode(enc)

print(dec)