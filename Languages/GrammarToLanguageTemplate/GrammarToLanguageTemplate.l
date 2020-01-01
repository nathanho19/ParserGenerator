0 0 <_ERASE_> [ \t]+
0 0 DeclarationAssignment =
0 0 DeclarationRHSOr \|
0 0 EraseLexerToken (?:<_ERASE_>)
0 0 SingleNewLineDelimiter [\r\n]
0 0 Word(\1) ((?:[A-Z][a-z]*)+)