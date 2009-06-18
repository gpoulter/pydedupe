"""Compute the Double Metaphone code for a string.

The Original Software is: "encode.py". The Initial Developer of the Original
Software is Dr Peter Christen (Department of Computer Science, Australian
National University).
 
Copyright (C) 2002 - 2008 the Australian National University and
others. All Rights Reserved.
 
Freely extensible biomedical record linkage (Febrl) - Version 0.4.1

See: http://datamining.anu.edu.au/linkage.html

dmetaphone is based on:
 - Lawrence Philips C++ code as published in C/C++ Users Journal (June 2000)
   and available at:
   http://www.cuj.com/articles/2000/0006/0006d/0006d.htm
 - Perl/C implementation
   http://www.cpan.org/modules/by-authors/id/MAURICE/

See also:
 - http://aspell.sourceforge.net/metaphone/
 - http://www.nist.gov/dads/HTML/doubleMetaphone.html
"""

__license__ = """
Copyright (C) 2008-2008 the Australian National University

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

def dmetaphone(s, maxlen=4):
    """Compute the Double Metaphone code for a string.

    @param s: A string containing a name. 
    
    @param maxlen: Maximal length of the returned code. If a code is longer
    than 'maxlen' it is truncated. Default value is 4.

    
    DESCRIPTION:
  """

    if (not s):
        return ''

    primary = ''
    secondary = ''
    alternate = ''
    primary_len = 0
    secondary_len = 0

    # Sub routines  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    #
    def isvowel(c):
        if (c in 'aeiouy'):
            return 1
        else:
            return 0

    def slavogermanic(str):
        if (str.find('w')>-1) or (str.find('k')>-1) or (str.find('cz')>-1) or \
           (str.find('witz')>-1):
            return 1
        else:
            return 0

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    length = len(s)
    if (length < 1):
        return ''
    last = length-1

    current = 0  # Current position in string
    workstr = s+'      '

    if (workstr[0:2] in ['gn','kn','pn','wr','ps']):
        current = current+1  # Skip first character

    if (workstr[0] == 'x'):  # Initial 'x' is pronounced like 's'
        primary = primary+'s'
        primary_len = primary_len+1
        secondary = secondary+'s'
        secondary_len = secondary_len+1
        current = current+1

    if (maxlen < 1):  # Calculate maximum length to check
        check_maxlen = length
    else:
        check_maxlen = maxlen

    while (primary_len < check_maxlen) or (secondary_len < check_maxlen):
        if (current >= length):
            break

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Main loop, analyse current character
        #
        c = workstr[current]

        if (c in 'aeiouy'):
            if (current == 0):  # All initial vowels map to 'a'
                primary = primary+'a'
                primary_len = primary_len+1
                secondary = secondary+'a'
                secondary_len = secondary_len+1
            current=current+1

        elif (c == 'b'):  # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            primary = primary+'p'
            primary_len = primary_len+1
            secondary = secondary+'p'
            secondary_len = secondary_len+1
            if (workstr[current+1] == 'b'):
                current=current+2
            else:
                current=current+1

        # elif (s == 'c'):  # C
        #    primary = primary+'s'
        #    primary_len = primary_len+1
        #    secondary = secondary+'s'
        #    secondary_len = secondary_len+1
        #    current = current+1

        elif (c == 'c'):  # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            if (current > 1) and (not isvowel(workstr[current-2])) and \
               workstr[current-1:current+2] == 'ach' and \
               (workstr[current+2] != 'i' and \
                (workstr[current+2] != 'e' or \
                 workstr[current-2:current+4] in ['bacher','macher'])):
                primary = primary+'k'  # Various germanic special cases
                primary_len = primary_len+1
                secondary = secondary+'k'
                secondary_len = secondary_len+1
                current = current+2
            elif (current == 0) and (workstr[0:6] == 'caesar'):
                primary = primary+'s'
                primary_len = primary_len+1
                secondary = secondary+'s'
                secondary_len = secondary_len+1
                current = current+2
            elif (workstr[current:current+4] == 'chia'): # Italian 'chianti'
                primary = primary+'k'
                primary_len = primary_len+1
                secondary = secondary+'k'
                secondary_len = secondary_len+1
                current = current+2
            elif (workstr[current:current+2] == 'ch'):
                if (current > 0) and (workstr[current:current+4] == 'chae'):
                    primary = primary+'k'  # Find 'michael'
                    primary_len = primary_len+1
                    secondary = secondary+'x'
                    secondary_len = secondary_len+1
                    current = current+2
                elif (current == 0) and \
                     (workstr[current+1:current+6] in ['harac','haris'] or \
                      workstr[current+1:current+4] in \
                      ['hor','hym','hia','hem']) and \
                     workstr[0:6] != 'chore':
                    primary = primary+'k'  # Greek roots, eg. 'chemistry'
                    primary_len = primary_len+1
                    secondary = secondary+'k'
                    secondary_len = secondary_len+1
                    current = current+2
                elif (workstr[0:4] in ['van ','von '] or \
                      workstr[0:3] == 'sch') or \
                     workstr[current-2:current+4] in \
                     ['orches','archit','orchid'] or \
                     workstr[current+2] in ['t','s'] or \
                     ((workstr[current-1] in ['a','o','u','e'] or \
                       current==0) and \
                      workstr[current+2] in \
                      ['l','r','n','m','b','h','f','v','w',' ']):
                    primary = primary+'k'
                    primary_len = primary_len+1
                    secondary = secondary+'k'
                    secondary_len = secondary_len+1
                    current = current+2
                else:
                    if (current > 0):
                        if (workstr[0:2] == 'mc'):
                            primary = primary+'k'
                            primary_len = primary_len+1
                            secondary = secondary+'k'
                            secondary_len = secondary_len+1
                            current = current+2
                        else:
                            primary = primary+'x'
                            primary_len = primary_len+1
                            secondary = secondary+'k'
                            secondary_len = secondary_len+1
                            current = current+2
                    else:
                        primary = primary+'x'
                        primary_len = primary_len+1
                        secondary = secondary+'x'
                        secondary_len = secondary_len+1
                        current=current+2
            elif (workstr[current:current+2] == 'cz') and \
                 (workstr[current-2:current+2] != 'wicz'):
                primary = primary+'s'
                primary_len = primary_len+1
                secondary = secondary+'x'
                secondary_len = secondary_len+1
                current=current+2
            elif (workstr[current+1:current+4] == 'cia'):
                primary = primary+'x'
                primary_len = primary_len+1
                secondary = secondary+'x'
                secondary_len = secondary_len+1
                current=current+3
            elif (workstr[current:current+2] == 'cc') and \
                 not (current==1 and workstr[0] == 'm'):
                if (workstr[current+2] in ['i','e','h']) and \
                   (workstr[current+2:current+4] != 'hu'):
                    if (current == 1 and workstr[0] == 'a') or \
                       (workstr[current-1:current+4] in ['uccee','ucces']):
                        primary = primary+'ks'
                        primary_len = primary_len+2
                        secondary = secondary+'ks'
                        secondary_len = secondary_len+2
                        current=current+3
                    else:
                        primary = primary+'x'
                        primary_len = primary_len+1
                        secondary = secondary+'x'
                        secondary_len = secondary_len+1
                        current=current+3
                else:  # Pierce's rule
                    primary = primary+'k'
                    primary_len = primary_len+1
                    secondary = secondary+'k'
                    secondary_len = secondary_len+1
                    current=current+2
            elif (workstr[current:current+2] in ['ck','cg','cq']):
                primary = primary+'k'
                primary_len = primary_len+1
                secondary = secondary+'k'
                secondary_len = secondary_len+1
                current=current+2
            elif (workstr[current:current+2] in ['ci','ce','cy']):
                if (workstr[current:current+3] in ['cio','cie','cia']):
                    primary = primary+'s'
                    primary_len = primary_len+1
                    secondary = secondary+'x'
                    secondary_len = secondary_len+1
                    current=current+2
                else:
                    primary = primary+'s'
                    primary_len = primary_len+1
                    secondary = secondary+'s'
                    secondary_len = secondary_len+1
                    current=current+2
            else:
                primary = primary+'k'
                primary_len = primary_len+1
                secondary = secondary+'k'
                secondary_len = secondary_len+1
                if (workstr[current+1:current+3] in [' c',' q',' g']):
                    current=current+3
                else:
                    if (workstr[current+1] in ['c','k','q']) and \
                       (workstr[current+1:current+3] not in ['ce','ci']):
                        current=current+2
                    else:
                        current=current+1

        elif (c == 'd'):  # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            if (workstr[current:current+2] == 'dg'):
                if (workstr[current+2] in ['i','e','y']):  # Eg. 'edge'
                    primary = primary+'j'
                    primary_len = primary_len+1
                    secondary = secondary+'j'
                    secondary_len = secondary_len+1
                    current=current+3
                else:  # Eg. 'edgar'
                    primary = primary+'tk'
                    primary_len = primary_len+2
                    secondary = secondary+'tk'
                    secondary_len = secondary_len+2
                    current=current+2
            elif (workstr[current:current+2] in ['dt','dd']):
                primary = primary+'t'
                primary_len = primary_len+1
                secondary = secondary+'t'
                secondary_len = secondary_len+1
                current=current+2
            else:
                primary = primary+'t'
                primary_len = primary_len+1
                secondary = secondary+'t'
                secondary_len = secondary_len+1
                current=current+1

        elif (c == 'f'):  # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            if (workstr[current+1] == 'f'):
                current=current+2
            else:
                current=current+1
            primary = primary+'f'
            primary_len = primary_len+1
            secondary = secondary+'f'
            secondary_len = secondary_len+1

        elif (c == 'g'):  # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            if (workstr[current+1] == 'h'):
                if (current > 0 and not isvowel(workstr[current-1])):
                    primary = primary+'k'
                    primary_len = primary_len+1
                    secondary = secondary+'k'
                    secondary_len = secondary_len+1
                    current=current+2
                elif (current==0):
                    if (workstr[current+2] == 'i'): # Eg. ghislane, ghiradelli
                        primary = primary+'j'
                        primary_len = primary_len+1
                        secondary = secondary+'j'
                        secondary_len = secondary_len+1
                        current=current+2
                    else:
                        primary = primary+'k'
                        primary_len = primary_len+1
                        secondary = secondary+'k'
                        secondary_len = secondary_len+1
                        current=current+2
                elif (current>1 and workstr[current-2] in ['b','h','d']) or \
                     (current>2 and workstr[current-3] in ['b','h','d']) or \
                     (current>3 and workstr[current-4] in ['b','h']):
                    current=current+2
                else:
                    if (current > 2) and (workstr[current-1] == 'u') and \
                       (workstr[current-3] in ['c','g','l','r','t']):
                        primary = primary+'f'
                        primary_len = primary_len+1
                        secondary = secondary+'f'
                        secondary_len = secondary_len+1
                        current=current+2
                    else:
                        if (current > 0) and (workstr[current-1] != 'i'):
                            primary = primary+'k'
                            primary_len = primary_len+1
                            secondary = secondary+'k'
                            secondary_len = secondary_len+1
                            current=current+2
                        else:
                            current=current+2
            elif (workstr[current+1] == 'n'):
                if (current==1) and (isvowel(workstr[0])) and \
                   (not slavogermanic(workstr)):
                    primary = primary+'kn'
                    primary_len = primary_len+2
                    secondary = secondary+'n'
                    secondary_len = secondary_len+1
                    current=current+2
                else:
                    if (workstr[current+2:current+4] != 'ey') and \
                       (workstr[current+1] != 'y') and \
                       (not slavogermanic(workstr)):
                        primary = primary+'n'
                        primary_len = primary_len+1
                        secondary = secondary+'kn'
                        secondary_len = secondary_len+2
                        current=current+2
                    else:
                        primary = primary+'kn'
                        primary_len = primary_len+2
                        secondary = secondary+'kn'
                        secondary_len = secondary_len+2
                        current=current+2
            elif (workstr[current+1:current+3] == 'li') and \
                 (not slavogermanic(workstr)):
                primary = primary+'kl'
                primary_len = primary_len+2
                secondary = secondary+'l'
                secondary_len = secondary_len+1
                current=current+2
            elif (current==0) and ((workstr[current+1] == 'y') or \
                                   (workstr[current+1:current+3] in \
                                    ['es','ep','eb','el','ey','ib','il','in','ie','ei','er'])):
                primary = primary+'k'
                primary_len = primary_len+1
                secondary = secondary+'j'
                secondary_len = secondary_len+1
                current=current+2
            elif (workstr[current+1:current+3] == 'er' or \
                  workstr[current+1] == 'y') and \
                 workstr[0:6] not in ['danger','ranger','manger'] and \
                 workstr[current-1] not in ['e','i'] and \
                 workstr[current-1:current+2] not in ['rgy','ogy']:
                primary = primary+'k'
                primary_len = primary_len+1
                secondary = secondary+'j'
                secondary_len = secondary_len+1
                current=current+2
            elif (workstr[current+1] in ['e','i','y']) or \
                 (workstr[current-1:current+3] in ['aggi','oggi']):
                if (workstr[0:4] in ['van ','von ']) or \
                   (workstr[0:3] == 'sch') or \
                   (workstr[current+1:current+3] == 'et'):
                    primary = primary+'k'
                    primary_len = primary_len+1
                    secondary = secondary+'k'
                    secondary_len = secondary_len+1
                    current=current+2
                else:
                    if (workstr[current+1:current+5] == 'ier '):
                        primary = primary+'j'
                        primary_len = primary_len+1
                        secondary = secondary+'j'
                        secondary_len = secondary_len+1
                        current=current+2
                    else:
                        primary = primary+'j'
                        primary_len = primary_len+1
                        secondary = secondary+'k'
                        secondary_len = secondary_len+1
                        current=current+2
            else:
                if (workstr[current+1] == 'g'):
                    current=current+2
                else:
                    current=current+1
                primary = primary+'k'
                primary_len = primary_len+1
                secondary = secondary+'k'
                secondary_len = secondary_len+1

        elif (c =='h'):  # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            if (current == 0 or isvowel(workstr[current-1])) and \
               isvowel(workstr[current+1]):
                primary = primary+'h'
                primary_len = primary_len+1
                secondary = secondary+'h'
                secondary_len = secondary_len+1
                current=current+2
            else:
                current=current+1

        elif (c =='j'):  # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            if (workstr[current:current+4] == 'jose') or \
               (workstr[0:4] == 'san '):
                if (current == 0 and workstr[4] == ' ') or \
                   (workstr[0:4] == 'san '):
                    primary = primary+'h'
                    primary_len = primary_len+1
                    secondary = secondary+'h'
                    secondary_len = secondary_len+1
                    current=current+1
                else:
                    primary = primary+'j'
                    primary_len = primary_len+1
                    secondary = secondary+'h'
                    secondary_len = secondary_len+1
                    current=current+1
            elif (current==0) and (workstr[0:4] != 'jose'):
                primary = primary+'j'
                primary_len = primary_len+1
                secondary = secondary+'a'
                secondary_len = secondary_len+1
                if (workstr[current+1] == 'j'):
                    current=current+2
                else:
                    current=current+1
            else:
                if (isvowel(workstr[current-1])) and \
                   (not slavogermanic(workstr)) and \
                   (workstr[current+1] in ['a','o']):
                    primary = primary+'j'
                    primary_len = primary_len+1
                    secondary = secondary+'h'
                    secondary_len = secondary_len+1
                else:
                    if (current == last):
                        primary = primary+'j'
                        primary_len = primary_len+1
                        #secondary = secondary+''
                        #secondary_len = secondary_len+0
                    else:
                        if (workstr[current+1] not in \
                            ['l','t','k','s','n','m','b','z']) and \
                           (workstr[current-1] not in ['s','k','l']):
                            primary = primary+'j'
                            primary_len = primary_len+1
                            secondary = secondary+'j'
                            secondary_len = secondary_len+1
                if (workstr[current+1] == 'j'):
                    current=current+2
                else:
                    current=current+1

        elif (c =='k'):  #  - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            if (workstr[current+1] == 'k'):
                current=current+2
            else:
                current=current+1
            primary = primary+'k'
            primary_len = primary_len+1
            secondary = secondary+'k'
            secondary_len = secondary_len+1

        elif (c == 'l'):  # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            if (workstr[current+1] == 'l'):
                if (current == (length-3)) and \
                   (workstr[current-1:current+3] in ['illo','illa','alle']) or \
                   ((workstr[last-1:last+1] in ['as','os']  or
                     workstr[last] in ['a','o']) and \
                    workstr[current-1:current+3] == 'alle'):
                    primary = primary+'l'
                    primary_len = primary_len+1
                    #secondary = secondary+''
                    #secondary_len = secondary_len+0
                    current=current+2
                else:
                    primary = primary+'l'
                    primary_len = primary_len+1
                    secondary = secondary+'l'
                    secondary_len = secondary_len+1
                    current=current+2
            else:
                primary = primary+'l'
                primary_len = primary_len+1
                secondary = secondary+'l'
                secondary_len = secondary_len+1
                current=current+1

        elif (c == 'm'):  # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            if (workstr[current-1:current+2] == 'umb' and \
                ((current+1) == last or \
                 workstr[current+2:current+4] == 'er')) or \
               workstr[current+1] == 'm':
                current=current+2
            else:
                current=current+1
            primary = primary+'m'
            primary_len = primary_len+1
            secondary = secondary+'m'
            secondary_len = secondary_len+1

        elif (c == 'n'):  # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            if (workstr[current+1] == 'n'):
                current=current+2
            else:
                current=current+1
            primary = primary+'n'
            primary_len = primary_len+1
            secondary = secondary+'n'
            secondary_len = secondary_len+1

        elif (c == 'p'):  # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            if (workstr[current+1] == 'h'):
                primary = primary+'f'
                primary_len = primary_len+1
                secondary = secondary+'f'
                secondary_len = secondary_len+1
                current=current+2
            elif (workstr[current+1] in ['p','b']):
                primary = primary+'p'
                primary_len = primary_len+1
                secondary = secondary+'p'
                secondary_len = secondary_len+1
                current=current+2
            else:
                primary = primary+'p'
                primary_len = primary_len+1
                secondary = secondary+'p'
                secondary_len = secondary_len+1
                current=current+1

        elif (c == 'q'):  # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            if (workstr[current+1] == 'q'):
                current=current+2
            else:
                current=current+1
            primary = primary+'k'
            primary_len = primary_len+1
            secondary = secondary+'k'
            secondary_len = secondary_len+1

        elif (c == 'r'):  # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            if (current==last) and (not slavogermanic(workstr)) and \
               (workstr[current-2:current] == 'ie') and \
               (workstr[current-4:current-2] not in ['me','ma']):
                # primary = primary+''
                # primary_len = primary_len+0
                secondary = secondary+'r'
                secondary_len = secondary_len+1
            else:
                primary = primary+'r'
                primary_len = primary_len+1
                secondary = secondary+'r'
                secondary_len = secondary_len+1
            if (workstr[current+1] == 'r'):
                current=current+2
            else:
                current=current+1

        elif (c == 's'):  # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            if (workstr[current-1:current+2] in ['isl','ysl']):
                current=current+1
            elif (current==0) and (workstr[0:5] == 'sugar'):
                primary = primary+'x'
                primary_len = primary_len+1
                secondary = secondary+'s'
                secondary_len = secondary_len+1
                current=current+1
            elif (workstr[current:current+2] == 'sh'):
                if (workstr[current+1:current+5] in \
                    ['heim','hoek','holm','holz']):
                    primary = primary+'s'
                    primary_len = primary_len+1
                    secondary = secondary+'s'
                    secondary_len = secondary_len+1
                    current=current+2
                else:
                    primary = primary+'x'
                    primary_len = primary_len+1
                    secondary = secondary+'x'
                    secondary_len = secondary_len+1
                    current=current+2
            elif (workstr[current:current+3] in ['sio','sia']) or \
                 (workstr[current:current+4] == 'sian'):
                if (not slavogermanic(workstr)):
                    primary = primary+'s'
                    primary_len = primary_len+1
                    secondary = secondary+'x'
                    secondary_len = secondary_len+1
                    current=current+3
                else:
                    primary = primary+'s'
                    primary_len = primary_len+1
                    secondary = secondary+'s'
                    secondary_len = secondary_len+1
                    current=current+3
            elif ((current==0) and (workstr[1] in ['m','n','l','w'])) or \
                 (workstr[current+1] == 'z'):
                primary = primary+'s'
                primary_len = primary_len+1
                secondary = secondary+'x'
                secondary_len = secondary_len+1
                if (workstr[current+1] == 'z'):
                    current=current+2
                else:
                    current=current+1
            elif (workstr[current:current+2] == 'sc'):
                if (workstr[current+2] == 'h'):
                    if (workstr[current+3:current+5] in \
                        ['oo','er','en','uy','ed','em']):
                        if (workstr[current+3:current+5] in ['er','en']):
                            primary = primary+'x'
                            primary_len = primary_len+1
                            secondary = secondary+'sk'
                            secondary_len = secondary_len+2
                            current=current+3
                        else:
                            primary = primary+'sk'
                            primary_len = primary_len+2
                            secondary = secondary+'sk'
                            secondary_len = secondary_len+2
                            current=current+3
                    else:
                        if (current==0) and (not isvowel(workstr[3])) and \
                           (workstr[3] != 'w'):
                            primary = primary+'x'
                            primary_len = primary_len+1
                            secondary = secondary+'s'
                            secondary_len = secondary_len+1
                            current=current+3
                        else:
                            primary = primary+'x'
                            primary_len = primary_len+1
                            secondary = secondary+'x'
                            secondary_len = secondary_len+1
                            current=current+3
                elif (workstr[current+2] in ['i','e','y']):
                    primary = primary+'s'
                    primary_len = primary_len+1
                    secondary = secondary+'s'
                    secondary_len = secondary_len+1
                    current=current+3
                else:
                    primary = primary+'sk'
                    primary_len = primary_len+2
                    secondary = secondary+'sk'
                    secondary_len = secondary_len+2
                    current=current+3
            elif (current==last) and \
                 (workstr[current-2:current] in ['ai','oi']):
                # primary = primary+''
                # primary_len = primary_len+0
                secondary = secondary+'s'
                secondary_len = secondary_len+1
                if (workstr[current+1] in ['s','z']):
                    current=current+2
                else:
                    current=current+1
            else:
                primary = primary+'s'
                primary_len = primary_len+1
                secondary = secondary+'s'
                secondary_len = secondary_len+1
                if (workstr[current+1] in ['s','z']):
                    current=current+2
                else:
                    current=current+1

        elif (c == 't'):  # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            if (workstr[current:current+4] == 'tion'):
                primary = primary+'x'
                primary_len = primary_len+1
                secondary = secondary+'x'
                secondary_len = secondary_len+1
                current=current+3
            elif (workstr[current:current+3] in ['tia','tch']):
                primary = primary+'x'
                primary_len = primary_len+1
                secondary = secondary+'x'
                secondary_len = secondary_len+1
                current=current+3
            elif (workstr[current:current+2] == 'th') or \
                 (workstr[current:current+3] == 'tth'):
                if (workstr[current+2:current+4] in ['om','am']) or \
                   (workstr[0:4] in ['von ','van ']) or (workstr[0:3] == 'sch'):
                    primary = primary+'t'
                    primary_len = primary_len+1
                    secondary = secondary+'t'
                    secondary_len = secondary_len+1
                    current=current+2
                else:
                    primary = primary+'0'
                    primary_len = primary_len+1
                    secondary = secondary+'t'
                    secondary_len = secondary_len+1
                    current=current+2
            elif (workstr[current+1] in ['t','d']):
                primary = primary+'t'
                primary_len = primary_len+1
                secondary = secondary+'t'
                secondary_len = secondary_len+1
                current=current+2
            else:
                primary = primary+'t'
                primary_len = primary_len+1
                secondary = secondary+'t'
                secondary_len = secondary_len+1
                current=current+1

        elif (c == 'v'):  # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            if (workstr[current+1] == 'v'):
                current=current+2
            else:
                current=current+1
            primary = primary+'f'
            primary_len = primary_len+1
            secondary = secondary+'f'
            secondary_len = secondary_len+1

        elif (c == 'w'):  # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            if (workstr[current:current+2] == 'wr'):
                primary = primary+'r'
                primary_len = primary_len+1
                secondary = secondary+'r'
                secondary_len = secondary_len+1
                current=current+2
            else:
                if (current==0) and (isvowel(workstr[1]) or \
                                     workstr[0:2] == 'wh'):
                    if (isvowel(workstr[current+1])):
                        primary = primary+'a'
                        primary_len = primary_len+1
                        secondary = secondary+'f'
                        secondary_len = secondary_len+1
                        #current=current+1
                    else:
                        primary = primary+'a'
                        primary_len = primary_len+1
                        secondary = secondary+'a'
                        secondary_len = secondary_len+1
                        #current=current+1
                if (current==last and isvowel(workstr[current-1])) or \
                   workstr[current-1:current+4] in \
                   ['ewski','ewsky','owski','owsky'] or \
                   workstr[0:3] == 'sch':
                    # primary = primary+''
                    # primary_len = primary_len+0
                    secondary = secondary+'f'
                    secondary_len = secondary_len+1
                    current=current+1
                elif (workstr[current:current+4] in ['witz','wicz']):
                    primary = primary+'ts'
                    primary_len = primary_len+2
                    secondary = secondary+'fx'
                    secondary_len = secondary_len+2
                    current=current+4
                else:
                    current=current+1

        elif (c == 'x'):  # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            if not (current==last and \
                    (workstr[current-3:current] in ['iau','eau'] or \
                     workstr[current-2:current] in ['au','ou'])):
                primary = primary+'ks'
                primary_len = primary_len+2
                secondary = secondary+'ks'
                secondary_len = secondary_len+2
            if (workstr[current+1] in ['c','x']):
                current=current+2
            else:
                current=current+1

        elif (c == 'z'):  # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            if (workstr[current+1] == 'h'):
                primary = primary+'j'
                primary_len = primary_len+1
                secondary = secondary+'j'
                secondary_len = secondary_len+1
                current=current+2
            else:
                if (workstr[current+1:current+3] in ['zo','zi','za']) or \
                   (slavogermanic(workstr) and \
                    (current > 0 and workstr[current-1] != 't')):
                    primary = primary+'s'
                    primary_len = primary_len+1
                    secondary = secondary+'ts'
                    secondary_len = secondary_len+2
                    if (workstr[current+1] == 'z'):
                        current=current+2
                    else:
                        current=current+1
                else:
                    primary = primary+'s'
                    primary_len = primary_len+1
                    secondary = secondary+'s'
                    secondary_len = secondary_len+1
                    if (workstr[current+1] == 'z'):
                        current=current+2
                    else:
                        current=current+1

        else:   # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            current=current+1

        # End main loop

    if (primary == secondary):
        # If both codes are the same set the second's length to 0 so it's not used
        secondary_len = 0

# else:
#   print 'Two D-metaphone codes for "%s": "%s" / "%s"' % (s,primary,secondary)

    # if (secondary_len > 0):
    #   return [primary[:maxlen], secondary[:maxlen]]
    # else:
    #   return [primary[:maxlen]]

    if (maxlen > 0):
        resstr = primary[:maxlen]  # Only return primary encoding
    else:
        resstr = primary

    return resstr
