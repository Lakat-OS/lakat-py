import plyvel

class DB:

    def __init__(self, name: str='lakat'):
        self.name = name 
        self.db = self.create(name)

    def create(self, name:str) :
        return plyvel.DB('/tmp/{name}/'.format(name=name), create_if_missing=True)

    def put(self, key:bytes, value: bytes):
        self.db.put(key, value)

    def get(self, key:bytes) -> bytes :
        return self.db.get(key)

    def delete(self, key:bytes):
        self.db.delete(key)

    def close(self):
        self.db.close()

# db = plyvel.DB('/tmp/{name}/'.format(name='lakat_test_1'), create_if_missing=True)

# db.put(b'key', b'value')

# val = db.get(b'key')

# print('val',val)

# bytes(string, 'utf-8')