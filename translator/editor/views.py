from django.shortcuts import render

# Create your views here.
import os
from docutils import core, io
from docutils.nodes import NodeVisitor
from pyparsing import ParseException as PE
from editor.parser import DocumentParser


SOURCE_LANGUAGE = 'en'
DIR_NAME_PREFIX = 'source-'
LANGUAGES = {
    'en': 0,
    'pl': 1
}

class ParseException(Exception):
    pass


class DocumentSource(object):

    def __init__(self, path, language):
        self._path = path
        self._lang = language

    def parsed(self):
        with open(self._path, 'r') as source:
            source_text = source.read().decode('utf-8')
        try:
            results = DocumentParser.parseString(source_text)
        except PE as exc:
            raise ParseException("%s in %s" % (exc, self._path))
        return results

    def get_language(self):
        return self._lang


class Paragraph(object):

    def __init__(self):
        self._texts = {}

    def set_for_source(self, source, text):
        self._texts[source] = text

    def set_empty_source(self, source):
        self._texts[source] = None

    def texts(self):
        texts = sorted(self._texts.items(), key=lambda item: LANGUAGES[item[0].get_language()])
        return [x[1] for x in texts]


class Document(object):
    def __init__(self, name, sources):
        """
        name - document name
        sources - list of directories, one for each language
        """
        self._name = name
        self._sources = sources

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
    print dir_items
    print proj_path
    sources = []
    for item in dir_items:
        item_path = os.path.join(proj_path, item)
        if not os.path.isdir(item_path):
            continue
        if not item.startswith(DIR_NAME_PREFIX):
            continue
        sources.append(item_path)
    return sources


def get_documents():
    sources = get_sources()
    documents = set([x for x in os.listdir(sources[0]) if x.endswith('.rst')])

    for item in sources[1:]:
        next_documents = set([x for x in os.listdir(item) if x.endswith('.rst')])
        documents = documents & next_documents

    return [Document(x, sources) for x in documents]


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


def match(first, second):
    with open(first, 'r') as source:
        source_text = source.read().decode('utf-8')


    #
    # parts = []
    # current = StringIO()
    #
    # for line in source_text.split("\n"):
    #     if line == '':
    #         parts.append(current.getvalue())
    #         current = StringIO()
    #         continue
    #     line = line + "\n"
    #     current.write(line)

    print parts
#
# document = list(documents)[0]
# match(os.path.join(sources[0], document), os.path.join(sources[1], document))


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
