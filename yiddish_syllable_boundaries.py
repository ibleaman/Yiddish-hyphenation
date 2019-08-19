# Script to find and add Yiddish syllable boundaries
# Author: Isaac L. Bleaman <bleaman@berkeley.edu>
# Date: 2019-08-19

# How to run script:
# python yiddish_syllable_boundaries.py -i WORD_LIST.txt -o WORD_LIST_SYLLABIFIED.txt

# sample input (new-line separated): אױסגעמוטשעט אַרױסגעלאָפֿן אָװנטברױט
# sample output: אױס-גע-מו-טשעט אַ-רױס-גע-לאָ-פֿן אָ-װנט-ברױט

# Note: This script will also standardize Yiddish unicode representations
# to avoid using precombined characters (except װ, ױ, ײ)

import argparse
import re
import itertools
import syllabifier  # from: https://sourceforge.net/p/p2tk/code/HEAD/tree/python/syllabify/syllabifier.py
                    # tweaked for python3

def readfile(filename):
    with open(filename, 'r') as textfile:
        data = textfile.readlines()
    data = [word.strip() for word in data]
    return data

def writefile(filename, wordlist):
    with open(filename, 'w') as textfile:
        for word in wordlist:
            textfile.write(word + '\n')

# combine multi Yiddish characters (אַ) into single Unicode chars (אַ)
def combine_chars(string):
    combinations = [
        ('אַ', 'אַ'),
        ('אָ', 'אָ'),
        ('בֿ', 'בֿ'),
        ('וּ', 'וּ'),
        ('וו', 'װ'),
        ('וי', 'ױ'),
        ('יִ', 'יִ'),
        ('יי', 'ײ'),
        ('ײַ', 'ײַ'),
        ('כּ', 'כּ'),
        ('פּ', 'פּ'),
        ('פֿ', 'פֿ'),
        ('שׂ', 'שׂ'),
        ('תּ', 'תּ')
    ]
    for letter in combinations:
        string = re.sub(letter[0], letter[1], string)
    return string

# separate single Yiddish characters (אַ) into multiple Unicode chars (אַ)
# except װ, ױ, ײ
def separate_chars(string):
    combinations = [
        ('אַ', 'אַ'),
        ('אָ', 'אָ'),
        ('בֿ', 'בֿ'),
        ('וּ', 'וּ'),
        ('יִ', 'יִ'),
        ('ײַ', 'ײַ'),
        ('כּ', 'כּ'),
        ('פּ', 'פּ'),
        ('פֿ', 'פֿ'),
        ('שׂ', 'שׂ'),
        ('תּ', 'תּ')
    ]
    for letter in combinations:
        string = re.sub(letter[0], letter[1], string)
    return string

# pre-process Yiddish strings in order to do correct syllabification
# replace consonantal yud with 'j'
# replace syllabic nun/lamed with 'ņ'/'Ņ'/'ļ'
def replace_consonant_j_syllabic_nl(string):
    string = re.sub('יאַ', 'jאַ', string)
    string = re.sub('יאָ', 'jאָ', string)
    string = re.sub('יו', 'jו', string)
    string = re.sub('יע', 'jע', string)
    string = re.sub('ייִ', 'jיִ', string)
    string = re.sub('יײַ', 'jײַ', string)
    string = re.sub('יײ', 'jײ', string)
    string = re.sub('יױ', 'jױ', string)

    # regex to find *syllabic* nun and lamed
    # any nun/lamed that isn't adjacent to a vowel
    string = re.sub(r'(?<!\s|אַ|ע|י|אָ|ו|ײ|ײַ|ױ|יִ|וּ)נ(?!אַ|ע|י|אָ|ו|ײ|ײַ|ױ|יִ|וּ)', 'ņ', string)
    string = re.sub(r'(?<!\s|אַ|ע|י|אָ|ו|ײ|ײַ|ױ|יִ|וּ)ן', 'Ņ', string)
    string = re.sub(r'(?<!\s|אַ|ע|י|אָ|ו|ײ|ײַ|ױ|יִ|וּ)ל(?!אַ|ע|י|אָ|ו|ײ|ײַ|ױ|יִ|וּ)', 'ļ', string)

    # undo that last step if we accidentally replaced word-initial nun/lamed
    if string.startswith('ņ'):
        string = 'נ' + string[1:]
    elif string.startswith('ļ'):
        string = 'ל' + string[1:]

    return ' '.join(list(string))

# generate the Yiddish patterns that will feed into syllabification algorithm
def generate_yiddish_patterns():

    ### STEP 1: create a a list of all possible syllable onsets (in Yiddish alphabet)

    # mapping from transliterations to Yiddish (combined) characters
    # this will be used to map onsets in Latin chars to Yiddish chars
    # NOTE: non-final letters only
    # NOTE: 'Y' mapped to 'j'; important later on
    transliterations = {
        'A': ['אַ'],
        'Ay': ['ײַ'],
        'B': ['ב'],
        'D': ['ד'],
        'E': ['ע'],
        'Ey': ['ײ'],
        'F': ['פֿ'],
        'G': ['ג'],
        'H': ['ה'],
        'I': ['י', 'יִ'],
        'K': ['ק', 'כּ'],
        'Kh': ['כ', 'ח'],
        'L': ['ל'],
        'M': ['מ'],
        'N': ['נ'],
        'O': ['אָ'],
        'Oy': ['ױ'],
        'P': ['פּ'],
        'R': ['ר'],
        'S': ['ס', 'שׂ', 'ת'],
        'Sh': ['ש'],
        'T': ['ט', 'תּ'],
        'Ts': ['צ'],
        'U': ['ו', 'וּ'],
        'V': ['װ', 'בֿ'],
        'Y': ['j'],
        'Z': ['ז'],
        'Zh': ['ז ש']
    }

    # list of all Yiddish vowels and list of singleton consonants
    vowels = [ # nuclei, really
        'אַ',
        'ע',
        'י',
        'אָ',
        'ו',
        'ײ',
        'ײַ',
        'ױ',
        'יִ',
        'וּ',
        'ņ', # not nun
        'Ņ', # not langer nun
        'ļ', # not lamed
    ]

    consonants = [
        'א',
        'ב',
        'בֿ',
        'ג',
        'ד',
        'ה',
        'װ',
        'ז',
        'ח',
        'ט',
        'j', # not yud
        'כּ',
        'כ',
        'ך',
        'ל', # this is never syllabic, since we'll have caught that and replaced earlier
        'מ',
        'ם',
        'נ', # this is never syllabic
        'ן', # this is never syllabic
        'ס',
        'ע',
        'פּ',
        'פֿ',
        'ף',
        'צ',
        'ץ',
        'ק',
        'ר',
        'ש',
        'שׂ',
        'תּ',
        'ת'
    ]

    # all allowable syllable onsets in Yiddish (to feed into Maximum Onset Principle)
    # adapted from Jacobs (2005:115-7)
    onsets = ['P T', 'P L', 'P R', 'P N', 'P S', 'P Sh', 'P Kh', 'P L', 'P K', 'T R', 'T M', 'B D', 'B L', 'B R', 'B G',
                'D L', 'D N', 'T N', 'T L', 'T K', 'T V', 'T F', 'T Kh', 'D R', 'D V', 'K N', 'K T', 'K D', 'K L', 'K S',
                'K R', 'K V', 'G N', 'G L', 'G R', 'G V', 'G Z', 'F L', 'F R', 'V L', 'V R', 'S M', 'S F', 'S V', 'S N',
                'S T', 'S D', 'S K', 'S P', 'S Kh', 'S R', 'S L', 'Z M', 'Z N', 'Z G', 'Z R', 'Z L', 'Z B', 'Sh M', 'Sh V',
                'Sh F', 'Sh N', 'Sh T', 'Sh P', 'Sh K', 'Sh Kh', 'Sh R', 'Sh L', 'Sh T Sh', 'Zh M', 'Zh L', 'Kh M', 'Kh V', 'Kh Sh', 'Kh S',
                'Kh L', 'Kh K', 'Kh Ts', 'Kh N', 'Kh R', 'Ts L', 'Ts N', 'Ts D', 'Ts V', 'T Sh V', 'M R', 'M L', 'Sh P R', 'Sh T R', 'Sh K R',
                'Sh P L', 'Sh K L', 'S P R', 'S T R', 'S K R', 'S P L', 'S K L',
                'T Sh', 'D Zh']

    # convert/expand 'S T' into all possibilities: ס ט, ס תּ, שׂ תּ, etc. for all other onsets
    all_onsets = []
    for onset in onsets:
        phonemes = onset.split(' ')
        onset_list = [transliterations[phoneme] for phoneme in phonemes]
        all_onsets.append(list(itertools.product(*onset_list)))
    all_onsets = [y for x in all_onsets for y in x] # flatten list

    all_onsets = [' '.join(onset) for onset in all_onsets]

    # onsets can include a null onset, and all singleton consonants
    all_onsets.append('')
    all_onsets += consonants

    ### STEP 2: compile Yiddish patterns to feed into syllabification algorithm

    yiddish_patterns = dict()
    yiddish_patterns['consonants'] = consonants
    yiddish_patterns['vowels'] = vowels
    yiddish_patterns['onsets'] = all_onsets

    return yiddish_patterns

def add_syllable_boundaries(yiddish_patterns, word):
    subwords_syllabified = []

    # split on punctuation, but retain punctuation marks
    subwords = re.split('([\.\-\\/!\?־„“”′״″"\';])', word)
    for subword in subwords:
        if subword not in ['"', "'", '.', '-', '\\', '/', '!', '?', '־', '„', '״', '“', '”', '′', '″', ';']:
            try:

                # syllabify word
                syllables = syllabifier.syllabify(yiddish_patterns, subword)
                result = ''
                for syllable in syllables:
                    for item in syllable:
                        if isinstance(item, list):
                            if len(item) > 0:
                                result += ''.join(item)
                    result += '-'

                # change the special Latin chars back to Yiddish chars
                result = re.sub('j', 'י', result)
                result = re.sub('ņ', 'נ', result)
                result = re.sub('Ņ', 'ן', result)
                result = re.sub('ļ', 'ל', result)
                result = re.sub(r'\-$', '', result)

                subwords_syllabified.append(result)
            except:
                subwords_syllabified = list(subword) # if there's a non-phoneme char in word, just add the word as-is
        else:
            subwords_syllabified.append(subword)

    return ''.join(subwords_syllabified)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Script to add syllable boundaries to a Yiddish word list.')
    parser.add_argument('-i', '--input', help='Path to a text file with one word per line', required=True)
    parser.add_argument('-o', '--output', help='Path to a text file that will be written, with one syllabified word per line', required=True)
    args = parser.parse_args()

    wordlist = readfile(args.input)

    syllabified_wordlist = []
    for word in wordlist:
        word = combine_chars(word)
        word = replace_consonant_j_syllabic_nl(word)

        yiddish = generate_yiddish_patterns()

        word = add_syllable_boundaries(yiddish, word)
        word = separate_chars(word)
        syllabified_wordlist.append(word)


    writefile(args.output, syllabified_wordlist)
