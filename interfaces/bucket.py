class BUCKET:
    def __init__(self, schema_id: bytes, public_key: bytes, parent_bucket: bytes or None, data: bytes, refs: bytes, timestamp: int):
        self.schema_id = schema_id
        self.public_key = public_key
        self.parent_bucket = parent_bucket
        self.data = data
        self.refs = refs
        self.timestamp = timestamp