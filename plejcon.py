try:
    import socket, os, sys, logging, time, base64, pexpect
except Exception, e:
    print('Could not import module: %s' % e)

def TestCON(host, port):
    s = socket.socket()
    try:
        log.debug(' %s: Testing port %s' % (host, port))
        s.settimeout(2)
        s.connect((host, port))
        log.debug(' %s: Port%s: Socket open' % (host, port))
        s.close()
        log.debug(' %s: Closing Socket' % host)
        return True
    except Exception, e:
        log.error(' %s: Socket "%s"' % (host, e))
        s.close()
        return False

def Creds():
    if os.path.isfile('creds.txt') == True:
        u, p = open('creds.txt', 'r').read().split(':')
        username = base64.b64decode(u)
        password = base64.b64decode(p)
        return (username, password)
    else:
        with open('creds.txt', 'w') as x:
            print('Cannot find file with creds, enter creds to make one.')
            username = raw_input('username: ')
            password = raw_input('password: ')
            x.write('%s:%s' % (base64.b64encode(username), base64.b64encode(password)))
            return (username, password)


def Main():
    try:
        host = sys.argv[1]
    except Exception, e:
        log.error(' Host argument missing  "%s"' % e)
        sys.exit()

    username, password = Creds()
    if TestCON(host, 22) == True:
        try:
            log.info(' Spawning SSH @ "%s"' % host)
            ssh = pexpect.spawn('ssh "%s"' % host)
            ssh.timeout=10000
            x = ssh.expect(['continue connecting','assword',pexpect.EOF,pexpect.TIMEOUT])
            if x == 0:
                log.info(' Auto adding SSH key for "%s"' % host)
                ssh.sendline('yes')
                x = ssh.expect(['continue connecting','assword',pexpect.EOF, pexpect.TIMEOUT])
            if x == 1:
                log.debug(' Sending password "%s"' % host)
                ssh.sendline(password)
            elif x == 2 or 3:
                print ssh.before
                log.debug(' Host probaby took to long time to respond :() "%s"' % host)
                sys.exit()
        except Exception, e:
            log.critical(' Could not complete ssh connection because "%s"' % e)
            ssh.interact()
            sys.exit()

    elif TestCON(host, 23) == True:
        try:
            log.info(' Spawning Telnet @ "%s"' % host)
            tel = pexpect.spawn('telnet "%s"' % host)
            x = tel.expect(['(?i)username', '(?i)login', pexpect.EOF, pexpect.TIMEOUT])
            if x == 0 or 1:
                tel.send(username + '\r')
                log.debug(' Sent username "%s"' % host)
                tel.expect('(?i)password', timeout=5)
                tel.send(password + '\r')
                log.debug(' Sent password "%s"' % host)
            elif x == 2:
                log.error(' Something went wrong :(')
                sys.exit()
            elif x == 3:
                log.error(' Connection timeout')
                sys.exit()
        except Exception, e:
            log.critical(' Something went wrong :( "%s"' % s)
            tel.interact()

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
    Main()
