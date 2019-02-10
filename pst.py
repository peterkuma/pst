#!/usr/bin/env python

import sys

WHITESPACE_B = [b' ', b'\f', b'\n', b'\r', b'\t', b'\v']
WHITESPACE = [ord(x) for x in WHITESPACE_B]
ESCAPE = {b'a': 7, b'b': 8, b'e': 27, b'f': 12, b'n': 10, b'r': 13, b't': 9, b'v': 11}

def b2u(s):
	if sys.version_info[0] >= 3:
		return ''.join([chr(x) for x in s])
	else:
		return u''.join([unichr(ord(x)) for x in s])

def readword(s, n):
	word = []
	q = b''
	i = n
	while i < len(s):
		if s[i] not in WHITESPACE:
			break
		i += 1
	if i == len(s):
		raise EOFError()
	escape = 0
	eos = False
	quote = False
	while i < len(s) and not eos:
		c = s[i]
		if escape == 1:
			if c in ESCAPE:
				word += [ESCAPE[c]]
				q += b'1'
				escape = 0
			elif c >= ord(b'0') and c <= ord(b'9'):
				word += [c - ord(b'0')]
				q += b'1'
				escape = 2
			else:
				word += [c]
				q += b'1'
				escape = 0
		elif escape > 1:
			if c >= ord(b'0') and c <= ord(b'9'):
				x = 8*word[-1] + c - ord(b'0')
				if x < 256:
					word[-1] = x
				else:
					del word[-1]
				if escape == 3:
					escape = 0
				else:
					escape += 1
			else:
				escape = 0
		elif c == ord(b'"'):
			quote = not quote
		elif c == ord(b'\\'):
			escape = 1
		elif c in WHITESPACE and not quote:
			break
		else:
			word += [c]
			q += b'1' if quote else b'0'
		i += 1
	if sys.version_info[0] >= 3:
		word = bytes(word)
	else:
		word = b''.join([chr(x) for x in word])
	if q.find(b'1') == -1:
		if word == b'true': return True, None, i
		if word == b'false': return False, None, i
		if word == b'none': return None, None, i
		try: return int(word), None, i
		except: pass
		try: return float(word), None, i
		except: pass
	return word, q, i

def insert(stack, x):
	if type(x) is dict and len(stack[-1]) > 0 and type(stack[-1][-1]) is dict:
		stack[-1][-1].update(x)
	else:
		stack[-1] += [x]

def decode(s, as_unicode=False):
	if as_unicode:
		u = lambda s: b2u(s) if type(s) is bytes else s
	else:
		u = lambda s: s
	s1 = bytearray(s)
	stack = [[]]
	n = 0
	key = None
	while True:
		try: word, q, m = readword(s1, n)
		except EOFError: break
		n = m
		if type(word) is bytes and word.endswith(b':') and q.endswith(b'0'):
			key = word[:-1]
			x = {u(key): None}
			insert(stack, x)
			continue
		elif type(word) is bytes and word.startswith(b'--') and q.startswith(b'00'):
			key = word[2:]
			x = {u(key): True}
			insert(stack, x)
		elif type(word) is bytes and word.startswith(b'-') and q.startswith(b'0'):
			for i in range(1, len(word)):
				x = {u(word[i:(i+1)]): True}
				insert(stack, x)
		elif word == b'{' and q == b'0':
			x = []
			if key is not None:
				insert(stack, {u(key): x})
			else:
				insert(stack, x)
			stack += [x]
		elif word == b'}' and q == b'0':
			del stack[-1]
		else:
			if key is not None:
				insert(stack, {u(key): u(word)})
			else:
				insert(stack, u(word))
		key = None
	return stack[0]

if __name__ == '__main__':
	import json
	if sys.version_info[0] >= 3:
		import os
		s = b' '.join([os.fsencode(y) for y in sys.argv[1:]])
	else:
		s = b' '.join(sys.argv[1:])
	print(json.dumps(decode(s, True), ensure_ascii=False))
