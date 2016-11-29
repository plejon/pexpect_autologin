#!usr/bin/python
try:
    import pexpect
except:
    print('module "pexpect" not found.')
    import sys
    sys.exit()

import socket, os, sys, logging, time, base64

def TryDiz(host):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        testssh = sock.connect_ex((host, 22))
        log.debug(' ssh socket return: %s' % testssh)
        testtel = sock.connect_ex((host, 23))
        log.debug(' telnet socket return: %s' % testtel)
        if testssh == 0:
            log.debug(' SSH open @ %s' % host)
            return True
        elif testtel == 0 or 106:
            log.debug(' Telnet open @ %s' % host)
            return False
        else:
            log.warning(' Could not verify if ssh/telnet service was open on "%s"' % host)
            sys.exit()
    except:
        log.error(' Connection timeout @ %s' % host)
        sys.exit()

def main():
    if os.path.isfile('creds.txt') == True:
        u, p = open('creds.txt', 'r').read().split(':')
        username = base64.b64decode(u)
        password = base64.b64decode(p)

    else:
        with open('creds.txt', 'w') as x:
            print('Cannot find file with creds, enter creds to make on.')
            username = raw_input('username: ')
            password = raw_input('password: ')
            x.write('%s:%s' % (base64.b64encode(username), base64.b64encode(password)))

    host = sys.argv[1]
    x = TryDiz(host)
    if x == True:
        log.info(' Spawning SSH @ "%s"' % host)
        ssh = pexpect.spawn('ssh "%s"' % host)
        x = ssh.expect(['continue connecting','assword',pexpect.EOF,pexpect.TIMEOUT],1)
        if x == 0:
            log.info(' Auto adding SSH key for "%s"' % host)
            ssh.sendline('yes')
            x = ssh.expect(['continue connecting','assword',pexpect.EOF])
        if x == 1:
            time.sleep(1)
            log.debug(' Sending password "%s"' % host)
            ssh.sendline(password)
        elif x == 2:
            print ssh.before
            sys.exit()
        elif x == 3:
            pass

    elif x == False:
        log.info(' Spawning Telnet @ "%s"' % host)
        tel = pexpect.spawn('telnet "%s"' % host)
        x = tel.expect(['(?i)username', '(?i)login', pexpect.EOF])
        try:
            if x == 0 or 1:
                tel.send(username + '\r')
                log.debug(' Sent username "%s"' % host)
                tel.expect('(?i)password', timeout=5)
                tel.send(password + '\r')
                log.debug(' Sent password "%s"' % host)

        except:
            log.error(' could probalby not send password. Hit return and enter pass')
            tel.interact()
            
    else:
        log.warning(' Telnet/SSH could not connect to "%s"' % host)
        sys.exit()

    try:
        if 'ssh' in locals():
            log.debug(' Trying to enable user interaction "%s"' % host)
            ssh.interact()
            sys.exit()

        elif 'tel' in locals():
            log.debug(' Trying to enable user interaction "%s"' % host)
            tel.interact()
            sys.exit()

    except Exception, e:
        log.error('{} "{}"'.format(str(e), str(host)))
        sys.exit()

if __name__ == '__main__':
    log = logging.getLogger('plejCON')
    logging.basicConfig(level=10)
    main()