#-*- coding: utf-8 -*-
from pprint import pprint
from pyparsing import OneOrMore, StringEnd, LineEnd, ZeroOrMore, Regex, Group, Literal, Word, alphas, Combine, \
    QuotedString, printables, Optional, Suppress


def debug(name):

    def inner_debug(text, loc, parsed):
        print name, loc, ":", "".join(parsed)[:50], '...'
    return inner_debug


Name = Word(alphas+"-_")
# EndOfLine = Literal("\n\r") | Literal("\r\n") | Literal("\n") | Literal("\r")
Whitespace = Regex(r"[ \t]")
Whitespace.leaveWhitespace()
EmptyLine = ZeroOrMore(Whitespace()) + LineEnd()
EndOfLines = Suppress(ZeroOrMore(Group(EmptyLine())))
EndOfLines.leaveWhitespace()
# TextLine = Regex("[ ]*[-a-zA-Z0-9().`>\"'$].*") + LineEnd()
TextLine = Regex("[ ]*[^\s].*") + LineEnd()
TextLine.leaveWhitespace()

BlockHeader = Literal(".. ") + Name + Literal("::") + Optional(OneOrMore(Whitespace()) + Name) + LineEnd()
Block = BlockHeader + LineEnd() + OneOrMore(OneOrMore(Whitespace) + Regex(".*\n"))
Block.setParseAction(debug("block"))

MultiLine = OneOrMore(TextLine)
Text = MultiLine + Suppress(LineEnd())
Text.setParseAction(debug("text"))

HeaderMarker = Regex("={3,}|-{3,}|_{3,}|\.{3,}|,{3,}") + LineEnd()
Header = Optional(HeaderMarker()) + TextLine() + HeaderMarker()
Header.setParseAction(debug("header"))

Part = EndOfLines() + Combine(Group(Block() | Header() | Text()))
Part("Part")
Parts = ZeroOrMore(Part)
DocumentParser = Parts() + EndOfLines + StringEnd()

DocumentParser.leaveWhitespace()

if __name__ == '__main__':
    s = u"""=======================
Wprowadzenie do Pythona
=======================

Zacznijmy od uruchomienia interpretera, który zainstalowaliśmy w poprzednim rozdziale. Uruchom:

.. code-block:: abc

    (warsztaty) ~$ python
    Python 3.4.0 (...)
    Type "copyright", "credits" or "license" for more information.

    >>>

Wcześniej pracowaliśmy w konsoli systemu operacyjnego i mogliśmy wydawać mu polecenia.
Zachętą dla nas był ``~$``. Po uruchomieniu polecenia ``python`` zmienił się znak zachęty na
``>>>``. To jest informacja dla nas, że teraz wydajemy wyłącznie polecenia w języku Python.


Teraz możemy coś policzyć, np. wpisując ``2 + 2``:

    >>> 2 + 2
    4

Python świetnie sprawdza się jako kalkulator:


Przedstaw się
=============

Napisy
------

.. code-block:: sh

    (warsztaty) ~$ python wizytowka.py
    Cześć, mam na imię Łukasz.
    (warsztaty) ~$

"""
    try:
        pprint(DocumentParser.parseString(s).asList())
    except Exception as exc:
        print exc
        print exc.markInputline()
        lines = s.splitlines()
        print lines[exc.lineno-1]
