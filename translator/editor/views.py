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

    def __init__(self, text=None, source=None, status=None):
        self._source = source
        self._text = text
        self._status = status

    def set_text(self, text):
        self._text = text

    def get_text(self):
        return self._text

    def set_source(self, source):
        self._source = source

    def __hash__(self):
        return hash(self._text)

    def __str__(self):
        return self._text.encode('utf-8')

    def __unicode__(self):
        return u'' if self._text is None else self._text

    def set_status(self, status):
        self._status = status

    def status(self):
        return self._status

    def is_ok(self):
        return self._status == Status.VALID

    def lang(self):
        return self._source.get_language()

    def is_source(self):
        return self.lang() == SOURCE_LANGUAGE


db = {}


class Paragraph(object):

    def __init__(self):
        # self._texts = {}
        # self._sources = {}
        # self._status = None
        self._text_objs = {}

    def set_for_source(self, source, text_obj):
        assert isinstance(text_obj, Text)
        language = source.get_language()
        self._text_objs[language] = text_obj
        # if language not in self._text_objs:
        #     self._text_objs[language] = Text(self)
        # self._text_objs[language].set_text(text)
        # self._text_objs[language].set_source(source)

    def set_empty_source(self, source):
        language = source.get_language()
        if language not in self._text_objs:
            self._text_objs[language] = Text()
        self._text_objs[language].set_text("")
        self._text_objs[language].set_source(source)

    def texts(self):
        self.do_status()
        # if self._text_objs is None:
        #     texts = sorted(self._texts.items(), key=lambda item: LANGUAGES[item[0]])
        #     text_objs = []
        #     for language, text in texts:
        #         text_obj = Text(self, language)
        #         text_objs.append(text_obj)
        #     self._text_objs = text_objs
        return self._text_objs.items()
    #
    # def do_hash(self):
    #     if self._hash is None:
    #         current = {}
    #         for key, value in self._texts.items():
    #             if value is None:
    #                 current[key] = None
    #             else:
    #                 current[key] = hash_paragraph(value)
    #         self._hash = current

    def do_status(self):
        source_obj = self._text_objs[SOURCE_LANGUAGE]
        # if self._status is None:

        # source_text = self._texts.get(SOURCE_LANGUAGE)
        if source_obj is None:
            for obj in self._text_objs.values():
                obj.set_status(Status.INVALID)
            return

        translations = paragraphs.search(where(SOURCE_LANGUAGE) == source_obj.get_text())

        if len(translations) > 1:
            raise Exception("There are to many results for text %s: %r" % (source_obj.get_text()[:20], translations))
        elif not translations:
            for obj in self._text_objs.values():
                obj.set_status(Status.INVALID)
        else:
            translation = translations[0]
            for lang, value in self._text_objs.items():
                if translation[lang] == value.get_text():
                    value.set_status(Status.VALID)
                else:
                    value.set_status(Status.INVALID)
        source_obj.set_status(Status.VALID)


class DocumentSource(object):

    def __init__(self, path, language):
        self._path = path
        self._lang = language
        self._texts = None

    def parsed(self):
        with open(self._path, 'r') as source:
            source_text = source.read().decode('utf-8')
        try:
            texts = []
            parser = Parser(StringIO(source_text))
            results = parser.parse()
            for result in results:
                text = Text(result)
                text.set_source(self)
                texts.append(text)
            self._texts = texts
        except PE as exc:
            raise ParseException("%s in %s" % (exc, self._path))
        return self._texts

    def get_language(self):
        return self._lang


class Document(object):
    def __init__(self, name, sources_paths):
        """
        name - document name
        sources - list of directories, one for each language
        """
        self._name = name
        sources = {}
        for source in sources_paths:
            file_name = os.path.basename(source)
            language = file_name[len(DIR_NAME_PREFIX):]
            path = os.path.join(source, self._name)
            sources[language] = DocumentSource(path, language)
        self._sources = sources
        self._paragraphs = None

    def __str__(self):
        return self._name

    def filter(self, name):
        return name == self._name

    def paragraphs(self):
        sources = self._sources
        parse_results = [(source, source.parsed()) for source in sources.values()]
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

    # def set_text(self, language, source_hash, text):
    #     self._sources[language].save(source_hash, text)


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
    translations = paragraphs.search(where(SOURCE_LANGUAGE) == data['source_text'])
    if len(translations):
        paragraphs.update(
            {data['target_language']: data['target_text']},
            where(SOURCE_LANGUAGE) == data['source_text'])
    else:
        paragraphs.insert(
            {
                data['source_language']: data['source_text'],
                data['target_language']: data['target_text']
            })
    return {}
