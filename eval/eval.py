import pandas as pd

def get_num_label_and_predicted(df):
    num_labels = []
    for l in df.label:
        if 'true' in l or 'True' in l or 'TRUE' in l or l == True:
            num_labels.append(1)
        elif 'false' in l or 'False' in l or 'FALSE' in l or l == False:
            num_labels.append(2)
        elif 'uncertain' in l or 'Uncertain' in l:
            num_labels.append(3)
    df['num_label'] = num_labels
    print(len(df.num_label))
    num_predicted = []
    for l in df.predicted:
        if 'true' in l or 'True' in l or 'TRUE' in l or l == True:
            num_predicted.append(1)
        elif 'false' in l or 'False' in l or 'FALSE' in l or l == False:
            num_predicted.append(2)
        elif 'uncertain' in l or 'Uncertain' in l:
            num_predicted.append(3)
    df['num_predicted'] = num_predicted
    return df

def eval(filename):
    df = pd.read_csv(filename, encoding = "ISO-8859-1")
    df.dropna(subset=['predicted'], inplace=True)
    df = get_num_label_and_predicted(df)

    print(df.iloc[0])

    matching = df.num_label == df.num_predicted
    print(matching[:10])
    print('sample size:', len(df))
    print('overall acc:', matching.value_counts(normalize=True)[True])

# def forms_in_depth(filename):
#     df = pd.read_csv(filename, encoding = "ISO-8859-1")
#     df.dropna(subset=['predicted'], inplace=True)
#     df = get_num_label_and_predicted(df)
#     for i in range(1,8):
#         depth_df = df[df.depth == i]
#         forms = {'Modus Ponens': 0, 'Modus Tonens': 0, 'Hypothetical Syllogism': 0, 'Disjunctive Syllogism': 0, 'Reductio Ad Absurdum': 0, 'Constructive Dilemma': 0, 'Disjunction Elimination': 0}
#         for arg in depth_df.arg:
#             for form in forms.keys():
#                 forms[form] += arg.count(form)
#         print(i)
#         print(forms)

if __name__ == "__main__":
    # eval('context_independent_eval\ci_independent_results.csv')
    eval('eval/3_shot_cot_w_depth_gpt4o_results.csv')