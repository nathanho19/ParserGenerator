import Parser

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
    return ast_to_grammar(ast)

def ast_to_grammar(ast):
    grammar = Parser.Grammar()
    for lhs, rhs in ast:
        grammar.add_rule(lhs, rhs)
    grammar.set_start_symbol('Start')
    grammar.finalize_rules()
    return grammar

def result_to_string(result):
    return Parser.Grammar.rules_to_string(result)