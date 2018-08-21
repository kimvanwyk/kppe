''' Execute kppe in the kimvanwyk/kppe container, voluming in the 
dir of the input file and various input dirs
'''

import os, os.path
import subprocess as sp

import docker

CONTAINER_NAME = 'kppe'
IMAGE_NAME = 'kimvanwyk/kppe:latest'

VOLUME_BASE = '/home/kimv/src/kppe/kppe_private'

VOLUMES = (('abbreviations','abbreviations'),('images','images'),('ref_tags','ref_tags'),('templates','templates'))
client = docker.from_env()

def call_kppe(in_path, args=[]):
    (workdir, in_name) = os.path.split(in_path)
    workdir = os.path.abspath(workdir)
    print(workdir, in_name)
    volumes = {}
    for (h,c) in VOLUMES:
        volumes[os.path.join(VOLUME_BASE, h)] = {'bind':f'/{c}', 'mode':'ro'}
    volumes[workdir] = {'bind':'/io', 'mode':'rw'}
    arg_string = ''
    if args:
        joined = " ".join(args)
        arg_string = f' "{joined}"'
    try:
        client.containers.run(IMAGE_NAME, command=f'{in_name}{arg_string}', name=CONTAINER_NAME,
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
    parser.add_argument('in_path', help='Path to the file to process')
    args = parser.parse_args()

    call_kppe(args.in_path)
