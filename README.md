# Basil

Simple Parser Library. Describe the syntax in a JSON file.

Features:
* Easy to use
* Syntax description in JSON, no complicated notation
* Transform parse tree to any type you want
* Helpful messages when parser runs into errors

Limitations:
* Does not detect conflicts
* Not designed for speed

### How to install

```sh
# If you use pip
pip install basil-parser==0.4.3

# If you use PDM
pdm install basil-parser==0.4.3
```


### How to use

If you're unfamiliar with parsers, please read the section on [lingo used](#lingo-used) below.

##### 1. Create the syntax JSON for your language.
See [this example](tests/json_parser/syntax.json), which describes the syntax of a subset of JSON.

The JSON should be an object with the following values:
* a `keyword_tokens` object, where the name is the token type in `snake_case` and the value is a regex for tokens of this type.
* a `regular_tokens` object, similar to keyword tokens, except names can't overlap. Keyword tokens are considered higher priority.
* a `filtered_tokens` array of strings. Lists token types that should be ignored. This is sometimes useful for getting rid of whitespace.
* a `nodes` object, where the name is the node type in `TITLE_CASE` and the value is an expression describing which configuration of child (tokens and nodes) is allowed, using this syntax:
    * `expr | expr`: choose one of the expressions
    * `(expr expr)`: combine expressions into one
    * `expr*`: repeat expression 0 or more times
    * `expr+`: repeat expression 1 or more times
    * `expr?`: expression is optional
* a `root_node` string value, indicating the node type of the root of the parse tree.


##### 2. Parse and transform

In your python code load the JSON with the `FileParser`. You only need to load the `FileParser` once, regardless of how many files are parsed, because it doesn't change any state when parsing files.

The output of the parser is hard to work with, so we transform it into something more workable. To allow the user to transform nodes and tokens into any type, a transformer function must be implemented with signatures as in the below example.

For a concrete working example, see how `parse_text_and_transform()` is used in `basil_json_loads()` in [this example](tests/json_parser/test_parser_transformed.py).


```py
from pathlib import Path
from basil.file_parser import FileParser

parser = FileParser(Path("path/to/your/syntax.json"))

transformed = parser.parse_text_and_transform(
    "code in your language",
    node_type="your root_node",
    node_transformer=node_transformer,
    token_transformer=token_transformer,
)

TRANSFORMED_TYPE = ... # Some union of types

def node_transformer(
    node_type: str, children: List[TRANSFORMED_TYPE | Token]
) -> TRANSFORMED_TYPE:
    # Translate to a TRANSFORMED_TYPE value based on the node type and it's children
    ...

def token_transformer(token: Token) -> TRANSFORMED_TYPE | Token:
    # Translate to TRANSFORMED_TYPE based on token.type or token.value
    # It is also possible to return `token` as is.
    ...
```

##### 3. Test

As usual, testing is optional but recommended. Regexes are tricky. The parser may not match things they way you expect. It is a good idea to test at least all nodes with some inputs that should match and some that should not. See [this file](tests/json_parser/test_parser.py) as an example.


### Lingo used

##### Tokenizer
Chops a file into a list of tokens, which are effectively small chunks of text. When a file is tokenized successfully, every character in the file is part of exactly one token. When the values of all tokens are pasted together, we get the original file.

##### Parser
Translates a list of tokens into a parse-tree consisting of tokens and nodes.

##### Token
A token is a piece of text (value) that has a certain token type. This is usually a single word or a sequence of characters indicating the start, end (such as brackets) or separation (such as comma's) of other parts of the file. Tokens are described by a regex in the syntax JSON.

##### Node
Contains a list of children Used to group tokens into a block of code, or data. The types of nodes and tokens that are accepted for a node type are described in the syntax JSON.


### Name
This project was called "Basil" because many people call their parser library parsley.

### License
This software is released under the [MIT license](./LICENSE.md).
