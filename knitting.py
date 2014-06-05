import re
import parsley

# Example from http://alliejon.es/blog/2014/03/24/adding-syntax-highlighting-to-knitting-patterns/
test = """
Rnd 1: K1, *k4, sl1, k1, sl1, k5; rep from * to last st, k1.
Rnd 2: K1, *k3, k2tog, yo, k1, yo, ssk, k4; rep from * to last st, k1.
Rnd 3: K1, *(k3, sl1) twice, k4; rep from * to last st, k1.
Rnd 4: K1, *k2, k2tog, yo, k3, yo, ssk, k3; rep from * to last st, k1.
Rnd 5: K1, *k2, sl1, k5, sl1, k3; rep from * to last st, k1.
Rnd 6: K1, *k1, k2tog, yo, k5, yo, ssk, k2; rep from * to last st, k1.
Rnd 7: K1, *(k1, sl1, k2, sl1) twice, k2; rep from * to last st, k1.
Rnd 8: K1, *k2tog, yo, k1, yo, ssk, k1; rep from * to last st, k1.
Rnd 9: K1, *sl1, k3, k1tbl, sl1, k4, sl1, k1; rep from * to last st, k1.
Rnd 10: K2tog, *yo, k3, yo, sl1, k2tog, psso; rep from * to last 6 sts, yo, k3, yo, ssk, k1.
Rnds 11-12: Knit.
""".strip()

grammar = """
digit = anything:x ?(x in '0123456789') -> x
number = <digit+>:ds -> int(ds)

knit = ('knit' | 'k') digit?:x -> 'knit', x
slip = ('slip' | 'sl') digit?:x -> 'slip', x
yarn_over = 'yo' -> 'yarn_over'
purl = ('purl' | 'p') -> 'purl'
ssk = 'ssk' -> 'ssk'
pass_over = 'psso' -> 'pass_over'
simple_command = pass_over | knit | slip | yarn_over | purl | ssk

not_new_command_or_eol = anything:x ?(x not in ',.') -> x

times = <'twice' | ('four' | 'five' | 'six' | 'seven') 'times'>:x -> x

simple_loop = '(' command_list:seq ')' ws times:rep -> 'simple_loop', seq, rep
big_loop = '*' command_list:seq '; rep from * to ' <not_new_command_or_eol*>:end -> 'big_loop', seq, end

together = simple_command:x ws 'tog' -> x, 'together'
tbl = simple_command:x ws 'tbl' -> x, 'tbl'
command = big_loop | simple_loop | together | tbl | simple_command

command_list = command:first (ws ',' ws command)*:rest -> [first] + rest
row = 'rnd' 's'? ws <number ('-' number)?>:x ':' ws command_list:y '.' ws -> 'row', x, y
rows = row*
"""

g = parsley.makeGrammar(grammar, {})
print 0, g('k2tog').command()
print 1, g('123').number()
print 2, g('Rnd 1: k1, yo, sl1.'.lower()).row()
print 3, g('Rnd 1: (k1, yo) twice, sl1.'.lower()).row()
print 4, g('*k3, sl1, k4; rep from * to last st'.lower()).big_loop()
print 5, g('*(k3, sl1) twice, k4; rep from * to last st'.lower()).big_loop()
print 6, g('Rnd 3: K1, *(k3, sl1) twice, k4; rep from * to last st, k1.'.lower()).row()
print 7, g('Rnd 1: K1, *k4, sl1, k1, sl1, k5; rep from * to last st, k1.'.lower()).row()
print 8, g('Rnd 2: K1, *k3, k2tog, yo, k1, yo, ssk, k4; rep from * to last st, k1.'.lower()).row()
print 0, g('knit').command()

for x in test.lower().split('\n'):
    print repr(x)
    print g(x).row()


# Knitting diagrams follow MATH conventions: y is UP!
# Knitting text commands follow PROGRAMMER conventions: y is DOWN! (of course since it follows normal reading conventions)

# 'rnd x:', 'round x:', '1st round', '1st row', 'row x'
# ',' -> separator
#
# # writes one, moves current position x+1
# 'k(?P<number>\d*)' -> knit
# 'sl' -> slip
# 'p' -> purl
#
# # Increases number of columns/stitches.
# 'yo' -> yarn over
# 'kfb' -> knit in the front and back of stitch
#
# # loops
# '\(x\) twice' -> perform entire sequence x twice
# '\*(?P<sequence>[^;]); rep from * to (?P<position>.+)' -> loop construct
# 'x to m' -> do x until marker
#
#
# # decreases counter 1
# 'psso' -> pass over (decrements pc 1!)
#
#
# # doesn't change counter
# 'xn ?tog' -> x together (eg "k2 tog" -> knit two together)
# 'pm' -> place marker
# 'rm' -> remove marker
# 'xtbl' -> through back loop
# 'slm' -> slip marker (marker position is unchanged, but moved to the other needle)
# 'wyif' -> with yarn in front
#
# Rnd 7:
#     K1,
#     *
#         (
#             k1,
#             sl1,
#             k2,
#             sl1
#         ) twice, \
#         k2;
#         rep from * to last st,
#     k1.