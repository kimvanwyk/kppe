#!/usr/bin/python3
''' Execute kppe in the kimvanwyk/kppe container, voluming in the 
dir of the input file and various input dirs
'''

import os, os.path
import subprocess as sp
import sys

import docker

CONTAINER_NAME = 'kppe'
IMAGE_NAME = 'kimvanwyk/kppe:latest'

VOLUME_BASE = '/home/kimv/src/kppe/kppe_private'

VOLUMES = [(os.path.join(VOLUME_BASE, v), v) for v in ('abbreviations', 'images', 'ref_tags')]
client = docker.from_env()

def call_kppe(template, in_path, args=[], templates_dir='templates'):
    (workdir, in_name) = os.path.split(in_path)
    workdir = os.path.abspath(workdir)
    volumes = {}
    VOLUMES.append((templates_dir, 'templates'))
    for (h,c) in VOLUMES:
        volumes[h] = {'bind':f'/{c}', 'mode':'ro'}
    volumes[workdir] = {'bind':'/io', 'mode':'rw'}
    arg_string = ''
    if args:
        joined = " ".join(args)
        arg_string = f' "{joined}"'
    try:
        client.containers.run(IMAGE_NAME, command=f'{template} {in_name}{arg_string}', name=CONTAINER_NAME,
                              volumes=volumes, auto_remove=False, stdin_open=True, stream=True, tty=True)
    finally:
        cont = None
        try:
            cont = client.containers.get(CONTAINER_NAME)
        except Exception:
            cont = None
        if cont:
            cont.stop()
            cont.remove(v=False)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Run a containerised kppe instance')
    parser.add_argument('template', help='Template to use')
    parser.add_argument('in_path', help='Path to the file to process')
    parser.add_argument('--templates_dir', default='templates', help='Template directory to use')
    args = parser.parse_args()

    if not os.path.exists(args.templates_dir):
        print(f'Supplied templates dir "{args.templates_dir}" is not a valid path')
        sys.exit(1)

    call_kppe(args.template, args.in_path, templates_dir=args.templates_dir)
