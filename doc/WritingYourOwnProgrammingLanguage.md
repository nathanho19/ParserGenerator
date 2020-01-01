Definitions/Vocabulary:
* Execute, run, and interpret are all synonyms.
* Compiled language and interpreted language are synonyms.
* Programming language:
	* That which assigns meaning to strings.
	* A compiler
* Compiler:
	* A lexer, parser, and interpreter
	* A program that takes in a string and interprets it
	* CompilerLexer, CompilerParser, [Compiler.py](/Compiler.py), [Lexer.py](/Lexer.py), [Parser.py](/Parser.py), and their dependencies.
* Program (of a programming language):
	* A string that is in the programming language. Note that a programming language may be a program of a different programming language.
* CompilerLexer:
	* A program that takes in a lexer description and returns a lexer table, which can later be converted into a Lexer.
* CompilerParser:
	* A program that takes in a grammar description and returns a Grammar.
* Lexer:
	* (of a language) A program whose input is a string and output is a sequence of tokens.
	* The python class implemented in [Lexer.py](/Lexer.py) and its helper functions or an instance of that class
	* an instance of Lexer
* Grammar:
	* The python class as implemented in [Parser.py](/Parser.py) and its helper functions
	* an instance of Grammar
* CLR:
	* The python class as implemented in [Parser.py](/Parser.py) and its helper functions
	* an instance of CLR
* Parser:
	* (of a language) A program whose input is a grammar and sequence of tokens and output is a parse tree of the sequence of tokens under the grammar.
	* [Parser.py](/Parser.py)
	* an instance of CLR
* AST (short for Abstract Syntax Tree):
	* an object of the type of the input of the interpreter
* Interpreter:
	* (of a language) A collection of:
		* a program that takes in a parse tree and returns an abstract syntax tree
		* a program that takes in an ast and possibly an input string and possibly return a value, print, write to files, etc
		* a program that takes in an ast and returns a human-readable string
		* a program that takes in an object of the same type as returned values and returns a human-readable string

What does a compiler consist of?
A compiler consists of a lexer, parser, and interpreter. A compiler can then be used to interpret programs of its language.

How does the lexer algorithm work:
CompilerLexer is the lexer algorithm. The lexer algorithm uses a table-driven state machine. A lexer rule (as represented in memory) has 5 elements, the beginning state, the ending state, the (optional) token name, the (optional) args expand string, and the regex, all of which are strings. For each state, the lexer table stores a sequence of rules. The lexer algorithm begins in state '0', which is zero represented as a string and with the entire input program string as the unparsed input string.

The lexer algorithm tries each rule of the state in order until a rule's regex matches with the front of the unparsed input. Then, the entire matching prefix of the unparsed input is consumed, expanded according to the rule's args expand string, and split by ', '. Then, a token with that rule's token name and those arguments is appended to the output token stream, and the state changes to the rule's ending state. If the rule does not contain an arg expand string, then the token will have no args passed. If the rule does not have a token name, then no token will be appended to the token stream. Tokens are a tuple of two elements, where the first element is a string whose value is the name of the token and the second element is a tuple of strings, one for each argument from the expanded string.

If the matching prefix is the empty string and the ending state is the beginning state, the rule is skipped, rather than applied. If no rule matches, the lexer fails. If the lexer state is 'Fail', the lexer fails.

What does creating a lexer consist of?
You will write a lexer description that CompilerLexer will turn into a lexer table, which will then be turned into a lexer. A lexer description is a list of transitions. Transitions may not be split over multiple lines. There may not be more than one transition per line. A transition begins with the beginning state, a space, an ending state, and a space. Both states must match [A-Za-z0-9]+. If the ending state is not 'Fail', then a token name must be supplied. The token name must match (?:[A-Z][a-z]\*)+. After a token, the args expand string may be supplied by inserting an open parentheses, the args expand string, a close parentheses, and a space. The args expand string must match [^\(\)\t\r\n]\*. The args expand string may be the empty string, in which case the empty string will be passed as the arg to the token. Finally, the regex is provided. Trailing spaces and tabs on the line will not appear in the regex. In fact, the lexer will fail if there is a trailing space or tab after the regex, since they are hard to notice when reading the lexer description. To include a space or tab at the end of the regex, write [ ] or [\t]. The regex must have at least one character. Writing exactly the value of ERASE_SYMBOL as the regex will result in a regex that matches the empty string and nothing else. To have a regex that matches the value of ERASE_SYMBOL and nothing else, wrap the value of ERASE_SYMBOL inside (?:). The lexer description lexer rules are described in CompilerLexer.l and the grammar rules are described in CompilerLexer.g. The lexer algorithm is described in Lexer.py.

How does the parser algorithm work?
The parser algorithm takes in a grammar and constructs an LR(1) parser for that grammar. Therefore, the grammar supplied must be LR(1). The returned parse tree is a tuple of two elements. The first element is a string whose value is the name of the left hand side of the rule and the second element is a tuple of parse trees in the order they appear in the rule used to reduce.

What does creating a grammar consist of?
You will write a grammar description that CompilerParser will turn into a grammar, which will then be turned into a parser.

The required form for the grammar is roughly Backus-Naur form. Symbol names are of the form (?:[A-Z][a-z]\*)+, and the right hand side of declarations are space-delimited symbol names, possibly joined with | as the or operator. The start symbol is Start. Productions with the empty string as the right hand side have the value of ERASE_SYMBOL as the symbol name, even if it doesn't match with (?:[A-Z][a-z]\*)+. Declarations may not be split over multiple lines. There may not be multiple declarations on the same line. There is not a string literal terminal. All terminal symbols come from the lexer. The exact lexer rules are described in CompilerParser.l and the exact grammar rules are described in CompilerParser.g.

What does creating an interpreter consist of?
The interpreter implements the following functions:
* parse_tree_to_ast(parse_tree):
	* parse_tree is a parse tree from the parser
	* the return value is an AST
* ast_to_string(ast):
	* ast is an AST
	* the return value is a human-readable representation of ast
* interpret(ast, arg):
	* a is an object of the same type as values returned by interpret
	* the return value is a human-readable representation of a
* result_to_string(result):
	* result is an object of the same type as values returned by interpret
	* the return value is a human-readable representation of result

The interpreter is written in python, although by convention, the file extension is .i, not .py.

How do I run my program?
First, place your programming language files into the following folder structure:
* Languages
	* LANG
		* LANG.l
		* LANG.g
		* LANG.i
where LANG refers to the name of your programming language and Languages is the [Langauges](/Langauges/) folder. You can also provide a .lc file instead of a .l file or a .gc file instead of a .g file.

Finally, run the command `python Compiler.py LANG PROGRAM ARG`, where PROGRAM is the path, name, and extension of your program file and ARG is an optional string that is passed to the interpret function along with the AST. If ARG is not provided, then the empty string is passed to interpret.
