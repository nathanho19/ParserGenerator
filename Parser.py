import os
assert 'ERASE_SYMBOL' in os.environ
ERASE_SYMBOL = os.environ['ERASE_SYMBOL']

from collections import deque

END_OF_FILE_SYMBOL = '<_END_OF_FILE_SYMBOL_>'

class Grammar:
    def __init__(self):
        # Grammar sets
        self._rules = []
        self._start_symbol = None
        self._augmented_start_symbol = None
        self._first_sets = None
        self._nonterminals_cache = None
        self._rhs_symbols_cache = None
        self._terminals_cache = None
        self._rules_by_lhs = dict()

        # Flags
        self._grammar_is_finalized = False

    def _construct_rule(lhs, rhs):
        assert isinstance(lhs, str)
        assert lhs

        for i in range(len(rhs)):
            assert isinstance(rhs[i], str)
        for i in range(len(rhs)):
            assert rhs[i]
            assert rhs[i] != ERASE_SYMBOL

        assert isinstance(rhs, tuple) or isinstance(rhs, list)

        return (lhs, tuple(rhs))

    def erase(self, lhs):
        # Check flags
        assert not self._grammar_is_finalized

        new_rule = Grammar._construct_rule(lhs, tuple())
        self._rules.append(new_rule)

        # Flush memoization of dependent data
        self._nonterminals_cache = None
        self._rhs_symbols_cache = None
        self._terminals_cache = None

        self._rules_by_lhs.pop(lhs, None)

    def add_rule(self, lhs, rhs):
        # Check flags
        assert not self._grammar_is_finalized

        new_rule = Grammar._construct_rule(lhs, rhs)
        self._rules.append(new_rule)

        # Flush memoization of dependent data
        self._nonterminals_cache = None
        self._rhs_symbols_cache = None
        self._terminals_cache = None

        self._rules_by_lhs.pop(lhs, None)

    def rule_to_string(rule):
        out = ''
        out += rule[0]
        if rule[1]:
            out += ' = '
            out += ' '.join(rule[1])
        else:
            out += ' Erase'
        return out

    def rules_to_string(self):
        if not self._grammar_is_finalized:
            self._sort_rules()
        
        out = ''
        for rule in self._rules:
            out += Grammar.rule_to_string(rule)
            out += '\n'
        return out

    # Excludes empty string and end of file
    def rhs_symbols(self):
        if self._rhs_symbols_cache is not None:
            return self._rhs_symbols_cache

        symbols = [symbol for _, rhs in self._rules for symbol in rhs]		# Gather symbols
        symbols = set(symbols)		# Remove duplicates
        symbols = sorted(symbols)		# Sort
        symbols = tuple(symbols)

        self._rhs_symbols_cache = symbols
        return symbols

    # Does not exclude self._start_symbol and self._augmented_start_symbol
    def nonterminals(self):
        if self._nonterminals_cache is not None:
            return self._nonterminals_cache

        symbols = [lhs for lhs, _ in self._rules]		# Gather symbols
        symbols = set(symbols)		# Remove duplicates
        symbols = sorted(symbols)		# Sort
        symbols = tuple(symbols)

        self._nonterminals_cache = symbols
        return symbols

    # Excludes empty string and end of file
    def terminals(self):
        if self._terminals_cache is not None:
            return self._terminals_cache

        out = [x for x in self.rhs_symbols() if x not in self.nonterminals()]
        out = tuple(out)

        self._terminals_cache = out
        return out

    # Augmented production rule is self._augmented_start_symbol = self.designated_start_symbol
    def set_start_symbol(self, start_symbol):
        # Check flags
        assert not self._grammar_is_finalized

        self._start_symbol = start_symbol

    def finalize_rules(self):
        # Check flags
        assert not self._grammar_is_finalized

        # Set self._augmented_start_symbol to a symbol not in the grammar
        _augmented_start_symbol_nonce_alphabet = '0123456789'
        candidate__augmented_start_symbol_nonces = deque(_augmented_start_symbol_nonce_alphabet)
        _augmented_start_symbol_format_string = '<_AUGMENTED_START_{:s}_>'
        while True:
            # Generate new symbol
            candidate_nonce = candidate__augmented_start_symbol_nonces.popleft()
            candidate__augmented_start_symbol = _augmented_start_symbol_format_string.format(candidate_nonce)

            # If not in the grammar, set and exit loop
            if candidate__augmented_start_symbol not in self.nonterminals():
                if candidate__augmented_start_symbol not in self.rhs_symbols():
                    self._augmented_start_symbol = candidate__augmented_start_symbol
                    break

            # If in the grammar, recursively generate new symbols
            for symbol in _augmented_start_symbol_nonce_alphabet:
                candidate__augmented_start_symbol_nonces.append(candidate_nonce + symbol)

        # Add augmented start production
        self._rules.append(Grammar._construct_rule(self._augmented_start_symbol, (self._start_symbol,)))

        # Flush memoization of dependent data
        self._nonterminals_cache = None
        self._rhs_symbols_cache = None
        self._terminals_cache = None

        # Simplify productions
        self._remove_unreachable_rules()

        self._sort_rules()

        # Assertions
        self._assert_grammar_is_augmented()

        # Set flags
        self._grammar_is_finalized = True

        # Compute grammar sets
        self._compute_first()

    def _sort_rules(self):
        # Check flags
        assert not self._grammar_is_finalized

        self._rules = tuple(sorted(set(self._rules)))

    def _remove_unreachable_rules(self):
        # Check flags
        assert not self._grammar_is_finalized

        while True:
            unseen_nonterminals = [lhs for lhs in self.nonterminals() if lhs != self._augmented_start_symbol and lhs not in self.rhs_symbols()]
            if unseen_nonterminals:
                self._rules = [rule for rule in self._rules if rule.lhs not in unseen_nonterminals]
            else:
                break

    def _assert_grammar_is_augmented(self):
        # Nothing produces self._augmented_start_symbol
        assert self._augmented_start_symbol is not None
        assert self._augmented_start_symbol not in self.rhs_symbols()

        # self._augmented_start_symbol has one rule
        augmented_start_rules = [rule for rule in self._rules if rule[0] == self._augmented_start_symbol]
        assert len(augmented_start_rules) == 1

        # self._augmented_start_symbol produces one symbol
        rhs = augmented_start_rules[0][1]
        assert len(rhs) == 1

        # self._augmented_start_symbol produces a nonterminal
        rhs_term = rhs[0]
        assert rhs_term in self.nonterminals()

    def _compute_first(self):
        # Check flags
        assert self._grammar_is_finalized
        
        self._first_sets = dict()

        for lhs in self.rhs_symbols():
            self._first_sets[lhs] = set()

        # Rule
        for t in self.terminals():
            self._first_sets[t].add(t)

        # Rule
        for lhs in self.nonterminals():
            if lhs != self._augmented_start_symbol:
                for rhs in [rhs for x, rhs in self._rules if x == lhs]:
                    if not rhs:
                        self._first_sets[lhs].add(ERASE_SYMBOL)
                    elif rhs[0] in self.terminals():
                        self._first_sets[lhs].add(rhs[0])

        run_loop = True
        while run_loop:
            run_loop = False
            for lhs in self.nonterminals():
                if lhs != self._augmented_start_symbol:
                    for rhs in [rhs for x, rhs in self._rules if x == lhs]:
                        counter = 0
                        while counter < len(rhs) and ERASE_SYMBOL in self._first_sets[rhs[counter]]:
                                counter += 1

                        # Rule
                        before = len(self._first_sets[lhs])
                        if counter == len(rhs):
                            self._first_sets[lhs].add(ERASE_SYMBOL,)
                        else:
                            self._first_sets[lhs].update(self._first_sets[rhs[counter]])
                        after = len(self._first_sets[lhs])
                        if before < after:
                            run_loop = True

    def print_first(self):
        # Check flags
        assert self._grammar_is_finalized
        
        set_to_print = self._first_sets.keys()

        set_to_print &= self.nonterminals()		# First of a terminal is not interesting

        for k in set_to_print:
            print('FIRST( {:s} )  = {{{:s}}}'.format(k, ', '.join(self.first((k,)))))

    # Sequence is a list of symbols
    def first(self, sequence):
        # Check flags
        assert self._grammar_is_finalized
        
        if len(sequence) == 0:
            raise ValueError('Tried to take first of the empty sequence')
            # return set((ERASE_SYMBOL,))
        elif len(sequence) == 1:
            if sequence[0] in self.nonterminals():
                return tuple(sorted(self._first_sets[sequence[0]]))
            else:
                return (sequence[0],)
        elif ERASE_SYMBOL in self._first_sets[sequence[0]]:
            return tuple(sorted((self._first_sets[sequence[0]] - set((ERASE_SYMBOL,))) | self.first(sequence[1:])))
        else:
            return tuple(sorted(self._first_sets[sequence[0]] - set((ERASE_SYMBOL,))))

    def rhs_of_rules_by_lhs(self, lhs):
        # Check flags
        assert self._grammar_is_finalized
        
        if lhs in self._rules_by_lhs:
            return self._rules_by_lhs[lhs]

        out = [rhs for x, rhs in self._rules if x == lhs]
        out = sorted(out)
        out = tuple(out)
        self._rules_by_lhs[lhs] = out
        return out

    def save_rules(self, file_name):
        assert file_name
        assert file_name[-1] != '/' and file_name[-1] != '\\'
        assert self._grammar_is_finalized
    
        # Compute string representation of rules
        write_string = ''
        for rule in self._rules:
            if rule[0] != self._augmented_start_symbol:
                if write_string:
                    write_string += '\n'
                write_string += rule[0]
                write_string += ' = '
                if rule[1]:
                    write_string += ' '.join(rule[1])
                else:
                    write_string += ERASE_SYMBOL
                    
        try:
            os.makedirs(os.path.dirname(file_name))
        except FileExistsError:
            pass
                
        # Write rules
        write_file = open(file_name, 'w')
        write_file.write(write_string)
        write_file.close()
        
        # Assert that saved rules match current rules
        import Compiler
        other = Compiler.program('CompilerParser', file_name, '')
        assert other._rules == self._rules

class CLR:
    def __init__(self, grammar):
        self.grammar = grammar

    def construct(self):
        assert self.grammar._grammar_is_finalized

        automaton, goto_memoization = self.compute_automaton()
        
        self.tables = self.compute_tables(automaton, goto_memoization)
        self.automaton = automaton
        self.goto_memoization = goto_memoization

    def create_item(lhs, rhs, lookahead):
        assert isinstance(rhs, tuple)
        assert ERASE_SYMBOL not in rhs

        return (lhs, tuple(), rhs, lookahead)

    def progress_item(item):
        lhs, alpha, bbeta, lookahead = item
        return (lhs, alpha + (bbeta[0],), bbeta[1:], lookahead)

    def print_item(item):
        lhs, alpha, bbeta, lookahead = item
        print('{:s} = {:s}. {:s}, {:s}'.format(lhs, ''.join([x + ' ' for x in alpha]), ''.join([x + ' ' for x in bbeta]), lookahead))

    def print_state(state):
        for item in state:
            CLR.print_item(item)

    def closure(self, state):
        if state in self.closure_memoization:
            return self.closure_memoization[state] + tuple()

        seen_items = set(state)
        out = deque(state)
        unprocessed_items = deque(state)

        i = 0
        while unprocessed_items:
            _, _, bbeta, lookahead = unprocessed_items.popleft()
            if bbeta and bbeta[0] in self.grammar.nonterminals():
                if (bbeta, lookahead) in self.closure_memoization2:
                    additional_items = self.closure_memoization2[(bbeta, lookahead)]
                else:
                    additional_items = set()
                    for rule in self.grammar.rhs_of_rules_by_lhs(bbeta[0]):
                        for t in self.grammar.first(bbeta[1:] + (lookahead,)):
                            new_item = CLR.create_item(bbeta[0], rule, t)
                            additional_items.add(new_item)
                    additional_items = tuple(sorted(additional_items))
                    self.closure_memoization2[(bbeta, lookahead)] = additional_items

                for new_item in additional_items:
                    if new_item not in seen_items:
                        seen_items.add(new_item)
                        out.append(new_item)
                        unprocessed_items.append(new_item)

        out = tuple(out)
        self.closure_memoization[state] = out
        return out + tuple()

    def goto(self, state, next_symbol):
        out = deque()
        seen_items = set()
        for (lhs, alpha, bbeta, lookahead) in state:
            if bbeta and bbeta[0] == next_symbol:
                next_item = CLR.progress_item((lhs, alpha, bbeta, lookahead))
                if next_item not in seen_items:
                    out.append(next_item)
                    seen_items.add(next_item)
        out = self.closure(tuple(out))
        return out

    def compute_automaton(self):
        self.closure_memoization = dict()
        self.closure_memoization2 = dict()
        goto_memoization = dict()

        augmented_start_item = CLR.create_item(self.grammar._augmented_start_symbol, tuple(self.grammar.rhs_of_rules_by_lhs(self.grammar._augmented_start_symbol))[0], END_OF_FILE_SYMBOL)
        augmented_start_state = (augmented_start_item,)
        augmented_start_state_closed = self.closure(augmented_start_state)
        automaton = [augmented_start_state_closed]

        i = 0
        while i < len(automaton):
            nexts = sorted(set([item[2][0] for item in automaton[i] if item[2]]))
            if nexts:
                goto_memoization[i] = dict()
            for b in nexts:
                candidate_state = self.goto(automaton[i], b)
                if candidate_state not in automaton:
                    goto_memoization[i][b] = len(automaton)
                    automaton += [candidate_state]
                else:
                    goto_memoization[i][b] = automaton.index(candidate_state)
            i += 1

        del self.closure_memoization
        del self.closure_memoization2
        return tuple(automaton), goto_memoization

    def print_automaton(self):
        for i, state in enumerate(self.automaton):
            print()
            print('I_{:d}:'.format(i))
            CLR.print_state(state)

    def print_gotos(self):
        print()
        for i in self.goto_memoization:
            for lookahead in self.goto_memoization[i]:
                print('GOTO( I_{:d} , {:s} ) = I_{:d}'.format(i, lookahead, self.goto_memoization[i][lookahead]))

    def print_gotos_inverse(self):
        # Compute inverse
        goto_inverse = dict()
        for state_number in self.goto_memoization:
            for lookahead in self.goto_memoization[state_number]:
                if self.goto_memoization[state_number][lookahead] not in goto_inverse:
                    goto_inverse[self.goto_memoization[state_number][lookahead]] = deque()
                goto_inverse[self.goto_memoization[state_number][lookahead]].append((state_number, lookahead))
        
        # Print inverse
        print()
        for state_number in goto_inverse:
            print('I_{:d} = {:s}'.format(state_number, ' = '.join(['GOTO( I_{:d} , {:s} )'.format(a, b) for a, b in goto_inverse[state_number]])))

    def compute_tables(self, automaton, goto_memoization):
        shift_table = dict()
        reduce_table = dict()
        goto_table = dict()

        # Rule 2a
        for state_number in range(len(automaton)):
            for (lhs, alpha, bbeta, lookahead) in automaton[state_number]:
                if bbeta and bbeta[0] in self.grammar.terminals():
                    if state_number not in shift_table:
                        shift_table[state_number] = dict()
                    shift_table[state_number][bbeta[0]] = goto_memoization[state_number][bbeta[0]]

        # Rule 2b
        for state_number in range(len(automaton)):
            for (lhs, alpha, bbeta, lookahead) in automaton[state_number]:
                if not bbeta:
                    if state_number not in reduce_table:
                        reduce_table[state_number] = dict()
                    if lookahead not in reduce_table[state_number]:
                        reduce_table[state_number][lookahead] = deque()
                    reduce_table[state_number][lookahead].append((lhs, alpha))

        # Rule 3
        for state_number in range(len(automaton)):
            for (lhs, alpha, bbeta, lookahead) in automaton[state_number]:
                if len(bbeta) > 0 and bbeta[0] in self.grammar.nonterminals():
                    if state_number not in goto_table:
                        goto_table[state_number] = dict()
                    goto_table[state_number][bbeta[0]] = goto_memoization[state_number][bbeta[0]]

        # Search for conflicts
        conflicts = deque()
        for state_number in reduce_table:
            for lookahead in reduce_table[state_number]:
                actions = deque()
                if state_number in shift_table and lookahead in shift_table[state_number]:
                    actions.append('Shift {:d}'.format(shift_table[state_number][lookahead]))
                for lhs, rhs in reduce_table[state_number][lookahead]:
                    actions.append('Reduce {:s} = {:s}'.format(lhs, str(rhs)))
                if len(actions) > 1:
                    conflicts.append((state_number, lookahead, actions))
        
        if conflicts:
            self.print_automaton()
            # self.print_gotos()
            self.print_gotos_inverse()
            
            # Compute goto inverse
            goto_inverse = dict()
            for state_number in goto_memoization:
                for lookahead in goto_memoization[state_number]:
                    if goto_memoization[state_number][lookahead] not in goto_inverse:
                        goto_inverse[goto_memoization[state_number][lookahead]] = deque()
                    goto_inverse[goto_memoization[state_number][lookahead]].append((state_number, lookahead))
            
            for i, (state_number, lookahead, actions) in enumerate(conflicts):
                # Print state information about the conflict
                print()
                print('Conflict {:d} in I_{:d}, {:s}'.format(i, state_number, lookahead))
                
                # Print conflicting actions
                for action in actions:
                    print(action)
                
                # Print inputs that trigger the conflict
                count = 0
                MAX_COUNT = 10
                states = deque(((state_number, lookahead, set((state_number,))),))
                while states and count < MAX_COUNT:
                    state_number, suffix, seen_states = states.popleft()
                    for previous_state_number, lookahead in goto_inverse[state_number]:
                        if lookahead in self.grammar.terminals():
                            new_suffix = lookahead + suffix
                        else:
                            new_suffix = suffix
                        if previous_state_number == 0:
                            print('Input: {:s}'.format(new_suffix))
                            count += 1
                            if MAX_COUNT <= count:
                                break
                        elif previous_state_number not in seen_states:
                            new_set = set(seen_states)
                            assert new_set is not seen_states
                            new_set.add(previous_state_number)
                            states.append((previous_state_number, new_suffix, new_set))

            print()
            raise RuntimeError('Grammar is not LR(1).')

        # Finalize table
        for state_number in reduce_table:
            for lookahead in reduce_table[state_number]:
                assert isinstance(reduce_table[state_number][lookahead], deque)
                assert len(reduce_table[state_number][lookahead]) == 1
                reduce_table[state_number][lookahead] = reduce_table[state_number][lookahead][0]

        return shift_table, reduce_table, goto_table

    def save_tables(self, file_name):
        write_file = open(file_name, 'w')
        for state_number in self.tables[0]:
            for t in self.tables[0][state_number]:
                write_file.write('s {:d} {:d} {:d}\n'.format(state_number, self.grammar.terminals().index(t), self.tables[0][state_number][t]))
        for state_number in self.tables[1]:
            for t in self.tables[1][state_number]:
                rule = self.tables[1][state_number][t]
                lhs, rhs = rule
                if t == END_OF_FILE_SYMBOL:
                    terminal_number = 0
                else:
                    terminal_number = 1 + self.grammar.terminals().index(t)
                write_file.write('r {:d} {:d} {:d}\n'.format(state_number, terminal_number, self.grammar._rules.index(rule)))
        for state_number in self.tables[2]:
            for nt in self.tables[2][state_number]:
                write_file.write('g {:d} {:d} {:d}\n'.format(state_number, self.grammar.nonterminals().index(nt), self.tables[2][state_number][nt]))
        write_file.close()

    def load_tables(self, file_name):
        read_file = open(file_name, 'r')
        content = read_file.readlines()
        read_file.close()

        content = [x.strip() for x in content]
        content = [x.split(' ') for x in content]
        content = [[x[0]] + [int(y) for y in x[1:]] for x in content]

        shift_table = dict()
        reduce_table = dict()
        goto_table = dict()

        for action, state_number, symbol_number, table_entry in content:
            if action == 's':
                if state_number not in shift_table:
                    shift_table[state_number] = dict()
                shift_table[state_number][self.grammar.terminals()[symbol_number]] = table_entry
            elif action == 'r':
                if symbol_number == 0:
                    terminal = END_OF_FILE_SYMBOL
                else:
                    terminal = self.grammar.terminals()[symbol_number - 1]
                if state_number not in reduce_table:
                    reduce_table[state_number] = dict()
                lhs, rhs = self.grammar._rules[table_entry]
                reduce_table[state_number][terminal] = (lhs, rhs)
            elif action == 'g':
                if state_number not in goto_table:
                    goto_table[state_number] = dict()
                goto_table[state_number][self.grammar.nonterminals()[symbol_number]] = table_entry
            else:
                raise RuntimeError


        self.tables = shift_table, reduce_table, goto_table

    def print_tables(self):
        print()
        for state_number in self.tables[0]:
            for t in self.tables[0][state_number]:
                print('ACTION [ {:d} , {:s} ] = SHIFT {:d}'.format(state_number, t, self.tables[0][state_number][t]))
                
        print()
        for state_number in self.tables[1]:
            for t in self.tables[1][state_number]:
                lhs, rhs = self.tables[1][state_number][t]
                print('ACTION [ {:d} , {:s} ] = REDUCE {:s} = {:s}'.format(state_number, t, lhs, ' '.join(rhs)))
                
        print()
        for state_number in self.tables[2]:
            for nt in self.tables[2][state_number]:
                print('GOTO [ {:d} , {:s} ] = {:d}'.format(state_number, nt, self.tables[2][state_number][nt]))

    def parse(self, token_stream):
        # Assert token_stream is valid
        for item in token_stream:
            assert isinstance(item, tuple)
            assert len(item) == 2
            terminal_name, args = item
            assert terminal_name
            assert isinstance(terminal_name, str)
            assert isinstance(args, tuple)
            assert terminal_name in self.grammar.terminals()

        # Aliases for tables
        shift_table, reduce_table, goto_table = self.tables

        # Append end of file symbol to input token_stream
        token_stream = list(token_stream)
        if not token_stream or token_stream[-1][0] != END_OF_FILE_SYMBOL:
            token_stream.append((END_OF_FILE_SYMBOL, tuple()))
        assert sum(1 for x in token_stream if x[0] == END_OF_FILE_SYMBOL)

        # Parser initial state
        stack = deque((0,))
        token_stream = deque(token_stream)
        out = deque()

        # While there is more to parse
        while len(token_stream) != 1 or len(stack) != 2 or stack[-1] != self.grammar._augmented_start_symbol:
            if stack[-1] in shift_table:
                if token_stream[0][0] in shift_table[stack[-1]]:
                    # Shift
                    next_state = shift_table[stack[-1]][token_stream[0][0]]
                    stack.append(token_stream.popleft())
                    stack.append(next_state)
                    out.append('Shift')
                    continue

            if stack[-1] in reduce_table:
                if token_stream[0][0] in reduce_table[stack[-1]]:
                    # Reduce
                    # Find rule
                    lhs, rhs = reduce_table[stack[-1]][token_stream[0][0]]
                    # Pop from stack
                    children = deque()
                    for _ in rhs:
                        stack.pop()
                        children.appendleft(stack.pop())
                    children = tuple(children)

                    # Accept
                    if len(token_stream) == 1 and lhs == self.grammar._augmented_start_symbol:
                        out.append('Accept')
                        stack.append((lhs, children))
                        return out, stack, token_stream

                    # Goto
                    next_state = goto_table[stack[-1]][lhs]
                    stack.append((lhs, children))
                    stack.append(next_state)
                    out.append('Reduce {:s} = {:s}'.format(lhs, ' '.join(rhs)))
                    continue

            out.append('Error')
            return out, stack, token_stream

        raise RuntimeError

    def parse_output_to_parse_tree(self, parse_output):
        stack = parse_output[1]
        assert parse_output[0][-1] == 'Accept'
        
        assert len(stack[-1]) == 2
        assert stack[-1][0] == self.grammar._augmented_start_symbol
        assert len(stack[-1][1]) == 1
        assert len(stack[-1][1][0]) == 2
        assert stack[-1][1][0][0] == self.grammar._start_symbol

        return stack[-1][1][0]
