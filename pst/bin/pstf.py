#!/usr/bin/env python3

import pst
import sys
import json

def main():
	if sys.version_info[0] >= 3:
		s = sys.stdin.buffer.read()
	else:
		s = sys.stdin.read()

	print(json.dumps(pst.decode(s, True), ensure_ascii=False))

if __name__ == '__main__':
	main()
