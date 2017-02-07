from __future__ import division

import math
import re
import statistics

from pyparsing import CaselessLiteral, Combine, Forward, Literal, Optional, ParseException, StringEnd, Word, ZeroOrMore, \
    alphanums, alphas, nums

# TODO: Redo all of this to make it faster.
# Source: http://pyparsing.wikispaces.com/file/view/SimpleCalc.py/30112812/SimpleCalc.py

exprStack = []
varStack = []
variables = {}


def pushFirst(str, loc, toks):
    exprStack.append(toks[0])


def assignVar(str, loc, toks):
    varStack.append(toks[0])


# define grammar
point = Literal('.')
e = CaselessLiteral('E')
plusorminus = Literal('+') | Literal('-')
number = Word(nums)
integer = Combine(Optional(plusorminus) + number)
floatnumber = Combine(integer +
                      Optional(point + Optional(number)) +
                      Optional(e + integer)
                      )

ident = Word(alphas, alphanums + '_')

plus = Literal("+")
minus = Literal("-")
limit = Literal("_")
mult = Literal("*")
div = Literal("/")
lpar = Literal("(").suppress()
rpar = Literal(")").suppress()
addop = plus | minus | limit
multop = mult | div
expop = Literal("^")
assign = Literal("=")

expr = Forward()
atom = ((e | floatnumber | integer | ident).setParseAction(pushFirst) |
        (lpar + expr.suppress() + rpar)
        )

factor = Forward()
factor << atom + ZeroOrMore((expop + factor).setParseAction(pushFirst))

term = factor + ZeroOrMore((multop + factor).setParseAction(pushFirst))
expr << term + ZeroOrMore((addop + term).setParseAction(pushFirst))
bnf = Optional((ident + assign).setParseAction(assignVar)) + expr

pattern = bnf + StringEnd()

# map operator symbols to corresponding arithmetic operations
operations = {
    "+": (lambda a, b: a + b),
    "-": (lambda a, b: a - b),
    "*": (lambda a, b: a * b),
    "/": (lambda a, b: a / b),
    "^": (lambda a, b: a ** b),
    "_": (lambda a, b: min(a, b))
}


# Recursive function that evaluates the stack
def evaluateStack(s):
    operator = s.pop()
    if operator in operations.keys():
        op2 = evaluateStack(s)
        op1 = evaluateStack(s)
        return operations[operator](op1, op2)
    elif operator == "PI":
        return math.pi
    elif operator == "E":
        return math.e
    elif re.search('^[a-zA-Z][a-zA-Z0-9_]*$', operator):
        if operator in variables.keys():
            return variables[operator]
        else:
            return 0
    elif re.search('^[-+]?[0-9]+$', operator):
        return float(operator)
    else:
        return float(operator)


class Calculator(object):
    def __init__(self, equation=None):
        self.equation = equation

    def solve(self, expression):
        try:
            pattern.parseString(expression)
        except ParseException:
            print("Cannot parse expression: {}".format(expression))
            return None
        result = evaluateStack(exprStack)
        return round(result, 2)


class Calc(object):
    def __init__(self):
        self.fields = {
            'abs': abs,
            'min': min,
            'max': max,
            'mode': statistics.mode,
            'print': print,
            'len': len,
            'round': round,
            'zip': zip,
            'sum': sum,
            'map': map,
            'int': int,
            'float': float
        }

    def add_fields(self, **fields):
        for key, value in fields.items():
            self.fields[key] = value

    def solve(self, equation):
        return eval(equation, {"__builtins__": None}, self.fields)