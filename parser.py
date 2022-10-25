import nltk
import sys

TERMINALS = """
Adj -> "country" | "dreadful" | "enigmatical" | "little" | "moist" | "red"
Adv -> "down" | "here" | "never"
Conj -> "and" | "until"
Det -> "a" | "an" | "his" | "my" | "the"
N -> "armchair" | "companion" | "day" | "door" | "hand" | "he" | "himself"
N -> "holmes" | "home" | "i" | "mess" | "paint" | "palm" | "pipe" | "she"
N -> "smile" | "thursday" | "walk" | "we" | "word"
P -> "at" | "before" | "in" | "of" | "on" | "to"
V -> "arrived" | "came" | "chuckled" | "had" | "lit" | "said" | "sat"
V -> "smiled" | "tell" | "were"
"""

NONTERMINALS = """
S -> NP VP
S -> NP VP PP
S -> NP VP NP VP
S -> NP VP VP NP
S -> NP VP PP VP NP PP
S -> NP VP PP PP
S -> NP VP VP PP

VP -> V | V NP | V PP | Adv V NP | V Adv | Conj NP V | Conj V
NP -> N | Det N | Det Adj N | Det Adj Adj N | Adj N | Conj N | Det Adj Adj Adj N
PP -> P | P NP | P NP Adv

"""

grammar = nltk.CFG.fromstring(NONTERMINALS + TERMINALS)
parser = nltk.ChartParser(grammar)


def main():

    # If filename specified, read sentence from file
    if len(sys.argv) == 2:
        with open(sys.argv[1]) as f:
            s = f.read()

    # Otherwise, get sentence as input
    else:
        s = input("Sentence: ")

    # Convert input into list of words
    s = preprocess(s)

    # Attempt to parse sentence
    try:
        trees = list(parser.parse(s))
    except ValueError as e:
        print(e)
        return
    if not trees:
        print("Could not parse sentence.")
        return

    # Print each tree with noun phrase chunks
    for tree in trees:
        tree.pretty_print()

        print("Noun Phrase Chunks")
        for np in np_chunk(tree):
            print(" ".join(np.flatten()))


def preprocess(sentence):
    """
    Convert `sentence` to a list of its words.
    Pre-process sentence by converting all characters to lowercase
    and removing any word that does not contain at least one alphabetic
    character.
    """
    # Convert sentence into a list of words
    sentence = nltk.tokenize.word_tokenize(sentence)

    # Process list to all lowercase words and removing non-alpha characters
    words = []
    for word in sentence:
        not_alpha = 0
        for letter in word:
            if letter.isalpha():
                break
            else:
                not_alpha += 1
        if not_alpha == 0:
            words.append(word.lower())

    return words


def np_chunk(tree):
    """
    Return a list of all noun phrase chunks in the sentence tree.
    A noun phrase chunk is defined as any subtree of the sentence
    whose label is "NP" that does not itself contain any other
    noun phrases as subtrees.
    """
    np = []

    for s in tree.subtrees(lambda t: t.height() == 3):
        if s.label() == "NP":
            np.append(s)

    return np


if __name__ == "__main__":
    main()
