from utils.trie.merkle_trie import MerkleTrie
# from db.db_interfaces import DB
from db.mock_local_db import MOCK_DB, PRIMITIVE_MOCK_DB
from config.db_cfg import DB_NAME, DB_FOLDER
from config.env import DEV_CROP_FILENAME_AFTER
import os
from typing import Mapping

# db = DB(name=DB_NAME)
db_path = os.path.abspath(os.path.join(os.getcwd(), DB_FOLDER))
db_interface = MOCK_DB(path=db_path, name=DB_NAME, crop_filename_after=0)
# db_interface = PRIMITIVE_MOCK_DB()
Trie = MerkleTrie
name_tries : Mapping[bytes, Trie] = dict()
data_tries : Mapping[bytes, Trie] = dict()

