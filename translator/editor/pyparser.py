from functools import partial
from pyparsing import OneOrMore, StringEnd, LineEnd, ZeroOrMore, Regex, Group, Literal, Word, alphas, Combine, \
    QuotedString, printables, Optional, Suppress, ParseException, Forward, indentedBlock


def debug(name):

    def inner_debug(text, loc, parsed):
        print name, loc, ":", "".join(parsed)[:50], '...'
    return inner_debug


class Node(object):

    def __init__(self, s, loc, toc):
        self._s = s
        self._loc = loc
        self._toc = list(toc)


class GenericNode(Node):

    def __init__(self, type_, s, loc, toc):
        super(GenericNode, self).__init__(s, loc, toc)
        self._type = type_

    def __str__(self):
        return "%s:\n    %s" % (self._type, "".join([str(x) for x in self._toc]))

    def __repr__(self):
        return "<GenericNode: %s>" % (self._type,)


def generic(name):
    return partial(GenericNode, name)


class _Parts(Node):

    def __str__(self):
        return " | ".join([str(x) for x in self._toc])


def dump(result, indent=0):
    if isinstance(result, basestring):
        print "%s%r" % (" " * indent, result)
        return
    assert not isinstance(result, basestring)
    print "%s%r" % (" " * indent, result)
    try:
        for x in iter(result):
            dump(x, indent+4)
    except TypeError:
        for x in iter(result._toc):
            dump(x, indent+4)


Name = Word(alphas+"-_")
# EndOfLine = Literal("\n\r") | Literal("\r\n") | Literal("\n") | Literal("\r")
Whitespace = Regex(r"[ \t]")
Whitespace.leaveWhitespace()
EmptyLine = ZeroOrMore(Whitespace()) + LineEnd()
EndOfLines = Suppress(ZeroOrMore(Group(EmptyLine())))
EndOfLines.leaveWhitespace()
TextLine = Regex(r"([^\s*]|[ ]+[^ ]).*") + LineEnd()
TextLine.leaveWhitespace()

BlockHeader = Literal(".. ") + Name + Literal("::") + Optional(OneOrMore(Whitespace()) + Name) + LineEnd()
Block = BlockHeader + LineEnd() + OneOrMore(OneOrMore(Whitespace) + Regex(".*\n"))
Block.setParseAction(debug("block"))
Block.setName('block')

MultiLine = Combine(OneOrMore(TextLine))
MultiLine.setParseAction(partial(GenericNode, 'multiline'))
Text = MultiLine + Suppress(LineEnd())
Text.setParseAction(partial(GenericNode, 'text'))
Text.setName('text')

# TextBeforeCode = MultiLine + Literal("::") + Suppress(LineEnd())
# TextBeforeCode.setParseAction(partial(GenericNode, 'textbeforecode'))
#
# TextAndCode = TextBeforeCode

ListItem = Regex(r"\*.*") + LineEnd() + Optional(MultiLine)
ListItem.leaveWhitespace()
ListItem.setParseAction(partial(GenericNode, 'listItem'))
ListItems = OneOrMore(ListItem)
List = ListItems + Suppress(LineEnd())

HeaderMarker = Regex("={3,}|-{3,}|_{3,}|\.{3,}|,{3,}") + LineEnd()
Header = Optional(HeaderMarker()) + TextLine() + HeaderMarker()
Header.setParseAction(partial(GenericNode, 'header'))

# Parts = Forward()
Part = Forward()


def parsed_indent(s, l, toc):
    if len(toc) > 0:
        return _Parts(s, l, [x[0] for x in toc[0]])


Part <<= EndOfLines() + \
         Combine(Block() | Header() | Text() | List()).setParseAction(generic('bhtl')) + \
         Optional(indentedBlock(Part, [1])).setParseAction(parsed_indent)
Part.setParseAction(partial(GenericNode, 'part'))
Parts = OneOrMore(Part)
# Parts <<= Part + Optional(indentedBlock(Parts, [0]))
# Parts = ZeroOrMore(Part)
Parts.setParseAction(_Parts)

DocumentParser = Parts() + EndOfLines + StringEnd()
DocumentParser.leaveWhitespace()
DocumentParser.setParseAction(partial(GenericNode, 'document'))


def parse(string):
    if not string.endswith("\n"):
        string += "\n"
    try:
        return DocumentParser.parseString(string)
    except ParseException as exc:
        print exc.line
        raise
