#!python2
# -*- coding: utf-8 -*-

from py3status.docstrings import core_module_docstrings

def fix(lines):
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


def create_readme(data):
    '''
    Create README.md text for the given module data.
    '''
    out = []
    # details
    for module in sorted(data.keys()):
        out.append(
            '\n{name}\n{underline}\n\n{details}\n'.format(
                name=module,
                underline='-' * len(module),
                details=''.join(fix(data[module])).strip()))
    return ''.join(out)


with open('../doc/modules-info.rst', 'w') as f:
    f.write(create_readme(core_module_docstrings(format='rst')))
