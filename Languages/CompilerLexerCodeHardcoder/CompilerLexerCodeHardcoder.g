Start = Start Transition | Transition

Transition = BeginState FailState Regex
Transition = BeginState EndState Regex
Transition = BeginState EndState Word Regex
Transition = BeginState EndState WordWithExpandString Regex