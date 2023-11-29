from ipld import marshal, multihash, unmarshal
import datetime
from typing_extensions import Literal
from collections.abc import Mapping
from db.database import DB
from utils.serialize import Serializer
from utils.encoding import _serializeAndMultihash
from lakat.timestamp import getTimestamp
from lakat.submit import _newSubmit



def __checkStableHeadExists(db: DB, stableHead: bytes) -> None:
    ## check whether the stableHead is valid
    if db.get(stableHead) is None:
        raise ValueError("stableHead cannot be found in database")

def __checkCorrectBranchType(branchType: Literal["proper", "twig", "sprout"]) -> None:
    ## check whether the branchType is valid
    if branchType not in ["proper", "twig", "sprout"]:
        raise ValueError("branchType must be one of 'proper', 'twig', 'sprout'")


def __checkValidParentBranch(db: DB, parentBranch: bytes) -> None:
    ## check whether the parentBranch is valid
    if db.get(parentBranch) is None:
        raise ValueError("parentBranch is not valid")


def __newBranch(
        db: DB,
        serializer : Serializer,
        branchType: Literal["proper", "twig", "sprout"],
        parentBranch: bytes or None,
        stableHead: bytes,
        acceptConflicts: bool,
        acceptedProofs: Mapping[str, str],
        consensusProps: Mapping[str, str],
        tokenProps: Mapping[str, str]) -> bytes:
    
    
    ## get the consensusRoot
    (
        serializedConsensusProps, 
        consensusRoot
    ) = _serializeAndMultihash(consensusProps)

    config = {
        "branchType": branchType,
        "acceptConflicts": acceptConflicts,
        "acceptedProofs": acceptedProofs,
        "consensusRoot": consensusRoot
        }
    
    (
        serializedConfig,
        configRoot
    ) = _serializeAndMultihash(config)


    if (tokenProps.get('exists') != True): 
        token = None,
    else:
        blockchainFlag = tokenProps.get('blockchainFlag')
        if blockchainFlag is None or blockchainFlag is False:
            raise ValueError("tokenProps must have a blockchainFlag set to True")
        if tokenProps.get('blockchain') is None:
            raise ValueError("tokenProps must have a blockchain set to a valid blockchain")
        if tokenProps.get('chainid') is None:
            raise ValueError("tokenProps must have a chainid set to a valid chainid")
        if tokenProps.get('address') is None:
            raise ValueError("tokenProps must have an address set to a valid address")
        if tokenProps.get('deploymentHash') is None:
            raise ValueError("tokenProps must have a deploymentHash set to a valid deploymentHash")
        
        serializedTokenProps = serializer.serialize(tokenProps)
        tokenRoot = multihash(serializedTokenProps)
        
        token = tokenRoot
        ## write token into database
        db.put(bytes(tokenRoot, 'utf-8'), serializedTokenProps)

    timestamp = getTimestamp()

    branch = {
        "parentBranch": parentBranch,
        "branchConfig": configRoot,
        "stableHead": stableHead,
        "sprouts": [],
        "sproutSelection": {},
        "branchToken": token,
        "timestamp": timestamp
    }
    encodedBranch = marshal(branch)
    branchId = multihash(encodedBranch)

    ## put entries into database

    db.put(
        bytes(consensusRoot, 'utf-8'),
        encodedConsensusProps
    )

    db.put(
        bytes(configRoot, 'utf-8'),
        encodedConfig
    )

    db.put(
        bytes(branchId, 'utf-8'),
        encodedBranch
    )

    return branchId




def __createGenesisBranch(
        db: DB,
        submitHash: bytes,
        branchType: Literal["proper", "twig"],
        acceptConflicts: bool, 
        acceptedProofs: Mapping[str, str],
        consensusProps: Mapping[str, str],
        tokenProps: Mapping[str, str]):


    __newBranch(
        db=db,
        branchType=branchType,
        parentBranch=None,
        stableHead=submitHash,
        acceptConflicts=acceptConflicts,
        acceptedProofs=acceptedProofs,
        consensusProps=consensusProps,
        tokenProps=tokenProps
    )

