# -*- coding: utf-8 -*-

import ast
import inspect

from py3status.docstrings import core_module_docstrings
from py3status.py3 import Py3


# some Py3 methods have constants as defaults we need to identify them here
CONSTANT_PARAMS = [
    ('log', 'level'),
    ('notify_user', 'level'),
]


def markdown_2_rst(lines):
    """
    Convert markdown to restructured text
    """
    out = []
    code = False
    for line in lines:
        # code blocks
        if line.strip() == '```':
            code = not code
            space = ' ' * (len(line.rstrip()) - 3)
            if code:
                out.append('\n\n%s.. code-block:: none\n\n' % space)
            else:
                out.append('\n')
        else:
            if code and line.strip():
                line = '    ' + line
            out.append(line)
    return out


def create_module_docs():
    """
    Create documentation for modules.
    """
    data = core_module_docstrings(format='rst')

    out = []
    # details
    for module in sorted(data.keys()):
        out.append(
            '\n{name}\n{underline}\n\n{details}\n'.format(
                name=module,
                underline='-' * len(module),
                details=''.join(markdown_2_rst(data[module])).strip()
            )
        )
    # write include file
    with open('../doc/modules-info.inc', 'w') as f:
        f.write(''.join(out))


def get_variable_docstrings(filename):
    """
    Go through the file and find all documented variables.
    That is ones that have a literal expression following them.

    Also get a dict of assigned values so that we can substitute constants.
    """

    def walk_node(parent, values=None, prefix=''):
        """
        walk the ast searching for docstrings/values
        """
        docstrings = {}
        if values is None:
            values = {}
        key = None
        for node in ast.iter_child_nodes(parent):
            if isinstance(node, ast.ClassDef):
                # We are in a class so walk the class
                docs = walk_node(node, values, prefix + node.name + '.')[0]
                docstrings[node.name] = docs
            elif isinstance(node, ast.Assign):
                key = node.targets[0].id
                if isinstance(node.value, ast.Num):
                    values[key] = node.value.n
                if isinstance(node.value, ast.Str):
                    values[key] = node.value.s
                if isinstance(node.value, ast.Name):
                    if node.value.id in values:
                        values[prefix + key] = values[node.value.id]
            elif isinstance(node, ast.Expr) and key:
                docstrings[key] = node.value.s
            else:
                key = None
        return docstrings, values

    with open(filename, 'r') as f:
        source = f.read()
    return walk_node(ast.parse(source))


def get_py3_info():
    """
    Inspect Py3 class and get constants, exceptions, methods
    along with their docstrings.
    """
    # get all documented constants and their values
    constants, values = get_variable_docstrings('../py3status/py3.py')
    # we only care about ones defined in Py3
    constants = constants['Py3']
    # sort them alphabetically
    constants = [(k, v) for k, v in sorted(constants.items())]

    # filter values as we only care about values defined in Py3
    values = dict([(v, k[4:]) for k, v in values.items() if k.startswith('Py3.')])

    def make_value(attr, arg, default):
        """
        If the methods parameter is defined as a constant then do a
        replacement.  Otherwise return the values representation.
        """
        if (attr, arg) in CONSTANT_PARAMS and default in values:
            return values[default]
        return repr(default)

    # inspect Py3 to find it's methods etc
    py3 = Py3()
    # no private ones
    attrs = [x for x in dir(py3) if not x.startswith('_')]
    exceptions = []
    methods = []
    for attr in attrs:
        item = getattr(py3, attr)
        if 'method' in str(item):
            # a method so we need to get the call parameters
            args, vargs, kw, defaults = inspect.getargspec(item)
            args = args[1:]
            len_defaults = len(defaults) if defaults else 0
            len_args = len(args)

            sig = []
            for index, arg in enumerate(args):
                # default values set?
                if len_args - index <= len_defaults:
                    default = defaults[len_defaults - len_args + index]
                    sig.append('%s=%s' % (arg, make_value(attr, arg, default)))
                else:
                    sig.append(arg)

            definition = '%s(%s)' % (attr, ', '.join(sig))
            methods.append((definition, item.__doc__))
            continue
        try:
            # find any exceptions
            if isinstance(item(), Exception):
                exceptions.append((attr, item.__doc__))
                continue
        except:
            pass
    return {
        'methods': methods,
        'exceptions': exceptions,
        'constants': constants,
    }


def auto_undent(string):
    """
    Unindent a docstring.
    """
    lines = string.splitlines()
    while lines[0].strip() == '':
        lines = lines[1:]
        if not lines:
            return []
    spaces = len(lines[0]) - len(lines[0].lstrip(' '))
    out = []
    for line in lines:
        num_spaces = len(line) - len(line.lstrip(' '))
        out.append(line[min(spaces, num_spaces):])
    return out


def create_py3_docs():
    """
    Create the include files for py3 documentation.
    """
    # we want the correct .rst 'type' for our data
    trans = {
        'methods': 'function',
        'exceptions': 'exception',
        'constants': 'attribute',
    }
    data = get_py3_info()
    for k, v in data.items():
        output = []
        for name, desc in v:
            output.append('')
            output.append('.. _%s:' % name)  # reference for linking
            output.append('')
            output.append('.. py:%s:: %s' % (trans[k], name))
            output.append('')
            output.extend(auto_undent(desc))
        with open('../doc/py3-%s-info.inc' % k, 'w') as f:
            f.write('\n'.join(output))


def create_auto_documentation():
    """
    Create any include files needed for sphinx documentation
    """
    create_module_docs()
    create_py3_docs()


if __name__ == '__main__':
    create_auto_documentation()
