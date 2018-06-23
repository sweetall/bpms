#!/usr/bin/env python3
# coding: utf-8

import sys
import subprocess


def start_redis():
    print("start redis")
    subprocess.call('redis-server &', shell=True)


def start_portal():
    print("start portal")
    subprocess.call('uwsgi --ini /mnt/code/portal/etc/uwsgi/uwsgi.ini', shell=True)


def start_nginx():
    print("start nginx")
    subprocess.call('/usr/local/nginx/sbin/nginx', shell=True)


def first_start_prepare():
    start_redis()
    start_portal()
    start_nginx()


if __name__ == '__main__':
    first_start_prepare()
