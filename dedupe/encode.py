"""
Transform and encode values
===========================

Values can be encoded for indexing, or transformed prior to comparison.

.. moduleauthor:: Graham Poulter
"""

import re


def dmetaphone(text):
    """Compute list of double-metaphone encodings of text.  See
    :mod:`dedupe.dmetaphone`."""
    import dmetaphone
    return dmetaphone.encode(text)


def normspace(text):
    """Strip multiple and trailing spaces.

    >>> normspace(' a  b  ')
    u'a b'
    """
    return re.sub(ur"\s+", u" ", text.strip())


def nospace(text):
    """Strip all whitespace.

    >>> nospace(" a  b  ")
    u'ab'
    """
    return re.sub(ur"\s+", u"", text.strip())


def lowstrip(text):
    """Lowcase and strip extra space.

    >>> lowstrip(" A  b  ")
    u'a b'
    """
    return normspace(text.lower())


def alnumsp(text):
    """Normalise space, strip punctuation.

    >>> alnumsp(" Joe (K) Ltd.  ")
    u'joe k ltd'
    """
    return normspace(re.sub(ur"\W+", u" ", text.lower()))


def digits(text):
    """Strip all except digits (for phone numbers).

    >>> digits("+27 (21) 1234567")
    '27211234567'
    """
    return re.sub(ur"\D+", "", text.strip())


def sorted_words(text):
    """Sort words.

    >>> sorted_words('c a b')
    'a b c'
    """
    return ' '.join(sorted(text.split(' ')))


def reverse(text):
    """Reverse text.

    >>> reverse('abc')
    'cba'
    """
    return text[::-1]


def urldomain(text):
    """Obtain the domain from the text of a URL.

    >>> urldomain("http://www.google.com")
    'google.com'
    >>> urldomain("www.google.com")
    'google.com'
    >>> urldomain("http://google.com")
    'google.com'
    >>> urldomain("http://www.google.com/a")
    'google.com'
    >>> urldomain("http://www.google.com/a/b")
    'google.com'
    """
    match = re.match(ur'(?:http://)?(?:www\.)?([^/]+)(?:/.*)?', text)
    if match is None:
        return text
    return match.group(1)


def emaildomain(text):
    """Obtain the domain from the text of an email address.

    >>> emaildomain("srtar@arst.com")
    'arst.com'
    >>> emaildomain("abc")
    'abc'
    """
    match = re.match(ur'([^@]+)@(.+)', text)
    if match is None:
        return text
    return match.group(2)


def wrap(*funcs):
    """Create a composited function from a list of unitary functions.
    For example, wrap(f1, f2, f3)(text) == f1(f2(f3(text)))

    :type funcs: function(U) V
    :param funcs: transformations to compose

    >>> wrap(sorted_words, reverse)("world hello")
    'dlrow olleh'
    """
    def _wrapper(text):
        # Innermost function gets applies first
        for func in funcs[::-1]:
            text = func(text)
        return text
    return _wrapper


class Normaliser:
    """Normalise terms in text using a dictionary mapping d[primary] ==
    [aliases]. Generates a regex to match each list of aliases, and when
    normalise is called on a text, it converts the text to use the primary
    form.

    >>> expansions = {'parkway': ['parkwy', 'pky', 'pkway'],
    ...  '' : ['co', 'company'],
    ...  'street' : ['str', r'st$'],
    ...  'promenade': ['prom'] }
    >>> norm = Normaliser(expansions)
    >>> norm('foo cooperative company')
    'foo cooperative'
    >>> norm('foo str')
    'foo street'
    >>> norm('foo St')
    'foo street'
    >>> norm('St John Prom')
    'St John promenade'
    >>> norm('Liesbeeck Pky pkWay')
    'Liesbeeck parkway parkway'
    """

    def __init__(self, aliases):
        import re
        self.aliases = aliases
        self.regexes = {}
        for primary, shortforms in self.aliases.iteritems():
            regex = r'\b(' + r'|'.join(shortforms) + r')\b'
            self.regexes[primary] = re.compile(regex, re.IGNORECASE)

    def normalise(self, text):
        """Convert aliases to primary form in the given text."""
        for primary, regex in self.regexes.iteritems():
            text = regex.sub(primary, text)
        return text.strip()
    __call__ = normalise
