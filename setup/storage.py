from utils.trie.merkle_trie import MerkleTrie
# from db.db_interfaces import DB
from db.mock_local_db import MOCK_DB, PRIMITIVE_MOCK_DB
from db.local_db import DB
from config.db_cfg import DB_NAME, DB_FOLDER, USE_MOCK_DATABASE
import os
from typing import Mapping

# db = DB(name=DB_NAME)
db_path = os.path.abspath(os.path.join(os.getcwd(), DB_FOLDER))

if USE_MOCK_DATABASE:
    db_interface = MOCK_DB(path=db_path, name=DB_NAME, crop_filename_after=0)
else:
    db_interface = DB(name=DB_NAME, create=True)


# Trie = MerkleTrie
name_tries : Mapping[bytes, MerkleTrie] = dict()
data_tries : Mapping[bytes, MerkleTrie] = dict()
interaction_tries : Mapping[bytes, MerkleTrie] = dict()

# branches
local_branches = list()

