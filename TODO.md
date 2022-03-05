# TODO

### Parse Errors
- show meaningful location where parsing failed
- forward file names in error messages

### Cleanup
- rename `new_parse_generic` to something better
- remove anything from `Tree` without symboltype

### Grammar parser
- add function to check if a generated parser is up to date with a grammar
- type up grammar for grammar parser
- get it to work, remove old manually typed grammar parser
- add test to see that parser is up to date with grammar
- warn if an unknown token name is encountered while parsing
