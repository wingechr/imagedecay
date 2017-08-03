# coding=utf-8

import os
import sphinx_rtd_theme

version = "0.1"
project = "imagedecay"
description = "Applying various custom image filters iteratively for fun."

author = "Christian Winger"
author_email = "c@wingechr.de"
license = "GPLv3"
language = "en"

copyright = ""
package = project.lower()
url = "https://github.com/wingechr/" + package

todo_include_todos = True
add_module_names = False
show_authors = True
html_show_sourcelink = False
html_show_sphinx = False
html_search_language = language
html_show_copyright = bool(copyright)
docs_path = 'docs'
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
html_theme_options = {}
html_theme = "sphinx_rtd_theme"
master_doc = 'index'
source_encoding = 'utf-8'
source_suffix = ['.rst', '.md']
pygments_style = 'sphinx'
html_logo = os.path.join(docs_path, '_static/logo.svg')
html_favicon = os.path.join(docs_path, '_static/favicon.ico')
templates_path = [os.path.join(docs_path, '_templates')]
exclude_dirs = []
nitpicky = True
html_use_index = True
add_function_parentheses = True
html_static_path = [os.path.join(docs_path, '_static')]
graphviz_output_format = 'svg'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.todo',
    'sphinx.ext.mathjax',
    'sphinx.ext.viewcode',
    'sphinx.ext.graphviz',     # ``dot`` must be in PATH
    'sphinxcontrib.napoleon',  # requires sphinxcontrib-napoleon
    # 'sphinx_fontawesome',    # broken
]

# Napoleon settings
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = False
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_use_keyword = True

# fix warnings about docstring referencing builtin types
nitpick_ignore = [
    ('py:obj', 'int'),
    ('py:obj', 'str'),
    ('py:obj', 'bool'),
    ('py:obj', 'optional')
]

# mathjax path realtiv to _static
mathjax_path = 'mathjax\MathJax.js'
