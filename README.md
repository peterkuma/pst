Plain Structured Text (PST)
===========================

PST is a format for encoding structured text similar to Bourne shell formatting
and JSON. PST supports strings, numbers (integers and floating-point), bool,
missing values (`none`), arrays, objects (key-value pairs),
single-character flags (`-x`), and string flags (`--abc`).
Relative to JSON, PST is simpler, while supporting much of its features.
PST aims to be human and machine readable, and suitable for command
line argument formatting, standard input/output and configuration file
formatting. PST is smilar to YAML, but supporing one-line expressions
(indentation does not matter).

Implementations of PST as a command-line program and a Python 2.7/3 function
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

```sh
pst <pst>...
```

where `<pst>` are PST-formatted words.

Prints JSON on the standard output.

### Python

```python
import pst
```

#### decode

```python
pst.decode(s, as_unicode=False)
```

Decode PST. `s` is PST (binary string) or a list
of PST, and `as_unicode` (bool) indicates
whether to convert binary strings in output to unicode.

#### decode_argv

```python
pst.decode_argv(argv, **kwargs)
```

Decode PST and split the resulting list into positional and named arguments.
`argv` is a list such as `sys.argv` and `kwargs` are keyword arguments passed
to `pst.decode`. Returns a tuple (`args`, `opts`), where `args` are positional
arguments and `opts` are named arguments.

Installation
------------

The installation requires Python 2.7 or Python 3.

To install in system directories:

```sh
pip3 install pst-format
# or from the archive directory:
python3 setup.py install
```

Append `--user` to install in user directories
(make sure `~/.local/bin` is in the `PATH` environmental variable).
Replace `pip3` with `pip` or `python3` with `python` to install with Python 2.

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

PST is a sequence of words separated by whitespace, encoded in 8-bit ASCII.

### Whitespace characters

Whitespace characters are space (` `), form-feed (`\f`), newline (`\n`),
carriage return (`\r`), horizontal tab (`\t`), and vertical tab (`\v`).

### Whitespace

Whitespace is a sequence of whitespace characters.

### Word

A word is a sequence of non-whitespace characters, and whitespace
characters if they are inside a quoted part. A quoted part of a word is a part
of a word enclosed in double quotes (`"`). A character inside a word preceded by
backslash (`\`) is escaped, and is treated literaly (loses its special meaning),
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

### 1.0.0 (2019-10-28)

- Support for explicit objects.

### 0.1.0 (2019-02-05)

Initial release.

License
-------

Public domain. See [LICENSE.md](LICENSE.md).
