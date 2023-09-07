#!/usr/bin/env python3

__version__ = '2.0.0'

import os
import sys

WHITESPACE = [b' ', b'\f', b'\n', b'\r', b'\t', b'\v']
WHITESPACE_ORD = [ord(x) for x in WHITESPACE]
ESCAPE = {b'a': 7, b'b': 8, b'e': 27, b'f': 12, b'n': 10, b'r': 13, b't': 9, b'v': 11}
ESCAPE_ORD = {ord(k): v for k, v in ESCAPE.items()}
ESCAPE2 = {v: k for k, v in ESCAPE.items()}
RESERVED = [b'{', b'}', b'{{', b'}}', b'true', b'false', b'none']
DIGITS = [b'0', b'1', b'2', b'3', b'4', b'5', b'6', b'7', b'8', b'9']
DIGITS_ORD = [ord(x) for x in DIGITS]

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
	if i == len(s) and whitespace != []:
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
	word = bytes(word)
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
		u = lambda x: x.decode('utf-8', 'surrogateescape') \
			if type(x) is bytes else x
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
			if len(stack) > 1 and stack[-1][0] == 'i':
				del stack[-1]
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

def decode_argv(argv, delim=True, as_unicode=False, **kwargs):
	argvb = [os.fsencode(x) for x in argv]
	args = []
	argvb1 = argvb
	if delim:
		try:
			i = argvb.index(b'--')
			argvb1 = argvb[:i]
			args = argv[(i+1):] if as_unicode else argvb[(i+1):]
		except ValueError: pass
	a = decode(argvb1, as_unicode=as_unicode, **kwargs)
	if len(argvb1) == 0:
		return args, {}
	elif type(a) is list:
		return [x for x in a if type(x) is not dict] + args, \
			{k: v for x in a if type(x) is dict \
				for k, v in x.items()}
	elif type(a) is dict:
		return args, a
	else:
		return [a] + args, {}

def encode_str(x, escape=False):
	if type(x) is not bytes:
		x = str(x).encode('utf-8', 'surrogateescape')
	s = []
	special = [ord(b'"')] + WHITESPACE_ORD
	quote = False
	if len(x) == 0 or \
	   x in RESERVED or \
	   x.endswith(b':') or \
	   x.startswith(b'-') or (
		   len(x) > 0 and \
		   x[0] != ord(b'.') and \
		   all(c in DIGITS_ORD or c == ord(b'.') for c in x) and \
		   sum(c == ord(b'.') for c in x) <= 1
	   ):
		quote = True
	for c in bytearray(x):
		if c in special:
			quote = True
		if c in [ord(b'"'), ord(b'\\')]:
			s += [ord(b'\\')] + [c]
		elif escape and c in ESCAPE2:
			s += [ord(b'\\'), ord(ESCAPE2[c])]
		elif escape and not (c >= 32 and c <= 126): # Is not printable.
			s += b'\\%03o' % c
		else:
			s += [c]
	s = bytes(s)
	return b'"%s"' % s if quote else s

def encode(x, encoder=None, indent=False, indent_len='tab', flags=False,
	short_flags=False, long_flags=False, escape=False,
	explicit=False, first=True, cur_indent=0):
	opts = {
		'encoder': encoder,
		'indent': indent,
		'indent_len': indent_len,
		'flags': flags,
		'short_flags': short_flags,
		'long_flags': long_flags,
		'escape': escape,
	}
	encoder = (lambda y: y) if encoder is None else encoder
	x = encoder(x)
	def indent_for(n):
		if indent_len == 'tab':
			return [b'\t']*n
		else:
			return [b' ']*(indent_len*n)
	s = []
	if type(x) is dict:
		if len(x) == 0:
			s += [b'{{', b'}}']
			if indent: s += [b'\n']
		else:
			if explicit:
				s += [b'{{']
				if indent: s += [b'\n']
				new_indent = (cur_indent + 1)
			else:
				new_indent = cur_indent
			sf = False
			for k, v in x.items():
				v = encoder(v)
				k_s = encode_str(k, escape)
				v_s = encode(v, explicit=True, first=False,
					cur_indent=new_indent,
					**opts)
				if short_flags or flags and \
				   len(k_s) == 1 and v == True:
					if not sf:
						s += [b'-' + k_s]
					else:
						s[-1] += k_s
					sf = True
				elif (long_flags or flags) and \
				   v == True:
					s += [b'--' + k_s]
					sf = False
				else:
					if indent:
						s += indent_for(new_indent)
					s += [k_s + b':'] + v_s
					if indent and explicit: s += [b'\n']
					sf = False
			if explicit:
				if indent:
					s += indent_for(cur_indent)
				s += [b'}}']
				if indent: s += [b'\n']
	elif type(x) in (list, tuple):
		if len(x) == 0:
			s += [b'{', b'}']
		else:
			if explicit:
				s += [b'{']
			y_prev = None
			y_next = None
			for i, y in enumerate(x):
				y_prev = x[i - 1] if i > 0 else None
				y_next = x[i + 1] if i + 1 < len(x) else None
				y = encoder(y)
				y_prev = encoder(y_prev)
				y_next = encoder(y_next)
				exp = type(y) in (list, tuple) or \
				      type(y) is dict and \
				      (type(y_prev) is dict or type(y_next) is dict)
				s += encode(y, explicit=exp, first=False,
					cur_indent=cur_indent, **opts)
			if explicit:
				s += [b'}']
	elif type(x) is bool:
		s += [b'true' if x else b'false']
	elif type(x) is int:
		s += [b'%d' % x]
	elif type(x) is float:
		s += [b'%f' % x]
	elif type(x) in (bytes, str):
		s += [b'%s' % encode_str(x, escape)]
	elif x is None:
		s += [b'none']
	else:
		raise ValueError('Unsupported type "%s"' % type(x))
	if first and s == [b'none']:
		s = []
	if not first:
		return s
	out = b''
	for i, word in enumerate(s):
		word_next = s[i + 1] if i + 1 < len(s) else None
		out += word \
			if word in (b'\n', b' ', b'\t') or \
			word_next in (b'\n', b' ', b'\t') \
			else word + b' '
	return out.strip()

if __name__ == '__main__':
	import json
	args = [os.fsencode(y) for y in sys.argv[1:]]
	s = json.dumps(pst.decode(args, True), ensure_ascii=False)
	sys.stdout.buffer.write(s.encode('utf-8', 'surrogateescape') + b'\n')
