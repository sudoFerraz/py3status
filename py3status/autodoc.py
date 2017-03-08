#!python2
# -*- coding: utf-8 -*-

import ast
import inspect
import os.path
import re

from subprocess import check_output

from py3status.docstrings import core_module_docstrings
from py3status.py3 import Py3
from py3status.screenshots import get_samples


# some Py3 have constants as defaults me need to identify them here
CONSTANT_PARAMS = [
    ('log', 'level'),
    ('notify_user', 'level'),
]
from py3status.image import create_screenshots


def fix(lines):
    """
    Convert markdown code blocks to restructured text
    """
    out = []
    code = False
    for line in lines:
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


def file_sort(my_list):
    """
    Sort a list of files in a nice way.
    eg item-10 will be after item-9
    """
    def alphanum_key(key):
        """
        Split the key into str/int parts
        """
        return [int(s) if s.isdigit() else s for s in re.split('([0-9]+)', key)]

    my_list.sort(key=alphanum_key)
    return my_list


def screenshots(screenshots_data, module_name):
    """
    Create .rst output for any screenshots a module may have.
    """
    shots = screenshots_data.get(module_name)
    print(shots)
    if not shots:
        return('')

    out = []
    for shot in file_sort(shots):
        path = '../doc/screenshots/%s.png' % shot
     #   path = os.path.join(
     #       os.path.dirname(os.path.abspath(__file__)), '..', 'doc', 'screenshots', '%s.png' % shot
     #   )
        if not os.path.exists(path):
            print('not found')
            print(path)
            continue
        out.append(
            u'\n.. image:: {}\n\n'.format(path)
        )
    print('found')
    return u''.join(out)


def create_module_docs():
    '''
    Create documentation for modules.
    '''
    data = core_module_docstrings(format='rst')
    # get screenshot data
    screenshots_data = {}
    samples = get_samples()
    for sample in samples.keys():
        module = sample.split('-')[0]
        if module not in screenshots_data:
            screenshots_data[module] = []
        screenshots_data[module].append(sample)

    out = []
    # details
    for module in sorted(data.keys()):
        out.append(
            '\n{name}\n{underline}\n\n{screenshots}{details}\n'.format(
                name=module,
                screenshots=screenshots(screenshots_data, module),
                underline='-' * len(module),
                details=''.join(fix(data[module])).strip()))
    # write include file
    with open('../doc/modules-info.rst', 'w') as f:
        f.write(''.join(out))


def get_variable_docstrings(filename):
    '''
    Go through the file and find all documented variables.
    That is ones that have a literal expression following them.

    Also get a dict of assigned values so that we can substitute contstants.
    '''

    def walk_node(parent, v=None, prefix=''):
        d = {}
        if v is None:
            v = {}
        key = None
        for node in ast.iter_child_nodes(parent):
            if isinstance(node, ast.ClassDef):
                # We are in a class
                d[node.name] = walk_node(node, v, prefix + node.name + '.')[0]
            elif isinstance(node, ast.Assign):
                key = node.targets[0].id
                if isinstance(node.value, ast.Num):
                    v[key] = node.value.n
                if isinstance(node.value, ast.Str):
                    v[key] = node.value.s
                if isinstance(node.value, ast.Name):
                    if node.value.id in v:
                        v[prefix + key] = v[node.value.id]
            elif isinstance(node, ast.Expr) and key:
                d[key] = node.value.s
            else:
                key = None
        return d, v

    with open(filename, 'r') as f:
        fstr = f.read()
    return walk_node(ast.parse(fstr))


def get_py3_info():
    """
    Inspect Py3 class and get constants, exceptions, methods
    along with their docstrings.
    """
    # get all documented constants
    constants, values = get_variable_docstrings('../py3status/py3.py')
    constants = constants['Py3']
    constants = [(k, v) for k, v in sorted(constants.items())]

    # filter values as we only care about constants defined in Py3
    values = dict([(v, k[4:]) for k, v in values.items() if k.startswith('Py3.')])

    def make_value(attr, arg, default):
        """
        If the methods parameter is defined as a constant then do a replace
        ment.  Otherwise return the values representation.
        """
        if (attr, arg) in CONSTANT_PARAMS and default in values:
            return values[default]
        return repr(default)

    py3 = Py3()
    attrs = [x for x in dir(py3) if not x.startswith('_')]
    exceptions = []
    methods = []
    for attr in attrs:
        item = getattr(py3, attr)
        if 'method' in str(item):

            args, vargs, kw, defaults = inspect.getargspec(item)
            args = args[1:]
            sig = []
            len_defaults = len(defaults) if defaults else 0
            len_args = len(args)
            for index, arg in enumerate(args):
                if len_args - index <= len_defaults:
                    default = defaults[len_defaults - len_args + index]
                    sig.append('%s=%s' % (arg, make_value(attr, arg, default)))
                else:
                    sig.append(arg)

            definition = '%s(%s)' % (attr, ', '.join(sig))
            methods.append((definition, item.__doc__))
            continue
        try:
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
    Unindent docstring.
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
            output.append('.. _%s:' % name)
            output.append('')
            output.append('.. py:%s:: %s' % (trans[k], name))
            output.append('')
            output.extend(auto_undent(desc))
        with open('../doc/py3-%s-info.inc' % k, 'w') as f:
            f.write('\n'.join(output))


def create_changelog():
    """
    Format the changelog
    """
    re_title = re.compile('^(\D*(\d+.\d+)\D*)\(([^)]*)\)\s*$')
    tags = check_output(['git', 'tag', '-l', '--sort=taggerdate']).decode('utf-8').splitlines()
    tags = list(reversed(tags))

    output = []
    output.append('')

    with open('../CHANGELOG', 'r') as f:
        for line in f:
            if not line.strip():
                output.append('')
            elif not line.startswith('*'):
                match = re_title.match(line)
                if match:
                    title = match.group(1)
                    version = match.group(2)
                    release_date = match.group(3)
                    output.append(title)
                    output.append('^' * len(title))
                    output.append('')
                    output.append(release_date)
                    output.append('')
                    try:
                        index = tags.index(version)
                    except ValueError:
                        index = -1
                        version = 'HEAD'
                    diff = '%s..%s' % (tags[index + 1], version)
                    authors = check_output(['git', 'log', diff, '--format="%aE"']).decode('utf-8')
                    authors = len(set(authors.splitlines()))
                    plural = 'author' if authors == 1 else 'authors'

                    commits = check_output(['git', 'log', '--oneline', diff, '--no-merges'])
                    commits = len(commits.splitlines())

                    date_start = check_output(['git', 'log', tags[index +1], '-1', '--format=%at']).strip()
                    date_end = check_output(['git', 'log', version, '-1', '--format=%at']).strip()
                    days = (int(date_end) - int(date_start)) // 86400
                    output.append('*%s days, %s %s, %s commits*' % (days, authors, plural, commits))
                    output.append('')
                    stats = check_output(['git', 'diff', '--shortstat', diff]).decode('utf-8')
                    output.append('*%s*' % stats.strip())
                    output.append('')
            else:
                output.append(line)

    with open('../doc/changelog.inc', 'w') as f:
        f.write('\n'.join(output))

def create_auto_documentation():
    """
    Create any include files needed for sphinx documentation
    """
    create_screenshots()
    create_module_docs()
    create_py3_docs()
    create_changelog()


if __name__ == '__main__':
    create_auto_documentation()
