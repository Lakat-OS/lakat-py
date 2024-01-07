class CONFIG:
    def __init__(self, branchType: int, acceptConflicts: bool, acceptedProofs, consensusRoot):
        self.branchType = branchType
        self.acceptConflicts = acceptConflicts
        self.acceptedProofs = acceptedProofs
        self.consensusRoot = consensusRoot