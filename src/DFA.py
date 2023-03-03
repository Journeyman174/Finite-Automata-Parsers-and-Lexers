import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

from typing import Callable, Generic, TypeVar
from src.NFA import NFA

S = TypeVar("S")
T = TypeVar("T")


class DFA(Generic[S]):

    def __init__(self, states, alphabet, delta, initState, finalStates):
        self.states = states
        self.alphabet = alphabet
        self.delta = delta
        self.initState = initState
        self.finalStates = finalStates
        self.lastState = 0  
        self.consumed = 0   

    def map(self, f: Callable[[S], T]) -> 'DFA[T]':
        deltaMap = {}
        deltaCopy = self.delta.copy()
        

        for (s, c) in self.delta:
            val = deltaCopy[(s, c)]
            del deltaCopy[(s, c)]
            deltaMap[(f(s), c)] = f(val)

        statesMap = {f(s) for s in self.states}
        finalsMap = {f(s) for s in self.finalStates}
        return DFA[T](statesMap, self.alphabet, deltaMap, f(self.initState), finalsMap)

    def next(self, from_state: S, on_chr: str) -> S:
        for key in self.delta:
            if key == (from_state, on_chr):
                self.lastState = self.delta[key]
                return self.delta[key]

        self.lastState = -1

        return -1

    def getStates(self) -> 'set[S]':
        return self.states

    def acceptsFromState(self, str: str, state: S) -> bool:
        if self.isFinal(state) and str == "" :
            return True
        if str != "":
            return self.acceptsFromState(str[1:], self.next(state, str[0]))

        return False

    def accepts(self, str: str) -> bool:
        return self.acceptsFromState(str, self.initState)

    def getLongestPrefix(self, str: str) -> str:
        ret = ""
        self.consumed = 0

        for i in range(1, len(str) + 1):
            word = str[:i]

            if self.accepts(word):
                ret = word
            elif self.lastState == -1:  # daca sunt in SINK_STATE atunci exit
                return ret

            self.consumed += 1

        return ret

    def isFinal(self, state: S) -> bool:
        return state in self.finalStates

    @staticmethod
    def fromPrenex(str: str) -> 'DFA[int]':
        N = NFA.fromPrenex(str)
        E = {state: N.getEpsClosure(state, set()) for state in N.states}
        initEpsClosure = [E[N.initState]]
        DFAstates = []
        DFAalphabet = N.alphabet
        DFAdelta = {}
        DFAinitial = tuple()
        DFAfinal = []

        for e in initEpsClosure:
            if tuple(e) not in DFAstates:
                DFAstates.append(tuple(e))

            for s in e:
                for c in N.alphabet:
                    value = set()
                    nextStates = N.next(s, c)
                    for t in nextStates:
                        value = value.union(E[t])
                    DFAtransition = (tuple(e), c)
                    if DFAtransition in DFAdelta:
                        DFAdelta[DFAtransition] = DFAdelta[DFAtransition].union(value)
                    elif len(value) > 0:
                        DFAdelta.update({DFAtransition: value})

                for c in N.alphabet:
                    DFAtransition = (tuple(e), c)
                    if DFAtransition in DFAdelta and DFAdelta[DFAtransition] not in initEpsClosure:
                        initEpsClosure.append(DFAdelta[DFAtransition])

        DFAinitial = tuple(E[N.initState])

        for key in DFAdelta:
            if tuple(DFAdelta[key]) not in DFAstates:
                DFAstates.append(tuple(DFAdelta[key]))
            DFAdelta[key] = tuple(DFAdelta[key])

        fstate = N.finalStates.pop()
        N.finalStates.add(fstate)
        for st in DFAstates:
            for s in st:
                if tuple(st) not in DFAfinal and s == fstate:
                    DFAfinal.append(tuple(st))

        return DFA(DFAstates, DFAalphabet, DFAdelta, DFAinitial, DFAfinal).map(lambda x: DFAstates.index(x))
