class CONFIG:
    def __init__(self, branchType: int, acceptConficts: bool, acceptedProofs, consensusRoot):
        self.branchType = branchType
        self.acceptConficts = acceptConficts
        self.acceptedProofs = acceptedProofs
        self.consensusRoot = consensusRoot