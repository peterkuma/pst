from setuptools import setup, find_packages

setup(
	name='pst-format',
	version='1.1.1',
	packages=find_packages(),
	scripts=['pst', 'pstf'],
	description='Plain Structured Text - data format suitable for I/O & command line',
	author='Peter Kuma',
	author_email='peter.kuma@fastmail.com',
	py_modules=['pst'],
	license="Public Domain",
	url='https://github.com/peterkuma/pst',
	classifiers=[
		'Development Status :: 5 - Production/Stable',
		'Environment :: Console',
		'Operating System :: OS Independent',
		'Programming Language :: Python :: 2.7',
		'Programming Language :: Python :: 3',
		'Topic :: Text Processing :: Markup',
		'Topic :: Utilities',
	]
)
