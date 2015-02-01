from django.shortcuts import render

# Create your views here.
import os
from docutils import core, io
from docutils.nodes import NodeVisitor
from editor.parser import DocumentParser


SOURCE_LANGUAGE = 'en'

class DocumentSource(object):

    def __init__(self, path):
        self._path = path

    def parsed(self):
        with open(self._path, 'r') as source:
            source_text = source.read().decode('utf-8')
        results = DocumentParser.parseString(source_text)
        return results


class Document(object):
    def __init__(self, name, sources):
        self._name = name
        self._sources = sources

    def __str__(self):
        return self._name

    def filter(self, name):
        return name == self._name

    def sources(self):
        sources = []
        for source in self._sources:
            path = os.path.join(source, self._name)
            sources.append(DocumentSource(path))
        return sources


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
        if not item.startswith('source-'):
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
