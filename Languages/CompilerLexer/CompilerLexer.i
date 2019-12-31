# Given a CompilerLexer lexer L and a string S, generates the token stream of S under L.

import os
assert 'ERASE_SYMBOL' in os.environ
ERASE_SYMBOL = os.environ['ERASE_SYMBOL']

import re
from collections import deque

DEBUG = True
DEBUG = False

def parse_tree_to_ast(parse_tree):
    node_type, children = parse_tree
    pattern = (node_type,) + tuple([x[0] for x in children])
    
    if node_type == 'Start':
        return tuple([x for child in children for x in parse_tree_to_ast(child)])
    if node_type == 'Transition':
        state = children[0][1][0]
        if children[1][0] == 'FailState':
            next_state = None
        else:
            next_state = children[1][1][0]
        if children[-1][1][0] == '' or children[-1][1][0] == ERASE_SYMBOL:
            regex = ''
        else:
            regex = children[-1][1][0]
        token_name = None
        expand_string = None
        if children[2][0] == 'WordWithExpandString':
            token_name = children[2][1][0]
            expand_string = children[2][1][1]
        elif children[2][0] == 'Word':
            token_name = children[2][1][0]
            
        return ((state, next_state, token_name, expand_string, regex),)
    
    print()
    print('Unhandled parse tree pattern: {:s}'.format(str(pattern)))
    raise NotImplementedError

def ast_to_string(ast):
    lexer_table = ast_to_lexer_table(ast)
    return lexer_table_to_string(lexer_table)

def interpret(ast, arg):
    return ast_to_lexer_table(ast)

def ast_to_lexer_table(ast):
    lexer_table = dict()
    for state, next_state, token_name, expand_string, regex in ast:
        if state not in lexer_table:
            lexer_table[state] = deque()
        if regex == ERASE_SYMBOL:
            regex = ''
        lexer_table[state].append((next_state, token_name, expand_string, regex))

    # Finalize lexer table
    lexer_table = finalize_lexer_table(lexer_table)
    return lexer_table

def lexer_table_to_string(lexer_table):
    validate_lexer_table(lexer_table)
    out = ''
    for state in lexer_table:
        for next_state, token_name, expand_string, regex in lexer_table[state]:
            if out:
                out += '\n'
            out += '{:s}'.format(state)
            out += ' '
            if next_state is None:
                out += 'Fail'
                out += ' '
            else:
                out += '{:s}'.format(next_state)
                out += ' '
                if expand_string is not None:
                    out += '{:s}({:s})'.format(token_name, expand_string)
                elif token_name is not None:
                    out += '{:s}'.format(token_name)
                else:
                    out += ERASE_SYMBOL
                out += ' '
            if regex == '':
                out += ERASE_SYMBOL
            else:
                out += '{:s}'.format(regex)
    return out

def result_to_string(result):
    return lexer_table_to_string(result)

def finalize_lexer_table(lexer_table):
    for key in lexer_table:
        lexer_table[key] = tuple(lexer_table[key])
    validate_lexer_table(lexer_table)
    return lexer_table

def validate_lexer_table(lexer_table):
    assert isinstance(lexer_table, dict)
    for state in lexer_table:
        assert isinstance(state, str)
        assert isinstance(lexer_table[state], tuple)
        
        for next_state, token_name, expand_string, regex in lexer_table[state]:
            assert next_state is None or isinstance(next_state, str)
            assert token_name is None or isinstance(token_name, str)
            assert expand_string is None or isinstance(expand_string, str)
            assert isinstance(regex, str)
            
            assert token_name or expand_string is None
            assert next_state is not None or token_name is None
            assert token_name != ERASE_SYMBOL
            assert token_name != 'Eat'		# This is from an old iteration where Eat was the symbol for 'output no nonterminal'
    
    # This is some failed attempt at asserting that there are no infinite loops due to empty productions
    # This is somewhat handled in a different level of the program
    # Also, this code was written several iterations ago
    # for regexes in lexer_table.values():
        # if len(regexes) > 1:
            # for regex, _, _ in regexes:
                # assert not re.match(regex, '')