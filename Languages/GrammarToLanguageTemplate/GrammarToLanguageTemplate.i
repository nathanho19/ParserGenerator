import Parser
import os
import re

def ast_to_string(ast):
    return str(ast)

def parse_tree_to_ast(parse_tree):
    node_type, children = parse_tree
    pattern = (node_type,) + tuple([x[0] for x in children])
    
    if node_type == 'MultipleNewLineDelimiter':
        return tuple()

    if node_type == 'Start':
        return tuple([x for child in children for x in parse_tree_to_ast(child)])
    if node_type == 'Declarations':
        return tuple([y for child in children for y in parse_tree_to_ast(child)])
    if node_type == 'Declaration':
        assert len(children) == 3

        assert children[0][0] == 'DeclarationLHS'
        assert children[1][0] == 'DeclarationAssignment'
        assert children[2][0] == 'DeclarationRHS'

        return tuple([(children[0][1][0][1][0], rhs) for rhs in DeclarationRHS_to_RHSs(children[2])])

    print()
    print('Unhandled parse tree pattern: {:s}'.format(str(pattern)))
    raise NotImplementedError

def handle_rule_rhs(parse_node):
    if parse_node[1][0][0] == 'EraseLexerToken':
        return tuple()
    else:
        return handle_symbol_sequence(parse_node[1][0])

def handle_symbol_sequence(parse_node):
    if len(parse_node[1]) == 1:
        return (parse_node[1][0][1][0],)
    else:
        return handle_symbol_sequence(parse_node[1][0]) + (parse_node[1][1][1][0],)

def DeclarationRHS_to_RHSs(parse_node):
    children = parse_node[1]
    if len(children) == 1:
        return (handle_rule_rhs(children[0]),)
    else:
        return DeclarationRHS_to_RHSs(children[0]) + (handle_rule_rhs(children[2]),)

def interpret(ast, arg):
    # Construct grammar from ast
    grammar = Parser.Grammar()
    for lhs, rhs in ast:
        grammar.add_rule(lhs, rhs)
    grammar.set_start_symbol('Start')
    grammar.finalize_rules()
    
    # Assert that grammar is parsable
    parser = Parser.CLR(grammar)
    parser.construct()
    
    # Create language directory
    try:
        os.makedirs('Languages/{0:s}/'.format(arg))
    except FileExistsError:
        pass
    
    # Write lexer file
    write_lexer_file = open('Languages/{0:s}/{0:s}.l'.format(arg), 'w')
    write_lexer_file.write('/*')
    write_lexer_file.write('\n * Terminals to lex:')
    write_lexer_file.write('\n *')
    for t in grammar.terminals():
        write_lexer_file.write('\n * {:s}'.format(t))
    write_lexer_file.write('\n */')
    write_lexer_file.write('\n\n')
    write_lexer_file.close()
    
    # Write grammar file
    grammar.save_rules('Languages/{0:s}/{0:s}.g'.format(arg))
    
    # Write interpreter file
    write_interpreter_file = open('Languages/{0:s}/{0:s}.i'.format(arg), 'w')
    
    # Write parse_tree_to_ast function
    write_interpreter_file.write('def parse_tree_to_ast(parse_tree):')
    write_interpreter_file.write('\n    node_type, children = parse_tree')
    write_interpreter_file.write('\n    pattern = (node_type,) + tuple([x[0] for x in children])')
    write_interpreter_file.write('\n')
    
    for lhs, rhs in grammar._rules:
        if lhs == grammar._augmented_start_symbol:
            continue

        if not rhs:
            rule_pattern = '(\'{:s}\',)'.format(lhs)
        else:
            rule_pattern = '(\'{:s}\', {:s})'.format(lhs, ', '.join(['\'{:s}\''.format(x) for x in rhs]))
        write_interpreter_file.write('\n    if pattern == {:s}:'.format(rule_pattern))
        write_interpreter_file.write('\n        raise NotImplementedError(\'Unhandled parse tree pattern: {:s}\')'.format(re.sub('\'', '\\\'', rule_pattern)))
    write_interpreter_file.write('\n\n    raise NotImplementedError(\'Unhandled parse tree pattern: {!s:s}\'.format(pattern))')
    
    # Write interpret function
    write_interpreter_file.write('\n\ndef interpret(ast, arg):')
    write_interpreter_file.write('\n    raise NotImplementedError')
    write_interpreter_file.write('\n    return None')
    
    # Write ast_to_string function
    write_interpreter_file.write('\n\ndef ast_to_string(ast):')
    write_interpreter_file.write('\n    raise NotImplementedError')
    write_interpreter_file.write('\n    return str(ast)')
    write_interpreter_file.write('\n    return ast')
    
    # Write result_to_string function
    write_interpreter_file.write('\n\ndef result_to_string(result):')
    write_interpreter_file.write('\n    raise NotImplementedError')
    write_interpreter_file.write('\n    return str(result)')
    write_interpreter_file.write('\n    return result')
    
    write_interpreter_file.close()
    
    return 'Success'

def result_to_string(result):
    return str(result)
