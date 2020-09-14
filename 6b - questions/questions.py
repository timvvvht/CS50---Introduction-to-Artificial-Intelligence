import nltk
import sys
import string
import os
import re
import numpy as np

FILE_MATCHES = 1
SENTENCE_MATCHES = 1


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python questions.py corpus")

    # Calculate IDF values across files
    files = load_files(sys.argv[1])
    file_words = {
        filename: tokenize(files[filename])
        for filename in files
    }
    file_idfs = compute_idfs(file_words)

    # Prompt user for query
    query = set(tokenize(input("Query: ")))

    # Determine top file matches according to TF-IDF
    filenames = top_files(query, file_words, file_idfs, n=FILE_MATCHES)

    # Extract sentences from top files
    sentences = dict()
    for filename in filenames:
        for passage in files[filename].split("\n"):
            for sentence in nltk.sent_tokenize(passage):
                tokens = tokenize(sentence)
                if tokens:
                    sentences[sentence] = tokens

    # Compute IDF values across sentences
    idfs = compute_idfs(sentences)

    # Determine top sentence matches
    matches = top_sentences(query, sentences, idfs, n=SENTENCE_MATCHES)
    for match in matches:
        print(match)


def load_files(directory):
    """
    Given a directory name, return a dictionary mapping the filename of each
    `.txt` file inside that directory to the file's contents as a string.
    """
    txtfiles = [i for i in os.listdir(directory)]
    txtdict = dict.fromkeys(txtfiles)
    for file in txtdict:
        with open(os.path.join(directory,file)) as f:
            txtdict[file] = f.read()
    return txtdict


def tokenize(document):
    """
    Given a document (represented as a string), return a list of all of the
    words in that document, in order.

    Process document by coverting all words to lowercase, and removing any
    punctuation or English stopwords.
    """

    text = document.lower()
    regex = re.compile(r'\W').findall(text)
    text = nltk.word_tokenize(text)
    text = [
        t for t in text if t not in nltk.corpus.stopwords.words("english")
                           and t not in string.punctuation
                           and t not in regex
    ]
    return text


def compute_idfs(documents):
    """
    Given a dictionary of `documents` that maps names of documents to a list
    of words, return a dictionary that maps words to their IDF values.

    Any word that appears in at least one of the documents should be in the
    resulting dictionary.
    """
    words = set()
    for document in documents.values():
        for word in document:
            words.add(word)

    idfs_dict = dict.fromkeys(words)

    for word in idfs_dict:
        constant = 0
        for document in documents.values():
            if word in document:
                constant += 1
        idfs_dict[word] = np.log(len(documents)/constant)

    return idfs_dict



def top_files(query, files, idfs, n):
    """
    Given a `query` (a set of words), `files` (a dictionary mapping names of
    files to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the filenames of the the `n` top
    files that match the query, ranked according to tf-idf.
    """
    tfidf = dict.fromkeys([i for i in files])

    for doc in tfidf:
        doc_tfidf = 0
        for word in query:
            word_TF = 0
            for text in files[doc]:
                if word == text:
                    word_TF += 1
            if word_TF != 0:
                doc_tfidf += word_TF * idfs[word]
        tfidf[doc] = doc_tfidf
    sorted_dict = sorted(tfidf.items(), key=lambda x: x[1], reverse=True)
    sorted_dict = sorted_dict[:n]
    toplist = [i[0] for i in sorted_dict]
    return toplist


def top_sentences(query, sentences, idfs, n):
    """
    Given a `query` (a set of words), `sentences` (a dictionary mapping
    sentences to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the `n` top sentences that match
    the query, ranked according to idf. If there are ties, preference should
    be given to sentences that have a higher query term density.
    """

    sentence_values = dict.fromkeys([i for i in sentences])

    for sentence in sentence_values:
        sentence_idf = 0
        for word in query:
            if word in sentences[sentence]:
                sentence_idf += idfs[word]
        sentence_values[sentence] = sentence_idf
    sorted_dict = sorted(sentence_values.items(), key=lambda x: x[1], reverse=True)
    sorted_dict = sorted_dict[:n]
    top_sentence_list = [i[0] for i in sorted_dict]
    return top_sentence_list


if __name__ == "__main__":
    main()
