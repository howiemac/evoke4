""" ungainly customisation of sassutils.builder.build_directory
"""
from sassutils.builder import *
from sass import compile
import os
import io


def build_directory(sass_path, css_path, output_style='nested',
                    _root_sass=None, _root_css=None):
    """Compiles all SASS/SCSS files in ``path`` to CSS.

    :param sass_path: the path of the directory which contains source files
                      to compile
    :type sass_path: :class:`str`, :class:`basestring`
    :param css_path: the path of the directory compiled CSS files will go
    :type css_path: :class:`str`, :class:`basestring`
    :param output_style: an optional coding style of the compiled result.
                         choose one of: ``'nested'`` (default), ``'expanded'``,
                         ``'compact'``, ``'compressed'``
    :type output_style: :class:`str`
    :returns: a dictionary of source filenames to compiled CSS filenames
    :rtype: :class:`collections.Mapping`

    .. versionadded:: 0.6.0
       The ``output_style`` parameter.

    """
    if _root_sass is None or _root_css is None:
        _root_sass = sass_path
        _root_css = css_path
    result = {}
    if not os.path.isdir(css_path):
        os.mkdir(css_path)
    for name in os.listdir(sass_path):
        sass_fullname = os.path.join(sass_path, name)
        if SUFFIX_PATTERN.search(name) and os.path.isfile(sass_fullname):
            if name[0] == '_':
                # Do not compile if it's partial
                continue
            css_fullname = os.path.join(css_path, name).replace('.sass', '.css')
            map_fullname = css_fullname + '.map'
            css, mapping = compile(filename=sass_fullname,
                          output_style=output_style,
                          source_map_filename=map_fullname,
                          include_paths=[_root_sass])
            with io.open(
                css_fullname, 'w', encoding='utf-8', newline='',
            ) as css_file:
                css_file.write(css)
            with io.open(
                map_fullname, 'w', encoding='utf-8', newline='',
            ) as map_file:
                map_file.write(mapping)
            result[os.path.relpath(sass_fullname, _root_sass)] = \
                os.path.relpath(css_fullname, _root_css)
        elif os.path.isdir(sass_fullname):
            css_fullname = os.path.join(css_path, name)
            subresult = build_directory(sass_fullname, css_fullname,
                                        output_style=output_style,
                                        _root_sass=_root_sass,
                                        _root_css=_root_css)
            result.update(subresult)
    return result
