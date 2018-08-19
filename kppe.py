#!/usr/bin/python

'''
Copyright (c) 2014, Kim van Wyk 
All rights reserved.  

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

Redistributions of source code must retain the above copyright
notice, this list of conditions and the following disclaimer. 
Redistributions in binary form must reproduce the above copyright
notice, this list of conditions and the following disclaimer in the
documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
'''

from collections import defaultdict, OrderedDict, namedtuple
from ConfigParser import SafeConfigParser
from glob import glob
import inspect
import json
import os
import os.path
import re
from subprocess import Popen, PIPE, STDOUT
import sys
from version import VERSION

ERROR = namedtuple('ERROR', ('code', 'name'))
code = 0
NO_ERROR = ERROR(code,  "NO_ERROR")
code += 1
BAD_REF_TAGS_FILE_ERROR = ERROR(code,  "BAD_REF_TAGS_FILE")
code += 1
BAD_TEMPLATE_DIR_ERROR = ERROR(code, "BAD_TEMPLATE_DIR")
code += 1
BAD_TEMPLATE_FILE_ERROR = ERROR(code, "BAD_TEMPLATE_FILE")
code += 1
PANDOC_ERROR = ERROR(code, "PANDOC_ERROR")
code += 1
UNKNOWN_ERROR = ERROR(code, "UNKNOWN_ERROR")
# Exceptions
class KppeExpection(Exception):
    pass
class BadRefTagsFileException(KppeExpection):
    error = BAD_REF_TAGS_FILE_ERROR
class BadTemplateDirException(KppeExpection):
    error = BAD_TEMPLATE_DIR_ERROR
class BadTemplateFileException(KppeExpection):
    error = BAD_TEMPLATE_FILE_ERROR

# determine the local path
frame = inspect.currentframe()
try:
    LOCAL_PATH = os.path.split(inspect.getframeinfo(frame)[0])[0]
finally:
    del frame
DEFAULT_TEMPLATE_PATH = os.path.join(LOCAL_PATH, 'default_templates')
STANDARD_TEMPLATE_PATH = os.path.join(LOCAL_PATH, 'templates')
STANDARD_ABBREV_PATH = os.path.join(LOCAL_PATH, 'abbreviations')

def latex_label(s):
    ''' Return a version of input string suitable for use as a Latex label
       - Lowercase all characters
       - Replace " ", "#", "\" with "_"
    '''
    for c in (' ', '#', '\\'):
        s = s.replace(c, '_')
    s = s.lower()
    return s

class TagReplace(object):
    ''' Hold a set of lines, and perform
    tag replacement on them.
    A tag is defined as anything inside a << >>,
    which starts with a lower case letter. Tag
    contents are seperated with ":"
    '''

    sig_size = 3
    sig_path = None

    def __init__(self, lines, abbrevs={}, ref_tags={}):
        self.lines = lines
        # track occurences of reference tags
        self.ref_count = defaultdict(int)
        self.action_count = defaultdict(int)
        # Set the path to signature files to be the path of kppe.py, if not otherwise set
        if not self.__class__.sig_path:
            self.__class__.sig_path = LOCAL_PATH
        self.abbrevs = abbrevs
        self.ref_tags = ref_tags
  
    def process(self):
        ''' Loop over each line, replacing all tags as they are encountered
        '''
        def process_line(match):
            ''' Process the tag match object and return a suitable replacement
            '''
            items = match.groups()[0].split(':')
            if (items[0] == 'ref') and (items[1] in self.ref_tags.keys()):
                # found a match, replace it and increase the count
                self.ref_count[items[1]] += 1
                return r"\label{%s%d}" % (items[1], self.ref_count[items[1]])

            elif items[0] == 'action':
                # extract the name of someone to assign an action to, labelling the point with
                # a converted version of the name (lowercase, with spaces and some punctuation replaced with "_")
                # Keep a dict mapping the name to the number of entries
                out = []
                for k in items[1:]:
                    # found an action, replace it with a suitable label and increase the count
                    self.action_count[k] += 1
                    out.append(r"\label{%s_%d}" % (latex_label(k), self.action_count[k]))
                if items[1:]:
                    out.extend(['', r'**\textcolor{magenta}{Action: %s}**' % ', '.join(items[1:]), ''])
                return '\n'.join(out)

            elif items[0] == 'heading':
                # Found a set of text to be centered and bolded
                out = [r'\begin{center}', '']
                for h in items[1:]:
                    out.extend([r'\textbf{%s}' % h, ''])
                out.extend([r'\end{center}', ''])
                return '\n'.join(out)

            elif items[0] == 'right':
                # Found a set of text to be placed on the right of the page
                out = [r'\begin{flushright}', '']
                for h in items[1:]:
                    out.extend([h, ''])
                out.extend([r'\end{flushright}', ''])
                return '\n'.join(out)

            elif items[0] == 'sig':
                # signature to be inserted. At least one part after sig: is expected:
                # the name of the sig file (without extension). This file should be stored
                # in the self.sig_path value, which defaults to the  kppe location

                # An optional additional argument gives the size, defaulting to sig_size
                # if not given
                # create file name
                if items[1:]:
                    fh = items[1]
                    f = os.path.join(self.sig_path, '%s.png' % fh).replace('\\', '/')
                # calculate size
                try:
                    size = float(items[2])
                except Exception as e:
                    size = self.sig_size
                return r'\includegraphics[width=%.1fcm]{%s}' % (size, f)

            elif items[0] == 'decision':
                # A decision needs to be marked up - bolded and made red. One argument is needed -
                # the text to bold
                return  r"**\textcolor{red}{%s}**" % items[1]

            elif items[0] == 'fill-in':
                # A fill-in should be underlined and made a light grey. One argument is needed -
                # the text to bold
                s = items[1]
                tot_len = 20
                if len(items) > 2:
                    # length modifier given. Otherwise use default of 20
                    tot_len = int(items[2])
                if len(s) < tot_len:
                    l = (tot_len - len(s))/2
                    s = '%s%s%s' % ('\quad ' * l, s, '\quad ' * l)
                return  r"\textcolor{Gray}{\underline{%s}}" % s

            elif items[0] in ('a', 'n', 'abbrev', 'name'):
                # Replace with a name, if there is a suitable entry in self.abbrevs. If there isn't an entry
                # don't replace the tag
                n = self.abbrevs.get(items[1], None)
                if n:
                    return n
                return ''
            # no tag match, return the whole line
            return match.string

        self.out = [re.sub("<<(.+?)>>", process_line, l) for l in self.lines]

    def get_text(self):
        # Add reference section, if there are refs
        if any(self.ref_count.values()):
            self.out.extend(['', '#District Projects', '', ''])

            keys = self.ref_tags.keys()
            keys.sort()

            for k in keys:
                t, prefix = self.ref_tags[k]
                if prefix:
                    prefix = prefix.strip() + ' '
                else:
                    prefix = ''
                if not self.ref_count[k]:
                    if not prefix:
                        c = 'Nothing to report.'
                    else:
                        # Don't add count if there is a prefix
                        c = ''
                else:
                    c = 'See %s.' % (', '.join('\\ref{%s%d}' % (k,i) for i in range(1, self.ref_count[k] + 1)))
                self.out.append('* **%s** - %s%s' % (t, prefix, c))

        # Add actions section, if there are any actions
        if any(self.action_count.values()):
            self.out.extend(['', '#Actions', '', ''])

            keys = self.action_count.keys()
            keys.sort()

            for k in keys:
                if self.action_count[k]:
                    c = 'See %s.' % (', '.join('\\ref{%s_%d}' % (latex_label(k),i) for i in range(1, self.action_count[k] + 1)))
                    self.out.append('* **%s** - %s' % (k, c))

        return '\n'.join(self.out)

def build_pdf(text, template, name, toc=False):
    ''' Build the provided *text* into a PDF via markdown2pdf, using the supplied full path to the *template*
    *name* is the output filename to use
    if *toc* evals as True, a table of contents is generated

    Return a tuple of (returned text, return code)
    '''
    # supply a path to the template image files, which will be the path the template is in
    path = os.path.split(os.path.abspath(template))[0].replace('\\', '/') + '/'
    if 'word' in template:
        template_arg = '--reference-doc=%s' % template
        ext = 'docx'
    else:
        template_arg = '--template=%s' % template
        ext = 'pdf'
    args = ['pandoc', '-s', '-V', 'fontsize:12', '-V', 'path:%s' % path, template_arg, '-o', '%s.%s' % (name, ext)]
    if toc:
        args.append('--toc')
    p = Popen(args, stdout=PIPE, stdin=PIPE, stderr=STDOUT)
    ret = p.communicate(input=text)[0]
    return (ret, p.returncode)

def get_ref_tags(filename):
    ''' Parse the supplied file of reference tags
    '''
    if not os.path.exists(filename):
        raise BadRefTagsFileException

    ref_tags = SafeConfigParser(defaults={'prefix':None})
    ref_tags.read(filename)
    d = {}
    for s in ref_tags.sections():
        if 'title' not in ref_tags.options(s):
            raise BadRefTagsFileException
        d[s] = (ref_tags.get(s,'title'),ref_tags.get(s, 'prefix'))
    return d

def get_template_dict(template_dir):
    l = []
    for d in (DEFAULT_TEMPLATE_PATH, template_dir):
        if not os.path.exists(d):
            raise BadTemplateDirException
        p = os.path.abspath(d)
        for f in [f for f in os.listdir(d) if not os.path.isdir(os.path.join(p,f))]:
            l.append((os.path.splitext(f)[0], os.path.join(p, f)))
    l.sort()
    return OrderedDict(l)

def get_template(template_name, templates_dir):
    templates = get_template_dict(templates_dir)
    if template_name not in templates:
        raise BadTemplateFileException
    return templates[template_name]

def exit(error = None, verbose=False):
    ''' Exit, using optional supplied ERROR value if given.
    If 'verbose', print additional info
    '''
    if (error is not None):
        if verbose:
            print 'Exit code: %d. Code name: %s' % (error.code, str(error.name))
        sys.exit(error.code)
    sys.exit()

if __name__ == '__main__':
    
    import argparse

    def list_templates(args):
        try:
            templates = get_template_dict(args.templates_dir)
        except BadTemplateDirException as e: 
            exit(e.error, args.verbose)
        print 'Available Templates:'
        print '\n'.join(['   %s' % t for t in templates.keys()])
        exit(NO_ERROR, args.verbose)

    def run_kppe(args):
        ''' Build a PDF, if supplied options are valid. Exit with an error code otherwise
        '''
        try:
            template = get_template(args.template, args.templates_dir)
        except (BadTemplateDirException, BadTemplateFileException) as e:
            exit(e.error, args.verbose)
        except Exception as e:
            exit(NO_ERROR, args.verbose)

        # build a list of abbreviations, sending an empty dict if there aren't any
        # Raise an error if an invalid file is supplied
        if os.path.exists(args.abbreviations_dir):
            abbrevs = {}
            for f in glob(os.path.join(args.abbreviations_dir, '*.json')):
                with open(f, 'r') as fh:
                    abbrevs.update(json.load(fh))

        # produce a ref tags file, if specified
        if args.ref_tags_file:
            try:
                ref_tags = get_ref_tags(args.ref_tags_file)
            except BadRefTagsFileException as e:
                exit(e.error, args.verbose)
            except Exception as e:
                exit(NO_ERROR, args.verbose)
        else:
            ref_tags = {}

        fh = open(args.file, 'r')
        tag = TagReplace([l.strip('\n') for l in fh.readlines()], abbrevs=abbrevs, ref_tags=ref_tags)
        tag.process()
        text = tag.get_text()
        if args.write_source_file:
            f = open('output.txt', 'w')
            f.write(text)
            f.close()
        ret, retcode = build_pdf(text, template, os.path.splitext(os.path.split(args.file)[1])[0], toc=args.toc)
        if args.verbose:
            print 'Pandoc output:'
            print
            print ret
        fh.close()
        # if pandoc did not report a 0 returncode, return a PANDOC_ERROR
        exit(PANDOC_ERROR if retcode else NO_ERROR, args.verbose)

    parser = argparse.ArgumentParser(description='Build a PDF with markdown2pdf')
    subparsers = parser.add_subparsers()

    parser_run_kppe = subparsers.add_parser('build', help='Build a PDF from the supplied file')
    parser_run_kppe.add_argument('template', help='Select a template to use')
    parser_run_kppe.add_argument('file', help='The pandoc file to process')
    parser_run_kppe.add_argument('--write-source-file', action='store_true', 
                                 help='Whether to save the generated source file. If set, the file is saved to output.txt')
    parser_run_kppe.add_argument('--toc', action='store_true',
                                 help='Also generate a table of contents')
    parser_run_kppe.add_argument('--abbreviations-dir', default=STANDARD_ABBREV_PATH, 
                                 help='Set the full path to the abbreviations directory. Defaults to "%(default)s"')
    parser_run_kppe.add_argument('--ref-tags-file', default=None, 
                                 help='Set the full path to a file of reference tags. If not set, no reference tags are used')
    parser_run_kppe.set_defaults(func=run_kppe)

    parser_list_templates = subparsers.add_parser('templates', help='Print a list of templates from the templates dir')
    parser_list_templates.set_defaults(func=list_templates)

    # a slight hack to get the same global options into each subparser, as they do not seem to inherit
    # from the parent, which is contrary to the argparse docs. 
    # A stackoverflow question (http://stackoverflow.com/questions/7066826/in-python-how-to-get-subparsers-to-read-in-parent-parsers-argument)
    # suggested giving a "parent={parser]" argument to the subparser call, but that causes a different argparse error
    for p in [parser_list_templates, parser_run_kppe]:
        p.add_argument('--templates-dir', default=STANDARD_TEMPLATE_PATH, 
                        help='Set the full path to the templates directory. Defaults to "%(default)s"')
        p.add_argument('--quiet', '-q', action='store_false', dest="verbose",
                       help='Whether to suppress information and status during operation')
        p.add_argument('--version', action='version',
                       version = "%(prog)s " + VERSION)

    args = parser.parse_args()
    args.func(args)
