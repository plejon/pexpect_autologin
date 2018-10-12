#!/usr/bin/env python3
import socket, os, sys, pexpect
from base64 import b64decode, b64encode


def testcon(host, port):
    try:
        s = socket.socket()
        s.settimeout(2)
        s.connect((host, port))
        s.close()
        return True
    except:
        return False


def creds():
    home = os.getenv('HOME')
    if os.path.isfile(f'{home}/creds.txt'):
        with open(f'{home}/creds.txt', 'r') as c:
            u, p = c.read().split(':')
            return b64decode(u), b64decode(p)
    else:
        print('write un/pw for storage in ~/creds.txt')
        u = input('username: ')
        p = input('password: ')
        with open(f'{home}/creds.txt', 'w') as c:
            c.write(f'{b64encode(u)}:{b64encode(p)}')
            return u, p


def login(h, s, p, un, pw):
    ex = ['continue connecting', '(?i)username',
          '(?i)login:', '(?i)password', 'diffie-hellman',
          pexpect.EOF, pexpect.TIMEOUT, 'denied']

    try:
        conn = pexpect.spawn(f'{s} {h}')
        conn.timeout=10000
        x = conn.expect(ex)
        if x is 0:
            conn.sendline('yes')
        elif x is 3 and p is 22:
            conn.sendline(pw)
            conn.interact()
            sys.exit()
        elif x is 1 or 2:
            conn.send(f'{un}\r')
        elif x == 4 or 5 or 6 or 7:
            print(f'failed connection to "{h}"')
            sys.exit()
        x = conn.expect(ex)
        if x == 3:
            conn.send(f'{pw}\r')
        elif x == 4 or 5 or 6 or 7:
            print(f'failed connection to {h}')
            sys.exit()
        conn.interact()
        sys.exit()
    except Exception as e:
        print(' Could not complete login-phase "%s"' % e)
        sys.exit()


def main():
    try:
        h = sys.argv[1]
    except IndexError:
        print('Execute with: script + <hostname>')
        sys.exit()
    un, pw = creds()
    if testcon(h, 22):
        login(h, 'ssh', 22, un, pw)
    elif testcon(h, 23):
        login(h, 'telnet', 23, un, pw)
    else:
        print(f'telnet/ssh not possible to {h}')
        sys.exit()


if __name__ == '__main__':
    main()
