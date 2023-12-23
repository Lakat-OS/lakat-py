from utils.trie.trie import MerkleTrie
from db.db_interface import DB
from db.mockdb import MOCK_DB
from config.db_cfg import DB_NAME, DB_FOLDER
from config.env import DEV_CROP_FILENAME_AFTER
import os


# db = DB(name=DB_NAME)
db_path = os.path.abspath(os.path.join(os.getcwd(), DB_FOLDER))
db = MOCK_DB(path=db_path, name=DB_NAME, create=True, crop_filename_after=DEV_CROP_FILENAME_AFTER)
# TODO: SHOULD be created only on branch creation
# trie = MerkleTrie(db=db, branchId="")
cached_tries = dict()

