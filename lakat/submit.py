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
    getDBSubmitsFromBuckets,
    getNameRegistryBucketId)
from lakat.proof import checkContributorProof
from utils.serialize import serialize, unserialize
from utils.encode.hashing import lakathash
from lakat.timestamp import getTimestamp
from lakat.trie import hexlify
from interfaces.submit import SUBMIT, SUBMIT_TRACE
from interfaces.branch import BRANCH
from setup.db_trie import db
from setup.db_trie import trie


def content_submit(contents: List[bytes], interactions: List[Mapping[str, any]], branchId: str, proof: bytes, msg: str, create_branch):

    #### CHECK CONTRIBUTOR PROOF #####################
    if not create_branch:
        success, emsg, code = checkContributorProof(branchId, proof)
        if not success:
            raise Exception(f"ERR: {code}! {emsg}")


    #### GET THE NAME RESOLUTION BUCKET ID ############
    nr_bckt_id = getNameRegistryBucketId(branchId, create_branch)
    

    #### INITIALIZATION ###############################
    db_submits = []          # list of database submits
    response = dict()        # dict of response data
    trie_insertions = list() # list of trie insertions


    #### PREPARE AND CREATE BUCKET DATA ###############
    # Cast the contents into bucket data.
    # buckets are dicts with "data" and "new_registrations" keys
    # The "data" key contains a dict where the keys are the schemata
    # and the values are all buckets of that given schema_id
    # The "new_registrations" key contains a list of new
    # name registrations. Each entry contains a dict with
    # the bucket id (key="id") and the bucket name (key="name").
    buckets = getBucketContentIdsAndNameRegistrations(
        contents=contents, 
        nameResolutionId=nr_bckt_id)
    # At this point one may only add a new registration for 
    # molecular buckets that are submitted in the same submit.
    # TODO: That should be relaxed. 
    
    
    #### IN CASE A NAME REGISTRY WAS SUBMITTED #######
    # store the name registry buckets (either a list with one 
    # or None) into the local variable ns_bckts
    ns_bckts = buckets["buckets"].get(DEFAULT_NAME_RESOLUTION_BUCKET_SCHEMA)


    #### GET THE SUBMIT TRACE ########################
    submit_trace_dict = getSubmitTrace(buckets, ns_bckts)


    #### GET THE NEW SUBMIT OBJECT ##################
    submit_dict = getSubmitObject(branchId, create_branch, msg, submit_trace_dict)


    #### UPDATE THE BRANCH STATE ####################
    (branch_dict, 
     nameResolutionBucketId,
     branch_trie_update) = createPrepareOrUpdateBranch(branchId, create_branch, submit_dict["id"], ns_bckts)
    updated_branch_id = branch_trie_update["key"]
    current_branch_state = branch_trie_update["value"]


    #### GET NEW NAME REGISTRATIONS ##################
    new_registration, nr_trie_bucket_data, nr_of_regs = nameRegistration(
        buckets, nameResolutionBucketId)


    #### STORE THE BUCKET DATA IN LOCAL VARIABLES ####
    # converts the buckts format into database submittable format
    db_submits.extend(getDBSubmitsFromBuckets(buckets))
    db_submits.append(submit_trace_dict)
    db_submits.append(submit_dict)
    db_submits.append(branch_dict)

    # Store the bucket ids and their type in the response
    response.update({
        "bucket_ids": buckets["ordered_bucket_ids"],
        "molecule_ids": [bckt["id"] for bckt in buckets["buckets"].get(DEFAULT_MOLECULAR_BUCKET_SCHEMA)],
        "branch_id": updated_branch_id,
        "branch_state": current_branch_state,
        "submit_id": submit_dict["id"],
        "submit_trac_id": submit_trace_dict["id"],
        "registered_names": buckets["new_registrations"],
        "nr_regs": nr_of_regs,
        "name_registration_deployed": buckets["name_resolution_deployed"],
        "msg": msg
    })


    # Trie insertions
    trie_insertions.append(branch_trie_update)
    if new_registration:
        trie_insertions.append(nr_trie_bucket_data)
    # Interaction Tre insertions
    interaction_trie_insertions = getInteractionInsertions(interactions)


    #### SUBMISSION OF DATA TO DB ##################
    DBSubmission(db_submits)

    
    ## TRIE UPDATE ######
    # TODO: Is it not a problem for the rootHash that the values are all ""
    ## put all the new buckets into the try and the new insertions
    trie.insert_many([
        (bckt["id"], "") for bckt in db_submits])
    # update the trie insertions.
    trie.insert_many([
        (ins["key"], ins["value"]) for ins in trie_insertions])
    # interaction values update
    trie.update_many_interactions([
        (ins["key"], ins["value"])
        for ins in interaction_trie_insertions])

    # if DEV_ENVIRONMENT == "LOCAL":
    trie.persist(db, interaction=False)
    trie.persist(db, interaction=True)

    return response


def getSubmitTrace(buckets, ns_bckts: list or None):

    submit_trace = SUBMIT_TRACE(
        changesTrace=[
            bckt["id"] 
            for bckt in getDBSubmitsFromBuckets(buckets)],
        pullRequests=[rq["id"] for rq in buckets["buckets"].get(DEFAULT_PULLREQUEST_BUCKET_SCHEMA)],
        nsRegistry={
            "ns_bucket": (ns_bckts[0]["id"] if ns_bckts else None),
            "new_registrations": buckets["new_registrations"]},
        reviewsTrace=[],
        socialTrace=[],
        sproutSelectionTrace=[]
    )

    serialized_submit_trace = serialize(submit_trace.__dict__)
    return {"id": lakathash(serialized_submit_trace), "data": serialized_submit_trace}


def getSubmitObject(branchId, create_branch, msg, submit_trace_dict):
    
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
    
    return {
        "id": lakathash(serialized_submit), 
        "data": serialized_submit}


# TODO: separate out those two cases with branch and without branch creation
def createPrepareOrUpdateBranch(branchId, create_branch, submit_id, ns_bckts):

    # create branch if needed
    if create_branch:
        ## NOTE: branchId might be none
        branch = BRANCH(
            parentBranch=branchId,
            branchConfig=bytes("", 'utf-8'),
            stableHead=submit_id, # submit_dict["id"],
            nameResolution=ns_bckts[0]["id"] if ns_bckts else None,
            sprouts=[],
            sproutSelection=[],
            branchToken=None,
            timestamp=getTimestamp()
        )
        nameResolutionBucketId = branch.nameResolution
        serialized_branch = serialize(branch.__dict__)
        branch_dict = {"id": lakathash(serialized_branch), "data": serialized_branch}
        branch_trie_update = dict(
            key=branch_dict["id"], value=branch_dict["id"])
        return (
            branch_dict, 
            nameResolutionBucketId, 
            branch_trie_update)
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
        branch_params.update({"stableHead": submit_id})
        if ns_bckts:
            branch_params.update({"nameResolution": ns_bckts[0]["id"]})
        branch_params.update({"timestamp":getTimestamp()})
        branch = BRANCH(**branch_params)
        nameResolutionBucketId = branch.nameResolution
        serialized_branch = serialize(branch.__dict__)
        branch_dict = {"id": lakathash(serialized_branch), "data": serialized_branch}
        branch_trie_update = dict(
            key=branchId, value=branch_dict["id"])
        return (
            branch_dict, 
            nameResolutionBucketId, 
            branch_trie_update)
    

def nameRegistration(buckets, nameResolutionBucketId):

    total_number_of_registrations_on_branch = -1
    if buckets["new_registrations"]:
        nameResolutionDecoded = trie.retrieve_value(nameResolutionBucketId)
        if not nameResolutionDecoded:
            nr_bucket_data = dict()
        else:
            nr_bucket_data = unserialize(
                nameResolutionDecoded.encode("utf-8"))
        nr_bucket_data.update({
            bckt["id"]: bckt["name"] 
            for bckt in buckets["new_registrations"]})
        total_number_of_registrations_on_branch = len(nr_bucket_data.keys())
        
        return (
            True, 
            dict(key=nameResolutionBucketId, 
                 value=serialize(nr_bucket_data).decode("utf-8")),
            total_number_of_registrations_on_branch)
        
    return False, dict(), total_number_of_registrations_on_branch


def getInteractionInsertions(interactions):
    return [
        dict(key=interaction["id"], value=serialize({"channel":channel,"value":interaction["value"]}).encode("utf-8")) 
        for channel, interaction_list in interactions.items() for interaction in interaction_list]
        
    
def DBSubmission(db_submits):
    # TODO: Maybe move to another folder
    results = db.multiquery([
        ("put", [bytes(item["id"], 'utf-8'), item["data"]]) for item in db_submits
    ])

    ## TODO: check if all the buckets are inserted successfully
    for result in results:
        if not result[1]:
            raise Exception("Error while inserting buckets")