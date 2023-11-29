class BUCKET:
    # the bucket class should have a schema_id (bytes), a public key (bytes), optionally a parent bucket (bytes), a data field (bytes), a refs field (bytes), and a timestamp field (int).
    def __init__(self, schema_id: bytes, public_key: bytes, parent_bucket: bytes or None, data: bytes, refs: bytes, timestamp: int):
        self.schema_id = schema_id
        self.public_key = public_key
        self.parent_bucket = parent_bucket
        self.data = data
        self.refs = refs
        self.timestamp = timestamp