from initialization.wp_structured_text import WikipediaStructuredText
from utils.serialize import serialize
from config.bucket_cfg import DEFAULT_ATOMIC_BUCKET_SCHEMA, DEFAULT_MOLECULAR_BUCKET_SCHEMA, BUCKET_ID_TYPE_NO_REF, BUCKET_ID_TYPE_WITH_ID_REF
from config.scrape_cfg import EXAMPLE_ARTICLE_TITLE
from initialization.test_interaction import getDefaultEmptyInteractions
from lakat.submit_old import content_submit
from initialization.wp_structured_diffs import Diff

def first_submit(edit, public_key, branchId):
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
        data_dict = {
            "schema_id": DEFAULT_ATOMIC_BUCKET_SCHEMA,
            "public_key": public_key,
            "parent_bucket": None,
            "data": serialize(part.content),
            "refs": serialize([])
        }
        contents.append(serialize(data_dict))
        order.append(i)
        submission_id_to_new_part_id[content_order_index] = i
        content_order_index += 1

    # # create a molecular bucket
    molecular_data = {
        "order":[{"id": oid, "type": BUCKET_ID_TYPE_NO_REF} for oid in order],
        "name": EXAMPLE_ARTICLE_TITLE}

    data_dict = {
        "schema_id": DEFAULT_MOLECULAR_BUCKET_SCHEMA,
        "public_key": public_key,
        "parent_bucket": None,
        "data": serialize(molecular_data),
        "refs": serialize([])}

    contents.append(serialize(data_dict))

    interactions = getDefaultEmptyInteractions()

    res = content_submit(
            contents=contents, 
            interactions=interactions,
            branchId=branchId, 
            proof=b'', 
            msg=msg, 
            create_branch=False)

    # now update the 
    for submission_id, new_part_id in submission_id_to_new_part_id.items():
        new_part_id_to_bucket_id[new_part_id] = res["bucket_ids"][submission_id]

    return new_part_id_to_bucket_id, res



def submit_new_edit(public_key, branchId, prev_edit, new_edit, article_id, part_id_to_bucket_id,  similarity_threshold=0.75, zero_level_similarity_threshold=0.95):

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
        
        data_dict = {
            "schema_id": DEFAULT_ATOMIC_BUCKET_SCHEMA,
            "public_key": public_key,
            "parent_bucket": None,
            "data": serialize(part.content),
            "refs": serialize([])
        }
        contents.append(serialize(data_dict))
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
        data_dict = {
            "schema_id": DEFAULT_ATOMIC_BUCKET_SCHEMA,
            "public_key": public_key,
            "parent_bucket": old_part_id,
            "data": serialize(new_part.content),
            "refs": serialize([])
        }
        contents.append(serialize(data_dict))
        order[modified["new_index"]] = {"id":content_order_index, "type": BUCKET_ID_TYPE_NO_REF}
        submission_id_to_new_part_id[content_order_index] = modified["new_index"]
        content_order_index += 1

    # check whether all the new parts are added
    if len(order) != len(new_parts):
        raise Exception("Not all new parts are added")

    ## create new molecular bucket
    molecular_data = {
        "order":order,
        "name": None}
    
    data_dict = {
        "schema_id": DEFAULT_MOLECULAR_BUCKET_SCHEMA,
        "public_key": public_key,
        "parent_bucket": article_id,
        "data": serialize(molecular_data),
        "refs": serialize([])
    }

    contents.append(serialize(data_dict))

    interactions = getDefaultEmptyInteractions()
    
    res = content_submit(
            contents=contents,
            interactions=interactions,
            branchId=branchId,
            proof=b'',
            msg=msg,
            create_branch=False)

    ## Now update the new_part_id_to_bucket_id
    # first update the submitted buckets
    for submission_id, new_part_id in submission_id_to_new_part_id.items():
        new_part_id_to_bucket_id[new_part_id] = res["bucket_ids"][submission_id]
    # next update the rearranged buckets
    for rearranged in df["rearranged"]:
        new_part_id_to_bucket_id[rearranged["new_index"]] = part_id_to_bucket_id[rearranged["old_index"]]
    # next update the modified buckets
    
    return new_part_id_to_bucket_id, res
