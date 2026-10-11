#!/usr/bin/env python3
"""Isolated QEMU HMP controller: no host command execution and no shell interpolation."""
import argparse
import os
import socket
import time
from pathlib import Path

KEYS = {' ': 'spc', '/': 'slash', '.': 'dot', '-': 'minus', '=': 'equal', ':': 'shift-semicolon', '_': 'shift-minus'}

def connect(path):
    s = socket.socket(socket.AF_UNIX)
    s.settimeout(4)
    s.connect(path)
    try:
        s.recv(4096)
    except socket.timeout:
        pass
    return s

def send(s, value):
    s.sendall((value + '\n').encode())
    time.sleep(.13)
    try:
        s.recv(8192)
    except socket.timeout:
        pass

def type_line(s, cmd):
    for ch in cmd:
        if ch.isalnum() and ch.isascii():
            send(s, 'sendkey ' + ch.lower())
        elif ch in KEYS:
            send(s, 'sendkey ' + KEYS[ch])
        else:
            raise ValueError('Unsupported keyboard character: ' + repr(ch))
    send(s, 'sendkey ret')

def main():
    a = argparse.ArgumentParser()
    a.add_argument('socket')
    a.add_argument('action', choices=['begin-install', 'framebuffer'])
    a.add_argument('--image')
    args = a.parse_args()
    with connect(args.socket) as s:
        if args.action == 'begin-install':
            send(s, 'sendkey ctrl-alt-f3')
            time.sleep(4)
            type_line(s, 'root')
            time.sleep(4)
            type_line(s, 'mount /dev/vda /mnt')
            time.sleep(3)
            type_line(s, 'bash /mnt/install-guest.sh')
            print('GUEST_INSTALL_SCRIPT_STARTED')
        else:
            target = Path(args.image).absolute()
            if not args.image or not target.parent.is_dir():
                raise ValueError('Missing screenshot destination')
            send(s, 'screendump ' + str(target))
            print('QEMU_FRAMEBUFFER_CAPTURED', target)

if __name__ == '__main__':
    main()