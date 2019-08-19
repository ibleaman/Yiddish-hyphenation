# Yiddish hyphenation

Scripts to syllabify and hyphenate Yiddish text:

1. `yiddish_syllable_boundaries.py`: input is a text file containing Yiddish words, written in the Yiddish alphabet according to YIVO guidelines, one word per line; output is a text file of the same structure, but with the syllable boundaries in each word marked off (בי-כל)

2. `yiddish_hyphenation_latex.py` input is a text file containing Yiddish sentences/paragraphs (so this can be an article, chapter, book, etc.); output is a .tex file of hyphenated words, which can be included directly in the preamble of a LaTeX document. The list of words comes from the input file, not from a dictionary.

Syllabification is phonemic, based on the Maximum Onset Principle and using the attested syllable onset clusters listed in Jacobs 2005 (pp. 115-7). Hyphenation is based on the recommendations published in the *Standardized Yiddish Orthography* (YIVO; paragraph 47), stating that hyphens should be inserted between prefixes/particles and roots but otherwise should follow syllable boundaries.

Known problems, which require a list of exceptions to fix:

* Words of Hebrew/Aramaic (*loshn-koydesh*) origin. It's not clear how best to hyphenate these in all cases, and the syllabification algorithm is poor because these words are not spelled phonemically.
* More to come. Please send me your feedback! I might produce an exception list myself if I have time and if there's interest.

Isaac L. Bleaman  
University of California, Berkeley  
bleaman@berkeley.edu  

