"""
This module provides utility functions for creating and working with buckets in the Lakat system.
Buckets are containers for data that can be referenced and linked together.
"""

from typing import List, Mapping
from config.encode_cfg import DEFAULT_CODEC
from config.bucket_cfg import BUCKET_ID_TYPE_NO_REF, BUCKET_ID_TYPE_WITH_ID_REF
from interfaces.bucket import BUCKET
from lakat.timestamp import getTimestamp
from lakat.errors import ERR_T_BCKT_1
from utils.encode.hashing import make_lakat_cid_and_serialize


def prepare_bucket(content_dict: Mapping[str, any], namespace: int) -> bytes:
    """
    Create a bucket from a content dictionary and serialize it.
    
    This function creates a BUCKET object using the provided content dictionary,
    adds a timestamp, and serializes it using the specified namespace.
    
    Parameters:
        content_dict (Mapping[str, any]): Dictionary containing the bucket data with keys:
            - schema_id: Schema identifier
            - signature: Cryptographic signature
            - public_key: The public key associated with the bucket
            - parent_bucket: Reference to parent bucket
            - root_bucket: Reference to root bucket
            - data: The actual data content
            - refs: References to other buckets
        namespace (int): The namespace for the bucket
        
    Returns:
        bytes: The content identifier (CID) of the created bucket
    """
    bucket = BUCKET(
        schema_id = content_dict["schema_id"],
        signature = content_dict["signature"],
        public_key = content_dict["public_key"],
        parent_bucket = content_dict["parent_bucket"],
        root_bucket = content_dict["root_bucket"],
        data = content_dict["data"],
        refs = content_dict["refs"],
        timestamp = getTimestamp()
    )
    return make_lakat_cid_and_serialize(content=bucket.__dict__, codec=DEFAULT_CODEC, namespace=namespace, branch_id_1= bytes(0), branch_id_2=bytes(0))
    

def get_bucket_ids_from_order(order: List[Mapping[str,any]], index_to_bucket_id):
    """
    Extract bucket IDs from an ordered list based on specified types.
    
    This function processes a list of entries that describe how to resolve bucket IDs.
    It handles two types of references:
    - BUCKET_ID_TYPE_NO_REF: Looks up the bucket ID using an index
    - BUCKET_ID_TYPE_WITH_ID_REF: Uses the ID directly from the entry
    
    Parameters:
        order (List[Mapping[str,any]]): List of entries specifying bucket references
            Each entry must contain:
            - "type": The type of reference (NO_REF or WITH_ID_REF)
            - "id": Either an index or an actual bucket ID depending on type
        index_to_bucket_id: Mapping from indices to actual bucket IDs
        
    Returns:
        List: A list of resolved bucket IDs in the specified order
        
    Raises:
        ERR_T_BCKT_1: If an unknown bucket ID type is encountered
    """
    content_bucket_ids = []
    for entry in order:
        if entry["type"] == BUCKET_ID_TYPE_NO_REF:
            content_bucket_ids.append(index_to_bucket_id[entry["id"]])
        elif entry["type"] == BUCKET_ID_TYPE_WITH_ID_REF:
            content_bucket_ids.append(entry["id"])
        else:
            raise ERR_T_BCKT_1
    return content_bucket_ids