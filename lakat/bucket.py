from typing import Dict, Union, List
from utils.serialize.codec import (serialize, unserialize)
from utils.encode.hashing import lakathash, lakatcid
from interfaces.bucket import BUCKET
from lakat.timestamp import getTimestamp
from config.bucket_cfg import (
    DEFAULT_ATOMIC_BUCKET_SCHEMA, 
    DEFAULT_MOLECULAR_BUCKET_SCHEMA,
    DEFAULT_PULLREQUEST_BUCKET_SCHEMA,
    DEFAULT_NAME_RESOLUTION_BUCKET_SCHEMA,
    BUCKET_ID_TYPE_NO_REF,
    BUCKET_ID_TYPE_WITH_ID_REF)
from config.encode_cfg import ENCODING_FUNCTION
from utils.schemata.bucket import check_schema
from setup.db_trie import db
from lakat.trie import get_trie, 


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
    

def prepare_molecular_bucket(content_dict: Dict[str, bytes], molecule_bucket_ids) -> bytes:
        
    if content_dict["schema_id"] == DEFAULT_MOLECULAR_BUCKET_SCHEMA:
        # get the data from content_dict["data"]
        # Create a dictionary for fast lookup

        # Get the bucketIds in the desired order
        bucket_data = serialize(molecule_bucket_ids)
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


def getBucketIdsFromMolecularContents(content_dict, index_to_bucketId):
    data = unserialize(content_dict["data"])
    # Create a dictionary for fast lookup
    content_bucket_ids = []
    for entry in data["order"]:
        if entry["type"] == BUCKET_ID_TYPE_NO_REF:
            content_bucket_ids.append(index_to_bucketId[entry["id"]])
        elif entry["type"] == BUCKET_ID_TYPE_WITH_ID_REF:
            content_bucket_ids.append(entry["id"])
        else:
            raise Exception("Invalid bucket id type")
    return content_bucket_ids


def getBucketContentIdsAndNameRegistrations(
        contents: List[bytes],
        nameResolutionId: None or str
    ) -> Dict[int, List[Dict[str, Union[int, bytes]]]]:
    """ get the bucket content and ids from the contents 
    """
    # store the eventual buckets
    atomicBuckets = list()
    molecularBuckets = list()
    # keep track of the various other types of buckets.
    nameResolutionBuckets = list()
    pullRequestBuckets = list()
    # keep track of indices and new name registrations.
    molecularBucketIndices = list()
    newRegistrations = list()

    # initialize some flags
    canStillRegisterNameResolution = nameResolutionId is None
    NameResolutionDeployed = False

    # STORE THE BUCKET IDS IN THE ORDER THEY APPEAR IN THE CONTENTS
    bucket_ids = [None] * len(contents)

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
            # store the bucket id in the order it appears in the contents
            bucket_ids[index] = bucketId
        
        elif content_dict["schema_id"] == DEFAULT_MOLECULAR_BUCKET_SCHEMA:
            molecularBucketIndices.append(index)
        
        elif content_dict["schema_id"] == DEFAULT_NAME_RESOLUTION_BUCKET_SCHEMA:
            # prepare name_space bucket for submission
            bucketId, bucketData = prepare_namespace_bucket(content_dict)
            if canStillRegisterNameResolution:
                nameResolutionBuckets.append({
                "id": bucketId, "data": bucketData, "index": index})
                # register bucket id
                bucket_ids[index] = bucketId
                # update NameResolutionDeployed
                NameResolutionDeployed = True
                ## CAN ONLY REGISTER NAME RESOLUTION ONCE
                canStillRegisterNameResolution = False
            else:
                # check if the nameResolutionId is the same as the bucketId
                message = "The nameResolution already exists"
                # raise Exception(message)
                print(message)
                # Mention Error in bucket Id
                bucket_ids[index] = 'ERR:NameResolutionAlreadyExists'
        else:
            raise Exception("Invalid content type")
    
    # create a dictionary for fast lookup of bucket ids given the index
    # with which it was submitted
    index_to_bucketId = {
        bucket["index"]: bucket["id"] 
        for bucket in atomicBuckets}
    
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
        # substitute all the ids with the actual bucket ids
        
        molecule_bucket_ids = getBucketIdsFromMolecularContents(content_dict, index_to_bucketId)
        # prepare bucket for submission
        bucketId, bucketData = prepare_molecular_bucket(
            content_dict, molecule_bucket_ids)
        # append data for database put-query.
        molecularBuckets.append(
            {"id": bucketId, "data": bucketData, "index": index})
        # register bucket id
        bucket_ids[index] = bucketId

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
        "new_registrations": newRegistrations,
        "ordered_bucket_ids": bucket_ids,
        "name_resolution_deployed": NameResolutionDeployed
    }

    return result


def getDBSubmitsFromBuckets(buckets: Dict[str, List[Dict[str, Union[int, bytes]]]]) -> List[Dict[str, Union[int, bytes]]]:
    return [v for bckt in buckets["buckets"].values() for v in bckt]


def getNameRegistryBucketId(branchId: str, submitId: str) -> None or str:
    """ Get the name registry bucket id from the branchId and submitId
    """
    if not submitId:
        # we need to get the nameRegistryBucketId from the currentHead of the branch (latest state)
        serialized_branch_data = db.get(bytes(branchId, ENCODING_FUNCTION))
        # get latest branch state
        branch_data = unserialize(serialized_branch_data)
        # get the name resolution bucket id
        name_resolution_bucket_id = branch_data["nameResolution"]
        # get trie root from latest branch state
        head = branch_data["stableHead"]
        # get trie root from the stable head
        trie_root = head["trieRoot"]
        # get the name resolution bucket data
        trie.trie

    serialized_submit_data = db.get(bytes(branchId, ENCODING_FUNCTION))
    if branchId and not create_branch:
        current_branch_state_id = trie.retrieve_value(branchId)
        serialized_branch_data = db.get(bytes(current_branch_state_id, 'utf-8'))
        if serialized_branch_data is None:
            raise Exception("Branch does not exist")
        branch_data = unserialize(serialized_branch_data)
        return branch_data["nameResolution"]
    return None


def createNameRegistryBucket(public_key: str):
    bucket = BUCKET(
        schema_id = DEFAULT_NAME_RESOLUTION_BUCKET_SCHEMA,
        public_key = public_key,
        parent_bucket = "",
        data = [dict(payload=serialize({}), storage_protocol = "")],
        refs = [],
        timestamp = getTimestamp()
    )
    bucketData = serialize(bucket.__dict__)
    return lakatcid(bucketData), bucketData


bucketId = getNameRegistryBucketId(branchId=targetBranchId, submitId=submitId)