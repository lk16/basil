# TODO

### Tokenize
[x] read all terminals and nonterminals from grammar file
[ ] maintain order of terminals in output file
[ ] check that parsers for non-tokens don't have a RegexParser
[ ] check that non-tokens don't have a SymbolParser
[ ] add all literals as internal tokens to token list
[ ] Implement TokenParser, that accepts exactly one type of token
[ ] Build Parser class tree as before, with TokenParser
[ ] Implement Tokenizer
[ ] tokenize input file
[ ] send tokenize input file into parser


### Parser generator
- warn if an unknown token name is encountered while parsing


### Parse Errors
- show meaningful location where parsing failed
- forward file names in error messages

### Docs
- start bragging in README
