#!/usr/bin/env python
try:
    import socket, os, sys, logging, base64, pexpect, getpass, socket
except Exception, e:
    print(e)

def TestCON(host, port):
    s = socket.socket()
    try:
        s.settimeout(2)
        s.connect((host, port))
        s.close()
        return True
    except Exception, e:
        s.close()
        return False

def Creds():
    home = os.getenv('HOME')
    if os.path.isfile('%s/creds.txt' % home) == True:
        u, p = open('%s/creds.txt' % home, 'r').read().split(':')
        username = base64.b64decode(u)
        password = base64.b64decode(p)
        return (username, password)
    else:
        with open('%s/creds.txt' % home, 'w') as x:
            print('Cannot find file with creds, enter creds to make one.')
            username = raw_input('username: ')
            password = getpass.getpass('password: ')
            x.write('%s:%s' % (base64.b64encode(username), base64.b64encode(password)))
            log.info(' username: %s + password stored in "creds.txt"' % username)
            return (username, password)

def exec_login(host, service, port, username, password):
    ex = ['continue connecting', '(?i)username', '(?i)login:',
          '(?i)password', 'diffie-hellman', pexpect.EOF, pexpect.TIMEOUT, 'denied']
    try:
        ptr = socket.gethostbyaddr(host)
        try:
            arec = socket.getfqdn(host)
        except:
            pass
        log.info(' Connecting...')
        if 'arec' in locals():
            log.info(' HOST: %s' % arec)
        log.info(' IP:   %s' % ptr[2][0])
        log.info(' PTR:  %s' % ptr[0])
    except:
        log.info('Connecting to %s' % host)
    try:
        conn = pexpect.spawn('%s %s' % (service, host))
        conn.timeout=10000
        x = conn.expect(ex)
        if x == 0:
            log.info(' Auto adding SSH key for "%s"' % host)
            conn.sendline('yes')
        elif x == 3 and port == 22:
            conn.sendline(password)
            conn.interact()
            sys.exit()
        elif x == 1 or 2:
            conn.send(username + '\r')
        elif x == 4 or 5 or 6 or 7:
            log.error(' EoF, timeout or bad sshcrypto @ "%s"' % host)
            sys.exit()
        x = conn.expect(ex)
        if x == 3:
            conn.send(password + '\r')
        elif x == 4 or 5 or 6 or 7:
            log.error(' EoF/timeout/denied @ "%s"' % host)
            sys.exit()
        conn.interact()
        sys.exit()
    except Exception, e:
        log.critical(' Could not complete login-phase "%s"' % e)
        sys.exit()

def Main():
    try:
        host = sys.argv[1]
    except Exception, e:
        log.error(' %s. Execute with: script + <hostname>' % e)
        sys.exit()

    username, password = Creds()
    if TestCON(host, 22) == True:
        exec_login(host, 'ssh', 22, username, password)
    elif TestCON(host, 23) == True:
        exec_login(host, 'telnet', 23, username, password)
    else:
        log.error(' telnet/ssh not possible: %s' % host)

if __name__ == '__main__':
    log = logging.getLogger('plejCON')
    logging.basicConfig(level=20)
    Main()
