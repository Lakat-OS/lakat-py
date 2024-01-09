# Lakat-Py

## Storage

Storage is achieved through a content-addressable decentralized key-value database. The database is decentralized and shared across the participants of the protocol. The keys are IPLD-formatted CIDs (Content identifiers). IPLD stands for interplanetary linked data. It is a format that stores a hash together with some metainformation. The first byte contains a version identifier, the next two bytes resolve to a codec-algorithm, namely an algorithm that can serialize and deserialize the hashed data. The remaining bytes are currently in a multihash format, moving to a slight variation in the near future. They contain the hash function identifier, then the hash length and finally the digest of that hashing algorithm with respect to the content. The resulting bytes are formatted in one of two ways: base58 or cvcvc. The latter is a homemade-encoding. Both allow for more readable content identifiers.

Every branch also has a Merkle-trie associated to it. The purpose of the trie is twofold. It acts as a fingerprint of submitted data and as such provides security for the branch making it close to impossible to retroactively change data as it would change the Merkle-root of the trie. Secondly it is used to store information about the branch and about the data that it points to. Each path inside the Merkle-trie resolves to a hexlified CID. The value at the end of the path is branch-specific information about the content stored for that key in the database. For example given the content `c={hello:"World"}`, then `h=CID(c)=Qmd...E` is the CID with CBOR-codec expressed in base58 and `h=0xf8ae...4` would be the base16 encoding. The hexlified path would be `path=['f','8','a','e',...]`. The value stored at the end of the path would be branch-specific meta-information about the content, for instance if user Alice liked the content this could be encoded and attached to that Merkle-trie-leaf.

There are two types of information attached to the trie: `data` and `interaction`. Data stores metadata and interaction stores user-interactions with that content. The `data` slot is used for versioning mostly. Every bucket or other content has itself a version history rooted in the original bucket or content. Original contents are those that have no parent or those whose parent does not already have children. The trie-data slot stores the current head of that content, i.e. the latest recognized version inside of that branch. Typical contents besides atomic buckets are molecular buckets, i.e. articles, branches, configs or name resolution buckets. The persistent identifier for a bucket is called bucket_stream_id.

The trie is created alongside the branch. The very first submit points to the latest trie root. 

### Name Resolution

Almost everything in Lakat is content addressable, except branches themselves. Unfortunately CIDs are hard to memorize and recognize for us. There is thus a name resolution. The task of the name resolution is to map names to branch_stream_ids. So by querying the name resolution (which is referenced inside the branch data) one can query the name. At this point we use a trie to store the name to bucket-stream-id.

### Hash namespaces

Buckets have global namespace. Config, name resolution, submits, submit traces and the trie has branch-specific namespaces

### Local Cache Database

Every client has a local cache where it stores as much information as needed (or as possible) to avoid making too many calls. Some clients


## Testing

```
curl -X POST http://localhost:3356/create_genesis_branch \
-H "Content-Type: application/json" \
-d '{"branch_type": 1, "signature": "V2VsdA==", "accept_conflicts": false, "msg": "V2VsdA=="}'
```
