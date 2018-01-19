import nltk
import inflect

from nltk.tokenize import word_tokenize

inflect = inflect.engine()


def is_noun(tag):
    return tag in ['NN', 'NNS', 'NNP', 'NNPS']


def is_verb(tag):
    return tag in ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']


def is_adverb(tag):
    return tag in ['RB', 'RBR', 'RBS']


def is_adjective(tag):
    return tag in ['JJ', 'JJR', 'JJS']


def get_tags(query):
    return nltk.pos_tag(word_tokenize(query))


def check_plural_form_noun(word):
    if inflect.singular_noun(word) is False:
        return True
    else:
        sing_word = inflect.singular_noun(word)
        plural_word = inflect.plural_noun(sing_word)
        if plural_word == word:
            return True
        else:
            return plural_word


def get_errors_plural_forn_nouns(message):
    errors = []
    position = -1
    tags = nltk.pos_tag(word_tokenize(message))
    for tag in tags:
        position = message.find(tag[0], position + 1)
        if is_noun(tag[1]):
            answer = check_plural_form_noun(tag[0])
            print(answer)
            if answer != True:
                errors.append({'ErrorType': 'error1', 'Position': position, 'Correct': answer})
    return errors
