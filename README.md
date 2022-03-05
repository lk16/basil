# Parser

This library allows users to write human-readable BNF-like grammars like below, which can be converted into parsers.

```
ROOT = (A | B) (C D)+

A = "something"

B = C | D

C = regex("ab*")

D = (A C)?
```
The generated parser will be saved in a python file that will accept the specified grammar and output a parse tree.

Conversion is as simple as:
```sh
generate_parser your_grammar.txt path_to_new_parser_file.py
```

Note that the grammar should have a `ROOT` token, which is the entrypoint of the parser and the root node of the resulting parse tree.

### Example usage inside this repo
The grammar for the grammar itself can be found [here](./parser/grammar/grammar.txt).
The [generated grammar parser](./parser/grammar/parser.py) is what is used inside this library for parsing any user-supplied grammar.

### Upcoming features
See the [TODO](TODO.md) file.
