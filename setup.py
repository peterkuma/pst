from setuptools import setup, find_packages

setup(
	name='pst-format',
	version='2.0.0',
	packages=find_packages(),
	scripts=['pst', 'pstf'],
	description='Plain Structured Text (PST)',
	author='Peter Kuma',
	author_email='peter@peterkuma.net',
	py_modules=['pst'],
	license="Public Domain",
	url='https://github.com/peterkuma/pst',
	classifiers=[
		'Development Status :: 5 - Production/Stable',
		'Environment :: Console',
		'Operating System :: OS Independent',
		'Programming Language :: Python :: 3',
		'Topic :: Text Processing :: Markup',
		'Topic :: Utilities',
	]
)
