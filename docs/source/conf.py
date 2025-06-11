# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys
sys.path.insert(0, os.path.abspath('../../../'))  # Path to your project root

project = 'RPG project'
copyright = '2025, s28436'
author = 's28436'
release = '1.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',  # For Google/NumPy style docstrings
    'sphinx_autodoc_typehints',  # Better type hint support
]

templates_path = ['_templates']
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# html_theme = 'alabaster'
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# -- Autodoc configuration --------------------------------------------------
autodoc_default_options = {
    'members': True,
    'member-order': 'alphabetical',
    'special-members': '__init__',
    'undoc-members': True,
    'exclude-members': '__weakref__'
}