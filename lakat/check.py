from lakat.errors import ERR_T_CGB_1, ERR_V_CGB_1, ERR_NIE_1, ERR_T_CGB_2, ERR_T_CGB_3, ERR_T_CGB_4, ERR_T_CGB_5
from config.branch_cfg import PROPER_BRANCH_TYPE_ID, TWIG_BRANCH_TYPE_ID
from utils.encode.hashing import varint_decode
from utils.encode.language import LANGUAGE_DECODING_TYPES

def check_inputs(*args, **kwargs):
    if args[0] == "create_genesis_branch":
        msg = kwargs["msg"]
        signature = kwargs["signature"]
        branch_type = kwargs["branch_type"]
        accept_conflicts = kwargs["accept_conflicts"]
        if not isinstance(signature, bytes):
            raise ERR_T_CGB_2
        if not isinstance(msg, bytes):
            raise ERR_T_CGB_1
        if branch_type not in [PROPER_BRANCH_TYPE_ID, TWIG_BRANCH_TYPE_ID]:
            raise ERR_V_CGB_1
        if not isinstance(accept_conflicts, bool):
            raise ERR_T_CGB_3
        
        # decode the msg
        msg_encoding_id, msg_encoding_id_length = varint_decode(msg)
        if msg_encoding_id not in LANGUAGE_DECODING_TYPES:
            raise ERR_T_CGB_4
        msg_encoding_length, msg_encoding_length_length = varint_decode(msg[msg_encoding_id_length:])
        if msg_encoding_length != len(msg[msg_encoding_id_length + msg_encoding_length_length:]):
            raise ERR_T_CGB_5
        
    else:
        raise ERR_NIE_1