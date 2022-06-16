#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import datetime

import beacon_api
from unittest.mock import MagicMock


# Get the project root dir, which is the parent dir of this
sys.path.insert(0, os.path.abspath("../beacon_api"))

# -- General configuration ------------------------------------------------


class Mock(MagicMock):
    """Mock some of the packages."""

    @classmethod
    def __getattr__(cls, name):
        """Get attributes."""
        return MagicMock()


# List modules need to be mocked
MOCK_MODULES = [
    "aiohttp",
    "asyncpg",
    "cyvcf2",
    "aiohttp_cors",
    "Cython",
    "numpy",
    "authlib.jose",
    "authlib.jose.errors",
    "uvloop",
    "aiocache",
    "aiocache.serializers",
]
sys.modules.update((mod_name, Mock()) for mod_name in MOCK_MODULES)

# If your documentation needs a minimal Sphinx version, state it here.
#
# needs_sphinx = '1.0'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.coverage",
    "sphinx.ext.ifconfig",
    "sphinx.ext.viewcode",
    "sphinx.ext.githubpages",
    "sphinx.ext.todo",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["templates"]

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
# source_suffix = ['.rst', '.md']
source_suffix = ".rst"

# The master toctree document.
master_doc = "index"

# Get current year
current_year = str(datetime.date.today().year)

# General information about the project.
project = "beacon-python"
copyright = f"2018 - {current_year}, {beacon_api.__copyright__} |"
author = beacon_api.__author__

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The short X.Y version.
version = str(beacon_api.__version__)
# The full version, including alpha/beta/rc tags.
release = str(beacon_api.__version__)

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = "en"

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This patterns also affecst html_static_path and html_extra_path
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = False


autosummary_generate = True

# -- Options for HTML output ----------------------------------------------

html_title = "beacon-python API"

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.

html_theme = "sphinx_rtd_theme"
html_theme_options = {"collapse_navigation": True, "sticky_navigation": True, "display_version": True, "prev_next_buttons_location": "bottom"}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["static"]

# Custom sidebar templates, must be a dictionary that maps document names
# to template names.
#
# This is required for the alabaster theme
# refs: http://alabaster.readthedocs.io/en/latest/installation.html#sidebars
html_sidebars = {
    "**": [
        # 'about.html',
        # 'navigation.html',
        # 'relations.html',  # needs 'show_related': True theme option to display
        # 'searchbox.html',
        # 'donate.html',
    ]
}

today_fmt = "%B %d, %Y"


def setup(app):
    """Add custom stylesheet."""
    app.add_css_file("custom.css")


# -- Other stuff ----------------------------------------------------------
htmlhelp_basename = "beacon-python"
man_pages = [(master_doc, "beacon-python", [author], 1)]
texinfo_documents = [(master_doc, "beacon-python", author, "Miscellaneous")]
