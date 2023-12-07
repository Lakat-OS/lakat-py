from typing import List, Mapping
from config.bucket_cfg import (
    DEFAULT_ATOMIC_BUCKET_SCHEMA, 
    DEFAULT_MOLECULAR_BUCKET_SCHEMA, 
    DEFAULT_PULLREQUEST_BUCKET_SCHEMA, 
    DEFAULT_REGISTRY_BUCKET_SCHEMA,
    DEFAULT_NAME_RESOLUTION_BUCKET_SCHEMA)
from config.dev_cfg import DEV_ENVIRONMENT
from lakat.bucket import (
    getBucketContentIdsAndNameRegistrations,
    getDBSubmitsFromBuckets)
from lakat.proof import checkContributorProof
from utils.serialize import serialize, unserialize
from utils.encode.hashing import lakathash
from lakat.timestamp import getTimestamp
from lakat.trie import hexlify
from interfaces.submit import SUBMIT, SUBMIT_TRACE
from interfaces.branch import BRANCH
from db_trie import db
from db_trie import trie


def content_submit(contents: List[bytes], interactions: List[Mapping[str, any]], branchId: bytes, proof: bytes, msg: str, create_branch):

    # serialized_branch_data = db.get(bytes(branchId, 'utf-8'))
    # if serialized_branch_data is None:
    #     raise Exception("Branch does not exist")
    if not create_branch:
        success, errmsg, errcode = checkContributorProof(branchId, proof)
        if not success:
            raise Exception(f"ERR: {errcode}! {errmsg}")
        
    ## Get the name resolution bucket id
    nr_bckt_id = None
    if branchId and not create_branch:
        print(">>> Trying to retrieve branchId (branchId = targetBranch)")
        current_branch_state_id = trie.retrieve_value(branchId)
        print('target branch:', branchId, ". type: ", type(branchId), '. current branch id:', current_branch_state_id, ". type:", type(current_branch_state_id))
        serialized_branch_data = db.get(bytes(current_branch_state_id, 'utf-8'))
        if serialized_branch_data is None:
            raise Exception("Branch does not exist")
        branch_data = unserialize(serialized_branch_data)
        nr_bckt_id = branch_data["nameResolution"]
    
    db_submits = []
    response = dict()
    # first create buckets from the atomic contents
    print(f"The nameResolution is {nr_bckt_id} and of type: {type(nr_bckt_id)}")
    buckets = getBucketContentIdsAndNameRegistrations(
        contents=contents, 
        nameResolutionId=nr_bckt_id)
    all_bucket_submits = getDBSubmitsFromBuckets(buckets)
    db_submits += all_bucket_submits
    response.update({b["id"]: "ATOMIC" for b in buckets["buckets"][DEFAULT_ATOMIC_BUCKET_SCHEMA]})
    response.update({b["id"]: "MOLECULAR" for b in buckets["buckets"][DEFAULT_MOLECULAR_BUCKET_SCHEMA]})
    
    
    ## GET the name resolution buckets
    ns_bckts = buckets["buckets"].get(DEFAULT_NAME_RESOLUTION_BUCKET_SCHEMA)

    submit_trace = SUBMIT_TRACE(
        changesTrace=[bckt["id"] for bckt in all_bucket_submits],
        pullRequests=[rq["id"] for rq in buckets["buckets"].get(DEFAULT_PULLREQUEST_BUCKET_SCHEMA)],
        nsRegistry={
            "ns_bucket": (ns_bckts[0]["id"] if ns_bckts else None),
            "new_registrations": buckets["new_registrations"]},
        reviewsTrace=[],
        socialTrace=[],
        sproutSelectionTrace=[]
    )

    serialized_submit_trace = serialize(submit_trace.__dict__)
    submit_trace_dict = {"id": lakathash(serialized_submit_trace), "data": serialized_submit_trace}
    db_submits.append(submit_trace_dict)
    response.update({submit_trace_dict["id"]: "SUBMIT_TRACE"})

    ## GET THE PARENT SUBMIT ID
    if create_branch and not branchId:
        # genesis submit
        parent_submit_id=None
    else:
        serialized_branch_data = db.get(bytes(branchId, 'utf-8'))
        if serialized_branch_data is None:
            raise Exception("Branch does not exist")
        branch_data = unserialize(serialized_branch_data)
        parent_submit_id=branch_data["stableHead"]
    
    submit = SUBMIT(
        parent_submit_id=parent_submit_id,
        submit_msg=msg,
        trie_root=trie.root.hash,
        submit_trace=submit_trace_dict["id"]
    )
    
    serialized_submit = serialize(submit.__dict__)
    submit_dict = {"id": lakathash(serialized_submit), "data": serialized_submit}
    db_submits.append(submit_dict)
    response.update({submit_dict["id"]: "SUBMIT"})

    trie_insertions = list()
    # create branch if needed
    nameResolutionBucketId = None
    if create_branch:
        ## NOTE: branchId might be none
        branch = BRANCH(
            parentBranch=branchId,
            branchConfig=bytes("", 'utf-8'),
            stableHead=submit_dict["id"],
            nameResolution=ns_bckts[0]["id"] if ns_bckts else None,
            sprouts=[],
            sproutSelection=[],
            branchToken=None,
            timestamp=getTimestamp()
        )
        nameResolutionBucketId = branch.nameResolution
        serialized_branch = serialize(branch.__dict__)
        branch_dict = {"id": lakathash(serialized_branch), "data": serialized_branch}
        db_submits.append(branch_dict)
        response.update({branch_dict["id"]: "BRANCH"})
        trie_insertions.append(dict(key=branch_dict["id"], value=branch_dict["id"]))
    else:
        # update the branch:
        # add the nameResolution to the branch if there is one
        
        if not branchId:
            raise Exception("Branch does not exist")
        
        branch_params = dict()
        
        current_branch_state_id = trie.retrieve_value(branchId)
        serialized_branch_data = db.get(bytes(current_branch_state_id, 'utf-8'))
        if serialized_branch_data is None:
            raise Exception("Branch does not exist")
        
        branch_data = unserialize(serialized_branch_data)
        branch_params.update(branch_data)
        branch_params.update({"stableHead": submit_dict["id"]})
        if ns_bckts:
            branch_params.update({"nameResolution": ns_bckts[0]["id"]})
        branch_params.update({"timestamp":getTimestamp()})
        branch = BRANCH(**branch_params)
        nameResolutionBucketId = branch.nameResolution
        serialized_branch = serialize(branch.__dict__)
        branch_dict = {"id": lakathash(serialized_branch), "data": serialized_branch}
        db_submits.append(branch_dict)
        response.update({branch_dict["id"]: "BRANCH UPDATE"})
        trie_insertions.append(dict(
            key=branchId,
            value=branch_dict["id"]))

    print('buckets["new_registrations"]: ', buckets["new_registrations"])
    
    if buckets["new_registrations"]:
        print(">>> INSERT New Name registration")
        nameResolutionDecoded = trie.retrieve_value(nameResolutionBucketId)
        print(f"nameResolutionBucket id is {nameResolutionBucketId} and its value is {nameResolutionDecoded} and the type is {type(nameResolutionDecoded)}")
        print(f"The hexlified version is {hexlify(nameResolutionBucketId)}.")
        if not nameResolutionDecoded:
            nr_bucket_data = dict()
        else:
            nr_bucket_data = unserialize(
                nameResolutionDecoded.encode("utf-8"))
        nr_bucket_data.update({
            bckt["id"]: bckt["name"] 
            for bckt in buckets["new_registrations"]})
        
        trie_insertions.append(
            dict(key=nameResolutionBucketId, 
                 value=serialize(nr_bucket_data).decode("utf-8")))
        
    trie_insertions.extend([
        dict(key=interaction["id"], value=serialize({"channel":channel,"value":interaction["value"]}).encode("utf-8")) 
        for channel, interaction_list in interactions.items() for interaction in interaction_list])

    results = db.multiquery([
        ("put", [bytes(item["id"], 'utf-8'), item["data"]]) for item in db_submits
    ])

    ## TODO: check if all the buckets are inserted successfully
    for result in results:
        if not result[1]:
            raise Exception("Error while inserting buckets")

    ## TRIE UPDATE ######
    ## put all the new buckets into the try and the new insertions
    trie.insert_many([
        (bckt["id"], "") 
        for bckt in db_submits
    ])

    # update the trie insertions.
    print('trie_insertions', trie_insertions)
    trie.insert_many([
        (ins["key"], ins["value"])
        for ins in trie_insertions])

    if DEV_ENVIRONMENT == "LOCAL":
        trie.persist(db)

    return response
    # submit = SUBMIT(
    #     parent_submit_id=branch_data["stableHead"],
    #     submit_msg=msg,
    #     trie_root=trie.root.hash,
    #     submit_trace=submit_trace
    # )

    # # TODO: implement submit and serialize it.