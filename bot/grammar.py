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


def check_to_be(word, tags, i):
    after_word = None
    after_word2 = None
    before_word = None
    after_tag = None
    if i > 0:
        before_word = tags[i - 1][0]
    if i + 1 < len(tags):
        after_word = tags[i + 1][0]
        after_tag = tags[i + 1][1]
    if i + 2 < len(tags):
        after_word2 = tags[i + 2][1]
    if word.lower() == 'i':
        if after_word in ['am', 'was', 'wasn\'t']:
            if is_verb(after_word2):
                return False
            else:
                return True
        elif is_verb(after_tag):
            return  True
        else:
            if before_word in ['am', 'was', 'wasn\'t', 'not']:
                return True
            else:
                return False
    elif word.lower() in ['you', 'we', 'they']:
        if after_word in ['are', 'were', 'weren\'t']:
            if is_verb(after_word2):
                return False
            else:
                return True
        else:
            if before_word in ['are', 'were', 'weren\'t', 'not']:
                return True
            else:
                return False
    elif word.lower() in ['he', 'she', 'it']:
        if after_word in ['is', 'was', 'wasn\'t']:
            if is_verb(after_word2):
                return False
            else:
                return True
        else:
            if before_word in ['is', 'was', 'wasn\'t', 'not']:
                return True
            else:
                return False
    else:
        return True


def check_object_pronouns(word, before_word, before_prep):
    if word in ['me', 'him', 'her', 'us', 'them']:
        if before_word[1] == 'IN':
            if is_verb(before_prep[1]):
                return True
            else:
                return False
        elif is_verb(before_word[1]):
            return True
        else:
            return False
    else:
        return True


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
    tags = nltk.pos_tag(word_tokenize(message))
    print(tags)
    for i, tag in enumerate(tags):
        position = message.find(tag[0], position + 1)
        answer = check_to_be(tag[0], tags, i)
        if not answer:
            errors.append({'ErrorType': 'error4 (to be)', 'Position': position, 'Correct': ''})
        if is_noun(tag[1]):
            answer = check_plural_form_noun(tag[0])
            if answer != True:
                errors.append({'ErrorType': 'error1', 'Position': position, 'Correct': answer})
        if is_pronoun(tag[1]):
            before_word = None
            after_word = None
            if i > 0:
                before_word = tags[i-1][0]
            if i+1 < len(tags):
                after_word = tags[i+1][0]
            answer = check_can_permission(before_word, after_word)
            if not answer:
                errors.append({'ErrorType': 'error2 (can/cant - permission)', 'Position': position, 'Correct': ''})
            before_word = None
            before_prep = None
            if i > 0:
                before_word = tags[i-1]
            if i - 1 > 0:
                before_prep = tags[i-2]
            answer = check_object_pronouns(tag[0],before_word,before_prep)
            if not answer:
                errors.append({'ErrorType': 'error3 (Object Pronouns)', 'Position': position, 'Correct': ''})

    return errors


