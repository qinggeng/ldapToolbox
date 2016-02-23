#-*- coding: utf-8 -*-
u"""LDAP客户端工具"""
import ldap as l
import ldap.modlist as modlist
from decorators import *
from tempfile import NamedTemporaryFile
import os
class Client:
	u"""LDAP客户端"""
	def __init__(self, **kwargs):
		u"""参数支持的关键字：
	bind: 绑定的dn
	password：密码
	server：服务器地址，可以是域名或者ip地址
	port：端口，默认389
	"""
		self.bindDN = kwargs.pop('bind', '')
		self.password = kwargs.pop('password', '')
		self.server = kwargs.pop('server', '')
		self.port = kwargs.pop('port', 389)
		self.connected = False

	def connect(self):
		u"""create a ldap connection"""
		c = l.open(self.server, port = self.port)
		c.set_option(l.OPT_NETWORK_TIMEOUT, 10)
		self.connection = c 
		self.connected = True
		return self.connected

	def error(self, msg):
		print msg

	@conn_required
	def bind(self, bindDN = None, password = None):
		u"""bind to a DN"""
		if bindDN == None:
			bindDN = self.bindDN
		else:
			self.bindDN = bindDN
		if password == None:
			password = self.password
		else:
			self.password = password
		c = self.connection
		try:
			self.binding = c.simple_bind_s(bindDN, password)
			return True
		except Exception, e:
			return False

	@conn_required
	def search(self, base, scope, filterstr = u'(objectClass=*)', attrlist = None, attrsonly = 0):
		u"""a wrapper of ldap.search"""
		c = self.connection
		return c.search_s(base, scope, filterstr, attrlist, attrsonly)

	def mkldifstr(self, attrs):
		dn = attrs.pop('dn')
		ldifStr = u'dn: %s\n' % (dn,)
		for attr in attrs:
			val = attrs[attr]
			if type(val) == list:
				for v in val:
					ldifStr += u'{k}: {v}\n'.format(k = attr, v = v)
			else:
				ldifStr +=  u'{k}: {v}\n'.format(k = attr, v = val)
		return ldifStr

	@conn_required
	def add(self, dn, attrs):
		attrs['dn'] = dn
		ldifStr = self.mkldifstr(attrs)
		with NamedTemporaryFile() as tf:
			tf.write(ldifStr)
			tf.flush()
			cmdStr = \
					u'ldapadd -h "{host}" -p {port} -x -w "{password}" -D "{dn}" -f "{ldif}"'.format(
							dn = self.bindDN, 
							password = self.password,
							ldif = tf.name,
							host = self.server,
							port = self.port)
			os.system('cat "%s"' % (tf.name, ))
			os.system(cmdStr)
			return cmdStr

	@conn_required
	def delete(self, dn):
		c = self.connection
		return c.delete_s(dn)

#	def treelizeEntries(self, entries):
#		for entry in entries:
#			dn, attrs = entry
#			rdns = dn.split(',')
#			print rdns, attrs


if __name__ == '__main__':
	from testSettings import settings
	from pprint import pprint
	client = Client(
			bind = settings['rootDN']['dn'], 
			password = settings['rootDN']['password'], 
			server = settings['server'])
	client.bind()
	#ret = client.search(settings['searchBase'], l.SCOPE_ONELEVEL)
	ret = client.search(settings['searchBase'], l.SCOPE_SUBTREE)
	pprint(ret)
	from testSettings import entryToAdd
	dn = entryToAdd['dn']
	attrs = entryToAdd['attrs']
	print 'will add'
	ret = client.search(settings['searchBase'], l.SCOPE_SUBTREE)
	pprint(ret)
	print client.add(dn, attrs)
	print 'added'
	ret = client.search(settings['searchBase'], l.SCOPE_SUBTREE)
	pprint(ret)
	print client.delete(dn)
	print 'delete'
	ret = client.search(settings['searchBase'], l.SCOPE_SUBTREE)
	pprint(ret)
