from StringIO import StringIO
import hashlib
from pprint import pprint
from django.shortcuts import render

import os
from docutils import core, io
from docutils.nodes import NodeVisitor
from pyparsing import ParseException as PE
from tinydb import where
from editor.ajax import json_view
from editor.parser import Parser
from editor.db import paragraphs


SOURCE_LANGUAGE = 'en'
DIR_NAME_PREFIX = 'source-'
LANGUAGES = {
    'en': 0,
    'pl': 1
}


class ParseException(Exception):
    pass


def hash_paragraph(text):
    m = hashlib.md5()
    m.update(text.encode('utf-8'))
    return m.hexdigest()


class Status(object):
    INVALID = 'invalid'
    VALID = 'valid'


class Text(object):

    def __init__(self, text, status, hashed, language):
        self._text = text
        self._status = status
        self._hashed = hashed
        self._language = language

    def __str__(self):
        return self._text.encode('utf-8')

    def __unicode__(self):
        return u'' if self._text is None else self._text

    def status(self):
        return self._status

    def is_ok(self):
        return self._status == Status.VALID

    def hash(self):
        return self._hashed

    def lang(self):
        return self._language

    def is_source(self):
        return self._language == SOURCE_LANGUAGE


class Paragraph(object):

    def __init__(self):
        self._texts = {}
        self._sources = {}
        self._status = None
        self._hash = None
        self._text_objs = None

    def set_for_source(self, source, text):
        self._texts[source.get_language()] = text
        self._sources[source.get_language()] = source

    def set_empty_source(self, source):
        self._texts[source.get_language()] = None

    def texts(self):
        self.do_status()
        if self._text_objs is None:
            texts = sorted(self._texts.items(), key=lambda item: LANGUAGES[item[0]])
            text_objs = []
            for language, text in texts:
                text_obj = Text(text, self._status[language], self._hash[language], language)
                text_objs.append(text_obj)
            self._text_objs = text_objs
        return self._text_objs

    def do_hash(self):
        if self._hash is None:
            current = {}
            for key, value in self._texts.items():
                if value is None:
                    current[key] = None
                else:
                    current[key] = hash_paragraph(value)
            self._hash = current

    def do_status(self):
        self.do_hash()
        invalid_status = {key: Status.INVALID for key, value in self._texts.items()}
        invalid_status[SOURCE_LANGUAGE] = Status.VALID
        if self._status is None:
            hashes = paragraphs.search(where(SOURCE_LANGUAGE) == self._hash[SOURCE_LANGUAGE])
            source_text = self._texts.get(SOURCE_LANGUAGE)
            if source_text is None:
                self._status = invalid_status
            elif len(hashes) > 1:
                raise Exception("There are to many results for text %s: %r" % (source_text[:20], hashes))
            elif not hashes:
                self._status = invalid_status
            else:
                hashes = hashes[0]
                status = {}
                for key, value in self._hash.items():
                    status[key] = Status.VALID if value == hashes[key] else Status.INVALID
                status[SOURCE_LANGUAGE] = Status.VALID
                self._status = status


class DocumentSource(object):

    def __init__(self, path, language):
        self._path = path
        self._lang = language

    def parsed(self):
        with open(self._path, 'r') as source:
            source_text = source.read().decode('utf-8')
        try:
            parser = Parser(StringIO(source_text))
            results = parser.parse()

        except PE as exc:
            raise ParseException("%s in %s" % (exc, self._path))
        return results

    def get_language(self):
        return self._lang


class Document(object):
    def __init__(self, name, sources):
        """
        name - document name
        sources - list of directories, one for each language
        """
        self._name = name
        self._sources = sources
        self._paragraphs = None

    def __str__(self):
        return self._name

    def filter(self, name):
        return name == self._name

    def sources(self):
        sources = []
        for source in self._sources:
            file_name = os.path.basename(source)
            language = file_name[len(DIR_NAME_PREFIX):]
            path = os.path.join(source, self._name)
            sources.append(DocumentSource(path, language))
        return sources

    def paragraphs(self):
        sources = self.sources()
        parse_results = [(source, source.parsed()) for source in sources]
        paragraphs = []
        empty = False
        while not empty:
            empty = True
            paragraph = Paragraph()
            for item in parse_results:
                source, parse_result = item
                if parse_result:
                    source_paragraph = parse_result.pop(0)
                    paragraph.set_for_source(source, source_paragraph)
                    empty = False
                else:
                    paragraph.set_empty_source(source)
            if not empty:
                paragraphs.append(paragraph)
        return paragraphs


def get_sources():
    path = os.path.realpath(__file__)
    proj_path = os.path.dirname(os.path.dirname(os.path.dirname(path)))
    dir_items = os.listdir(proj_path)
    sources = []
    for item in dir_items:
        item_path = os.path.join(proj_path, item)
        if not os.path.isdir(item_path):
            continue
        if not item.startswith(DIR_NAME_PREFIX):
            continue
        sources.append(item_path)
    return sources


_documents_cache = None


def get_documents():
    global _documents_cache
    if _documents_cache is None:
        sources = get_sources()
        documents = set([x for x in os.listdir(sources[0]) if x.endswith('.rst')])

        for item in sources[1:]:
            next_documents = set([x for x in os.listdir(item) if x.endswith('.rst')])
            documents = documents | next_documents

        _documents_cache = [Document(x, sources) for x in documents]
    return _documents_cache


def internals(input_string, source_path=None, destination_path=None,
              input_encoding='unicode', settings_overrides=None):
    """
    Return the document tree and publisher, for exploring Docutils internals.

    Parameters: see `html_parts()`.
    """
    if settings_overrides:
        overrides = settings_overrides.copy()
    else:
        overrides = {}
    overrides['input_encoding'] = input_encoding
    output, pub = core.publish_programmatically(
        source_class=io.StringInput, source=input_string,
        source_path=source_path,
        destination_class=io.NullOutput, destination=None,
        destination_path=destination_path,
        reader=None, reader_name='standalone',
        parser=None, parser_name='restructuredtext',
        writer=None, writer_name='null',
        settings=None, settings_spec=None, settings_overrides=overrides,
        config_section=None, enable_exit_status=None)
    return pub.writer.document, pub


class MyVisitor(NodeVisitor):
    def unknown_visit(self, node):
        print "Visiting", node


def document_list_view(request):
    documents = get_documents()
    return render(
        request,
        'editor/document_list.html',
        {'documents': documents})


def document_view(request, name):
    documents = get_documents()
    document = filter(lambda x: x.filter(name), documents)[0]
    return render(
        request,
        'editor/document_item.html',
        {'document': document})


@json_view
def set_valid(data, request):
    pprint(data)
    hashes = paragraphs.search(where(SOURCE_LANGUAGE) == data['source_hash'])
    return {}
    if len(hashes):
        paragraphs.update(
            {data['target_language']: data['target_hash']},
            where(SOURCE_LANGUAGE) == data['source_hash'])
    else:
        paragraphs.insert(
            {
                data['source_language']: data['source_hash'],
                data['target_language']: data['target_hash']
            })
    return {}
