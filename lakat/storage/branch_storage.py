from setup import storage

def get_local_branches():
    return storage.local_branches

def add_branch_to_local_storage(branch_id: bytes):
    storage.local_branches.append(branch_id)