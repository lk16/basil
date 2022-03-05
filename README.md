# Parser

Library that helps with parsing. For an example see [aaa](https://github.com/lk16/aaa), which uses this package.

Allows users to write human-readable BNF-like grammars like this:

```
ROOT = (A | B) (C D)+

A = "something"

B = C | D

C = regex("ab*")

D = (A C)?
```

These grammars can be converted in a python parser file that will accept the specified grammar and output a grammar tree.

Conversion is as simple as:
```sh
generate_parser your_grammar.txt path_to_new_parser_file.py
```

### Example usage inside this repo
The grammar for the grammar itself can be found [here](./parser/grammar/grammar.txt).
The [generated grammar parser](./parser/grammar/parser.py) is what is used inside this library for parsing any grammar.


### Upcoming features
See the [TODO](TODO.md) file.
