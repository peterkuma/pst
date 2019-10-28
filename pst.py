#!/usr/bin/env python

import os
import sys

WHITESPACE = [b' ', b'\f', b'\n', b'\r', b'\t', b'\v']
WHITESPACE_ORD = [ord(x) for x in WHITESPACE]
ESCAPE = {b'a': 7, b'b': 8, b'e': 27, b'f': 12, b'n': 10, b'r': 13, b't': 9, b'v': 11}
ESCAPE_ORD = {ord(k): v for k, v in ESCAPE.items()}

def b2u(s):
	"""Convert string s to unicode."""
	if sys.version_info[0] >= 3:
		return ''.join([chr(x) for x in s])
	else:
		return u''.join([unichr(ord(x)) for x in s])

def readword(s, n, whitespace=None):
	"""Read a word from string s, starting at position n. whitespace
	is a list of whitespace characters (WHITESPACE if None). Returns a tuple
	of a word, quotation indicator string and the current position."""
	whitespace = WHITESPACE_ORD \
		if whitespace is None \
		else [ord(x) for x in whitespace]
	word = []
	q = b'' # Quotation indicator string: 1 if quoted, 0 if not quoted.
	i = n
	while i < len(s):
		if s[i] not in whitespace:
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
			if c in ESCAPE_ORD:
				word += [ESCAPE_ORD[c]]
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
		elif c in whitespace and not quote:
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
	"""Insert element x in stack."""
	if type(x) is dict:
		if stack[-1][0] in ('i', 'e'):
			stack[-1][1].update(x)
		else:
			stack[-1][1].append(x)
			stack.append(['i', x])
	else:
		if stack[-1][0] == 'a':
			stack[-1][1] += x
		elif stack[-1][0] == 'i':
			del stack[-1]
			stack[-1][1] += x

def decode(s, as_unicode=False):
	if as_unicode:
		u = lambda x: b2u(x) if type(x) is bytes else x
	else:
		u = lambda x: x
	sb = [bytearray(x) for x in s] \
		if type(s) is list \
		else bytearray(s)
	# Elements are put in stack, where the first item is the whole PST,
	# and the last item is the current element. An item is a list of two:
	# (1) 'a' (array) or 'i' (implicit object) or 'e' (explicit object) and
	# (2) the element.
	stack = [['a', []]]
	n = 0
	key = None
	while True:
		if type(sb) is list:
			if n >= len(sb):
				break
			word, q, m = readword(sb[n], 0, whitespace=[])
			n += 1
		else:
			try: word, q, m = readword(sb, n)
			except EOFError: break
			n = m
		if type(word) is bytes and word.endswith(b':') and \
			q.endswith(b'0'): # Key.
			key = word[:-1]
			x = {u(key): None}
			insert(stack, x)
			continue
		elif type(word) is bytes and word.startswith(b'--') and \
			q.startswith(b'00'): # String flag.
			key = word[2:]
			x = {u(key): True}
			insert(stack, x)
		elif type(word) is bytes and word.startswith(b'-') and \
			q.startswith(b'0'): # Single-character flag.
			for i in range(1, len(word)):
				x = {u(word[i:(i+1)]): True}
				insert(stack, x)
		elif word == b'{' and q == b'0': # Array open.
			x = []
			if key is not None:
				insert(stack, {u(key): x})
			else:
				insert(stack, [x])
			stack.append(['a', x])
		elif word == b'}' and q == b'0': # Array close.
			if len(stack) > 1 and stack[-1][0] == 'a':
				del stack[-1]
		elif word == b'{{' and q == b'00': # Explicit object open.
			x = {}
			if key is not None:
				insert(stack, {u(key): x})
			else:
				insert(stack, [x])
			stack.append(['e', x])
		elif word == b'}}' and q == b'00': # Explicit object close.
			if len(stack) > 1 and stack[-1][0] == 'e':
				del stack[-1]
		else:
			if key is not None:
				insert(stack, {u(key): u(word)})
			else:
				insert(stack, [u(word)])
		key = None
	# If PST is empty, collapse to null, if array of length 1 collapse
	# to the first value, otherwise keep the whole PST.
	if len(stack[0][1]) == 0: return None
	elif len(stack[0][1]) == 1: return stack[0][1][0]
	else: return stack[0][1]

def decode_argv(argv, **kwargs):
	if sys.version_info[0] >= 3:
		a = decode([os.fsencode(y) for y in argv], **kwargs)
	else:
		a = decode(argv, **kwargs)
	if type(a) is list:
		return [x for x in a if type(x) is not dict], \
			{k: v for x in a if type(x) is dict \
				for k, v in x.items()}
	elif type(a) is dict:
		return [], a
	elif a is None:
		return [], {}
	else:
		return [a], {}

if __name__ == '__main__':
	import json
	if sys.version_info[0] >= 3:
		args = [os.fsencode(y) for y in sys.argv[1:]]
	else:
		args = sys.argv[1:]
	print(json.dumps(decode(args, True), ensure_ascii=False))
