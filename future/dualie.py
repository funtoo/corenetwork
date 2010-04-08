#!/usr/bin/python2.6

import re

class StopCommand(object):
	def __init__(self,start_pat, stop_pat, stop_pos):
		self.start_pat = start_pat
		self.stop_pat = stop_pat
		self.stop_pos = stop_pos

	def expand(self,groups):
		mygroups = []
		for pos in self.stop_pos:
			mygroups.append(groups[pos])
		return self.stop_pat % tuple(mygroups)
		

class Application(object):

	def __init__(self,handlers):
		self.handlers = []
		self.add_handlers(handlers)
		self.negate = []

	def add_handlers(self,handlers):
		for regex, handler, stop in handlers:
			stopcmd, stoppos = stop
			if regex[-1] != "$":
				regex += "$"
			self.handlers.append((re.compile(regex),handler(regex, stopcmd, stoppos)))
	
	def process(self,lines):
		for line in lines:
			for regex, handler in self.handlers:
				match = regex.match(line)
				if match:
					self.negate = [ handler.expand(match.groups()) ] + self.negate
					break

app = Application([
	(r"brctl addbr (.*)", StopCommand, ("brctl delbr %s",[0]) ),
	(r"ip link set (.*) up", StopCommand, ("ip link set %s down",[0])),
	(r"ip route add (.*)", StopCommand, ("ip route del %s",[0])),
	(r"resolvconf -a (.*)", StopCommand, ("resolvconf -d %s",[0])),
	(r"echo 1 > (/proc/sys/net.*)", StopCommand, ("echo 0 > %s",[0])),
	(r"echo 0 > (/proc/sys/net.*)", StopCommand, ("echo 1 > %s",[0])),
	(r"iptables -N (.*)", StopCommand, ("iptables -F %s",[0])), # need to add -X
	(r"iptables -P (.*) DROP", StopCommand, ("iptables -P %s ACCEPT",[0])),
	(r"ifconfig (.*) (.*) netmask (.*) up", StopCommand, ("ifconfig %s down",[0])),
])


app.process(["hi", "ifconfig eth0 207.66.127.100 netmask 255.255.255.0 up", "ip link set eth0 up", "resolvconf -a eth0", "ip route add default foo bar", "echo 1 > /proc/sys/net/ipv4/ip_forward"])
print
for line in app.negate:
	print line
