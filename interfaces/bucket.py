from typing import List

class BUCKET:
    def __init__(self, schema_id: str, public_key: str, parent_bucket: str, data: str, storage_protocols: List[str], refs: bytes, timestamp: int):
        self.schema_id = schema_id
        self.public_key = public_key
        self.parent_bucket = parent_bucket
        self.data = data
        self.storage_protocols = storage_protocols
        self.refs = refs
        self.timestamp = timestamp