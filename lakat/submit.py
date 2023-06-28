from db.database import DB


def _newSubmit(
        db: DB,
        contentkey: str,
        content: str
        ) -> bytes:
    
    contentHash = bytes(contentkey, 'utf-8')
    db.put(contentHash, bytes(content, 'utf-8'))
    return contentHash
