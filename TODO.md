# TODO

### Parser generator
- warn if an unknown token name is encountered while parsing
- put `parse()` function in generated parser.
- `parse()` should remove all nodes without symbol
- add some syntax to parse tree to get certain symbols to not show up in resulting parse tree

### Cleanup
- rename `new_parse_generic` to something better

### Parse Errors
- show meaningful location where parsing failed
- forward file names in error messages
