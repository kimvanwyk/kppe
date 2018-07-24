.. KPPE documentation master file, created by
   sphinx-quickstart on Fri Jun 15 11:59:40 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

kppe
================================

Contents:

.. toctree::
   :maxdepth: 2
   
   operation
   tags 
   api

Introduction
=============

kppe is a Python wrapper around *pandoc*'s `Markdown2pdf <http://johnmacfarlane.net/pandoc/README.html#markdown2pdf|Markdown2pdf>`_, which parses the input for a few additional tags which *pandoc* does not support. The ability to select from one of several LaTeX templates is also included. As it wraps around *Markdown2pdf*, it is intended specifically for generating PDF documents via LaTeX with *pandoc*.

Some of the functionality of kppe is fairly heavily tied to my requirements for generating documents for the `North Durban Lions Club <http://www.northdurbanlions.org.za>`_ and for `Lions District 410C <http://lionsdist410c.lionnet.org.za>`_ and `Multiple District 410 <http://lionnet.org.za>`_, but the code could be modified to suit a different set of PDF generation requirements. A template is also included which adds no specific headers or footers, but still supports the other kppe options, useful to me for non-Lions documents.

The odd seeming name is an acronym of "**K**\ im's **P**\ andoc **P**\ ython **E**\ xtensions".
