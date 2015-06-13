#-*- coding: utf-8 -*-
from StringIO import StringIO
from pprint import pprint
from pyparsing import OneOrMore, StringEnd, LineEnd, ZeroOrMore, Regex, Group, Literal, Word, alphas, Combine, \
    QuotedString, printables, Optional, Suppress
import re

from docutils.utils import new_document
from docutils.parsers.rst import Parser as DocutilsRSTParser
from docutils.frontend import OptionParser
from docutils.nodes import section, paragraph, Text, title, system_message, literal, footnote_reference, literal_block, problematic, title_reference, bullet_list, list_item, block_quote, doctest_block, definition_list, definition_list_item, comment, term, definition, rubric, footnote
from sphinx.directives import code, other
from sphinx.ext.doctest import TestsetupDirective, TestcleanupDirective, DoctestDirective, TestcodeDirective, TestoutputDirective
from docutils.parsers.rst import directives


def debug(name):

    def inner_debug(text, loc, parsed):
        print name, loc, ":", "".join(parsed)[:50], '...'
    return inner_debug

#
# Name = Word(alphas+"-_")
# # EndOfLine = Literal("\n\r") | Literal("\r\n") | Literal("\n") | Literal("\r")
# Whitespace = Regex(r"[ \t]")
# Whitespace.leaveWhitespace()
# EmptyLine = ZeroOrMore(Whitespace()) + LineEnd()
# EndOfLines = Suppress(ZeroOrMore(Group(EmptyLine())))
# EndOfLines.leaveWhitespace()
# # TextLine = Regex("[ ]*[-a-zA-Z0-9().`>\"'$].*") + LineEnd()
# TextLine = Regex("[ ]*[^\s].*") + LineEnd()
# TextLine.leaveWhitespace()
#
# BlockHeader = Literal(".. ") + Name + Literal("::") + Optional(OneOrMore(Whitespace()) + Name) + LineEnd()
# Block = BlockHeader + LineEnd() + OneOrMore(OneOrMore(Whitespace) + Regex(".*\n"))
# Block.setParseAction(debug("block"))
#
# MultiLine = OneOrMore(TextLine)
# Text = MultiLine + Suppress(LineEnd())
# Text.setParseAction(debug("text"))
#
# HeaderMarker = Regex("={3,}|-{3,}|_{3,}|\.{3,}|,{3,}") + LineEnd()
# Header = Optional(HeaderMarker()) + TextLine() + HeaderMarker()
# Header.setParseAction(debug("header"))
#
# Part = EndOfLines() + Combine(Group(Block() | Header() | Text()))
# Part("Part")
# Parts = ZeroOrMore(Part)
# DocumentParser = Parts() + EndOfLines + StringEnd()
#
# DocumentParser.leaveWhitespace()


class State(object):
    PARAGRAPH_START = 'PARAGRAPH_START'
    PARAGRAPH = 'PARAGRAPH'
    CODE = 'CODE'
    PARAGRAPH_END = 'PARAGRAPH_END'
    LIST = 'LIST'

SECTION_CHARS = '! " # $ % & \' ( ) * + , - . / : ; < = > ? @ [ \\ ] ^ _ ` { | } ~'.split()
CODE_RE = re.compile(r"^\.\.\s+code-block::\s+\w+$")


class Parser(object):

    def __init__(self, stream):
        self.stream = stream
        self.state = State.PARAGRAPH
        self.parts = []
        self.cur_line = stream.readline()
        self.cur_part = StringIO()
        self.indent = 0
        self.list_indent = 0
        self.previous_list_indent = self.list_indent
        self.previous_indent = self.indent
        self.eof = False

    def parse(self):
        while not self.eof:
            # print self.state
            # print repr(self.get_cur_line())
            # print
            if self.state == State.PARAGRAPH_START:
                self.parse_paragraph_start()
                continue
            if self.state == State.PARAGRAPH:
                self.parse_paragraph()
                continue
            if self.state == State.CODE:
                self.parse_code()
                continue
            if self.state == State.PARAGRAPH_END:
                self.parse_paragraph_end()
                continue
            if self.state == State.LIST:
                self.parse_list()
                continue
        self.parts.append(self.cur_part.getvalue())
        return self.parts

    def get_next_line(self):
        cur_line = self.stream.readline()
        if cur_line == '':
            self.eof = True
        self.cur_line = cur_line
        self.previous_list_indent = self.list_indent
        self.previous_indent = self.indent
        self.list_indent = self.get_list_indent(cur_line)
        self.indent = self.get_line_indent(cur_line)
        return self.cur_line

    def get_cur_line(self):
        return self.cur_line

    def get_line_indent(self, line):
        indent = 0
        for c in line:
            if c in (' ', '*'):
                indent += 1
            else:
                break
        return indent

    def get_list_indent(self, line):
        indent = 0
        for c in line:
            if c in (' ',):
                indent += 1
            else:
                break
        return indent

    def parse_paragraph_end(self):
        line = self.get_cur_line()
        if len(line.strip()) == 0:
            self.get_next_line()
            return
        self.indent = self.get_line_indent(line)
        matched = CODE_RE.match(line)
        if matched:
            self.state = State.CODE
            return
        if line.startswith("* "):
            self.state = State.LIST
            return
        self.state = State.PARAGRAPH
        return

    def parse_list(self):
        line = self.get_cur_line()
        if line.startswith("* "):
            self.next_part()
            self.cur_part.write(line)
            self.get_next_line()
            return
        if self.indent < self.previous_indent:
            self.state = State.PARAGRAPH_END
            return
        self.cur_part.write(line)
        self.get_next_line()
        return

    def next_part(self):
        self.parts.append(self.cur_part.getvalue())
        self.cur_part = StringIO()

    def parse_paragraph_start(self):
        """
         -> ???
        """
        line = self.get_cur_line()
        assert len(line.strip()) > 0
        self.parse_paragraph()
        line = self.get_cur_line()
        if len(set(line)) == 1 and line[0] in SECTION_CHARS and len(line) > 2:
            self.next_part()
            self.state = State.PARAGRAPH_END
            self.get_next_line()
            return

    def parse_code(self):
        line = self.get_cur_line()
        matched = CODE_RE.match(line)
        indent = self.get_line_indent(line)
        if indent == 0 and len(line.strip()) > 0 and not matched:
            # print "Line is %r, switching to PARAGRAPH" % (line,)
            self.state = State.PARAGRAPH_START
            self.next_part()
            return
        self.cur_part.write(line)
        self.get_next_line()

    def parse_paragraph(self):
        line = self.get_cur_line()
        if line.strip().endswith("::"):
            self.state = State.PARAGRAPH
            self.cur_part.write(line)
            next_line = self.get_next_line()
            if next_line.strip() == '':
                self.state = State.CODE
                self.next_part()
            return
        if len(line.strip()):
            self.state = State.PARAGRAPH
            self.cur_part.write(line)
            self.get_next_line()
            return
        self.state = State.PARAGRAPH_END
        self.next_part()
        self.get_next_line()


class RSTParser(object):

    def __init__(self, inputFile):
        self.stream = inputFile
        self.check_points = []

    def walk_paragraph(self, document):
        self.check_points.append(document.line)
        if document.line is None:
            print document.tagname
            raise Exception()
        print document.line
        for x in document:
            if isinstance(x, (Text, literal, problematic, title_reference)):
                print " ", x.tagname, x.astext()
            elif isinstance(x, (literal_block, problematic)):
                self.walk_paragraph(x)
            elif isinstance(x, (footnote_reference,)):
                pass
            else:
                raise Exception("Unknown node %r" % (x,))

    def walk(self, document):
        for x in document:
            if isinstance(x, (section, bullet_list, list_item, block_quote, definition_list, definition_list_item, definition, footnote)):
                self.walk(x)
            elif isinstance(x, (paragraph, title, literal, literal_block, term, rubric)):
                self.walk_paragraph(x)
            elif isinstance(x, (doctest_block, )):
                self.walk_paragraph(x)
            elif isinstance(x, (comment, )):
                self.walk_paragraph(x)
            elif isinstance(x, system_message):
                pass
                print " ERR: ", x.astext()
            else:
                raise Exception("Unknown node %r" % (x,))

    def simple_walk(self, document, indent=0):
        for x in document:
            # if isinstance(x, system_message):
            #     continue
            print " " * indent, x.tagname, x.line, repr(x.astext()[:30])
            self.simple_walk(x.children, indent+2)

    def parse(self):
        directives.register_directive('testsetup', TestsetupDirective)
        directives.register_directive('testcleanup', TestcleanupDirective)
        directives.register_directive('doctest', DoctestDirective)
        directives.register_directive('testcode', TestcodeDirective)
        directives.register_directive('testoutput', TestoutputDirective)

        parser = DocutilsRSTParser()
        self.parser = parser
        input = self.stream.read().decode('utf-8')
        settings = OptionParser(components=(DocutilsRSTParser,)).get_default_values()
        document = new_document(self.stream.name, settings)
        parser.parse(input, document)
        self.simple_walk(parser.document)
        lines = input.split("\n")
        return parser