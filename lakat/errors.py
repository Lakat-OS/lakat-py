
### Errors for lakat.py

################################################################
### CREATE GENESIS BRANCH ERRORS ###############################
################################################################

# Type Errors
ERR_T_CGB_1 = TypeError("ERR_T_CGB_1: msg must be of type bytes")
ERR_T_CGB_2 = TypeError("ERR_T_CGB_2: signature must be of type bytes")
ERR_T_CGB_3 = TypeError("ERR_T_CGB_3: accept_conflicts must be of type bool")
ERR_T_CGB_4 = TypeError("ERR_T_CGB_4: msg must be encoded with a valid encoding type")
ERR_T_CGB_5 = TypeError("ERR_T_CGB_5: msg length does not match encoding length")

# Value Errors
ERR_V_CGB_1 = ValueError("ERR_V_CGB_1: branch_type must be either 'proper' (= 0) or 'twig' (= 1)")


################################################################
### BUCKET ERRORS ##############################################
################################################################

# Type Errors
ERR_T_BCKT_1 = Exception("ERR_T_BCKT_1: Invalid bucket id type")

################################################################
### TWIG CONTENT SUBMIT ########################################
################################################################

# Not found errors
ERR_N_TCS_1 = Exception("ERR_N_TCS_1: Branch not found")


################################################################
### CHECK INPUT ERRORS #########################################
################################################################


# Not Implemented Errors
ERR_NIE_1 = NotImplementedError("ERR_NIE_1: check_inputs not implemented for this function")

# Not found errors
ERR_N_HASH_1 = Exception("ERR_N_HASH_1: Branch_ids need to be supplied!")