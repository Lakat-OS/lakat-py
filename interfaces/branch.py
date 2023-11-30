from typing import List

class BRANCH:
    def __init__(self, parentBranch: bytes or None, branchConfig: bytes, stableHead, sprouts: List[bytes], sproutSelection, branchToken, timestamp):
        self.parentBranch = parentBranch
        self.branchConfig = branchConfig
        self.stableHead = stableHead
        self.sprouts = sprouts
        self.sproutSelection = sproutSelection
        self.branchToken = branchToken
        self.timestamp = timestamp


# class SubmitStruct:
#     def __init__(self, proof, sig, parent, msg, trieRoot, submitTrace):
#         self.proof = proof
#         self.sig = sig
#         self.msg = msg
#         self.parent = parent
#         self.trieRoot = trieRoot
#         self.submitTrace = submitTrace

# class Proof:
#     def __init__(self, publicKey, proofType, proofsBucketId, proofData):
#         self.proofType = proofType
#         self.proofData = proofData
#         self.publicKey = publicKey
#         self.proofsBucketId = proofsBucketId
        

# def pull_request_submit(contributor_proof: Proof, issuing_branch, requesting_branch, target_branch):
#     ## check whether the contributor_proof is valid, i.e. is the public key really the signer of the message pointed at in the contributor proof.

#     ## create context data bucket (review container)

#     ## leaves a trace of the information about the pull request in the pullRequests entry of the submitTrace, namely pointers to the review container, to the target branch and the requesting branch.

#     ## create a new submit with the contributor proof as the submitter, the review container as the submit data, and the issuing branch as the parent branch.
    
#     pass



# def review_submit():
#     pass

# def merge_submit():
#     # check whether the merge is valid, i.e. the merge is between the requesting branch and the target branch, and the merge is between the latest commit of the requesting branch and the latest commit of the target branch. 
#     # also check that all the proofs are valid, i.e. people who contributed to so in a legitimate way.
#     pass

# from enum import Enum
# from typing import Dict, Union, List
# from ipld import (
#     marshal as serialize, 
#     multihash, 
#     unmarshal as unserialize
# )

# class BUCKET:
#     # the bucket class should have a schema_id (bytes), a public key (bytes), optionally a parent bucket (bytes), a data field (bytes), a refs field (bytes), and a timestamp field (int).
#     def __init__(self, schema_id: bytes, publicKey: bytes, parentBucket: bytes or None, data: bytes, refs: bytes, timestamp: int):
#         self.schema_id = schema_id
#         self.publicKey = publicKey
#         self.parentBucket = parentBucket
#         self.data = data
#         self.refs = refs
#         self.timestamp = timestamp
    
# DEFAULT_ATOMIC_BUCKET_SCHEMA = 1
# DEFAULT_MOLECULAR_BUCKET_SCHEMA = 2



# def getTimestamp() -> int:
#     return 1

# def prepare_atomic_bucket(content_dict: Dict[str, bytes]) -> bytes:
#     bucket = BUCKET(
#         schema_id = content_dict["schema_id"],
#         publicKey = content_dict["public_key"],
#         parentBucket = content_dict["parent_bucket"],
#         data = content_dict["data"],
#         refs = content_dict["refs"],
#         timestamp = getTimestamp()
#     )
#     bucketData = serialize(bucket)
#     return multihash(bucketData), bucketData
    

# def prepare_molecular_bucket(content_dict: Dict[str, bytes], atomicBuckets: List[Dict[str, Union[int, bytes]]]) -> bytes:
        
#     if content_dict["schema_id"] == DEFAULT_MOLECULAR_BUCKET_SCHEMA:
#         # get the data from content_dict["data"]
#         order = unserialize(content_dict["data"])
#         # Create a dictionary for fast lookup
#         index_to_bucketId = {bucket["index"]: bucket["bucketId"] for bucket in atomicBuckets}

#         # Get the bucketIds in the desired order
#         bucket_data = serialize([index_to_bucketId[idx] for idx in order])
#         bucket = BUCKET(
#             schema_id = content_dict["schema_id"],
#             publicKey = content_dict["public_key"],
#             parentBucket = content_dict["parent_bucket"],
#             data = bucket_data,
#             refs = content_dict["refs"],
#             timestamp = getTimestamp()
#         )
#         bucketData = serialize(bucket)
#         return multihash(bucketData), bucketData
#     else:
#         raise Exception("Invalid content type")
    

# def getBucketContentAndIds(contents: List[bytes]) -> Dict[int, List[Dict[str, Union[int, bytes]]]]:
#     """ get the bucket content and ids from the contents 
#     """
#     atomicBuckets = list()
#     molecularBuckets = list()
#     molecularBucketIndices = list()
#     for index, content in enumerate(contents):
#         content_dict = unserialize(content)
#         if content_dict["schema_id"] == DEFAULT_ATOMIC_BUCKET_SCHEMA:
#             bucketId, bucketData = prepare_atomic_bucket(content_dict)
#             atomicBuckets.append({"bucketId": bucketId, "bucketData": bucketData, "index": index})
#         elif content_dict["schema_id"] == DEFAULT_MOLECULAR_BUCKET_SCHEMA:
#             molecularBucketIndices.append(index)
#         else:
#             raise Exception("Invalid content type")
        
#     # then create buckets from the molecular contents
#     for index in molecularBucketIndices:
#         content = unserialize(contents[index])
#         bucketId, bucketData = prepare_molecular_bucket(content, atomicBuckets)
#         molecularBuckets.append({"bucketId": bucketId, "bucketData": bucketData, "index": index})
    
#     return {
#         DEFAULT_ATOMIC_BUCKET_SCHEMA: atomicBuckets, 
#         DEFAULT_MOLECULAR_BUCKET_SCHEMA: molecularBuckets
#         }


# def checkProof(branchId: int, proof: bytes) -> bool:
#     return True

# def content_submit(contents: List[bytes], branchId: int, proof: bytes):
#     # first create buckets from the atomic contents
#     buckets = getBucketContentAndIds(contents)

#     if not checkProof(branchId, proof):
#         raise Exception("Invalid proof")
    
#     # then write the buckets to the database
#     db.multiquery([
#         ("put", [bucket["bucketId"], bucket["bucketData"]]) for bucket in buckets
#     ])
    


