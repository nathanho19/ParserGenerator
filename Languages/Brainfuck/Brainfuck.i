from collections import deque

def parse_tree_to_ast(parse_tree):
    node_type, children = parse_tree
    pattern = (node_type,) + tuple([x[0] for x in children])
    
    if node_type == 'Start':
        # Traverse the list using pointer
        current = parse_tree
        out = deque()
        while current[1][0][0] == 'Start':
            for token in parse_tree_to_ast(current[1][1])[::-1]:
                out.appendleft(token)
            current = current[1][0]
        
        # Handle last element
        for token in parse_tree_to_ast(current[1][0])[::-1]:
            out.appendleft(token)
        return tuple(out)
    if node_type == 'Expression':
        return handle_expression(parse_tree)

    print()
    print('Unhandled parse tree pattern: {:s}'.format(str(pattern)))
    raise NotImplementedError

def handle_expression(parse_tree):
    node_type, children = parse_tree
    pattern = (node_type,) + tuple([x[0] for x in children])

    assert node_type == 'Expression'
    
    if children[0][0] == 'Operation':
        return (children[0][1][0][0],)
    else:
        subtree = parse_tree_to_ast(children[1])
        return ('OpenBrackets',) + subtree + ('CloseBrackets',)

    print()
    print('Unhandled parse tree pattern: {:s}'.format(str(pattern)))
    raise NotImplementedError

def ast_to_string(ast):
    out = ''
    for token in ast:
        if token == 'OpenBrackets':
            out += '['
        elif token == 'CloseBrackets':
            out += ']'
        elif token == 'Plus':
            out += '+'
        elif token == 'Minus':
            out += '-'
        elif token == 'Left':
            out += '<'
        elif token == 'Right':
            out += '>'
        elif token == 'Read':
            out += ','
        elif token == 'Print':
            out += '.'
    return out

def interpret(ast, arg):
    memory = dict()
    loop_stack = deque()
    out = deque()
    
    memory_pointer = 0
    instruction_pointer = 0
    arg_pointer = 0
    
    while instruction_pointer < len(ast):
        instruction = ast[instruction_pointer]
        
        if instruction == 'OpenBrackets':
            if memory_pointer in memory and memory[memory_pointer] != 0:
                loop_stack.append(instruction_pointer)
                instruction_pointer += 1
            else:
                instruction_pointer += 1
                count = 1
                while count > 0:
                    if ast[instruction_pointer] == 'OpenBrackets':
                        count += 1
                    if ast[instruction_pointer] == 'CloseBrackets':
                        count -= 1
                    instruction_pointer += 1
            continue
        elif instruction == 'CloseBrackets':
            if memory_pointer in memory and memory[memory_pointer] != 0:
                loop_position = loop_stack[-1]
                instruction_pointer = loop_position + 1
            else:
                loop_stack.pop()
                instruction_pointer += 1
            continue
        elif instruction == 'Read':
            if arg_pointer < len(arg):
                val = ord(arg[arg_pointer])
                assert 0 <= val
                assert val <= 255
                
                # Convention: No filtering of input string
                memory[memory_pointer] = val
                arg_pointer += 1
            else:
                # Convention: Read EOF or after -> Set cell to 0
                memory[memory_pointer] = 0
            instruction_pointer += 1
            continue
        elif instruction == 'Print':
            if memory_pointer not in memory:
                out.append(chr(0))
            else:
                out.append(chr(memory[memory_pointer]))
            instruction_pointer += 1
            continue
        elif instruction == 'Left':
            memory_pointer -= 1
            
            # Convention: memory_pointer < 0 -> Abort
            if memory_pointer < 0:
                raise RuntimeError
            instruction_pointer += 1
            continue
        elif instruction == 'Right':
            # Convention: right unbounded memory
            memory_pointer += 1
            instruction_pointer += 1
            continue
        elif instruction == 'Plus':
            if memory_pointer not in memory:
                memory[memory_pointer] = 0
            # Convention: 8 bit memory
            memory[memory_pointer] = (memory[memory_pointer] + 1) % 256
            instruction_pointer += 1
            continue
        elif instruction == 'Minus':
            if memory_pointer not in memory:
                memory[memory_pointer] = 0
            # Convention: 8 bit memory
            memory[memory_pointer] = (memory[memory_pointer] - 1) % 256
            instruction_pointer += 1
            continue
        
        print()
        print('Instruction not supported: {:s}'.format(instruction))
        raise RuntimeError
    
    out = tuple(out)
    return ''.join(out)

def result_to_string(result):
    return result