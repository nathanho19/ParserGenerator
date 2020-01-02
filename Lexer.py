# Given a CompilerLexer lexer L and a string S, generates the token stream of S under L.

import os
assert 'ERASE_SYMBOL' in os.environ
ERASE_SYMBOL = os.environ['ERASE_SYMBOL']

import sys
import re
from collections import deque

DEBUG = True
DEBUG = False

class LexerFactory:
    def from_table(table):
        table = finalize_lexer_table(table)
        out = Lexer()
        out.lexer_table = table
        return out

class Lexer:
    def __init__(self):
        self.lexer_table = None
    
    def lex(self, content):
        validate_lexer_table(self.lexer_table)
        
        index = 0
        state = '0'
        out = deque()
        while index < len(content):
            found_match = False
            for i, (next_state, token_name, expand_string, regex) in enumerate(self.lexer_table[state]):
                match = re.match(regex, content[index:])
                # Go to fail state
                if next_state is None and match and match.group(0):
                    raise RuntimeError('Lexer entered fail state.')
                
                # Only accept nonempty matches or matches where the state changes
                # Regexes that match the empty string always match, so perhaps only accept an empty match if it is the last rule and invalid ast otherwise
                if match and (match.group(0) or state != next_state):
                    index += len(match.group(0))
                    state = next_state
                    if token_name is not None:
                        out.append(Lexer._construct_token(token_name, expand_string, match))
                    found_match = True
                    break
            if not found_match:
                print()
                print('Lexer dump begin.')
                print('State: {:s}'.format(state))
                print('Stream: {!s:s}'.format(out))
                print('Unparsed input: {:s}'.format(content[index:]))
                print('Lexer dump end.')
                raise RuntimeError('Lexer failed to find a match.')

        return out

    def lex_file(self, file_name):
        content = Lexer._file_to_string(file_name)
        return self.lex(content)
        
    def save_table(self, file_name):
        validate_lexer_table(self.lexer_table)
        table_as_string = lexer_table_to_string(self.lexer_table)
        
        write_file = open(file_name, 'w')
        write_file.write(table_as_string)
        write_file.close()

    def _construct_token(token_name, expand_string, match):
        if expand_string is None:
            return (token_name, tuple())

        args_expand_strings = re.split('[ \t]*,[ \t]*', expand_string)
        args = tuple([match.expand(x) for x in args_expand_strings])
        return (token_name, args)

    def _file_to_string(file_name):
        assert isinstance(file_name, str)
        
        file = open(file_name, 'r')
        content = file.readlines()
        file.close()
        
        content = ''.join(content)
        return content

def parse_tree_to_ast(parse_tree):
    raise NotImplementedError
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
            assert token_name != 'Eat'        # This is from an old iteration where Eat was the symbol for 'output no nonterminal'
    
    # This is some failed attempt at asserting that there are no infinite loops due to empty productions
    # This is somewhat handled in a different level of the program
    # Also, this code was written several iterations ago
    # for regexes in lexer_table.values():
        # if len(regexes) > 1:
            # for regex, _, _ in regexes:
                # assert not re.match(regex, '')

if __name__ == '__main__':
    # This is an example of using the lexer
    # This program lexes sys.argv[2] using lexer from sys.argv[1]    
    
    # Get input
    if len(sys.argv) != 3:
        sys.stdout.write('You provided {:d} arguments. You must provide 2 arguments.'.format(len(sys.argv) - 1))
        sys.exit(1)
        
    # Aliases
    lexer_file_name = sys.argv[1]
    program_file_name = sys.argv[2]
    
    # Construct lexer
    ProgramLexer = LexerFactory.from_file(lexer_file_name)
    
    # Read file
    content_file = open(program_file_name, 'r')
    string_to_lex = content_file.readlines()
    content_file.close()
    string_to_lex = ''.join(string_to_lex)
    
    # Lex
    token_stream = ProgramLexer.lex(string_to_lex)
    
    # Print
    sys.stdout.write('\n')
    sys.stdout.write(' '.join([x[0] + str(x[1]) for x in token_stream]))
    sys.stdout.write('\n')