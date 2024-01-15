import re
import difflib
from initialization.wp_structured_text import WikipediaStructuredText
from initialization.wp_structured_text import Part
from typing import Mapping, List, Tuple

def _is_identical(part1, part2):
    return part1.full_text == part2.full_text

def _get_similarity(part1, part2):
    matcher = difflib.SequenceMatcher(None, part1.full_text, part2.full_text)
    # The ratio is a measure of the sequences' similarity
    return matcher.ratio()

def _has_same_title_and_super_title(part1, part2):
    return part1.title == part2.title and part1.super_title == part2.super_title

def _are_summaries(part1, part2):
    return part1.level == 1 and part2.level == 1


class Diff:

    def __init__(self, 
        old: WikipediaStructuredText, 
        new: WikipediaStructuredText
    ):
        self.old = old
        self.new = new


    def compare(self, similarity_threshold=0.7, zero_level_similarity_threshold=0.9,check_unpartnered=False):
            text1_parts = self.old.extract_parts()
            text2_parts = self.new.extract_parts()

            rearranged, could_be_new_or_modified, modified, new, deleted, partnered_indices, potentially_new_indices = [], [], [], [], [], [], []

            # Step 1: Find identical and potential new or modified parts
            for j, part2 in enumerate(text2_parts):
                found_partner = False
                for i, part1 in enumerate(text1_parts):
                    if _is_identical(part1, part2):
                        rearranged.append({'old_index': i, 'new_index': j})
                        partnered_indices.append(i)
                        found_partner = True
                        break
                if not found_partner:
                    could_be_new_or_modified.append((j, part2))

            # Step 2: Filter could_be_new_or_modified list
            for j, part2 in could_be_new_or_modified:
                similar_found = False
                for i, part1 in enumerate(text1_parts):
                    if i not in partnered_indices:
                        similarity = _get_similarity(part1, part2)
                        cond1 =  part1.level!=0 and similarity >= similarity_threshold
                        cond2 =  part1.level==0 and similarity >= zero_level_similarity_threshold                        
                        cond3= _has_same_title_and_super_title(part1, part2)
                        cond4= _are_summaries(part1, part2)

                        if cond1 or cond2 or cond3 or cond4:
                            modified.append({'old_index': i, 'new_index': j, 'score': similarity})
                            partnered_indices.append(i)
                            similar_found = True
                            break
                        
                if not similar_found:
                    potentially_new_indices.append(j)
            
            # Now the potentially_new_indices are those indices in part 2 that are neither identical nor similar to any part in part 1
            
            new_indices = []
            # Step 3: Identify deleted parts
            for i, part1 in enumerate(text1_parts):
                if i not in partnered_indices:
                    if check_unpartnered:
                        # Check if part1 is similar to any unpartnered part in text2
                        similar_found = False
                        for j in potentially_new_indices:
                            part2 = text2_parts[j]
                            similarity = _get_similarity(part1, part2)
                            cond1 =  part1.level!=0 and similarity >= similarity_threshold
                            cond2 =  part1.level==0 and similarity >= zero_level_similarity_threshold  
                            if cond1 or cond2:
                                # add to modified
                                if j in [m["new_index"] for m in modified]:
                                    raise(f"Error: modified part {j} is already in modified list of new indices")
                                if i in [m["old_index"] for m in modified]:
                                    raise(f"Error: modified part {i} is already in modified list of old indices")
                                
                                modified.append({'old_index': i, 'new_index': j, 'score': similarity})
                                similar_found = True
                                
                                break
                        if not similar_found:
                            new_indices.append(j)
                            deleted.append(i)
                    else:
                        deleted.append(i)
                else: 
                    continue
            
            # Step 4: Identify added parts that are clearly new.
            for j in new_indices:
                new.append(j)

            # Step 5: Identify new parts
            for j in potentially_new_indices:
                if j not in new_indices:
                    new.append(j)

            return {'rearranged': rearranged, 'modified': modified, 'new': new, 'deleted': deleted}
    
    def test_create_initial_submit(self, check_edit, verbose = False):
        continue_flag = False
        if "*" not in check_edit:
            # check if there is stuff in texthidden
            if "texthidden" in check_edit:
                # check if there is content in texthidden
                if check_edit.get("texthidden"):
                    # just put this content to the "*" entry
                    check_edit["*"] = check_edit["texthidden"]
                else:
                    # the entry is inaccessible. Just skip 
                    continue_flag = True
            else:
                # the entry is inaccessible. Just skip 
                continue_flag = True
            
        if check_edit.get("texthidden") and verbose:
            print(f" There is texthidden in edit {check_edit['revid']}")

        return check_edit, continue_flag