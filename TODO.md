# TODO

### Tokenize
[ ] move `InternalParseError` into `ParseError`
[ ] implement `flatten` decorator for non terminals
[ ] replace `prune hard` and `prune soft` by `prune`, for terminal it's hard, for non-terminal it's soft.
[ ] keep track of failed token type matches in parser and use for suggestions on fail

### Parse Errors
- show meaningful location where parsing failed
- forward file names in error messages

### Docs
- start bragging in README
