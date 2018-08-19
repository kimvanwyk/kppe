FROM kimvanwyk/pandoc:latest

LABEL name=kimvanwyk/kppe
MAINTAINER kimvanwyk

RUN apt-get update && apt-get -y install \
   python3 \
&& apt-get autoremove \
&& rm -rf /var/lib/apt/lists/*

ADD src/ /app

VOLUME /abbreviations
VOLUME /io
VOLUME /templates
VOLUME /images
VOLUME /ref_tags

WORKDIR /io

ENV LANG C.UTF-8

ENTRYPOINT ["/usr/bin/python3", "/app/kppe.py", "build", "--abbreviations-dir", "/abbreviations", "--templates-dir", "/templates", "--images-dir", "/images", "--ref-tags-dir", "/ref_tags", "no_frills_latex"]
