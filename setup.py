from setuptools import setup, find_packages

setup(
	name='pst-format',
	version='2.1.0',
	packages=['pst', 'pst.bin'],
	entry_points={
		'console_scripts': [
			'pst = pst.bin.pst:main',
			'pstf = pst.bin.pstf:main',
		],
	},
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
