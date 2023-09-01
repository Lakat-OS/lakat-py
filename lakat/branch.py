from ipld import marshal, multihash, unmarshal
import datetime
from typing_extensions import Literal
from collections.abc import Mapping
from db.database import DB
from lakat.timestamp import getTimestamp
from lakat.submit import _newSubmit




def _newBranch(
        db: DB,
        # creator: bytes,
        branchType: Literal["proper", "twig", "sprout"],
        parentBranch: bytes or None,
        stableHead: bytes,
        acceptConflicts: bool,
        acceptedProofs: Mapping[str, str],
        consensusProps: Mapping[str, str],
        tokenProps: Mapping[str, str]) -> bytes:
    
    ## check whether the branchType is valid
    if branchType not in ["proper", "twig", "sprout"]:
        raise ValueError("branchType must be one of 'proper', 'twig', 'sprout'")
    
    ## check whether the stableHead is valid
    if db.get(stableHead) is None:
        raise ValueError("stableHead cannot be found in database")
    
    ## check whether the parentBranch is valid
    if isinstance(parentBranch, bytes):
        if db.get(parentBranch) is None:
            raise ValueError("parentBranch is not valid")
    
    ## get the consensusRoot
    encodedConsensusProps = marshal(consensusProps)
    consensusRoot = multihash(encodedConsensusProps)

    config = {
        "branchType": branchType,
        "acceptConflicts": acceptConflicts,
        "acceptedProofs": acceptedProofs,
        "consensusRoot": consensusRoot
        }
    encodedConfig = marshal(config)
    configRoot = multihash(encodedConfig)

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
        encodedTokenProps = marshal(tokenProps)
        tokenRoot = multihash(encodedTokenProps)
        token = tokenRoot
        ## write token into database
        db.put(bytes(tokenRoot, 'utf-8'), encodedTokenProps)

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




def createGenesisBranch(
        db: DB,
        branchType: Literal["proper", "twig"],
        acceptConflicts: bool, 
        acceptedProofs: Mapping[str, str],
        consensusProps: Mapping[str, str],
        tokenProps: Mapping[str, str]):
    
    ## create null submit

    submitHash = _newSubmit(
        db=db,
        contentkey='Hallo',
        content='Jooo'
    )

    _newBranch(
        db=db,
        branchType=branchType,
        parentBranch=None,
        stableHead=submitHash,
        acceptConflicts=acceptConflicts,
        acceptedProofs=acceptedProofs,
        consensusProps=consensusProps,
        tokenProps=tokenProps
    )

