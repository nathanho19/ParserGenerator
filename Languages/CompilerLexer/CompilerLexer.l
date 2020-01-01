0 0 <_ERASE_> [ \t\r\n]+
0 0 <_ERASE_> #[^\r\n]+
0 5 <_ERASE_> /\*
0 1 BeginState(\1) ([A-Za-z0-9]+)[ \t]+
1 3 FailState Fail[ \t]+
1 2 EndState(\1) ([A-Za-z0-9]+)[ \t]+
2 3 WordWithExpandString(\1, \2) ((?:[A-Z][a-z]*)+)\(([^\(\)\t\r\n]*)\)[ \t]+
2 3 <_ERASE_> (?:<_ERASE_>)[ \t]+
2 3 Word(\1) ((?:[A-Z][a-z]*)+)[ \t]+
3 0 Regex() (?:<_ERASE_>)[\r\n]
3 4 Regex(\1) ([^\r\n]*[^ \t\r\n])
4 Fail [ \t]
4 0 <_ERASE_> <_ERASE_>
5 6 <_ERASE_> \*/
5 5 <_ERASE_> (a|[^a])
6 6 <_ERASE_> [ \t]
6 0 <_ERASE_> [\r\n]