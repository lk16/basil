# TODO

### Parser generator
- naming consistency of decorators in grammar with code
- make `@ banned values` taken one `TOKEN_COMPOUND_EXPRESSION` and ban any string that matches that expression
- `parse_generic` should take param for `root_name: str` item (for debugging) that defaults to `ROOT`
- warn if an unknown token name is encountered while parsing


### Parse Errors
- show meaningful location where parsing failed
- forward file names in error messages

### Docs
- start bragging in README
