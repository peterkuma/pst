#!/usr/bin/env python3

import pst
import sys
import os
import json

def main():
	args = [os.fsencode(y) for y in sys.argv[1:]]
	s = json.dumps(pst.decode(args, True), ensure_ascii=False)
	sys.stdout.buffer.write(s.encode('utf-8', 'surrogateescape') + b'\n')

if __name__ == '__main__':
	main()
