Plain Structured Text (PST)
===========================

PST is a format for encoding structured text similar to Bourne shell formatting
and JSON. PST supports strings, numbers (integers and floating-point), bool,
missing values (`none`), arrays, objects (key-value pairs),
single-character flags (`-x`), and string flags (`--abc`).
Relative to JSON, PST is simpler, while supporting much of its features.
PST aims to be human and machine readable, and suitable for command-line
argument formatting, standard input/output and configuration file
formatting. PST is similar to YAML, but supporting one-line expressions
(indentation does not matter).

Implementations of PST as a command-line program and a Python 3 function
are available.

Complex example
---------------

This example is adapted from Wikipedia and is licensed under the
[CC BY-SA 3.0](https://en.wikipedia.org/wiki/Wikipedia:Text_of_Creative_Commons_Attribution-ShareAlike_3.0_Unported_License)
license.

PST:

```
firstName: John
lastName: Smith
isAlive: true
age: 27
address: {{
	streetAddress: "21 2nd Street"
	city: "New York"
	state: NY
	postalCode: 10021-3100
}}
phoneNumbers: {
	{{ type: home number: "212 555-1234" }}
	{{ type: office number: "646 555-4567" }}
	{{ type: mobile number: "123 456-7890" }}
}
children: { }
spouse: none
```

JSON:

```json
{
  "firstName": "John",
  "lastName": "Smith",
  "isAlive": true,
  "age": 27,
  "address": {
    "streetAddress": "21 2nd Street",
    "city": "New York",
    "state": "NY",
    "postalCode": "10021-3100"
  },
  "phoneNumbers": [
    {
      "type": "home",
      "number": "212 555-1234"
    },
    {
      "type": "office",
      "number": "646 555-4567"
    },
    {
      "type": "mobile",
      "number": "123 456-7890"
    }
  ],
  "children": [],
  "spouse": null
}
```

The same PST could be supplied as command-line arguments (albeit very long):

```sh
pst firstName: John lastName: Smith isAlive: true age: 27 address: {{ \
streetAddress: "21 2nd Street" city: "New York" state: NY postalCode: \
10021-3100 }} phoneNumbers: { {{ type: home number: "212 555-1234" }} \
{{ type: office number: "646 555-4567" }} {{ type: mobile number: \
"123 456-7890" }} } children: { } spouse: none
```

would output the following JSON:

```json
{"children": [], "phoneNumbers": [{"number": "212 555-1234", "type": "home"}, {"number": "646 555-4567", "type": "office"}, {"number": "123 456-7890", "type": "mobile"}], "firstName": "John", "isAlive": true, "spouse": null, "age": 27, "lastName": "Smith", "address": {"state": "NY", "streetAddress": "21 2nd Street", "city": "New York", "postalCode": "10021-3100"}}
```

Informal description
--------------------

PST is composed of a sequence of words, which encode elementary types
such as strings, integers, floating-point numbers or arbitrarily nested complex
types such as arrays (list) and objects (dict).

Strings do not need to be
quoted unless they contain white space, special characters which could be
interpreted as a number or bracket. Words composed of digits are implicitly
converted to numbers unless quoted.

Curly brackets enclose arrays. Double curly brackets enclose explicit objects.
Objects are composed of key-value pairs, which can be located inline
(implicit objects) or inside double curly brackets (explicit objects).
Unlike implicit objects, it is possible to use explicit objects as the value of
a key-value pair. Flags beginning with a dash and double dash are converted
to key-value pairs.

Any amount of white space or indentation is equivalent to a single space.
Separation between words, brackets, special characters such as `:` in the key of
a key-value pair matters.

8-bit ASCII-compatible character encoding is assumed. Strings can contain any
binary data by using escape characters. Conversion from UTF-8 character
encoding to Unicode is supported by the Python PST API.

PST is designed to be compatible with JSON, while also being suitable for
command-line argument passing. For example, special characters which would
clash with other uses are not used: `(`, `)` have special interpretation
in Bash, `[`, `]` are commonly used in documentation of command-line programs
to denote optional arguments. Implicit objects make it easy to denote named
command-line arguments. Flags ensure established syntax can be used to express
command-line arguments. Arrays and objects enable complex
command-line arguments. No need for quoting common strings and no commas make
it easier to write PST than JSON.

Examples
--------

```
# Empty
PST:
JSON: null

# Single string
PST: a
JSON: ["a"]

# Quoted string
PST: "a b"
JSON: "a b"

# Partially-quoted string
PST: a"b c"
JSON: "ab c"

# Two strings
PST: a b
JSON: ["a", "b"]

# Two strings separated by a newline
PST:
a
b
JSON: ["a", "b"]

# Key-value pair
PST: a: 1
JSON: {"a": 1}

# Sequence of key-value pairs
PST: a: 1 b: 2
JSON: {"a": 1, "b": 2}

# Sequence of key-value pairs and a string
PST: a: 1 b: 2 c
JSON: [{"a": 1, "b": 2}, "c"]

# Empty array
PST: { }
JSON: []

# String and an empty array
PST: a { }
JSON: ["a", []]

# Empty object
PST: {{ }}
JSON: {}

# String and an empty object
PST: a {{ }}
JSON: ["a", {}]

# String and an array
PST: a { b c }
JSON: ["a", ["b", "c"]]

# An array as value followed by a string
PST: a: { b c } d
JSON: [{"a": ["b", "c"]}, "d"]

# Literals
PST: true false none
JSON: [true, false, null]

# Single-character flags
PST: -ab
JSON {"a": true, "b": true}

# String flag
PST: --ab
JSON: {"ab": true}
```

Usage
-----

### Command line

#### pst

```sh
pst <pst>...
```

Convert PST-formatted arguments to JSON. Prints JSON to the standard output.

#### pstf

```
pstf < input.pst
```

Convert PST-formatted standard input to JSON. Prints JSON to the standard
output.

### Python

```python
import pst
```

#### decode

```python
pst.decode(s, as_unicode=False)
```

Decode PST. `s` is PST (binary string) or a list of PST. If `as_unicode` (bool)
is `True`, convert strings to Unicode on output by assuming the UTF-8 encoding.
Invalid UTF-8 bytes are encoded using the "surrogateescape" encoding in the
U+DCxx Unicode range.

#### decode_argv

```python
pst.decode_argv(argv, delim=True, **kwargs)
```

Decode PST and split the resulting list into positional and named arguments.
`argv` is a list such as `sys.argv` and `kwargs` are keyword arguments passed
to `pst.decode`. Returns a tuple (`args`, `opts`), where `args` are positional
arguments and `opts` are named arguments. If `delim` is True, interpret a
standalone double-dash argument (`--`) in `argv` as an end of options delimiter,
after which all arguments are treated as literal string arguments.

#### encode

```python
pst.encode(x, encoder=None, indent=False, indent_len='tab', flags=False, short_flags=False, long_flags=False, escape=False)
```

Encode Python structure `x` consisting of list, tuple, dict, byte, str, int and
float as PST (either as scalars or nested). Returns bytes. `encoder` is a
user-defined function to transform individual elements of the structure to one
of the above types before they are read by the encoder. If `indent` is true,
output indentation is applied. `indent_len` is the number of space characters
used for indentation or `tab` for indentation with the tab character. If
`flags` is true, key-value pairs with a value of true are encoded as flags. If
`short_flags` is true, key-value pairs with a value of true and
single-character key are encoded as single-character flags. If `long_flags` is
true, key-value pairs with a value of true and multiple-character key are
encoded as string flags. If `escape` is true, non-printable ASCII characters in
strings are encoded as escape sequences.

Installation
------------

The installation requires Python 3.

To install in system directories:

```sh
# To install from PyPI:
pip3 install pst-format

# Or, to install from this repository:
pip3 install .

# Note: On some Python distibutions pip3 and python3 are only available as
# "pip" and "python", respectively.
```

If installed in user's home directory, make sure `~/.local/bin` is in the
`PATH` environment variable.

Shell compatibility
-------------------

```sh
mkdir example
cd example
mkdir a b
pst *
["a", "b"]
touch a/1 a/2 b/3 b/4
pst a: { a/* } b: { b/* }
[{"a": ["a/1", "a/2"], "b": ["b/3", "b/4"]}]

# Better
pst a: { $(ls a/* --quoting-style c) } b: { $(ls b/* --quoting-style c) }
[{"a": ["1", "2"], "b": ["3", "4"]}]
```

Syntax
------

### PST

PST is a sequence of words separated by white space, encoded in 8-bit ASCII.

### White space characters

White space characters are space (` `), form-feed (`\f`), newline (`\n`),
carriage return (`\r`), horizontal tab (`\t`), and vertical tab (`\v`).

### White space

White space is a sequence of white space characters.

### Word

A word is a sequence of non-white space characters, and white space
characters if they are inside a quoted part. A quoted part of a word is a part
of a word enclosed in double quotes (`"`). A character inside a word preceded by
backslash (`\`) is escaped, and is treated literally (loses its special meaning),
unless it is one of the ANSI C quotes, in which case it is translated to the
corresponding 8-bit ASCII character:

- `\a`: alert/bell (7)
- `\b`: backspace (8)
- `\e`: escape (27)
- `\f`: form feed (12)
- `\n`: newline (10)
- `\r`: carriage return (13)
- `\t`: horizontal tab (9)
- `\v`: vertical tab (11)
- `\nnn`: octal value *nnn*, one to three digits

### Literal

Non-quoted words `true`, `false`, `none` are literals, and are interpreted as
true, false, null (respectively).

### Integer

An integer is a word composed of non-quoted digits.

### Floating-point number

A floating-point number is a words composed of non-quoted digits and a
non-quoted dot (`.`), beginning with a digit.

### Number

A number is an integer or a floating-point number.

### Bracket

A bracket is a word which is a non-quoted opening or closing curly
bracket (`{`, `}`).

### Double bracket

A double bracket is a word which is a non-quoted opening or closing double
curly bracket (`{{`, `}}`).

### Key

A word ending with a non-quoted colon (`:`) is a key.

### String

A string is a word which is not a key, literal, number, bracket,
double bracket, single-character flag or a string flag.

### Array

An array is a PST enclosed in square brackets.

### Value

A value is a string, literal, number, or array following a key.

### Key-value pair

A key followed by a value is a key-value pair.

### Implicit object

An implicit object is a sequence of one or more key-value pairs not enclosed
in brackets. An implicit object cannot be the value in a key-value pair.

### Explicit object

An explicit object is a sequence of zero or more key-value pairs enclosed
in double brackets. An explicit object can be the value in a key-value pair.
Words inside the brackets which are not key-value pairs are ignored.

### Single-character flag

Single-character flags are characters in a word beginning with an non-quoted
dash (`-`). Single-character flag is interpreted as an implicit object
`{c: True}`, where `c` is the character.

### String flag

A string flag is a string in a word beginning with an non-quoted double-dash
(`--`). String flag is interpreted as an implicit object `{s: True}`, where `s`
is the string.

Changelog
---------

### 2.0.0 (2022-11-21)

- Added a double-dash (`--`) delimiter option to decode\_argv and this is now the default (potentially breaks compatibility).
- Removed obsolete Python 2.7 code.

### 1.2.1 (2022-10-12)

- Fixed Unicode encoding.
- Fixed indentation of empty objects.
- Fixed application of encoder.
- Dropped support for Python 2.7.

### 1.2.0 (2022-07-30)

- Added encode function.
- Fixed parsing of empty strings.
- Fixed closing of implicit object inside list.
- Improved documentation.
- Dropped support for Python 2.

### 1.1.1 (2019-10-28)

- Added pstf.

### 1.0.0 (2019-10-28)

- Support for explicit objects.

### 0.1.0 (2019-02-05)

Initial release.

License
-------

Public domain. See [LICENSE.md](LICENSE.md).
