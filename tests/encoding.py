from ipld import marshal, multihash, unmarshal

hi = {
    'a': 1,
    'b': {
        "A": "Alice",
        "B": "Bob"
    }
}

serialized = marshal(hi)
print('serialized', serialized)
print('Its of type ', type(serialized))

deserialized = unmarshal(serialized)
print('deserialized', deserialized)
print('Its of type', type(deserialized))