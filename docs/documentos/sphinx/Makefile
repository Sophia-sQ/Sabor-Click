# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = source
BUILDDIR      = build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile singletxt

# Gera a documentação do backend em um ÚNICO arquivo de texto:
#   $(BUILDDIR)/text/index.txt
# (como o index.rst concentra todos os módulos num só documento, a saída
#  do builder de texto é um arquivo único).
singletxt:
	@$(SPHINXBUILD) -b text "$(SOURCEDIR)" "$(BUILDDIR)/text" $(SPHINXOPTS) $(O)
	@echo "Documentação gerada em: $(BUILDDIR)/text/index.txt"

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
