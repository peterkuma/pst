from setuptools import setup, find_packages

setup(
	name='pst',
	version='0.1.0',
	packages=find_packages(),
	scripts=['pst'],
	description='Plain Structured Text',
	author='Peter Kuma',
	author_email='peter.kuma@fastmail.com',
	py_modules=['pst'],
	license="Public Domain",
	classifiers=[
		'Environment :: Console',
		'Operating System :: OS Independent',
		'Programming Language :: Python :: 2.7',
		'Programming Language :: Python :: 3',
		'Topic :: Text Processing :: Markup',
		'Topic :: Utilities',
	]
)
