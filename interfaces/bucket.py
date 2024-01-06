from typing import List

class BUCKET:
    def __init__(self, schema_id: int, signature: bytes, public_key: bytes, parent_bucket: bytes, data: bytes, refs: bytes, timestamp: int):
        self.schema_id = schema_id
        self.signature = signature
        self.public_key = public_key
        self.parent_bucket = parent_bucket
        self.data = data
        self.refs = refs
        self.timestamp = timestamp