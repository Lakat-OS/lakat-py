from typing import Dict, Union, List
from utils.serialize import (serialize, unserialize)
from utils.encode.hashing import hash
from interfaces.bucket import BUCKET
from lakat.timestamp import getTimestamp
from config.bucket_cfg import DEFAULT_ATOMIC_BUCKET_SCHEMA, DEFAULT_MOLECULAR_BUCKET_SCHEMA

def prepare_atomic_bucket(content_dict: Dict[str, bytes]) -> bytes:
    bucket = BUCKET(
        schema_id = content_dict["schema_id"],
        public_key = content_dict["public_key"],
        parent_bucket = content_dict["parent_bucket"],
        data = content_dict["data"],
        refs = content_dict["refs"],
        timestamp = getTimestamp()
    )
    bucketData = serialize(bucket.__dict__)
    return hash(bucketData), bucketData
    

def prepare_molecular_bucket(content_dict: Dict[str, bytes], atomicBuckets: List[Dict[str, Union[int, bytes]]]) -> bytes:
        
    if content_dict["schema_id"] == DEFAULT_MOLECULAR_BUCKET_SCHEMA:
        # get the data from content_dict["data"]
        order = unserialize(content_dict["data"])
        # Create a dictionary for fast lookup
        index_to_bucketId = {bucket["index"]: bucket["bucketId"] for bucket in atomicBuckets}

        # Get the bucketIds in the desired order
        bucket_data = serialize([index_to_bucketId[idx] for idx in order])
        bucket = BUCKET(
            schema_id = content_dict["schema_id"],
            public_key = content_dict["public_key"],
            parent_bucket = content_dict["parent_bucket"],
            data = bucket_data,
            refs = content_dict["refs"],
            timestamp = getTimestamp()
        )
        bucketData = serialize(bucket.__dict__)
        return hash(bucketData), bucketData
    else:
        raise Exception("Invalid content type")
    

def getBucketContentAndIds(contents: List[bytes]) -> Dict[int, List[Dict[str, Union[int, bytes]]]]:
    """ get the bucket content and ids from the contents 
    """
    atomicBuckets = list()
    molecularBuckets = list()
    molecularBucketIndices = list()
    for index, content in enumerate(contents):
        # print('content', content)
        content_dict = unserialize(content)
        if content_dict["schema_id"] == DEFAULT_ATOMIC_BUCKET_SCHEMA:
            bucketId, bucketData = prepare_atomic_bucket(content_dict)
            atomicBuckets.append({"bucketId": bucketId, "bucketData": bucketData, "index": index})
        elif content_dict["schema_id"] == DEFAULT_MOLECULAR_BUCKET_SCHEMA:
            molecularBucketIndices.append(index)
        else:
            raise Exception("Invalid content type")
        
    # then create buckets from the molecular contents
    for index in molecularBucketIndices:
        content = unserialize(contents[index])
        bucketId, bucketData = prepare_molecular_bucket(content, atomicBuckets)
        molecularBuckets.append({"bucketId": bucketId, "bucketData": bucketData, "index": index})
    
    return {
        DEFAULT_ATOMIC_BUCKET_SCHEMA: atomicBuckets, 
        DEFAULT_MOLECULAR_BUCKET_SCHEMA: molecularBuckets
        }
