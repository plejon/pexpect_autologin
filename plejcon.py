#!usr/bin/python
try:
    import pexpect
except:
    print('module "pexpect" not found.')
    import sys
    sys.exit()

import socket, os, sys, logging, time

def TryDiz(host):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        testssh = sock.connect_ex((host, 22))
        testtel = sock.connect_ex((host, 23))
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
        log.error(' Connection failed @ %s' % host)
        sys.exit()

def main():
    if os.path.isfile('creds.txt') == True:
        username, password = open('creds.txt', 'r').read().split(':')
    else:
        with open('creds.txt', 'w') as x:
            print('Cannot find file with creds, enter creds to make on.')
            username = raw_input('username: ')
            password = raw_input('password: ')
            x.write('%s:%s' % (username, password))

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
        x = tel.expect(['(?i)username', '(?i)login'])
        if x == 1 or 2:
            log.debug(' Sending username "%s"' % host)
            tel.sendline(username)
        tel.expect('(?i)password')
        log.debug(' Sending password "%s"' % host)
        tel.sendline(password)
        
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
    logging.basicConfig(level=20)
    main()