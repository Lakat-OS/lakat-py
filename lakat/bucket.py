from typing import Dict, Union, List
from utils.serialize import (serialize, unserialize)
from utils.encode.hashing import lakathash
from interfaces.bucket import BUCKET
from lakat.timestamp import getTimestamp
from config.bucket_cfg import (
    DEFAULT_ATOMIC_BUCKET_SCHEMA, 
    DEFAULT_MOLECULAR_BUCKET_SCHEMA,
    DEFAULT_PULLREQUEST_BUCKET_SCHEMA,
    DEFAULT_NAME_RESOLUTION_BUCKET_SCHEMA)
from utils.schemata.bucket import check_schema
from setup.db_trie import db, trie


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
    return lakathash(bucketData), bucketData
    

def prepare_molecular_bucket(content_dict: Dict[str, bytes], atomicBuckets: List[Dict[str, Union[int, bytes]]]) -> bytes:
        
    if content_dict["schema_id"] == DEFAULT_MOLECULAR_BUCKET_SCHEMA:
        # get the data from content_dict["data"]
        data = unserialize(content_dict["data"])
        # Create a dictionary for fast lookup
        index_to_bucketId = {bucket["index"]: bucket["id"] for bucket in atomicBuckets}

        # Get the bucketIds in the desired order
        bucket_data = serialize([index_to_bucketId[idx["id"]] for idx in data["order"]])
        bucket = BUCKET(
            schema_id = content_dict["schema_id"],
            public_key = content_dict["public_key"],
            parent_bucket = content_dict["parent_bucket"],
            data = bucket_data,
            refs = content_dict["refs"],
            timestamp = getTimestamp()
        )
        bucketData = serialize(bucket.__dict__)
        return lakathash(bucketData), bucketData
    else:
        raise Exception("Invalid content type")

def prepare_namespace_bucket(content_dict: Dict[str, bytes]) -> bytes:
    bucket = BUCKET(
        schema_id = content_dict["schema_id"],
        public_key = content_dict["public_key"],
        parent_bucket = content_dict["parent_bucket"],
        data = content_dict["data"],
        refs = content_dict["refs"],
        timestamp = getTimestamp()
    )
    bucketData = serialize(bucket.__dict__)
    return lakathash(bucketData), bucketData



def getBucketContentIdsAndNameRegistrations(
        contents: List[bytes],
        nameResolutionId: None or str
    ) -> Dict[int, List[Dict[str, Union[int, bytes]]]]:
    """ get the bucket content and ids from the contents 
    """
    atomicBuckets = list()
    molecularBuckets = list()
    nameResolutionBuckets = list()
    pullRequestBuckets = list()
    molecularBucketIndices = list()
    newRegistrations = list()
    for index, content in enumerate(contents):
        # unpack content
        content_dict = unserialize(content)
        # check for schema id
        if content_dict["schema_id"] == DEFAULT_ATOMIC_BUCKET_SCHEMA:
            # check if the content adheres to schema format.
            success, msg, err = check_schema(
                data=content_dict["data"], 
                schema=content_dict["schema_id"])
            if not success:
                raise Exception(f"ERR: {err}! {msg}")
            # prepare bucket for submission
            bucketId, bucketData = prepare_atomic_bucket(content_dict)
            # append data for database put-query.
            atomicBuckets.append(
                {"id": bucketId, "data": bucketData, "index": index})
        
        elif content_dict["schema_id"] == DEFAULT_MOLECULAR_BUCKET_SCHEMA:
            molecularBucketIndices.append(index)
        
        elif content_dict["schema_id"] == DEFAULT_NAME_RESOLUTION_BUCKET_SCHEMA:
            # prepare name_space bucket for submission
            bucketId, bucketData = prepare_namespace_bucket(content_dict)
            if not nameResolutionId:
                nameResolutionBuckets.append({
                "id": bucketId, "data": bucketData, "index": index})
            else:
                # check if the nameResolutionId is the same as the bucketId
                message = "The nameResolutionId already exists"
                # raise Exception(message)
                print(message)
        else:
            raise Exception("Invalid content type")
        
    # then create buckets from the molecular contents
    for index in molecularBucketIndices:
        # unpack content
        content_dict = unserialize(contents[index])
        # check schema
        success, msg, err = check_schema(
                data=content_dict["data"], 
                schema=content_dict["schema_id"])
        if not success:
            raise Exception(f"ERR: {err}! {msg}")
        # prepare bucket for submission
        bucketId, bucketData = prepare_molecular_bucket(
            content_dict, atomicBuckets)
        # append data for database put-query.
        molecularBuckets.append(
            {"id": bucketId, "data": bucketData, "index": index})

        content_data_dict = unserialize(content_dict["data"])
        if content_data_dict["name"]:
            # If there is a name given in the molecular bucket it should be registered.
            # TODO: There should probably also be another constraint on the name, like a regex. And if the molecular bucket has a parent_bucket, then there should be some constraints as to registering an new name.
            newRegistrations.append({
                "id":bucketId, 
                "name": content_data_dict["name"]})

    result = {
        "buckets":
            {
                DEFAULT_ATOMIC_BUCKET_SCHEMA: atomicBuckets, 
                DEFAULT_MOLECULAR_BUCKET_SCHEMA: molecularBuckets,
                DEFAULT_PULLREQUEST_BUCKET_SCHEMA: pullRequestBuckets,
                DEFAULT_NAME_RESOLUTION_BUCKET_SCHEMA: nameResolutionBuckets
            },
        "new_registrations": newRegistrations
    }

    return result


def getDBSubmitsFromBuckets(buckets: Dict[str, List[Dict[str, Union[int, bytes]]]]) -> List[Dict[str, Union[int, bytes]]]:
    return [v for bckt in buckets["buckets"].values() for v in bckt]


def getNameRegistryBucketId(branchId: str, create_branch: bool) -> None or str:
    if branchId and not create_branch:
        current_branch_state_id = trie.retrieve_value(branchId)
        serialized_branch_data = db.get(bytes(current_branch_state_id, 'utf-8'))
        if serialized_branch_data is None:
            raise Exception("Branch does not exist")
        branch_data = unserialize(serialized_branch_data)
        return branch_data["nameResolution"]
    return None