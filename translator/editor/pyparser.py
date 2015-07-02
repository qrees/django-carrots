from functools import partial
from pyparsing import OneOrMore, StringEnd, LineEnd, ZeroOrMore, Regex, Group, Literal, Word, alphas, Combine, \
    QuotedString, printables, Optional, Suppress


def debug(name):

    def inner_debug(text, loc, parsed):
        print name, loc, ":", "".join(parsed)[:50], '...'
    return inner_debug


class Node(object):

    def __init__(self, s, loc, toc):
        self._s = s
        self._loc = loc
        self._toc = toc


class GenericNode(Node):

    def __init__(self, type_, s, loc, toc):
        super(GenericNode, self).__init__(s, loc, toc)
        self._type = type_

    def __str__(self):
        return "%s:\n%s" % (self._type, "".join(self._toc,))


class _Parts(Node):

    def __str__(self):
        return "".join(self._toc,)


Name = Word(alphas+"-_")
# EndOfLine = Literal("\n\r") | Literal("\r\n") | Literal("\n") | Literal("\r")
Whitespace = Regex(r"[ \t]")
Whitespace.leaveWhitespace()
EmptyLine = ZeroOrMore(Whitespace()) + LineEnd()
EndOfLines = Suppress(ZeroOrMore(Group(EmptyLine())))
EndOfLines.leaveWhitespace()
# TextLine = Regex("[ ]*[-a-zA-Z0-9().`>\"'$].*") + LineEnd()
TextLine = Regex(r"([^\s*]|[ ]+[^ ]).*") + LineEnd()
TextLine.leaveWhitespace()

BlockHeader = Literal(".. ") + Name + Literal("::") + Optional(OneOrMore(Whitespace()) + Name) + LineEnd()
Block = BlockHeader + LineEnd() + OneOrMore(OneOrMore(Whitespace) + Regex(".*\n"))
Block.setParseAction(debug("block"))

MultiLine = OneOrMore(TextLine)
Text = MultiLine + Suppress(LineEnd())
Text.setParseAction(partial(GenericNode, 'text'))

ListItem = Regex(r"\*.*") + LineEnd() + Optional(MultiLine)
ListItem.leaveWhitespace()
ListItem.setParseAction(partial(GenericNode, 'listItem'))
ListItems = OneOrMore(ListItem)
List = ListItems + Suppress(LineEnd())

HeaderMarker = Regex("={3,}|-{3,}|_{3,}|\.{3,}|,{3,}") + LineEnd()
Header = Optional(HeaderMarker()) + TextLine() + HeaderMarker()
Header.setParseAction(partial(GenericNode, 'header'))

Part = EndOfLines() + Combine(Group(Block() | Header() | Text() | List()))
Part("Part")
Parts = ZeroOrMore(Part)
Parts.setParseAction(_Parts)

DocumentParser = Parts() + EndOfLines + StringEnd()
DocumentParser.leaveWhitespace()
DocumentParser.setParseAction(lambda s, loc, toc: str(toc[0]))