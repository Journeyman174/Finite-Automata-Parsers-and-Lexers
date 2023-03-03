
REGEX_TO_PRENEX = {'+': "PLUS", '?': "MAYBE", '*': "STAR", '&': "CONCAT", '|': "UNION"}
BINARY = ["&", "|"]
UNARY = ['+', '?', '*']


class BTreeNode:
    def __init__(self, data):
        self.data = data

    def __repr__(self):
        return f"{self.data}"


class BinaryNode(BTreeNode):
    def __init__(self, data):
        super().__init__(data)
        self.right = None
        self.left = None

    def __repr__(self):
        return f"{REGEX_TO_PRENEX[self.data]} {self.left} {self.right}"


class UnaryNode(BTreeNode):
    def __init__(self, data):
        super().__init__(data)
        self.child = None

    def __repr__(self):
        return f"{REGEX_TO_PRENEX[self.data]} {self.child}"


def getInstance(character) -> BTreeNode:
    ret: BTreeNode

    if character in BINARY:
        ret = BinaryNode(character)
    elif character in UNARY:
        ret = UnaryNode(character)
    else:
        ret = BTreeNode(character)

    return ret


def buildExpTree(s):
    nodes = []
    characters = []
    priorities = {'&': 2, '|': 1, '*': 3, "+": 3, '?': 3, '(': 0, ')': 0}

    i = 0
    while i < len(s):

        if s[i] == '(':
            if i > 1:
                if s[i - 1] not in "(|&":
                    s = s[:i] + '&' + s[i:]
                    continue
            characters.append(s[i])

        elif s[i] not in priorities:
            if i > 1:
                if s[i - 1] not in "(|&":
                    s = s[:i] + '&' + s[i:]
                    continue
            t = getInstance(s[i])
            nodes.append(t)

        elif priorities[s[i]] > 0:

            while (characters and characters[-1] != '('
                   and ((s[i] != '*' and priorities[characters[-1]] > priorities[s[i]])
                   or (s[i] == '*' and priorities[characters[-1]] == priorities[s[i]]))):

                op = characters.pop()
                t = getInstance(op)

                if isinstance(t, BinaryNode):
                    t.right = nodes.pop()
                    t.left = nodes.pop()
                elif isinstance(t, UnaryNode):
                    t.child = nodes.pop()

                nodes.append(t)

            characters.append(s[i])

        elif s[i] == ')':

            while len(characters) != 0 and characters[-1] != '(':
                op = characters.pop()
                t = getInstance(op)

                if isinstance(t, BinaryNode):
                    t.right = nodes.pop()
                    t.left = nodes.pop()
                elif isinstance(t, UnaryNode):
                    t.child = nodes.pop()
                nodes.append(t)
            characters.pop()

        i += 1
    t = nodes.pop()
    return t
