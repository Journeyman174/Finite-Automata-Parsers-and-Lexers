from typing import Callable, Generic, TypeVar, Tuple
import string

S = TypeVar("S")
T = TypeVar("T")

SPECIAL = {         # encode special STRINGS into EMOJI so that they are differentiated when parsing a REJEX
    ")": "👺",
    "(": "😈",
    "*": "💀",
    "+": "👽",
    " ": "👻",
    "[A-Z]": "🥨",
    "[a-z]": "🌯",
    "[0-9]": "🥚",
}

class NFA(Generic[S]):

    def __init__(self, states, alphabet, delta, initState, finalStates):
        self.states = states
        self.alphabet = alphabet
        self.delta = delta
        self.initState = initState
        self.finalStates = finalStates

    def map(self, f: Callable[[S], T]) -> 'NFA[T]':
        deltaMap = {}
        deltaCopy = self.delta.copy()
        for (s, c) in self.delta:
            sd = deltaCopy[(s, c)]
            del deltaCopy[(s, c)]
            nextstates = {f(x) for x in sd}
            deltaMap[(f(s), c)] = nextstates
        
        statesMap = {f(s) for s in self.states}
        alphaMap = self.alphabet
        initMap = f(self.initState)
        finalMap = {f(s) for s in self.finalStates}

        return NFA[T](statesMap, alphaMap, deltaMap, initMap, finalMap)

    def next(self, from_state: S, on_chr: str) -> 'set[S]':
        for key in self.delta:
            if key == (from_state, on_chr):
                return self.delta[key]
        return set()

    def getStates(self) -> 'set[S]':
        return self.states

    def acceptsFromState(self, str: str, state: S, steps: int) -> bool:
        if steps == 100: 
            return False
        if self.isFinal(state) and str == "":
            return True
        if len(str) > 0:
            for s in self.next(state, "eps"):
                if self.acceptsFromState(str, s, steps + 1) :
                    return True
            for s in self.next(state, str[0]):
                if self.acceptsFromState(str[1:], s, steps + 1) : 
                    return True    
        return False

    def accepts(self, str: str) -> bool:
        return self.acceptsFromState(str, self.initState, 0)

    def isFinal(self, state: S) -> bool:
        return state in self.finalStates

    def getEpsClosure(self, state: S, visited: set) -> 'set[S]':
        visited.add(state)
        for s in self.next(state, "eps"):
            if s not in visited:
                self.getEpsClosure(s, visited)
        return visited

    @staticmethod
    def process(stack: list[str], index=0) -> Tuple['NFA[int]', int]:
        p = stack.pop(0)
        states: set = set()
        alphabet: set = set()
        delta: dict = {}
        init_s: int
        final_s: set = set()

        if p == "UNION":
            start = index
            finish = index + 1

            n1, index = NFA.process(stack, index + 2)
            n1_s = n1.initState
            n1_f = n1.finalStates.copy().pop()

            n2, index = NFA.process(stack, index)
            n2_s = n2.initState
            n2_f = n2.finalStates.copy().pop()

            states.add(start)
            states.add(finish)
            states.update(n1.states)
            states.update(n2.states)

            alphabet.update(n1.alphabet)
            alphabet.update(n2.alphabet)

            delta.update({
                (start, "eps"): {n1_s, n2_s},
                (n1_f, "eps"): {finish} | n1.delta.get((n1_f, "eps"), set()),
                (n2_f, "eps"): {finish} | n2.delta.get((n2_f, "eps"), set())
            })
            delta.update(n1.delta)
            delta.update(n2.delta)

            init_s = start
            final_s.add(finish)

        elif p == "CONCAT":
            n1, index = NFA.process(stack, index + 2)
            n1_s = n1.initState
            n1_f = n1.finalStates.copy().pop()

            n2, index = NFA.process(stack, index + 2)
            n2_s = n2.initState
            n2_f = n2.finalStates.copy().pop()

            states.update(n1.states)
            states.update(n2.states)

            alphabet.update(n1.alphabet)
            alphabet.update(n2.alphabet)

            delta.update({
                (n1_f, "eps"): {n2_s} | n1.delta.get((n1_f, "eps"), set()),
            })
            delta.update(n1.delta)
            delta.update(n2.delta)

            init_s = n1_s
            final_s.add(n2_f)

        elif p == "STAR":
            start = index
            finish = index + 1

            n, index = NFA.process(stack, index + 2)
            n_s = n.initState
            n_f = n.finalStates.copy().pop()

            states.update({start, finish})
            states.update(n.states)

            alphabet.update(n.alphabet)

            delta.update({
                (start, "eps"): {n_s, finish},
                (n_f, "eps"): {n_s, finish} | n.delta.get((n_f, "eps"), set())
            })
            delta.update(n.delta)

            init_s = start
            final_s.add(finish)

        elif p == "MAYBE":
            start = index
            finish = index + 1

            n, index = NFA.process(stack, index + 2)
            n_s = n.initState
            n_f = n.finalStates.copy().pop()

            states.update({start, finish})
            states.update(n.states)

            alphabet.update(n.alphabet)

            delta.update({
                (start, "eps"): {n_s, finish},
                (n_f, "eps"): {finish} | n.delta.get((n_f, "eps"), set())
            })
            delta.update(n.delta)

            init_s = start
            final_s.add(finish)

        elif p == "PLUS":
            start = index
            finish = index + 1

            n, index = NFA.process(stack, index + 2)
            n_s = n.initState
            n_f = n.finalStates.copy().pop()

            states.update({start, finish})
            states.update(n.states)

            alphabet.update(n.alphabet)

            delta.update({
                (start, "eps"): {n_s},
                (n_f, "eps"): {n_s, finish} | n.delta.get((n_f, "eps"), set())
            })
            delta.update(n.delta)

            init_s = start
            final_s.add(finish)

        elif p == "[0-9]":
            start = index
            finish = index + 1
            index += 2

            states.add(start)
            states.add(finish)

            alphabet.update(list("0123456789"))

            delta.update({
                (start, c): {finish} for c in "0123456789"
            })

            init_s = start
            final_s.add(finish)

        elif p == "[a-z]":
            start = index
            finish = index + 1
            index += 2

            states.add(start)
            states.add(finish)

            alphabet.update(list(string.ascii_lowercase))

            delta.update({
                (start, c): {finish} for c in string.ascii_lowercase
            })

            init_s = start
            final_s.add(finish)

        elif p == "[A-Z]":
            start = index
            finish = index + 1
            index += 2

            states.add(start)
            states.add(finish)

            alphabet.update(list(string.ascii_uppercase))

            delta.update({
                (start, c): {finish} for c in string.ascii_uppercase
            })

            init_s = start
            final_s.add(finish)

        elif p == "SPACE":
            start = index
            finish = index + 1
            index += 2

            states.add(start)
            states.add(finish)

            alphabet.update(" ")

            delta.update({
                (start, " "): {finish}
            })

            init_s = start
            final_s.add(finish)

        else:
            start = index
            finish = index + 1
            index += 2

            states.add(start)
            states.add(finish)

            alphabet.update(p) if p != "eps" else None

            delta.update({
                (start, p): {finish}
            })

            init_s = start
            final_s.add(finish)

        ret = NFA(states, alphabet, delta, init_s, final_s)
        return ret, index


    @staticmethod
    def fromPrenex(str: str) -> 'NFA[int]':
        for sp, encoding in SPECIAL.items():
            str = str.replace(encoding, "'" + sp + "'" if sp == " " else sp)

        aux = ""
        lst = list(str)

        while len(lst):
            c = lst.pop(0)
            if c == "'":
                c = lst.pop(0)
                if c == " ":
                    c = "SPACE"
                lst.pop(0)
            aux += c
        str = aux

        stack = str.split(" ")

        ret = NFA.process(stack)[0]
        return ret