Plain Structured Text (PST)
===========================

**Development status:** Beta

PST is a format for structured text modelled after Bourne shell expressions
and JSON. PST supports strings, numbers (integers and floating-point), boolean,
missing values (none), arrays, objects (key-value pairs),
single-character flags, and string flags.
Relative to JSON, PST is simpler, while supporting many of its features.
PST aims to be a unified human and machine-readable format for command
line argument passing and standard input/output formatting which is easier
to read and write than JSON. PST is smilar to YAML, but simpler, supporing
one-line expressions, and is more consistent with conventions on GNU systems.

Examples
--------

Empty
```
PST: 
JSON: []
```

Single string
```
PST: a
JSON: ["a"]
```

Quoted string
```
PST: "a b"
JSON: ["a b"]
```

Partially-quoted string
```
PST: a"b c"
JSON: ["ab c"]
```

Two strings
```
PST: a b
JSON: ["a", "b"]
```

Two string separated by a newline
```
PST:
a
b
JSON: ["a", "b"]
```

Key-value pair
```
PST: a: 1
JSON: [{"a": 1}]
```

Sequence of key-value pairs
```
PST: a: 1 b: 2
JSON: [{"a": 1, "b": 2}]
```

Sequence of key-value pairs and a string
```
PST: a: 1 b: 2 c
JSON: [{"a": 1, "b": 2}, "c"]
```

Empty array
```
PST: { }
JSON: [[]]
```

String and an empty array
```
PST: a { }
JSON: ["a", []]
```
String and an array
```
PST: a { b c }
JSON: ["a", ["b", "c"]]
```

An array as value followed by a string
```
PST: a: { b c } d
JSON: [{"a": ["b", "c"]}, "d"]
```

Literals
```
PST: true false none
JSON: [true, false, null]
```

Single-character flags
```
PST: -ab
JSON [{"a": true, "b": true}]
```

String flag
```
PST: --ab
JSON: [{"ab": true}]
```

Usage
-----

Implementations of PST as a command-line program and a Python function
are available.

Command line:

```sh
pst <pst>...
```

where <pst> are PST words. Prints JSON on the standard output.

Python:

```python
import pst
s = "<pst>"
pst.decode(s)
```

where <pst> is a PST text (binary string). Returns a list.

Shell compatibility
-------------------

```
mkdir example
cd example
mkdir a b
pst * # ["a", "b"]
touch a/1 a/2 b/3 b/4
pst a: { a/* } b: { b/* }
[{"a": ["a/1", "a/2"], "b": ["b/3", "b/4"]}]

# Better
pst a: { $(ls a/* --quoting-style c) } b: { $(ls b/* --quoting-style c) }
[{"a": ["1", "2"], "b": ["3", "4"]}]
```

Complex example
---------------

This example is adapted from Wikipedia and licensed under the
[CC BY-SA 3.0](https://en.wikipedia.org/wiki/Wikipedia:Text_of_Creative_Commons_Attribution-ShareAlike_3.0_Unported_License).
license.

PST:

```
firstName: John
lastName: Smith
isAlive: true
age: 27
address: {
	streetAddress: "21 2nd Street"
	city: "New York"
	state: NY
	postalCode: 10021-3100
}
phoneNumbers: [
	{ type: home number: "212 555-1234" }
	{ type: office number: "646 555-4567" }
	{ type: mobile number: "123 456-7890" }
]
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
  "address": [{
    "streetAddress": "21 2nd Street",
    "city": "New York",
    "state": "NY",
    "postalCode": "10021-3100"
  }],
  "phoneNumbers": [
    [{
      "type": "home",
      "number": "212 555-1234"
    }],
    [{
      "type": "office",
      "number": "646 555-4567"
    }],
    [{
      "type": "mobile",
      "number": "123 456-7890"
    }]
  ],
  "children": [],
  "spouse": null
}
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

Word is a sequence of non-whitespace characters, and whitespace
characters if they are inside a quoted part. A quoted part of a word is a part
of a word enclosed in double quotes (`"`). A character inside a word preceded by
backslash (`\`) is escaped and is treated literaly (loses its special meaning).

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

### Brackets

A bracket is a word which is a non-quoted opening or closing bracket (`{`, `}`).

### Key

A word ending with a non-quoted colon (:) is a key.

### String

A String is a word which is not a key, literal, number, or a bracket.

### Array

An array is a PST enclosed in brackets ("{", "}").

### Value

A value is a string, literal, number, or array following a key.

### Key-value pair

A key followed by a value is a key-value pair.

### Object

An object is a sequence of key-value pairs.

### Single-character flag

Single-character flags are characters in a word beginning with an non-quoted
dash (`-`). Single-character flags are interpreted as {c: True}, where c
is the character.

### String flag

A string flag is a string in a word beginning with an non-quoted double-dash
(`--`). String flag is interpreted as {s: True}, where s is the string.

License
-------

Public domain. See [LICENSE.md](LICENSE.md).
