Declaration = DeclarationLHS DeclarationAssignment DeclarationRHS
DeclarationLHS = Word
DeclarationRHS = DeclarationRHS DeclarationRHSOr RuleRHS
DeclarationRHS = RuleRHS
Declarations = Declaration
Declarations = Declarations MultipleNewLineDelimiter Declaration
MultipleNewLineDelimiter = MultipleNewLineDelimiter SingleNewLineDelimiter
MultipleNewLineDelimiter = SingleNewLineDelimiter
RuleRHS = EraseLexerToken
RuleRHS = SymbolSequence
Start = <_ERASE_>
Start = Declarations
Start = Declarations MultipleNewLineDelimiter
Start = MultipleNewLineDelimiter
Start = MultipleNewLineDelimiter Declarations
Start = MultipleNewLineDelimiter Declarations MultipleNewLineDelimiter
SymbolSequence = SymbolSequence Word
SymbolSequence = Word