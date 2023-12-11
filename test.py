from utils.signing.create_keys import create_key_pair
from utils.signing.sign import get_public_key_from_file
from utils.serialize import (serialize, unserialize)
# import DB

from config.bucket_cfg import DEFAULT_ATOMIC_BUCKET_SCHEMA, DEFAULT_MOLECULAR_BUCKET_SCHEMA, BUCKET_ID_TYPE_NO_REF

from setup.db_trie import db
from setup.db_trie import trie
from lakat.submit import content_submit

create_key_pair_flag = False
just_delete_db = False
if __name__ == '__main__':

    if just_delete_db:
        db.close()
        exit()

    key_file_prefix="lakat"
    if create_key_pair_flag:
        private_key_path, public_key_path = create_key_pair(key_file_prefix=key_file_prefix)

    # retrieve
    pub_key = get_public_key_from_file(key_file_prefix=key_file_prefix)

    # print('pubkey', pub_key)
    # make some example submit Data:
    introduction = "Introduction"
    results = "Results"
    conclusion = "Conclusion"
    atomic = [introduction, results, conclusion]
    
    contents = list()
    for data in atomic:
        data_dict = {
            "schema_id": DEFAULT_ATOMIC_BUCKET_SCHEMA,
            "public_key": pub_key,
            "parent_bucket": None,
            "data": serialize(data),
            "refs": serialize([])
        }
        contents.append(serialize(data_dict))
    
    molecular_data = [
        {"id":0, "type": BUCKET_ID_TYPE_NO_REF},
        {"id":1, "type": BUCKET_ID_TYPE_NO_REF},
        {"id":2, "type": BUCKET_ID_TYPE_NO_REF}]
    
    contents.append(serialize({
        "schema_id": DEFAULT_MOLECULAR_BUCKET_SCHEMA,
        "public_key": pub_key,
        "parent_bucket": None, 
        "data": serialize(molecular_data),
        "refs": serialize([]) 
    }))

    res = content_submit(
        contents=contents, 
        branchId=None, 
        proof=b'', 
        msg='test', 
        create_branch=True)
    
    only_one_atomic = 1
    contents = list()
    for key, value in res.items():
        if value=="ATOMIC" and only_one_atomic:
            only_one_atomic = 0
            # print('ATOMIC', unserialize(db.get(key.encode())))
            data = "The full Introduction\n\nSome more text."
            data_dict = {
                "schema_id": DEFAULT_ATOMIC_BUCKET_SCHEMA,
                "public_key": pub_key,
                "parent_bucket": key,
                "data": serialize(data),
                "refs": serialize([])
            }
            contents.append(serialize(data_dict))

    for key, value in res.items():
        if value == 'BRANCH':
            # print('BRANCH', unserialize(db.get(key.encode())))
            # print('Submit another content')
            res2 = content_submit(
                contents=contents, 
                branchId=key.encode(), 
                proof=b'', 
                msg='another test', 
                create_branch=False)
            # print('res2', res2)
    
    # db.close()
    # create a branch

    # print('queries', queries)
    # results = db.multiquery(queries)
    # print(results)

    # retrieve 
    # for query in queries:
    #     key = query[1][0]
    #     value = db.get(key)
    #     print('value', unserialize(value))
    #     pass


