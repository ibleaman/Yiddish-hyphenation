# Script to generate LaTeX hyphenation file for Yiddish
# Author: Isaac L. Bleaman <bleaman@berkeley.edu>
# Date: 2019-08-19

# How to run script:
# python yiddish_hyphenation_latex.py -i YIDDISH_DOCUMENT.tex -o LATEX_HYPHENATION.tex

# The script accepts a Yiddish text file as input, and outputs
# a file of hyphenated words that can be then \input{} directly into a
# LaTeX document preamble.

# It's similar to the syllable boundaries script, except that this doesn't
# add hyphens in the middle of prefixes, per YIVO's spelling recommendations.
# e.g.: זיך אָנעסן is "on-e-sn" ("on" is a prefix/particle) not: o-ne-sn (per normal syllabification)

# Note: This will only be useful in LaTeX if your original Yiddish text file
# is written with the YIVO orthography, using non-precombined characters (except
# for three: װ, ײ, ױ)

import argparse
import re
import yiddish_syllable_boundaries

def readfile(filename):
    with open(filename, 'r') as textfile:
        data = textfile.read()
    return data

def writeTeXfile(filename, wordlist):
    with open(filename, 'w') as textfile:
        textfile.write('\\hyphenation{')
        for word in wordlist:
            textfile.write(word + '\n')
        textfile.write('}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Script to add hyphenation to a Yiddish word list.')
    parser.add_argument('-i', '--input', help='Path to a Yiddish text document', required=True)
    parser.add_argument('-o', '--output', help='Path to a TeX file that will be written, with one hyphenated word per line', required=True)
    parser.add_argument('-s', '--system', choices=['jacobs', 'viler'], help='Syllabification system: "jacobs" follows Maximum Onset Principle using all the onsets from Jacobs (2005:115-7); "viler" follows syllabification of Yankev Viler, cited by Jacobs (2005:125)', required=True)
    args = parser.parse_args()

    text = readfile(args.input)

    # tokenize the text, splitting on spaces and punctuation, and get unique words
    unique_words = re.split(r'[\s,\.\?!„“־\-;:\(\)\–\—׳‘’]', text)
    unique_words = sorted(set(unique_words))

    # List of verbal particles from Jacobs (2005:210)
    # Supplemented by list of verbal prefixes (ant- ba- ge- der- far- tse-)
    prefixes = (
        'אַדורכ',
        'דורכ',
        'אַהינ',
        'אַהער',
        'אַװעק',
        'אױס',
        'אומ',
        'אונטער',
        'אױפֿ',
        'אַנטקעגנ',
        'אַקעגנ',
        'קעגנ',
        'איבער',
        'אײַנ',
        'אָנ',
        'אַנידער',
        'אָפּ',
        'אַראָפּ',
        'אַרױס',
        'אַרומ',
        'אַרױפֿ',
        'אַריבער',
        'אַרײַנ',
        'בײַ',
        'מיט',
        'נאָכ',
        'פֿונאַנדער',
        'פֿאַנאַנדער',
        'פֿאָר',
        'פֿאָרױס',
        'אַפֿער',
        'אַפֿיר',
        'פֿיר',
        'צוזאַמענ',
        'צונױפֿ',
        'צוריק',
        'צו',
        'קריק',
        'קאַריק',
        'פֿאַרבײַ',
        'אַנט',
        'באַ',
        'גע',
        'דער',
        'פֿאַר',
        'צע',
    )

    # add hyphens after prefixes and append; if none, just append the word
    words_prefixes_separated = []
    for word in unique_words:
        if not word.startswith(prefixes):
            words_prefixes_separated.append(word)
        else:
            word_added = False
            for prefix in prefixes:
                if word.startswith(prefix) and not word.endswith(prefix): # if word starts with but not= prefix
                    words_prefixes_separated.append(prefix + '-' + word[len(prefix):])
                    word_added = True
                    break
            if not word_added: # if whole word = prefix (e.g., אַריבער)
                words_prefixes_separated.append(word)

    # add hyphenation throughout
    hyphenated_words = []
    yiddish = yiddish_syllable_boundaries.generate_yiddish_patterns(args.system)
    for word in words_prefixes_separated:
        word = yiddish_syllable_boundaries.combine_chars(word)
        word = yiddish_syllable_boundaries.replace_consonant_j_syllabic_nl(word)
        word = yiddish_syllable_boundaries.add_syllable_boundaries(yiddish, word)
        word = yiddish_syllable_boundaries.separate_chars(word)
        if '-' in word:
            hyphenated_words.append(word)

    writeTeXfile(args.output, hyphenated_words)
