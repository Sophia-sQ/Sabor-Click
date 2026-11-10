import sys
import os

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

sys.path.insert(0, os.path.abspath("../../../../"))   # raiz = diretório atual


project = 'Sabor & Click'
copyright = "2026, Rafaella Sant'anna, Kleber da Silva, Sophia Sales, Thiago Vinícius"
author = "Rafaella Sant'anna, Kleber da Silva, Sophia Sales, Thiago Vinícius"
release = '1.0.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode", 
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinx.ext.githubpages",
    "sphinx_autodoc_typehints",
    "sphinx_copybutton",
    "sphinx_markdown_builder",
]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "flask": ("https://flask.palletsprojects.com/en/stable/", None),
    "sqlalchemy": ("https://docs.sqlalchemy.org/en/20/", None),
}

napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = True
napoleon_use_param = True
napoleon_use_rtype = True

autodoc_mock_imports = ["flask_sqlalchemy", "flask_mail"]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

language = 'pt_BR'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "clarity"

html_theme_options = {
    "default_theme": "system",     
    "font_stack": "default",       
    "navigation_with_keys": True,  
    "show_toc_level": 2,
}

html_static_path = ['_static']
