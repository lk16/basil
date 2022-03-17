# TODO

### Tokenize
[ ] rename symbol type to token type everywhere
[ ] change `LINE` to `(DECORATOR)* TOKEN_DEFINITION`
[ ] create `tree_to_python_tokenizer_expression()`
[ ] move tokenizer functions into Parser
[ ] keep track of failed token type matches in parser and use for suggestions on fail

### Parse Errors
- show meaningful location where parsing failed
- forward file names in error messages

### Docs
- start bragging in README
