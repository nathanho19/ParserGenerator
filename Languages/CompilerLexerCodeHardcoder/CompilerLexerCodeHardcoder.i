import os
assert 'ERASE_SYMBOL' in os.environ
ERASE_SYMBOL = os.environ['ERASE_SYMBOL']

import Lexer
import re

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
    
    raise NotImplementedError('Unhandled parse tree pattern: {:s}'.format(str(pattern)))

def interpret(ast, arg):
    lexer_table = Lexer.ast_to_lexer_table(ast)
    
    table_as_string = _lexer_table_to_python_code_dictionary(lexer_table)
    
    write_file = open(arg, 'w')
    write_file.write(table_as_string)
    write_file.close()
    
    return 'Success'

def _lexer_table_to_python_code_dictionary(lexer_table):
    Lexer.validate_lexer_table(lexer_table)
    
    requires_erase_symbol = False
    
    out = ''
    out += 'from collections import deque'
    
    out += '\n\ndef construct_lexer_table():'
    out += '\n\tout = dict()'
    for state in lexer_table:
        out += '\n\n\tout[\'{:s}\'] = deque()'.format(state)
        for next_state, token_name, expand_string, regex in lexer_table[state]:
            out += '\n\tout[\'{:s}\'].append(('.format(state)
            if next_state is None:
                out += 'None, '
            else:
                out += '\'{:s}\', '.format(next_state)
            if token_name is None:
                out += 'None, '
            else:
                out += '\'{:s}\', '.format(token_name)
            if expand_string is None:
                out += 'None, '
            else:
                out += 'r\'{:s}\', '.format(expand_string)
            regex_contains_erase_search = re.search(ERASE_SYMBOL, regex)
            if regex_contains_erase_search:
                requires_erase_symbol = True
                out += 'r\'{:s}\'.format(ERASE_SYMBOL)'.format(re.sub(ERASE_SYMBOL, '{:s}', regex))
            else:
                out += 'r\'{:s}\''.format(regex)
            out += '))'
    out += '\n\n\treturn out'
    
    if requires_erase_symbol:
        erase_symbol_import = ''
        erase_symbol_import += 'import os'
        erase_symbol_import += '\nassert \'ERASE_SYMBOL\' in os.environ'
        erase_symbol_import += '\nERASE_SYMBOL = os.environ[\'ERASE_SYMBOL\']'
        erase_symbol_import += '\n\n'
        out = erase_symbol_import + out
    
    return out

def ast_to_string(ast):
    return Lexer.lexer_table_to_string(Lexer.ast_to_lexer_table(ast))

def result_to_string(result):
    return result