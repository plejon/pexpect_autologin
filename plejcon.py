import socket, os, sys, logging, time, base64, pexpect, getpass

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
	if os.path.isfile('creds.txt') == True:
		u, p = open('creds.txt', 'r').read().split(':')
		username = base64.b64decode(u)
		password = base64.b64decode(p)
		return (username, password)
	else:
		with open('creds.txt', 'w') as x:
			print('Cannot find file with creds, enter creds to make one.')
			username = raw_input('username: ')
			password = getpass.getpass('password: ')
			x.write('%s:%s' % (base64.b64encode(username), base64.b64encode(password)))
			log.info(' username: %s + password stored in "creds.txt"' % username)
			return (username, password)

def exec_login(host, service, port, username, password):
	ex = ['continue connecting', '(?i)username', '(?i)login:', '(?i)password', 'diffie-hellman', pexpect.EOF, pexpect.TIMEOUT]
	try:
		log.info(' Connecting to "%s"' % host)
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
		elif x == 4 or 5 or 6:
			log.error(' EoF, timeout or bad sshcrypto @ "%s"' % host)
			sys.exit()
		x = conn.expect(ex)
		if x == 3:
			conn.send(password + '\r')
		elif x == 4 or 5 or 6:
			log.error(' EoF or timeout "%s"' % host)
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
		log.error(' Host argument missing  "%s"' % e)
		sys.exit()
		
	username, password = Creds()
	if TestCON(host, 22) == True:
		exec_login(host, 'ssh', 22, username, password)
	elif TestCON(host, 23) == True:
		exec_login(host, 'telnet', 23, username, password)
	else:
		log.error(' Telnet or SSH not possible')
		sys.exit()

if __name__ == '__main__':
	log = logging.getLogger('plejCON')
	logging.basicConfig(level=10)
	Main()