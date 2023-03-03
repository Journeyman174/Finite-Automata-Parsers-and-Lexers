from __future__ import annotations


from src.BTree import buildExpTree
from src.NFA import SPECIAL


class Parser:
    # This function should:
    # -> Classify input as either character(or string) or operator
    # -> Convert special inputs like [0-9] to their correct form
    # -> Convert escaped characters
    # You can use Character and Operator defined in Regex.py
    @staticmethod
    def preprocess(regex: str) -> list:
        pass

    # This function should construct a prenex expression out of a normal one.
    @staticmethod
    def toPrenex(s: str) -> str:
        aux = ""
        l = list(s)
        while len(l):
            c = l.pop(0)
            if c == "'":
                aux += SPECIAL.get(l[0], l[0])
                l = l[2:]
            else:
                aux += c
        s = aux
        s = s.replace("[0-9]", SPECIAL.get("[0-9]"))
        s = s.replace("[a-z]", SPECIAL.get("[a-z]"))
        s = s.replace("[A-Z]", SPECIAL.get("[A-Z]"))
        if s == "eps" or s == "void":
            return s
        s = '(' + s + ')'
        tree = buildExpTree(s)
        res = str(tree)
        return res
