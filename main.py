from ipld import marshal, multihash, unmarshal
from db.base import DB
from lakat.branch import _newBranch
from lakat.submit import _newSubmit
from lakat.branch import createGenesisBranch    

db_name = 'lakat_test_1'

if __name__ == '__main__':
    db = DB(name=db_name)
    createGenesisBranch(
        db=db,
        branchType='proper',
        acceptConflicts=True,
        acceptedProofs={},
        consensusProps={},
        tokenProps={}
    )
    # db.put(b'key', b'value')
    # val = db.get(b'keys')
    # print('val',type(val))

    with db.db.iterator() as it:
        for k, v in it:

            print('k',k, 'v',v)

    db.close()