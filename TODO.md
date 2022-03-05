# TODO

### Parse Errors
- show meaningful location where parsing failed
- forward file names in error messages

### Cleanup
- rename `new_parse_generic` to something better
- remove anything from `Tree` without symboltype

### Parser generator
- type up grammar for grammar parser
- get it to work, remove old manually typed grammar parser
- warn if an unknown token name is encountered while parsing
- reformat generated parser with black
