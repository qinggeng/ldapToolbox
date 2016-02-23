#-*- coding: utf-8 -*-
from functools import wraps
def conn_required(func):
	@wraps(func)
	def func_wrapper(self, *args, **kwagrs):
		if self.connected == False:
			self.connect()
		if self.connected == False:
			self.error('method needs connected to server')
		return func(self, *args, **kwagrs)
	return func_wrapper

def bind_required(func):
	@wrap(func)
	def func_wrapper(self, *args, **kwagrs):
		if self.binding == False:
			self.bind()
		if self.binding == False:
			self.error('method failed to bind on a DN')
		return func(self, *args, **kwagrs)
	return func_wrapper

#def test_deco(func):
#	def func_wrapper(self, *args, **kwargs):
#		print 'wrapper worked'
#		return func(self, *args, **kwargs)
#	print 'wrapped'
#	return func_wrapper
#
#if __name__ == '__main__':
#	class Stub:
#		def __init__(self):
#			print 'stub init'
#		
#		@test_deco
#		def foo(self, bar):
#			print 'func worked', bar
#	
#	st = Stub()
#	st.foo(None)
#	pass
