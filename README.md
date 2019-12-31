How do I write my own programming language?
See doc/WritingYourOwnProgrammingLanguage.md

What are all these new file formats?
The file formats and their usual extensions are as follows:
	lexer description = .l
	lexer code = .lc
	grammar description = .g
	grammar code = .gc
	parser table = .pt
	interpreter = .i
File extensions are only by convention. However, currently, the compiler recognizes file formats by file extension.

I'm a power user. What can I do?
You can go into Compiler.py and Lexer.py to turn verbose logging on and off through the DEBUG variable. You can go into Compiler.py and change the file search locations. You can read about the inner workings of Compiler in Compiler.py, Parser.py, and Lexer.py. The backend file dependencies described in doc/BackendDetails.md. You can carefully modify those files directly to compile new types of lexer descriptions and grammar descriptions and interpreters.