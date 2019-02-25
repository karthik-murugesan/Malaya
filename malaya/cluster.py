import numpy as np
import itertools

_accepted_pos = [
    'ADJ',
    'ADP',
    'ADV',
    'ADX',
    'CCONJ',
    'DET',
    'NOUN',
    'NUM',
    'PART',
    'PRON',
    'PROPN',
    'SCONJ',
    'SYM',
    'VERB',
    'X',
]
_accepted_entities = [
    'OTHER',
    'law',
    'location',
    'organization',
    'person',
    'quantity',
    'time',
    'event',
]


def cluster_words(list_words):
    """
    cluster similar words based on structure, eg, ['mahathir mohamad', 'mahathir'] = ['mahathir mohamad']

    Parameters
    ----------
    list_words : list of str

    Returns
    -------
    string: list of clustered words
    """
    if not isinstance(list_words, list):
        raise ValueError('list_words must be a list')
    if not isinstance(list_words[0], str):
        raise ValueError('list_words must be a list of strings')

    dict_words = {}
    for word in list_words:
        found = False
        for key in dict_words.keys():
            if word in key or any(
                [word in inside for inside in dict_words[key]]
            ):
                dict_words[key].append(word)
                found = True
            if key in word:
                dict_words[key].append(word)
        if not found:
            dict_words[word] = [word]
    results = []
    for key, words in dict_words.items():
        results.append(max(list(set([key] + words)), key = len))
    return list(set(results))


def _pad_sequence(
    sequence,
    n,
    pad_left = False,
    pad_right = False,
    left_pad_symbol = None,
    right_pad_symbol = None,
):
    sequence = iter(sequence)
    if pad_left:
        sequence = itertools.chain((left_pad_symbol,) * (n - 1), sequence)
    if pad_right:
        sequence = itertools.chain(sequence, (right_pad_symbol,) * (n - 1))
    return sequence


def ngrams(
    sequence,
    n,
    pad_left = False,
    pad_right = False,
    left_pad_symbol = None,
    right_pad_symbol = None,
):
    """
    generate ngrams

    Parameters
    ----------
    sequence : list of str
        list of tokenize words
    n : int
        ngram size

    Returns
    -------
    ngram: list
    """
    sequence = _pad_sequence(
        sequence, n, pad_left, pad_right, left_pad_symbol, right_pad_symbol
    )

    history = []
    while n > 1:
        try:
            next_item = next(sequence)
        except StopIteration:
            return
        history.append(next_item)
        n -= 1
    for item in sequence:
        history.append(item)
        yield tuple(history)
        del history[0]


def pos_entities_ngram(
    result_pos,
    result_entities,
    ngram = (1, 3),
    accept_pos = ['NOUN', 'PROPN', 'VERB'],
    accept_entities = ['law', 'location', 'organization', 'person', 'time'],
):
    """
    generate ngrams

    Parameters
    ----------
    result_pos : list of tuple
        result from POS recognition
    result_entities : list of tuple
        result of Entities recognition
    ngram : tuple
        ngram sizes
    accept_pos : list of str
        accepted POS elements
    accept_entities : list of str
        accept entities elements

    Returns
    -------
    result: list
    """
    if not isinstance(result_pos, list):
        raise ValueError('result_pos must be a list')
    if not isinstance(result_pos[0], tuple):
        raise ValueError('result_pos must be a list of tuple')
    if not isinstance(ngram, tuple):
        raise ValueError('ngram must be a tuple')
    if not len(ngram) == 2:
        raise ValueError('ngram size must equal to 2')
    if not isinstance(accept_pos, list):
        raise ValueError('accept_pos must be a list')
    if not isinstance(accept_entities, list):
        raise ValueError('accept_entites must be a list')
    if not all([i in _accepted_pos for i in accept_pos]):
        raise ValueError(
            'accept_pos must be a subset or equal of supported POS, please run malaya.describe_pos() to get supported POS'
        )
    if not all([i in _accepted_entities for i in accept_entities]):
        raise ValueError(
            'accept_entites must be a subset or equal of supported entities, please run malaya.describe_entities() to get supported entities'
        )

    words = []
    sentences = []
    for no in range(len(result_pos)):
        if (
            result_pos[no][1] in accept_pos
            or result_entities[no][1] in accept_entities
        ):
            words.append(result_pos[no][0])
    for gram in range(ngram[0], ngram[1] + 1, 1):
        gram_words = list(ngrams(words, gram))
        for sentence in gram_words:
            sentences.append(' '.join(sentence))
    return list(set(sentences))


def sentence_ngram(sentence, ngram = (1, 3)):
    """
    generate ngram for a text

    Parameters
    ----------
    sentence: str
    ngram : tuple
        ngram sizes

    Returns
    -------
    result: list
    """
    if not (sentence, str):
        raise ValueError('sentence must be a string')
    if not isinstance(ngram, tuple):
        raise ValueError('ngram must be a tuple')
    if not len(ngram) == 2:
        raise ValueError('ngram size must equal to 2')

    words = sentence.split()
    sentences = []
    for gram in range(ngram[0], ngram[1] + 1, 1):
        gram_words = list(ngrams(words, gram))
        for sentence in gram_words:
            sentences.append(' '.join(sentence))
    return list(set(sentences))


def cluster_pos(result):
    """
    cluster similar POS

    Parameters
    ----------
    result: list

    Returns
    -------
    result: list
    """
    if not isinstance(result, list):
        raise ValueError('result must be a list')
    if not isinstance(result[0], tuple):
        raise ValueError('result must be a list of tuple')
    if not all([i[1] in _accepted_pos for i in result]):
        raise ValueError(
            'elements of result must be a subset or equal of supported POS, please run malaya.describe_pos() to get supported POS'
        )

    output = {
        'ADJ': [],
        'ADP': [],
        'ADV': [],
        'ADX': [],
        'CCONJ': [],
        'DET': [],
        'NOUN': [],
        'NUM': [],
        'PART': [],
        'PRON': [],
        'PROPN': [],
        'SCONJ': [],
        'SYM': [],
        'VERB': [],
        'X': [],
    }
    last_label, words = None, []
    for word, label in result:
        if last_label != label and last_label:
            joined = ' '.join(words)
            if joined not in output[last_label]:
                output[last_label].append(joined)
            words = []
            last_label = label
            words.append(word)

        else:
            if not last_label:
                last_label = label
            words.append(word)
    return output


def cluster_entities(result):
    """
    cluster similar Entities

    Parameters
    ----------
    result: list

    Returns
    -------
    result: list
    """
    if not isinstance(result, list):
        raise ValueError('result must be a list')
    if not isinstance(result[0], tuple):
        raise ValueError('result must be a list of tuple')
    if not all([i[1] in _accepted_entities for i in result]):
        raise ValueError(
            'elements of result must be a subset or equal of supported POS, please run malaya.describe_pos() to get supported POS'
        )

    output = {
        'OTHER': [],
        'law': [],
        'location': [],
        'organization': [],
        'person': [],
        'quantity': [],
        'time': [],
        'event': [],
    }
    last_label, words = None, []
    for word, label in result:
        if last_label != label and last_label:
            joined = ' '.join(words)
            if joined not in output[last_label]:
                output[last_label].append(joined)
            words = []
            last_label = label
            words.append(word)

        else:
            if not last_label:
                last_label = label
            words.append(word)
    return output
