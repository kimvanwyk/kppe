FROM registry.gitlab.com/kimvanwyk/document-containers/pandoc:latest

LABEL name=kimvanwyk/kppe
MAINTAINER kimvanwyk

USER root
RUN apt-get update && apt-get -y install \
   python3.8 \
&& apt-get autoremove \
&& rm -rf /var/lib/apt/lists/*

COPY src/ /app
RUN chmod ugo+rwx /app

RUN mkdir /abbreviations; chown appuser:appuser /abbreviations
VOLUME /io
RUN mkdir /templates; chown appuser:appuser /templates
RUN mkdir /images; chown appuser:appuser /images
RUN mkdir /ref_tags; chown appuser:appuser /ref_tags

USER appuser
WORKDIR /io

ENV LANG C.UTF-8

ENTRYPOINT ["/usr/bin/python3", "/app/kppe.py", "build", "--abbreviations-dir", "/abbreviations", "--templates-dir", "/templates", "--images-dir", "/images", "--ref-tags-dir", "/ref_tags"]
CMD ["no_frills_latex"]
