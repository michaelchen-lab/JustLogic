import pandas as pd
import matplotlib.pyplot as plt

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

def eval_by_conclusion_type(filenames, depth):
    colors = ['#1E40AF', '#AF1E89', '#AF8D1E', '#1EAF44']
    fa_conclusions = ['Therefore, \[0]', 'Therefore, Either', 'Therefore, Not \(If']
    fia_conclusions = ['Therefore, Not \[', 'Therefore, Not \(Either', 'Therefore, If']

    all_acc_over_conc_type = []
    for name, filename in filenames.items():
        df = pd.read_csv(filename, encoding = "ISO-8859-1")
        df.dropna(subset=['predicted'], inplace=True)
        df = get_num_label_and_predicted(df)

        conclusions = []
        for arg in df.arg:
            conc = arg[arg.index('Therefore,'):]
            if '\n\n' in conc:
                conc = conc[:conc.index('\n\n')]
            conclusions.append(conc)
        df['sym_conclusion'] = conclusions

        # df['sym_conclusion'] = [arg[arg.index('Therefore,'):] if '\n\n' not in arg else arg for arg in df.arg]
        df = df[df.depth <= depth]

        factually_accurate_df = df[df['sym_conclusion'].str.contains('|'.join(fa_conclusions))]
        fa_matching = factually_accurate_df.num_label == factually_accurate_df.num_predicted
        factually_inaccurate_df = df[df['sym_conclusion'].str.contains('|'.join(fia_conclusions))]
        # factually_inaccurate_df = df[df['arg'].str.contains('Therefore, Not \[')]
        fia_matching = factually_inaccurate_df.num_label == factually_inaccurate_df.num_predicted

        print('factually accurate size:', len(fa_matching))
        print('factually accurate acc:', fa_matching.value_counts(normalize=True)[True])
        print('factually inaccurate size:', len(fia_matching))
        print('factually inaccurate acc:', fia_matching.value_counts(normalize=True)[True])

        # all_acc_over_conc_type[name] = [fa_matching.value_counts(normalize=True)[True], fia_matching.value_counts(normalize=True)[True]]
        all_acc_over_conc_type.append({
            'Model': name,
            'FA': fa_matching.value_counts(normalize=True)[True],
            'FIA': fia_matching.value_counts(normalize=True)[True]
        })

    results_df = pd.DataFrame.from_records(all_acc_over_conc_type)
    results_df.plot(x='Model', y=['FA', 'FIA'], kind='bar', rot=0, color=colors).legend(
        loc='upper right'
    )
    plt.title('Acc. over Conclusion Type (Depth≤{depth})'.format(depth=depth))
    plt.ylabel('Accuracy')
    plt.ylim((0.0,1.1))
    plt.savefig('eval/acc_over_conc_type_depth_{depth}.png'.format(depth=depth), dpi=800)
    plt.show()


if __name__ == "__main__":
    eval('eval/3_shot_cot_w_depth_openai_o1_results.csv')
    # eval_by_conclusion_type({
    #     'OpenAI o1-preview': 'eval/3_shot_cot_w_depth_openai_o1_results.csv',
    #     'GPT-4o': 'eval/3_shot_cot_w_depth_gpt4o_results.csv',
    #     'GPT-4': 'eval/3_shot_cot_w_depth_gpt4_results.csv',
    #     'Llama3-70B': 'eval/3_shot_cot_w_depth_llama70B_results.csv',
    #     'Llama3-8B': 'eval/3_shot_cot_w_depth_llama8B_results.csv'
    # }, 1)