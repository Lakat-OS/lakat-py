import varint
from utils.encode.hashing import varint_decode
from config.encode_cfg import ENCODING_FUNCTION

# Decoding type mapping
LANGUAGE_DECODING_TYPES = {
    1: 'utf-8',
    2: 'utf-16',
    3: 'utf-32',
    4: 'ascii',
    5: 'iso-8859-1',
    6: 'windows-1252',
    7: 'gb18030'
}

# Encoding type mapping
LANGUAGE_ENCODING_TYPES = {
    'utf-8': 1,
    'utf-16': 2,
    'utf-32': 3,
    'ascii': 4,
    'iso-8859-1': 5,
    'windows-1252': 6,
    'gb18030': 7
}

def encode_string_standard(s):
    return encode_string(s, ENCODING_FUNCTION)


def encode_string(s, encoding_type='utf-8'):
    """
    Encodes a string with a specified encoding and prepends the encoding type and length using varints.

    :param s: String to be encoded.
    :param encoding_type: Encoding type ('utf-8', 'utf-16', 'utf-32', 'ascii', 'iso-8859-1', 'windows-1252', 'gb18030').
    :return: Encoded bytes including the header.
    """

    # Encode the string
    encoded_str = s.encode(encoding_type)

    # Encode the encoding type and length as varints
    encoding_byte = varint.encode(LANGUAGE_ENCODING_TYPES.get(encoding_type, 1))  # Default to utf-8
    length_bytes = varint.encode(len(encoded_str))

    # Combine the encoded type, length, and string data
    return encoding_byte + length_bytes + encoded_str

def decode_bytes(encoded_bytes):
    """
    Decodes the given bytes to a string based on the custom format using varints.

    :param encoded_bytes: Bytes to be decoded.
    :return: Decoded string.
    """

    # Decode the encoding type
    encoding_type_value, offset = varint_decode(encoded_bytes)
    encoding_type = LANGUAGE_DECODING_TYPES.get(encoding_type_value, 'utf-8')  # Default to utf-8

    # Decode the length
    length, length_offset = varint_decode(encoded_bytes[offset:])

    # Extract and decode the string
    string_data = encoded_bytes[offset + length_offset:offset + length_offset + length]
    return string_data.decode(encoding_type)