''' Execute kppe in the kimvanwyk/kppe container, voluming in the 
dir of the input file and various input dirs
'''

import os, os.path

CONTAINER_NAME = 'kppe'

VOLUME_BASE = '/home/kimv/src/kppe/kppe_private'

VOLUMES = {os.path.join(VOLUME_BASE, 'abbreviations'): '/abbreviations',
           os.path.join(VOLUME_BASE, 'images'): '/images',
           os.path.join(VOLUME_BASE, 'ref_tags'): '/ref_tags',
           os.path.join(VOLUME_BASE, 'templates'): '/templates',
}
VOLUME_PATH = ' -v '.join(f'{k}:{v}' for (k,v) in VOLUMES.items())

import os.path
import subprocess as sp

def call_kppe(in_path, args=[]):
    (workdir, in_name) = os.path.split(in_path)
    workdir = os.path.abspath(workdir)
    try:
        arg_string = ' '.join(args)
        out = sp.check_output(f'docker run --rm --name {CONTAINER_NAME} -v {VOLUME_PATH} -v {workdir}:/io kimvanwyk/kppe:latest {in_name} {"".join(args)}', 
                              shell=True)
        print(out)
    except sp.CalledProcessError as e:
        print(f'Error: {e.output}')

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Run a containerised kppe instance')
    parser.add_argument('in_path', help='Path to the file to process')
    args = parser.parse_args()

call_kppe(args.in_path)
