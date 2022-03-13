# TODO

### Tokenize
[x] read all terminals and nonterminals from grammar file
[x] maintain order of terminals in output file
[x] check that terminals don't have a SymbolParser or repeat-family parsers
[x] check that parsers for non-terminals don't have a RegexParser
[x] add all literals as internal tokens to token list
[x] terminal_rules should only have RegexTokenizers
[x] Implement Tokenizer
[x] Re-implement all Parsers
[x] Implement TokenParser, that accepts exactly one type of token
[x] tokenize input file
[ ] send tokenize input file into parser

### Parse Errors
- show meaningful location where parsing failed
- forward file names in error messages

### Docs
- start bragging in README
