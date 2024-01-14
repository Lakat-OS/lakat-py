from initialization.wp_structured_text import WikipediaStructuredText
from config.bucket_cfg import DEFAULT_ATOMIC_BUCKET_SCHEMA, DEFAULT_MOLECULAR_BUCKET_SCHEMA, BUCKET_ID_TYPE_NO_REF, BUCKET_ID_TYPE_WITH_ID_REF
from config.scrape_cfg import EXAMPLE_ARTICLE_TITLE
from initialization.wp_structured_diffs import Diff
from utils.encode.bytes import encode_bytes_to_base64_str
from utils.format.rpc_call import wrap_rpc_call
import lakat.submit.functions as lakat_submit_functions
import inspection.branch as inspection_branch

def first_submit(edit, branchId):
    structured_text_old = WikipediaStructuredText(edit["*"])
    old_parts = structured_text_old.parts
    comment = edit["comment"]
    author = edit["user"]
    msg =  f"{comment}. By '{author}'."

    contents = list()
    order = list()
    submission_id_to_new_part_id = dict()
    new_part_id_to_bucket_id = dict()
    content_order_index = 0
    for i, part in enumerate(old_parts):
        bucket_content_dict = {
                "data": part.content,  
                "schema": DEFAULT_ATOMIC_BUCKET_SCHEMA, 
                "parent_id": encode_bytes_to_base64_str(bytes(0)), 
                "signature": encode_bytes_to_base64_str(bytes(1)), 
                "refs": []
            }
        contents.append(bucket_content_dict)
        order.append(i)
        submission_id_to_new_part_id[content_order_index] = i
        content_order_index += 1

    # # create a molecular bucket
    molecular_data = {
        "order":[{"id": oid, "type": BUCKET_ID_TYPE_NO_REF} for oid in order],
        "name": EXAMPLE_ARTICLE_TITLE}

    mol_bucket_content_dict = {
        "schema": DEFAULT_MOLECULAR_BUCKET_SCHEMA,
        "signature": encode_bytes_to_base64_str(bytes(1)), 
        "parent_id": encode_bytes_to_base64_str(bytes(0)),
        "data": molecular_data,
        "refs": []
    }

    contents.append(mol_bucket_content_dict)

    proof = encode_bytes_to_base64_str(bytes(1))
    public_key = encode_bytes_to_base64_str(bytes(1))
    submit_kwargs = dict(branch_id=branchId, contents=contents, public_key=public_key, proof=proof, msg=msg)

    # return call
    branch_state_id = wrap_rpc_call(
        function=lakat_submit_functions.submit_content_for_twig,
        schema=lakat_submit_functions.submit_content_for_twig_schema,
        kwargs=submit_kwargs)
    
    branch_data = wrap_rpc_call(
        function=inspection_branch.get_branch_data_from_branch_state_id,
        schema=inspection_branch.get_branch_data_from_branch_state_id_schema,
        kwargs=dict(branch_state_id=branch_state_id, deserialize_buckets=False))

    deployed_bucket_ids = branch_data['submit_trace']['new_buckets']
    molecular_bucket_id = deployed_bucket_ids[-1]

    # now update the 
    for submission_id, new_part_id in submission_id_to_new_part_id.items():
        new_part_id_to_bucket_id[new_part_id] = deployed_bucket_ids[submission_id]

    return new_part_id_to_bucket_id, molecular_bucket_id



def submit_new_edit(public_key, branchId, prev_edit, new_edit, molecular_bucket_id, part_id_to_bucket_id,  similarity_threshold=0.75, zero_level_similarity_threshold=0.95):

    ### FUNCTION BEGINS HERE
    str_text_old = WikipediaStructuredText(prev_edit["*"])
    str_text_new = WikipediaStructuredText(new_edit["*"])
    comment = new_edit["comment"]
    author = new_edit["user"]
    msg =  f"{comment}. By '{author}'."

    diff = Diff(old=str_text_old, new=str_text_new)
    df = diff.compare(
        similarity_threshold=similarity_threshold, zero_level_similarity_threshold=zero_level_similarity_threshold)

    
    ## initialize lists and dicts
    new_part_id_to_bucket_id = dict()
    submission_id_to_new_part_id = dict()

    new_parts = str_text_new.parts
    order = [None for _ in range(len(new_parts))]
    ## add new buckets
    content_order_index = 0
    contents = list()
    for j in df["new"]:
        part = new_parts[j]
        
        bucket_content_dict = {
                "data": part.content,  
                "schema": DEFAULT_ATOMIC_BUCKET_SCHEMA, 
                "parent_id": encode_bytes_to_base64_str(bytes(0)), 
                "signature": encode_bytes_to_base64_str(bytes(1)), 
                "refs": []
            }
        contents.append(bucket_content_dict)

        order[j] = ({"id":content_order_index, "type": BUCKET_ID_TYPE_NO_REF})
        submission_id_to_new_part_id[content_order_index] = j
        content_order_index += 1

    ## add the rearranged buckets
    for rearranged in df["rearranged"]:
        old_part_id = part_id_to_bucket_id[rearranged["old_index"]]
        new_part = new_parts[rearranged["new_index"]]
        order[rearranged["new_index"]] = {"id":old_part_id, "type": BUCKET_ID_TYPE_WITH_ID_REF}

    ## add modified buckets
    for modified in df["modified"]:
        old_part_id = part_id_to_bucket_id[modified["old_index"]]
        new_part = new_parts[modified["new_index"]]
        bucket_content_dict = {
                "data": new_part.content,  
                "schema": DEFAULT_ATOMIC_BUCKET_SCHEMA, 
                "parent_id": old_part_id, 
                "signature": encode_bytes_to_base64_str(bytes(1)), 
                "refs": []
            }
        contents.append(bucket_content_dict)
        order[modified["new_index"]] = {"id":content_order_index, "type": BUCKET_ID_TYPE_NO_REF}
        submission_id_to_new_part_id[content_order_index] = modified["new_index"]
        content_order_index += 1

    # check whether all the new parts are added
    if len(order) != len(new_parts):
        raise Exception("Not all new parts are added")

    ## create new molecular bucket
    molecular_data = {
        "order":order,
        "name": ""}

    mol_bucket_content_dict = {
        "schema": DEFAULT_MOLECULAR_BUCKET_SCHEMA,
        "signature": encode_bytes_to_base64_str(bytes(1)), 
        "parent_id": molecular_bucket_id,
        "data": molecular_data,
        "refs": []
    }
    contents.append(mol_bucket_content_dict)
    proof=encode_bytes_to_base64_str(bytes(1))
    submit_kwargs = dict(branch_id=branchId, contents=contents, public_key=public_key, proof=proof, msg=msg)

    # return call
    branch_state_id = wrap_rpc_call(
        function=lakat_submit_functions.submit_content_for_twig,
        schema=lakat_submit_functions.submit_content_for_twig_schema,
        kwargs=submit_kwargs)
    branch_data = wrap_rpc_call(
        function=inspection_branch.get_branch_data_from_branch_state_id,
        schema=inspection_branch.get_branch_data_from_branch_state_id_schema,
        kwargs=dict(branch_state_id=branch_state_id, deserialize_buckets=False))

    deployed_bucket_ids = branch_data['submit_trace']['new_buckets']
    molecular_bucket_id = deployed_bucket_ids[-1]
    ## Now update the new_part_id_to_bucket_id
    # first update the submitted buckets
    for submission_id, new_part_id in submission_id_to_new_part_id.items():
        new_part_id_to_bucket_id[new_part_id] = deployed_bucket_ids[submission_id]
    # next update the rearranged buckets
    for rearranged in df["rearranged"]:
        new_part_id_to_bucket_id[rearranged["new_index"]] = part_id_to_bucket_id[rearranged["old_index"]]
    # next update the modified buckets
    
    return new_part_id_to_bucket_id, molecular_bucket_id
