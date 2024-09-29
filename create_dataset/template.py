from logic import *
from natural_lang import *
import json
import pandas as pd

class ArgTemplate:

    def __init__(self, depth=3, sentgen=None):
        self.statement_num = 0
        self.nl_sents = []

        self.intended_depth = depth
        self.current_depth = 0

        self.leaf_premises = []
        self.sentgen = sentgen
        self.arg = self.create_arg_template()
        self.leaf_premises = self.get_leaf_premises()

        self.q_type = np.random.choice(['True', 'False', 'Uncertain'])
        self.question = self.gen_question()

    def __str__(self):
        arg_str = self.arg.__str__()
        # for i, nl_sent in enumerate(self.nl_sents):
        #     arg_str = arg_str.replace("["+str(i)+"]", nl_sent)
        return arg_str

    def create_arg_template(self):

        # Step 1: Generate conclusion
        conclusion = self.new_basic()
        if np.random.choice(['Negate', None], p=[0.3,0.7]) == 'Negate':
            conclusion = negate(conclusion)
        
        # Step 2: First arg
        relevant_arg_forms = {
            'Statement': [ModusPonens, ModusTollens, DisjunctiveSyllogism, ReductioAdAbsurdum, DisjunctionElimination],
            'Negation': [ModusPonens, ModusTollens, DisjunctiveSyllogism, ReductioAdAbsurdum, DisjunctionElimination],
            'Conditional': [ModusPonens, ModusTollens, HypotheticalSyllogism, DisjunctiveSyllogism, ReductioAdAbsurdum, DisjunctionElimination],
            'Disjunction': [ModusPonens, ModusTollens, DisjunctiveSyllogism, ReductioAdAbsurdum, ConstructiveDilemma, DisjunctionElimination]
        }
        arg = random.choice(relevant_arg_forms[conclusion.__name__()])
        # arg = DisjunctiveSyllogism
        arg = arg(*self.new_arg_statements(form_type=arg.__name__, conclusion=conclusion))
        self.current_depth += 1

        # Step 3: Sub-arguments
        premise_names = [i for i in dir(arg) if 'premise' in i]
        leaf_premises = [getattr(arg, p) for p in premise_names]
        while True:
            # Randomly choose the no. of premises and the actual premises to create an arg for
            max_args = min(self.intended_depth - self.current_depth, len(leaf_premises))
            if max_args == 0:
                break # the intended depth has been reached
            no_of_args = np.random.choice(list(range(1,max_args+1)), replace=False)
            premises_to_add_args = np.random.choice(leaf_premises, no_of_args, replace=False)

            leaf_premises = [] # Prepare to update with new leaf premises
            for premise in premises_to_add_args:
                arg_form = random.choice(relevant_arg_forms[premise.__name__()])
                premise.arg = arg_form(*self.new_arg_statements(form_type=arg_form.__name__, conclusion=premise))
                self.current_depth += 1
                
                premise_names = [i for i in dir(premise.arg) if 'premise' in i]
                leaf_premises.extend([getattr(premise.arg, p) for p in premise_names])
        
        return arg

    def new_basic(self):
        # Helper function to randomly choose one of the three basic forms
        all_basics = [Statement, Conditional, Disjunction]
        form = np.random.choice(all_basics, p=[0.8,0.1,0.1]) 
        # The probability ratio can be tweaked based on how complex we want the arg template to be.

        if form.__name__ == 'Statement':
            self.statement_num += 1
            nl_sents = []
            while len(nl_sents) != 1:
                test_sent = self.sentgen.gen()[0]
                if test_sent not in self.nl_sents:
                    nl_sents.append(test_sent)
            self.nl_sents.extend(nl_sents)
            return form(str(self.statement_num - 1), nl_sents=nl_sents)
        elif form.__name__ in ['Conditional', 'Disjunction']:
            self.statement_num += 2
            nl_sents = []
            while len(nl_sents) != 2:
                test_sent = self.sentgen.gen()[0]
                if test_sent not in self.nl_sents:
                    nl_sents.append(test_sent)
            self.nl_sents.extend(nl_sents)
            return form(Statement(str(self.statement_num - 2)), Statement(str(self.statement_num - 1)), nl_sents=nl_sents)

    def new_arg_statements(self, form_type=None, conclusion=None):
        
        if form_type in ['ModusPonens', 'DisjunctiveSyllogism']:
            return (self.new_basic(), conclusion)
        elif form_type == 'ModusTollens':
            return (negate(conclusion), self.new_basic())
        elif form_type == 'ReductioAdAbsurdum':
            return (negate(conclusion), self.new_basic())
        elif form_type == 'HypotheticalSyllogism': # only conditional conclusions
            return (conclusion.x, self.new_basic(), conclusion.y)
        elif form_type == 'DisjunctionElimination':
            return (self.new_basic(), self.new_basic(), conclusion)
        elif form_type == 'ConstructiveDilemma': # only disjunctive conclusions
            return (self.new_basic(), self.new_basic(), conclusion.x, conclusion.y)
    
    def get_leaf_premises(self):
        leaf_premises = []
        args = [self.arg]
        while len(args) != 0:
            new_args = []
            for arg in args:
                premise_names = [i for i in dir(arg) if 'premise' in i]
                for p in premise_names:
                    premise = getattr(arg, p)
                    if premise.arg == None:
                        leaf_premises.append(premise)
                    else:
                        new_args.append(premise.arg)
            args = new_args
        return leaf_premises

    def gen_question(self):
        if self.q_type == 'True':
            return self.arg.conclusion.nl()
        elif self.q_type == 'False':
            return negate(self.arg.conclusion).nl()
        elif self.q_type == 'Uncertain': # generate a random statement of a similar topic
            if self.arg.conclusion.__name__() == 'Statement':
                sent = self.sentgen.gen_similar_sent(self.arg.conclusion.x_sent)
            elif self.arg.conclusion.__name__() == 'Negation':
                sent = negate(Statement('c', nl_sents=[self.sentgen.gen_similar_sent(self.arg.conclusion.x.x_sent)])).nl()
            elif self.arg.conclusion.__name__() == 'Conditional':
                if np.random.choice(['x', 'y']) == 'x':
                    x = Statement('x', nl_sents=[self.sentgen.gen_similar_sent(self.arg.conclusion.x.x_sent)])
                    sent = Conditional(x, self.arg.conclusion.y).nl()
                else:
                    y = Statement('y', nl_sents=[self.sentgen.gen_similar_sent(self.arg.conclusion.y.x_sent)])
                    sent = Conditional(self.arg.conclusion.x, y).nl()
            elif self.arg.conclusion.__name__() == 'Disjunction':
                x = Statement('x', nl_sents=[self.sentgen.gen_similar_sent(self.arg.conclusion.x.x_sent)])
                y = Statement('y', nl_sents=[self.sentgen.gen_similar_sent(self.arg.conclusion.y.x_sent)])
                sent = Disjunction(x, y).nl()
            return sent

if __name__ == '__main__':
    seed = 1
    random.seed(seed)
    np.random.seed(seed)

    dataset = []
    sentgen = SentGen()
    for depth in range(1,8):
        seed = depth - 1
        random.seed(seed)
        np.random.seed(seed)
        for i in range(1000):
            template = ArgTemplate(depth=depth, sentgen=sentgen)

            nl_premises = [p.nl() for p in template.leaf_premises]
            dataset.append({
                "id": i,
                "premises": nl_premises,
                "conclusion": template.arg.conclusion.nl(),
                "question": template.question,
                "label": template.q_type,
                "arg": template.__str__(),
                "statements": dict(zip(range(len(template.nl_sents)), template.nl_sents)),
                "depth": depth
            })

            if i % 100 == 0:
                df = pd.DataFrame.from_records(dataset)
                df.to_csv('dataset.csv', index=False)
                print('{x} records saved.'.format(x=i))

    df = pd.DataFrame.from_records(dataset)
    df.to_csv('dataset.csv', index=False)