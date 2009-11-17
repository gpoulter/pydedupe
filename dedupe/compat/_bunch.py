"""
:mod:`bunch` -- Attribute-accessible dictionary
===============================================

.. module:: bunch
   :synopsis: Turn a dictionary into an object
.. moduleauthor:: Graham Poulter
"""

class bunch(object):
    """Populate an object the attributes passed via the constructor.  Syntactic
    sugar for a dictionary with well-known keys."""

    def __init__(self, **kwds):
        self.__dict__.update(kwds)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __repr__(self):
        args = sorted('%s=%s' % (k, repr(v)) for (k,v) in vars(self).items())
        return 'bunch(%s)' % ', '.join(args)

    def __str__(self):
        args = sorted('%s=%s' % (k, str(v)) for (k,v) in vars(self).items())
        return '<%s>' % ', '.join(args)
