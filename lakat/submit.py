from typing import List
from config.bucket_cfg import DEFAULT_ATOMIC_BUCKET_SCHEMA, DEFAULT_MOLECULAR_BUCKET_SCHEMA
from lakat.bucket import getBucketContentAndIds
from lakat.proof import checkContributorProof
from utils.serialize import serialize, unserialize
from interfaces.submit import SUBMIT
from setup import db
from setup import trie


def content_submit(contents: List[bytes], branchId: bytes, proof: bytes, msg: str, create_branch):

    # serialized_branch_data = db.get(bytes(branchId, 'utf-8'))
    # if serialized_branch_data is None:
    #     raise Exception("Branch does not exist")
    if not create_branch:
        if not checkContributorProof(branchId, proof):
            raise Exception("Invalid proof")
    
    # first create buckets from the atomic contents
    buckets = getBucketContentAndIds(contents)
    
    allbuckets = buckets[DEFAULT_ATOMIC_BUCKET_SCHEMA] + buckets[DEFAULT_MOLECULAR_BUCKET_SCHEMA]

    results = db.multiquery([
        ("put", [bytes(bucket["bucketId"], 'utf-8'), bucket["bucketData"]]) for bucket in allbuckets
    ])

    ## TODO: check if all the buckets are inserted successfully

    trie.insert_many([
        (bucket["bucketId"], str(bucket["bucketData"])) for bucket in allbuckets
    ])

    trie.persist(db)

    
    # branch_data = unserialize(serialized_branch_data)

    # submit_trace = []  ## TODO: implement submit trace
    
    # submit = SUBMIT(
    #     parent_submit_id=branch_data["stableHead"],
    #     submit_msg=msg,
    #     trie_root=trie.root.hash,
    #     submit_trace=submit_trace
    # )

    # # TODO: implement submit and serialize it.