# coding=utf-8
from StringIO import StringIO
from pprint import pprint
from django.test import TestCase
from editor.parser import Parser, RSTParser
from editor.pyparser import DocumentParser


lists = u"""
paragraph

* list item 1
 * list item 2
* list item 2.1 next line
* list item 2.2
* list item 3

paragraph
"""

code = u"""
paragraph::

    code line 1
    code line 2

    code line 3

another paragraph

last paragraph"""


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


class TestParser(TestCase):

    def test_pyparser(self):
        result = DocumentParser.parseString(lists)
        print result[0]

    def test_parse(self):
        parser = Parser(StringIO(s))
        parts = parser.parse()

        self.assertEqual(parts, [
            u"""=======================
Wprowadzenie do Pythona
=======================

""",
            u"""Zacznijmy od uruchomienia interpretera, który zainstalowaliśmy w poprzednim rozdziale. Uruchom:

""", u""".. code-block:: abc

    (warsztaty) ~$ python
    Python 3.4.0 (...)
    Type "copyright", "credits" or "license" for more information.

    >>>

""", u"""Wcześniej pracowaliśmy w konsoli systemu operacyjnego i mogliśmy wydawać mu polecenia.
Zachętą dla nas był ``~$``. Po uruchomieniu polecenia ``python`` zmienił się znak zachęty na
``>>>``. To jest informacja dla nas, że teraz wydajemy wyłącznie polecenia w języku Python.

""", u"""
Teraz możemy coś policzyć, np. wpisując ``2 + 2``:

""", u"""    >>> 2 + 2
    4

""", u"""Python świetnie sprawdza się jako kalkulator:

""", u"""
Przedstaw się
=============

""", u"""Napisy
------

""", u""".. code-block:: sh

    (warsztaty) ~$ python wizytowka.py
    Cześć, mam na imię Łukasz.
    (warsztaty) ~$

"""])

    def print_results(self, parts):
        for result in parts:
            print repr(result[:50])

    def test_list(self):
        parser = Parser(StringIO(lists))
        parts = parser.parse()
        pprint(parts)
        # self.assertEqual(parts, [
        #     u"\n",
        #     u"paragraph\n\n",
        #     u"* list item 1\n",
        #     u"* list item 2\n",
        #     u"  * list item 2.1\n    next line\n  * list item 2.2\n",
        #     u"* list item 3\n",
        #     u"paragraph\n"
        # ])

    def test_code(self):
        parser = Parser(StringIO(code))
        parts = parser.parse()
        self.print_results(parts)

    def test_parser_big(self):
        with open('../source-en/python_xmas_tree.rst') as plik:
            text = plik.read()
            text = text.decode('utf-8')
            text = StringIO(text)
        parser = Parser(text)
        results = parser.parse()
        #pprint(results)
    #
    # def test_parser_rst(self):
    #     with open('../source-en/python_xmas_tree.rst') as plik:
    #         parser = RSTParser(plik)
    #         result = parser.parse()
    #     # self.simple_walk(result.document, 0)
    #     # self.walk(result.document)

    def test_db(self):
        pass
