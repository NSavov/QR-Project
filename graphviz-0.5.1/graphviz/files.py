# files.py - save, render, view

"""Save DOT code objects, render with Graphviz dot, and open in viewer."""

import os
import io
import codecs

from ._compat import text_type

from . import backend, tools

__all__ = ['File', 'Source']


class Base(object):

    _format = 'pdf'
    _engine = 'dot'
    _encoding = 'utf-8'

    @property
    def format(self):
        """The output format used for rendering ('pdf', 'png', ...)."""
        return self._format

    @format.setter
    def format(self, format):
        format = format.lower()
        if format not in backend.FORMATS:
            raise ValueError('unknown format: %r' % format)
        self._format = format

    @property
    def engine(self):
        """The layout commmand used for rendering ('dot', 'neato', ...)."""
        return self._engine

    @engine.setter
    def engine(self, engine):
        engine = engine.lower()
        if engine not in backend.ENGINES:
            raise ValueError('unknown engine: %r' % engine)
        self._engine = engine

    @property
    def encoding(self):
        """The encoding for the saved source file."""
        return self._encoding

    @encoding.setter
    def encoding(self, encoding):
        if encoding is not None:
            codecs.lookup(encoding)
        self._encoding = encoding


class File(Base):

    directory = ''

    _default_extension = 'gv'

    def __init__(self, filename=None, directory=None, format=None, engine=None, encoding=None):
        if filename is None:
            name = getattr(self, 'name', None) or self.__class__.__name__
            filename = '%s.%s' % (name, self._default_extension)
        self.filename = filename

        if directory is not None:
            self.directory = directory

        if format is not None:
            self.format = format

        if engine is not None:
            self.engine = engine

        if encoding is not None:
            self.encoding = encoding

    def _repr_svg_(self):
        return self.pipe(format='svg').decode(self._encoding)

    def pipe(self, format=None):
        """Return the source piped through the Graphviz layout command.

        Args:
            format: The output format used for rendering ('pdf', 'png', etc.).
        Returns:
            Binary (encoded) stdout of the layout command.
        """
        if format is None:
            format = self._format

        data = text_type(self.source).encode(self._encoding)

        outs = backend.pipe(self._engine, format, data)

        return outs

    @property
    def filepath(self):
        return os.path.join(self.directory, self.filename)

    def save(self, filename=None, directory=None):
        """Save the DOT source to file.

        Args:
            filename: Filename for saving the source (defaults to name + '.gv')
            directory: (Sub)directory for source saving and rendering.
        Returns:
            The (possibly relative) path of the saved source file.
        """
        if filename is not None:
            self.filename = filename
        if directory is not None:
            self.directory = directory

        filepath = self.filepath
        tools.mkdirs(filepath)

        data = text_type(self.source)

        with io.open(filepath, 'w', encoding=self.encoding) as fd:
            fd.write(data)

        return filepath

    def render(self, filename=None, directory=None, view=False, cleanup=False):
        """Save the source to file and render with the Graphviz engine.

        Args:
            filename: Filename for saving the source (defaults to name + '.gv')
            directory: (Sub)directory for source saving and rendering.
            view: Open the rendered result with the default application.
            cleanup: Delete the source file after rendering.
        Returns:
            The (possibly relative) path of the rendered file.
        Raises:
            RuntimeError: If the Graphviz executable is not found.
            RuntimeError: If viewer opening is requested but not supported.
        """
        filepath = self.save(filename, directory)

        rendered = backend.render(self._engine, self._format, filepath)

        if cleanup:
            os.remove(filepath)

        if view:
            self._view(rendered, self._format)

        return rendered

    def view(self, filename=None, directory=None, cleanup=False):
        """Save the source to file, open the rendered result in a viewer.

        Args:
            filename: Filename for saving the source (defaults to name + '.gv')
            directory: (Sub)directory for source saving and rendering.
            cleanup: Delete the source file after rendering.
        Returns:
            The (possibly relative) path of the rendered file.
        Raises:
            RuntimeError: If the Graphviz executable is not found.
            RuntimeError: If opening the viewer is not supported.

        Short-cut method for calling ``render()`` with ``view=True``.
        """
        return self.render(view=True,
            filename=filename, directory=directory, cleanup=cleanup)

    def _view(self, filepath, format):
        """Start the right viewer based on file format and platform."""
        methodnames = [
            '_view_%s_%s' % (format, backend.PLATFORM),
            '_view_%s' % backend.PLATFORM,
        ]
        for name in methodnames:
            view_method = getattr(self, name, None)
            if view_method is not None:
                break
        else:
            raise RuntimeError('%r has no built-in viewer support for %r '
                'on %r platform' % (self.__class__, format, backend.PLATFORM))
        view_method(filepath)

    _view_darwin = staticmethod(backend.view.darwin)
    _view_linux = staticmethod(backend.view.linux)
    _view_windows = staticmethod(backend.view.windows)


class Source(File):
    """Verbatim DOT source code string to be rendered by Graphviz.

    Args:
        source: The verbatim DOT source code string.
        filename: Filename for saving the source (defaults to name + '.gv').
        directory: (Sub)directory for source saving and rendering.
        format: Rendering output format ('pdf', 'png', ...).
        engine: Layout command used ('dot', 'neato', ...).
        encoding: Encoding for saving the source.

    .. note::
        All parameters except source are optional and can be changed under
        their corresponding attribute name after instance creation.
    """

    def __init__(self, source, filename=None, directory=None, format=None, engine=None, encoding=None):
        super(Source, self).__init__(filename, directory, format, engine, encoding)
        self.source = source
