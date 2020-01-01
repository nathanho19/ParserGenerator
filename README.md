# ParserGenerator
This repo hosts a tool for rapidly implementing programming language interpreters. Lexer and grammar specifications are given in a custom format and interpreters are implemented fully with python code.

## What technologies does ParserGenerator use?
To recognize tokens, the lexer uses python's re module for regular expresions. The parser uses the LR(1) parser technique. The interpreter is its own python module.

## How do I write my own programming language?
See [doc/WritingYourOwnProgrammingLanguage.md](/doc/WritingYourOwnProgrammingLanguage.md)

## What are all the new file types?
File extensions are only by convention. However, currently, the compiler recognizes file types by file extension.

Extension | File Type | Description
---: | :--- | :---
.i | interpreter | Executes a parse tree
.g | grammar description | Rules for converting a sequence of tokens to a parse tree
.gc | grammar code | Python code representation of a grammar
.l | lexer description | Rules for converting a string to a sequence of tokens
.lc | lexer code |  Python code representation of a lexer
.pt | parser table | Saved and loaded to save computation time

## I'm a power user. What can I do?
You can:
* Turn verbose logging on and off through the DEBUG variable in [Compiler.py](/Compiler.py) and [Lexer.py](/Lexer.py).
* Change the file search locations in [Compiler.py](/Compiler.py).
* Modify the inner workings of the backend to accept new types of lexer descriptions, grammar descriptions, and interpreters. The backend is described in [doc/BackendDetails.md](/doc/BackendDetails.md).
