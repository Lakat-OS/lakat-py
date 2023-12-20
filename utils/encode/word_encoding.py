
import itertools

vowels = 'aeiou'
consonants = 'bcdfghjklmnpqrstvwxyz'

# Generate CVCVC words
def generate_cvcvc_words():
    return [''.join(word) for word in itertools.product(consonants, vowels, consonants, vowels, consonants)]

cvcvc_words = generate_cvcvc_words()

# Adjusted the size of CVCVC words list to avoid index out of range
words_count = len(cvcvc_words)

# Forward mapping: Number to Word Sequence
def number_to_word_sequence(number):
    word_sequence = []
    while number > 0:
        number, idx = divmod(number, words_count)
        word_sequence.append(cvcvc_words[idx])
    return '-'.join(reversed(word_sequence))

def get_index(letter, group):
    return group.index(letter)

def single_word_to_number(word):
    c1, v1, c2, v2, c3 = word
    return (get_index(c1, consonants) * len(vowels) * len(consonants) * len(vowels) * len(consonants) +
            get_index(v1, vowels) * len(consonants) * len(vowels) * len(consonants) +
            get_index(c2, consonants) * len(vowels) * len(consonants) +
            get_index(v2, vowels) * len(consonants) +
            get_index(c3, consonants))

# Reverse mapping: Word Sequence to Number
def word_sequence_to_number(word_sequence):
    words = word_sequence.split('-')
    number = 0
    for word in words:
        number = number * words_count + single_word_to_number(word)
    return number