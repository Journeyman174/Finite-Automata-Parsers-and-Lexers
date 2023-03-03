from typing import Tuple, List, Dict, Union
from DFA import DFA
from Parser import Parser


class Lexer:

    """
        This constructor initializes the lexer with a configuration
        The configuration is passed as a dictionary TOKEN -> REGEX

        You are encouraged to use the functions from the past stages to parse the regexes
    """
    def __init__(self, configurations: Dict[str, str]) -> None:
        self.machines = {key: DFA.fromPrenex(Parser.toPrenex(regex)) for key, regex in configurations.items()}

    """
        The main functionality of the lexer, receives a word and lexes it
        according to the provided configuration.

        The return value is either a List of tuples (TOKEN, LEXEM) if the lexer succedes
        or a string message if the lexer fails
    """

    # noinspection PyCompatibility
    def lex(self, word: str) -> Union[List[Tuple[str, str]], str]:
        consumed = ""
        result = []

        while consumed != word:
            step = [(key, dfa.getLongestPrefix(word[len(consumed):])) for key, dfa in self.machines.items()]

            res = ""
            key = ""
            for t in step:
                machine = t[0]
                prefix = t[1]
                if len(prefix) > len(res):
                    res = prefix
                    key = machine
            if res == "":
                char_count = len(consumed) + max([dfa.consumed for _, dfa in self.machines.items()])
                line = word[:char_count].count("\n")
                last_endl = char_count - 1 - word[:char_count][::-1].find("\n")
                if char_count == len(word):
                    return f"No viable alternative at character EOF, line {line}"
                else:
                    return f"No viable alternative at character {last_endl}, line {line}"
            result.append((key, res))
            consumed += res

        return result
