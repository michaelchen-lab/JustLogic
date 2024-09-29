import random
import numpy as np
import json

# Basic
with open('expressions.json') as f:
    EXPS = json.load(f)

class Conditional:
    def __init__(self, x, y, nl_sents=None):
        self.x = x
        self.y = y
        if nl_sents != None:
            self.x.x_sent = nl_sents[0]
            self.y.x_sent = nl_sents[1]
            self.x_sent = nl_sents[0]
            self.y_sent = nl_sents[1]
        self.exp = np.random.choice(EXPS['Conditional'])
        self._arg = None
        self.negate = False
    
    def __str__(self, base=False):
        exp = '{start}If {x}, then {y}.{end}'
        return exp.format(
            start = '(' if base==False else '',
            end = ')' if base==False else '',
            x = self.x.__str__(),
            y = self.y.__str__()
        )

    def nl(self, base=True):
        if base==False:
            exp = 'if {x}, then {y}'
        else:
            exp = self.exp
        exp = exp.format(
            x = self.x.nl(base=False),
            y = self.y.nl(base=False)
        )
        # if base==False:
        #     exp = exp[:1].lower() + exp[1:-1]
        return exp

    def __name__(self):
        return 'Conditional'

    @property
    def arg(self): 
        return self._arg

    @arg.setter
    def arg(self, arg):
        # Ensure argument's conclusion leads to this statement
        assert self.__str__(base=False) == arg.conclusion.__str__(base=False)
        self._arg = arg

class Disjunction:
    def __init__(self, x, y, nl_sents=None):
        self.x = x
        self.y = y
        if nl_sents != None:
            self.x.x_sent = nl_sents[0]
            self.y.x_sent = nl_sents[1]
            self.x_sent = nl_sents[0]
            self.y_sent = nl_sents[1]
        self.exp = np.random.choice(EXPS['Disjunction'])
        self._arg = None
    
    def __str__(self, base=False):
        exp = '{start}Either {x} or {y}.{end}'
        return exp.format(
            start = '(' if base==False else '',
            end = ')' if base==False else '',
            x=self.x, 
            y=self.y
        )

    def nl(self, base=True):
        if base==False:
            exp = 'either {x} or {y}'
        else:
            exp = self.exp
        exp = exp.format(
            x = self.x.nl(base=False),
            y = self.y.nl(base=False)
        )
        # if base==False:
        #     exp = exp[:1].lower() + exp[1:-1]
        return exp

    def __name__(self):
        return 'Disjunction'

    @property
    def arg(self): 
        return self._arg

    @arg.setter
    def arg(self, arg):
        # Ensure argument's conclusion leads to this statement
        assert self.__str__(base=False) == arg.conclusion.__str__(base=False)
        self._arg = arg

class Statement:
    def __init__(self, x, nl_sents=None):
        self.x = x
        self.x_sent = None
        if nl_sents != None:
            self.x_sent = nl_sents[0]
        self.exp = np.random.choice(EXPS['Statement'])
        self._arg = None
    
    def __str__(self, base=False):
        exp = '{x}'
        return exp.format(
            x = '['+self.x+']'
        )
    
    def nl_default(self):
        return self.x_sent

    def nl(self, base=True):
        if base:
            if self.exp == '{x}.':
                return self.exp.format(x = self.x_sent)
            else:
                return self.exp.format(x = self.x_sent[:1].lower() + self.x_sent[1:-1])
        else:
            return self.x_sent[:1].lower() + self.x_sent[1:-1]

    def __name__(self):
        return 'Statement'

    @property
    def arg(self): 
        return self._arg

    @arg.setter
    def arg(self, arg):
        # Ensure argument's conclusion leads to this statement
        assert self.__str__(base=False) == arg.conclusion.__str__(base=False)
        self._arg = arg

class Negation:
    def __init__(self, x, exp=None):
        # Negation applies to all basic forms, not just Statement
        if type(x) == str: x = Statement(x)
        self.exp = np.random.choice(EXPS['Negation'])

        self.x = x
    
    def __str__(self, base=False):
        exp = '{start}Not {x}.{end}'
        return exp.format(
            start = '(' if base==False else '',
            end = ')' if base==False else '',
            x=self.x
        )

    def nl(self, base=True):
        exp = self.exp.format(x = self.x.nl(base=False))
        if base==False:
            exp = exp[:1].lower() + exp[1:-1]
        return exp

    def __name__(self):
        return 'Negation'

    def __getattr__(self, name):
        return getattr(self.x, name)
    
    @property
    def arg(self): 
        return self.x._arg

    @arg.setter
    def arg(self, arg):
        # Ensure argument's conclusion leads to this statement
        assert self.__str__() == arg.conclusion.__str__()
        self.x._arg = arg
    
def negate(x):
    if type(x) == str: x = Statement(x)

    if x.__name__() != 'Negation':
        return Negation(x)
    elif x.__name__() == 'Negation': 
        return x.x # return back to Statement class

class ModusPonens:
    def __init__(self, x, y):
        if type(x) == str: x = Statement(x)
        if type(y) == str: y = Statement(y)

        self.premise1 = Conditional(x, y)
        self.premise2 = x
        self.conclusion = y
    
    def __str__(self, i=1):
        return 'Modus Ponens: \n{p1} {sc1}\n{p2} {sc2}\nTherefore, {c}.{sc1_arg}{sc2_arg}'.format(
            p1 = self.premise1.__str__(base=True),
            sc1 = '[SC1-{i}]'.format(i=i) if self.premise1.arg != None else '',
            p2 = self.premise2.__str__(base=True),
            sc2 = '[SC2-{i}]'.format(i=i) if self.premise2.arg != None else '',
            c  = self.conclusion.__str__(base=True),

            sc1_arg = '\n\n[SC1-{i}]\n'.format(i=i)+self.premise1.arg.__str__(i=i+1) if self.premise1.arg != None else '',
            sc2_arg = '\n\n[SC2-{i}]\n'.format(i=i)+self.premise2.arg.__str__(i=i+1) if self.premise2.arg != None else '',
        )

    def __name__(self):
        return 'ModusPonens'

class ModusTollens:
    def __init__(self, x, y):
        if type(x) == str: x = Statement(x)
        if type(y) == str: y = Statement(y)

        self.premise1 = Conditional(x, y)
        self.premise2 = negate(y)
        self.conclusion = negate(x)
    
    def __str__(self, i=1):
        return 'Modus Tonens: \n{p1} {sc1}\n{p2} {sc2}\nTherefore, {c}.{sc1_arg}{sc2_arg}'.format(
            p1 = self.premise1.__str__(base=True),
            sc1 = '[SC1-{i}]'.format(i=i) if self.premise1.arg != None else '',
            p2 = self.premise2.__str__(base=True),
            sc2 = '[SC2-{i}]'.format(i=i) if self.premise2.arg != None else '',
            c  = self.conclusion.__str__(base=True),

            sc1_arg = '\n\n[SC1-{i}]\n'.format(i=i)+self.premise1.arg.__str__(i=i+1) if self.premise1.arg != None else '',
            sc2_arg = '\n\n[SC2-{i}]\n'.format(i=i)+self.premise2.arg.__str__(i=i+1) if self.premise2.arg != None else '',
        )

    def __name__(self):
        return 'ModusTollens'

class HypotheticalSyllogism:
    def __init__(self, x, y, z):
        if type(x) == str: x = Statement(x)
        if type(y) == str: y = Statement(y)
        if type(z) == str: z = Statement(z)

        self.premise1 = Conditional(x, y)
        self.premise2 = Conditional(y, z)
        self.conclusion = Conditional(x, z)
    
    def __str__(self, i=1):
        return 'Hypothetical Syllogism: \n{p1} {sc1}\n{p2} {sc2}\nTherefore, {c}.{sc1_arg}{sc2_arg}'.format(
            p1 = self.premise1.__str__(base=True),
            sc1 = '[SC1-{i}]'.format(i=i) if self.premise1.arg != None else '',
            p2 = self.premise2.__str__(base=True),
            sc2 = '[SC2-{i}]'.format(i=i) if self.premise2.arg != None else '',
            c  = self.conclusion.__str__(base=True),

            sc1_arg = '\n\n[SC1-{i}]\n'.format(i=i)+self.premise1.arg.__str__(i=i+1) if self.premise1.arg != None else '',
            sc2_arg = '\n\n[SC2-{i}]\n'.format(i=i)+self.premise2.arg.__str__(i=i+1) if self.premise2.arg != None else '',
        )

    def __name__(self):
        return 'HypotheticalSyllogism'

class DisjunctiveSyllogism:
    def __init__(self, x, y):
        if type(x) == str: x = Statement(x)
        if type(y) == str: y = Statement(y)

        self.premise1 = Disjunction(x, y)
        self.premise2 = negate(x)
        self.conclusion = y
    
    def __str__(self, i=1):
        return 'Disjunctive Syllogism: \n{p1} {sc1}\n{p2} {sc2}\nTherefore, {c}.{sc1_arg}{sc2_arg}'.format(
            p1 = self.premise1.__str__(base=True),
            sc1 = '[SC1-{i}]'.format(i=i) if self.premise1.arg != None else '',
            p2 = self.premise2.__str__(base=True),
            sc2 = '[SC2-{i}]'.format(i=i) if self.premise2.arg != None else '',
            c  = self.conclusion.__str__(base=True),

            sc1_arg = '\n\n[SC1-{i}]\n'.format(i=i)+self.premise1.arg.__str__(i=i+1) if self.premise1.arg != None else '',
            sc2_arg = '\n\n[SC2-{i}]\n'.format(i=i)+self.premise2.arg.__str__(i=i+1) if self.premise2.arg != None else '',
        )

    def __name__(self):
        return 'DisjunctiveSyllogism'

class ReductioAdAbsurdum:
    def __init__(self, x, y):
        if type(x) == str: x = Statement(x)
        if type(y) == str: y = Statement(y)

        self.premise1 = Conditional(x, y)
        self.premise2 = Conditional(x, negate(y))
        self.conclusion = negate(x)
    
    def __str__(self, i=1):
        return 'Reductio Ad Absurdum: \n{p1} {sc1}\n{p2} {sc2}\nTherefore, {c}.{sc1_arg}{sc2_arg}'.format(
            p1 = self.premise1.__str__(base=True),
            sc1 = '[SC1-{i}]'.format(i=i) if self.premise1.arg != None else '',
            p2 = self.premise2.__str__(base=True),
            sc2 = '[SC2-{i}]'.format(i=i) if self.premise2.arg != None else '',
            c  = self.conclusion.__str__(base=True),

            sc1_arg = '\n\n[SC1-{i}]\n'.format(i=i)+self.premise1.arg.__str__(i=i+1) if self.premise1.arg != None else '',
            sc2_arg = '\n\n[SC2-{i}]\n'.format(i=i)+self.premise2.arg.__str__(i=i+1) if self.premise2.arg != None else '',
        )

    def __name__(self):
        return 'ReductioAdAbsurdum'

class ConstructiveDilemma:
    def __init__(self, x, y, a, b):
        if type(x) == str: x = Statement(x)
        if type(y) == str: y = Statement(y)
        if type(a) == str: x = Statement(a)
        if type(b) == str: y = Statement(b)

        self.premise1 = Disjunction(x, y)
        self.premise2 = Conditional(x, a)
        self.premise3 = Conditional(y, b)
        self.conclusion = Disjunction(a, b)
    
    def __str__(self, i=1):
        return 'Constructive Dilemma: \n{p1} {sc1}\n{p2} {sc2}\n{p3} {sc3}\nTherefore, {c}.{sc1_arg}{sc2_arg}{sc3_arg}'.format(
            p1 = self.premise1.__str__(base=True),
            sc1 = '[SC1-{i}]'.format(i=i) if self.premise1.arg != None else '',
            p2 = self.premise2.__str__(base=True),
            sc2 = '[SC2-{i}]'.format(i=i) if self.premise2.arg != None else '',
            p3 = self.premise3.__str__(base=True),
            sc3 = '[SC3-{i}]'.format(i=i) if self.premise3.arg != None else '',
            c  = self.conclusion.__str__(base=True),

            sc1_arg = '\n\n[SC1-{i}]\n'.format(i=i)+self.premise1.arg.__str__(i=i+1) if self.premise1.arg != None else '',
            sc2_arg = '\n\n[SC2-{i}]\n'.format(i=i)+self.premise2.arg.__str__(i=i+1) if self.premise2.arg != None else '',
            sc3_arg = '\n\n[SC3-{i}]\n'.format(i=i)+self.premise3.arg.__str__(i=i+1) if self.premise3.arg != None else '',
        )

    def __name__(self):
        return 'ConstructiveDilemma'

class DisjunctionElimination:
    def __init__(self, x, y, a):
        if type(x) == str: x = Statement(x)
        if type(y) == str: y = Statement(y)
        if type(a) == str: x = Statement(a)

        self.premise1 = Disjunction(x, y)
        self.premise2 = Conditional(x, a)
        self.premise3 = Conditional(y, a)
        self.conclusion = a
    
    def __str__(self, i=1):
        return 'Disjunction Elimination: \n{p1} {sc1}\n{p2} {sc2}\n{p3} {sc3}\nTherefore, {c}.{sc1_arg}{sc2_arg}{sc3_arg}'.format(
            p1 = self.premise1.__str__(base=True),
            sc1 = '[SC1-{i}]'.format(i=i) if self.premise1.arg != None else '',
            p2 = self.premise2.__str__(base=True),
            sc2 = '[SC2-{i}]'.format(i=i) if self.premise2.arg != None else '',
            p3 = self.premise3.__str__(base=True),
            sc3 = '[SC3-{i}]'.format(i=i) if self.premise3.arg != None else '',
            c  = self.conclusion.__str__(base=True),

            sc1_arg = '\n\n[SC1-{i}]\n'.format(i=i)+self.premise1.arg.__str__(i=i+1) if self.premise1.arg != None else '',
            sc2_arg = '\n\n[SC2-{i}]\n'.format(i=i)+self.premise2.arg.__str__(i=i+1) if self.premise2.arg != None else '',
            sc3_arg = '\n\n[SC3-{i}]\n'.format(i=i)+self.premise3.arg.__str__(i=i+1) if self.premise3.arg != None else '',
        )

    def __name__(self):
        return 'DisjunctionElimination'
