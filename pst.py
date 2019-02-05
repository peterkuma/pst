#!/usr/bin/env python

WHITESPACE = [' ', '\f', '\n', '\r', '\t', '\v']
ESCAPE = {'a': 7, 'b': 8, 'e': 27, 'f': 12, 'n': 10, 'r': 13, 't': 9, 'v': 11}

def readword(s, n):
	word = []
	q = ''
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
				word += chr(ESCAPE[c])
				q += '1'
				escape = 0
			elif ord(c) >= ord('0') and ord(c) <= ord('9'):
				word += chr(ord(c) - ord('0'))
				q += '1'
				escape = 2
			else:
				word += c
				q += '1'
				escape = 0
		elif escape > 1:
			if ord(c) >= ord('0') and ord(c) <= ord('9'):
				x = 8*ord(word[-1]) + ord(c) - ord('0')
				if x < 256:
					word[-1] = chr(x)
				else:
					word[-1] = ''
				if escape == 3:
					escape = 0
				else:
					escape += 1
			else:
				escape = 0
		elif c == '"':
			quote = not quote
		elif c == '\\':
			escape = 1
		elif c in WHITESPACE and not quote:
			break
		else:
			word += c
			q += '1' if quote else '0'
		i += 1
	word = ''.join(word)
	if q.find('1') == -1:
		if word == 'true': return True, None, i
		if word == 'false': return False, None, i
		if word == 'none': return None, None, i
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

def decode(s):
	stack = [[]]
	n = 0
	key = None
	while True:
		try: word, q, m = readword(s, n)
		except EOFError: break
		n = m
		if type(word) is str and word.endswith(':') and q.endswith('0'):
			key = word[:-1]
			x = {key: None}
			insert(stack, x)
			continue
		elif type(word) is str and word.startswith('--') and q.startswith('00'):
			key = word[2:]
			x = {key: True}
			insert(stack, x)
		elif type(word) is str and word.startswith('-') and q.startswith('0'):
			for key in word[1:]:
				x = {key: True}
				insert(stack, x)
		elif word == '{' and q == '0':
			x = []
			if key is not None:
				insert(stack, {key: x})
			else:
				insert(stack, x)
			stack += [x]
		elif word == '}' and q == '0':
			del stack[-1]
		else:
			if key is not None:
				insert(stack, {key: word})
			else:
				insert(stack, word)
		key = None
	return stack[0]

if __name__ == '__main__':
	import sys
	import json
	x = decode(' '.join(sys.argv[1:]))
	print(json.dumps(x, ensure_ascii=False))
