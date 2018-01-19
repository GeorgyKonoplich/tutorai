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


def is_pronoun(tag):
    return tag in ['PRP$', 'PRP', 'WP', 'WP$']


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


def check_can_permission(before_word, after_word):
    if (before_word is None) or (after_word is None):
        return True
    elif after_word in ['can\'t', 'can', 'cannot']:
        return True
    elif before_word not in ['can\'t', 'can', 'cannot', 'not']:
        return False
    else:
        return True



def get_errors_plural_forn_nouns(message):
    errors = []
    position = -1
    words = word_tokenize(message)
    tags = nltk.pos_tag(word_tokenize(message))
    for i, tag in enumerate(tags):
        position = message.find(tag[0], position + 1)
        if is_noun(tag[1]):
            answer = check_plural_form_noun(tag[0])
            if answer != True:
                errors.append({'ErrorType': 'error1', 'Position': position, 'Correct': answer})
        if is_pronoun(tag[1]):
            before_word = None
            after_word = None
            if i > 0:
                before_word = words[i-1]
            if i+1 < len(words):
                after_word = words[i+1]
            answer = check_can_permission(before_word, after_word)
            if not answer:
                errors.append({'ErrorType': 'error2 (can/cant - permission)', 'Position': position, 'Correct': ''})

    return errors

