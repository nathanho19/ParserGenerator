The backend files are:
	Compiler.py
	Parser.py
	Lexer.py
	Languages/CompilerGrammarCodeHardcoder/*
	Languages/CompilerLexerCodeHardcoder/*
	Languages/CompilerParser/*
	Languages/CompilerLexer/*

Parser:
Grammar.save_rules calls program CompilerParser to validate the saved table

CompilerLexer:
program('CompilerLexer', file_name, _) will build a lexer table from the description in file_name
the returned lexer table will be finalized
the lexer table can be turned into a Lexer using LexerFactory.from_table

CompilerParser:
program('CompilerParser', file_name, _) will build a grammar from the description in file_name
the grammar will be finalized
the grammar's start symbol is Start
the grammar can be turned into a parser using Parser.CLR

Compiler:
Input: A programming language, which is a lexer, grammar, and interpreter, and a program in that language

If the lexer is available in .lc form, the compiler calls it
If the lexer is available in .l form, the compiler calls program CompilerLexer lexer_file_name

If the grammar is available in .gc form, the compiler calls it
If the grammar is available in .g form, the compiler calls program CompilerParser grammar_file_name

If the parsing table is available in .pt form, the compiler loads the parsing tables
Otherwise, the compiler constructs the parsing tables using CLR.construct

If the .l file is not available, Lexer.save_table
If the .lc file is not available, program CompilerLexerCodeHardcoder
If the .g file is not available, Grammar.save_rules
if the .gc file is not available, program CompilerGrammarCodeHardcoder
If the .pt file is not available, CLR.save_tables

Dependencies:
If CompilerParser.gc is not available, then in attempting to construct the grammar it will call itself to construct the grammar. Therefore, CompilerParser.gc must be available.
If CompilerLexer.lc is not available, then in attempting to construct the lexer it will call itself to construct the lexer. Therefore, CompilerLexer.lc must be available. Therefore, CompilerLexer must have its compiler available in .lc form.
If CompilerParser.lc is not available and CompilerLexerCodeHardcoder.gc are not available, then CompilerParser will call CompilerLexerCodeHardcoder to construct CompilerParser.lc before returning the parse tree and CompilerLexerCodeHardcoder will call CompilerParserCompilerParser to construct the grammar before constructing CompilerParser.lc. Therefore, at least one of CompilerParser.lc and CompilerLexerCodeHardcoder.gc must be available.
If CompilerLexer.gc is not available and CompilerGrammarCodeHardcoder.lc are not available, then CompilerLexer will call CompilerGrammarCodeHardcoder to construct CompilerLexer.gc before returning the token stream and CompilerGrammarCodeHardcoder will call CompilerParserCompilerParser to construct the token stream before constructing CompilerLexer.gc. Therefore, at least one of CompilerLexer.gc and CompilerGrammarCodeHardcoder.lc must be available.
If CompilerLexer.gc and CompilerParser.lc are not available, then when attempting to parse, CompilerLexer will call CompilerParser, which in attempting to lex, will call CompilerLexer. Therefore, one of CompilerLexer.gc and CompilerParser.lc must be available.
Most files require ERASE_SYMBOL to be set in os.environ. Its value is used as a keyword in the lexers and grammars, so its value must be consistent across all files.
