# Given a programming language, which is a lexer, parser, and interpreter, and a program in the programming language, compiles and runs the program under the programming language.

import os
import sys

DEBUG = True
DEBUG = False

def program(programming_language_name, program_file_name, program_arg):
    import imp
    import Lexer
    import Parser

    if DEBUG:
        print('Start of program(\'{:s}\', \'{:s}\', \'{:s}\')'.format(programming_language_name, program_file_name, program_arg))

    # File locations
    lexer_code_file_name = 'Languages/{0:s}/{0:s}.lc'.format(programming_language_name)
    lexer_file_name = 'Languages/{0:s}/{0:s}.l'.format(programming_language_name)
    grammar_code_file_name = 'Languages/{0:s}/{0:s}.gc'.format(programming_language_name)
    grammar_file_name = 'Languages/{0:s}/{0:s}.g'.format(programming_language_name)
    parser_table_file_name = 'Languages/{0:s}/{0:s}.pt'.format(programming_language_name)
    interpreter_file_name = 'Languages/{0:s}/{0:s}.i'.format(programming_language_name)

    # Load lexer
    if os.path.isfile(lexer_code_file_name):
        # Try to find .lc
        assert os.path.exists(lexer_code_file_name)
        
        if DEBUG:
            print('Loading {:s} lexer code from {:s}.'.format(programming_language_name, lexer_code_file_name))

        ProgramLexerModule = imp.load_source('{:s}Lexer'.format(programming_language_name), lexer_code_file_name)
        lexer_table = ProgramLexerModule.construct_lexer_table()
        program_lexer = Lexer.LexerFactory.from_table(lexer_table)
        
        if DEBUG:
            print('Loaded  {:s} lexer code from {:s}.'.format(programming_language_name, lexer_code_file_name))
    elif os.path.isfile(lexer_file_name):
        # Try to find .l
        assert not os.path.exists(lexer_code_file_name)
        assert not os.path.isfile(lexer_code_file_name)
        assert os.path.exists(lexer_file_name)
        
        if DEBUG:
            print('Loading {:s} lexer description from {:s}.'.format(programming_language_name, lexer_file_name))
            
        if programming_language_name == 'CompilerLexer':
            raise RuntimeError('CompilerLexer .lc file missing. Using the .l file will cause an infinite loop.')
        lexer_table = program('CompilerLexer', lexer_file_name, '')
        program_lexer = Lexer.LexerFactory.from_table(lexer_table)
        
        if DEBUG:
            print('Loaded  {:s} lexer description from {:s}.'.format(programming_language_name, lexer_file_name))
    else:
        raise RuntimeError('{:s} ;exer file missing.'.format(programming_language_name))

    # Lex phase
    token_stream = program_lexer.lex_file(program_file_name)
    
    if DEBUG:
        print('Token stream is:')
        print('\n'.join(['\t{!s:s}'.format(x) for x in token_stream]))

    # Load grammar
    if os.path.isfile(grammar_code_file_name):
        # Try to find .gc
        assert os.path.exists(grammar_code_file_name)
        
        if DEBUG:
            print('Loading {:s} grammar code from {:s}.'.format(programming_language_name, grammar_code_file_name))

        ProgramGrammarModule = imp.load_source('{:s}Grammar'.format(programming_language_name), grammar_code_file_name)
        grammar = ProgramGrammarModule.construct_grammar()
        
        if DEBUG:
            print('Loaded  {:s} grammar code from {:s}.'.format(programming_language_name, grammar_code_file_name))
    elif os.path.isfile(grammar_file_name):
        # Try to find .g
        assert not os.path.exists(grammar_code_file_name)
        assert not os.path.isfile(grammar_code_file_name)
        assert os.path.exists(grammar_file_name)
        
        if DEBUG:
            print('Loading {:s} grammar description from {:s}.'.format(programming_language_name, grammar_file_name))
        
        if programming_language_name == 'CompilerParser':
            raise RuntimeError('CompilerParser .gc file missing. Using the .g file will cause an infinite loop.')
        grammar = program('CompilerParser', grammar_file_name, '')
        
        if DEBUG:
            print('Loaded  {:s} grammar description from {:s}.'.format(programming_language_name, grammar_file_name))
    else:
        raise RuntimeError('{:s} grammar file missing.'.format(programming_language_name))

    # Load parser
    parser = Parser.CLR(grammar)
    if os.path.isfile(parser_table_file_name):
        # Try to find .pt
        assert os.path.exists(parser_table_file_name)
        
        if DEBUG:
            print('Loading {:s} parsing tables from {:s}.'.format(programming_language_name, parser_table_file_name))

        parser.load_tables(parser_table_file_name)
        
        if DEBUG:
            print('Loaded  {:s} parsing tables from {:s}.'.format(programming_language_name, parser_table_file_name))
    else:
        assert not os.path.exists(parser_table_file_name)
        assert not os.path.isfile(parser_table_file_name)
        
        if DEBUG:
            print('Constructing {:s} parsing tables.'.format(programming_language_name, parser_table_file_name))
        
        # Construct parser tables
        parser.construct()
        
        if DEBUG:
            print('Constructed  {:s} parsing tables.'.format(programming_language_name, parser_table_file_name))

    # Parse phase
    parse_output = parser.parse(token_stream)
    
    # Failed parse error handling
    if parse_output[0][-1] != 'Accept':
        print()
        print('Parse failed. Parse output dump below:')
        
        # Print actions
        print('Actions:')
        for action in parse_output[0]:
            print('\t{:s}'.format(action))
        
        # Print stack
        print('Stack:')
        stack = tuple(parse_output[1])
        for i in range(0, len(stack), 2):
            if i + 1 < len(stack):
                PRINT_PARSE_NODE_VALUE = False
                if PRINT_PARSE_NODE_VALUE:
                    print('\t{:d} {:s} = {!s:s}'.format(stack[i], stack[i + 1][0], stack[i + 1]))
                else:
                    print('\t{:d} {:s}'.format(stack[i], stack[i + 1][0]))
            else:
                print('\t{:d}'.format(stack[i]))

        # Print unparsed input
        print('Input:')
        for item in parse_output[2]:
            print('\t{!s:s}'.format(item))
        print()
        raise RuntimeError('Parse failed.')

    # Extract parse tree
    parse_tree = parser.parse_output_to_parse_tree(parse_output)

    if DEBUG:
        print()
        print('Parse tree is:')
        try:
            print(parse_tree)
        except RecursionError:
            print('RecursionError: Too long to print.')
        print()

    if DEBUG:
        print('Loading {:s} interpreter from {:s}.'.format(programming_language_name, programming_language_name))
            
    # Initialize interpreter
    ProgramInterpreterModule = imp.load_source('{:s}Interpreter'.format(programming_language_name), interpreter_file_name)
    
    if DEBUG:
        print('Loaded  {:s} interpreter from {:s}.'.format(programming_language_name, programming_language_name))
    
    # Construct AST
    ast = ProgramInterpreterModule.parse_tree_to_ast(parse_tree)
    
    if DEBUG:
        ast_as_string = ProgramInterpreterModule.ast_to_string(ast)
        print()
        print('Abstract Syntax Tree is:')
        print(ast_as_string)

    # Interpret phase
    result = ProgramInterpreterModule.interpret(ast, program_arg)
    
    if DEBUG:
        result_as_string = ProgramInterpreterModule.result_to_string(result)
        print()
        print('Result as a string, which has length {:d}:'.format(len(result_as_string)))
        print(result_as_string)
        
    # Save lexer
    if not os.path.isfile(lexer_file_name):
        assert not os.path.exists(lexer_file_name)
        assert os.path.exists(lexer_code_file_name)
        assert os.path.isfile(lexer_code_file_name)
        
        if DEBUG:
            print('Saving {:s} lexer description in {:s}.'.format(programming_language_name, lexer_file_name))
        
        program_lexer.save_table(lexer_file_name)
        
        if DEBUG:
            print('Saved  {:s} lexer description in {:s}.'.format(programming_language_name, lexer_file_name))
        
    # Save lexer code
    if not os.path.isfile(lexer_code_file_name):
        assert not os.path.exists(lexer_code_file_name)
        assert os.path.exists(lexer_file_name)
        assert os.path.isfile(lexer_file_name)
        
        if DEBUG:
            print('Saving {:s} lexer code in {:s}.'.format(programming_language_name, lexer_code_file_name))
            
        program('CompilerLexerCodeHardcoder', lexer_file_name, lexer_code_file_name)
        
        if DEBUG:
            print('Saved  {:s} lexer code in {:s}.'.format(programming_language_name, lexer_code_file_name))

    # Save grammar
    if not os.path.isfile(grammar_file_name):
        assert not os.path.exists(grammar_file_name)
        assert os.path.exists(grammar_code_file_name)
        assert os.path.isfile(grammar_code_file_name)
        
        if DEBUG:
            print('Saving {:s} grammar description in {:s}.'.format(programming_language_name, grammar_file_name))
        
        grammar.save_rules(grammar_file_name)
        
        if DEBUG:
            print('Saved  {:s} grammar description in {:s}.'.format(programming_language_name, grammar_file_name))
        
    # Save grammar code
    if not os.path.isfile(grammar_code_file_name):
        assert not os.path.exists(grammar_code_file_name)
        assert os.path.exists(grammar_file_name)
        assert os.path.isfile(grammar_file_name)
        
        if DEBUG:
            print('Saving {:s} grammar code in {:s}.'.format(programming_language_name, grammar_code_file_name))
            
        program('CompilerGrammarCodeHardcoder', grammar_file_name, grammar_code_file_name)
        
        if DEBUG:
            print('Saved  {:s} grammar code in {:s}.'.format(programming_language_name, grammar_code_file_name))

    # Save parser tables
    if not os.path.isfile(parser_table_file_name):
        assert not os.path.exists(parser_table_file_name)
        
        if DEBUG:
            print('Saving {:s} parser tables in {:s}.'.format(programming_language_name, parser_table_file_name))
        
        parser.save_tables(parser_table_file_name)
        
        if DEBUG:
            print('Saved  {:s} parser tables in {:s}.'.format(programming_language_name, parser_table_file_name))
        
    # Return
    return result

if __name__ == '__main__':
    ERASE_SYMBOL = '<_ERASE_>'
    assert 'ERASE_SYMBOL' not in os.environ or os.environ['ERASE_SYMBOL'] == ERASE_SYMBOL
    os.environ['ERASE_SYMBOL'] = ERASE_SYMBOL
    
    if len(sys.argv) < 3 or 4 < len(sys.argv):
        sys.stdout.write('You provided {:d} arguments. You must provide 2 or 3 arguments.'.format(len(sys.argv) - 1))
        sys.exit(1)

    if len(sys.argv) == 4:
        result = program(sys.argv[1], sys.argv[2], sys.argv[3])
    elif len(sys.argv) == 3:
        result = program(sys.argv[1], sys.argv[2], '')
    else:
        raise RuntimeError

    if not DEBUG:
        result = str(result)
        sys.stdout.write(result)