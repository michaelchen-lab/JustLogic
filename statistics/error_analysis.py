import pandas as pd
import numpy as np
import statsmodels.api as sm
import matplotlib
import matplotlib.pyplot as plt
matplotlib.rcParams.update({'font.size': 12})

def get_dataframe(filename):
    df = pd.read_csv(filename, converters={'premises': pd.eval}, encoding = "ISO-8859-1")
    df.dropna(subset=['predicted'], inplace=True)
    df['accuracy'] = df.label == df.predicted
    df.replace(to_replace={'accuracy' : {True: 1, False: 0}}, inplace = True)
    df['num_of_premises'] = df.premises.str.len()
    return df

def get_acc_over_depth(filenames):
    colors = ['#AF8D1E', '#1E40AF', '#AF1E89']
    for name, filename in filenames.items():
        df = get_dataframe(filename)

        acc_over_depth = {}
        for depth in df.depth.unique():
            matching = df[df.depth == depth].label == df[df.depth == depth].predicted
            acc_over_depth[depth] = matching.value_counts(normalize=True)[True]
        plt.plot(acc_over_depth.keys(), acc_over_depth.values(), label=name, color=colors[0])
        colors = colors[1:]
    plt.title('Acc. over Reasoning Depth')
    plt.xlabel('Reasoning Depth')
    plt.ylabel('Accuracy')
    plt.legend()
    plt.savefig('error_analysis/acc_over_depth.png', dpi=800)
    plt.show()

def get_acc_over_arg_form(filenames):
    colors = ['#1EAF44', '#1E40AF', '#AF1E89']
    forms = ['Modus Ponens', 'Modus Tonens', 'Hypothetical Syllogism', 'Disjunctive Syllogism', 'Reductio Ad Absurdum', 'Constructive Dilemma', 'Disjunction Elimination']
    short_forms = ['MP', 'MT', 'HS', 'DS', 'RAA', 'CD', 'DE']
    all_acc_over_form = {'Form': short_forms}
    for name, filename in filenames.items():
        df = get_dataframe(filename)

        acc_over_form = {}
        for f in forms:
            form_df = df[df.arg.str.contains(f)]
            form_df = form_df[form_df.depth < 3]
            matching = form_df.label == form_df.predicted
            acc_over_form[f] = matching.value_counts(normalize=True)[True]
        all_acc_over_form[name] = list(acc_over_form.values())
    results_df = pd.DataFrame.from_dict(all_acc_over_form)
    results_df.plot(x='Form', y=list(filenames.keys()), kind='bar', rot=0, color=colors).legend(
        loc='center', bbox_to_anchor=(0.7, 0.87)
    )
    # plt.xticks(rotation=90, ha='right')
    plt.title('Acc. over Argument Form')
    plt.ylabel('Accuracy')

    plt.savefig('error_analysis/acc_over_arg_form.png', dpi=800)
    plt.show()
    #     plt.bar(acc_over_form.keys(), acc_over_form.values(), label=name)
    # plt.legend()
    # plt.show()

def get_acc_over_bform(filenames):

    for name, filename in filenames.items():
        df = get_dataframe(filename)

        forms = ['Either', 'If', 'Not']
        df['form_count'] = pd.Series(0, index=np.arange(len(df)))
        for f in forms:
            df.form_count += df.arg.str.count(f)
        df.form_count = df.form_count
        acc_over_bform = {}
        for i in range(1,15):
            form_df = df[(df.form_count >= (i*5-4)) & (df.form_count <= (i*5))]
            matching = form_df.label == form_df.predicted
            acc_over_bform[str(i*5-4)+'-'+str(i*5)] = matching.value_counts(normalize=True)[True]
        plt.plot(acc_over_bform.keys(), acc_over_bform.values(), label=name)
    
    plt.xlabel('No. of Basic Forms')
    plt.ylabel('Accuracy')
    plt.legend()
    # plt.savefig('error_analysis/acc_over_basic_form.png', dpi=800)
    plt.show()

def error_analysis(filename):
    df = pd.read_csv(filename, converters={'premises': pd.eval}, encoding = "ISO-8859-1")
    df.dropna(subset=['predicted'], inplace=True)
    df['accuracy'] = df.label == df.predicted
    df.replace(to_replace={'accuracy' : {True: 1, False: 0}}, inplace = True)
    df['num_of_premises'] = df.premises.str.len()

    # accuracy over reasoning depth
    acc_over_depth = {}
    for depth in df.depth.unique():
        matching = df[df.depth == depth].label == df[df.depth == depth].predicted
        acc_over_depth[depth] = matching.value_counts(normalize=True)[True]
    print(acc_over_depth)
    print()
    plt.plot(acc_over_depth.keys(), acc_over_depth.values())
    plt.show()
    
    # accuracy over arg forms (depth <= 2)
    acc_over_form = {}
    forms = ['Modus Ponens', 'Modus Tonens', 'Hypothetical Syllogism', 'Disjunctive Syllogism', 'Reductio Ad Absurdum', 'Constructive Dilemma', 'Disjunction Elimination']
    for f in forms:
        form_df = df[df.arg.str.contains(f)]
        form_df = form_df[form_df.depth < 3]
        matching = form_df.label == form_df.predicted
        acc_over_form[f] = [matching.value_counts(normalize=True)[True], len(matching)]
    print(acc_over_form)
    print()

    # accuracy over basic form
    forms = ['Either', 'If', 'Not']
    df['form_count'] = pd.Series(0, index=np.arange(len(df)))
    for f in forms:
        df.form_count += df.arg.str.count(f)
    df.form_count = df.form_count
    acc_over_bform = {}
    for i in range(1,15):
        form_df = df[(df.form_count >= (i*5-4)) & (df.form_count <= (i*5))]
        matching = form_df.label == form_df.predicted
        acc_over_bform[i] = [matching.value_counts(normalize=True)[True], len(matching)]
    print(acc_over_bform)

    model = sm.formula.logit("accuracy ~   + depth + form_count + num_of_premises",
                    data=df).fit()

    print(model.summary())
    print('\n')

if __name__ == "__main__":
    all_colors = ['#1E40AF', '#AF1E89', '#AF8D1E', '#1EAF44']
    get_acc_over_arg_form({
        # 'OpenAI o1-preview': 'eval/3_shot_cot_w_depth_openai_o1_results.csv',
        'Llama3-70B': 'eval/3_shot_cot_w_depth_llama70B_results.csv',
        'GPT-4': 'eval/3_shot_cot_w_depth_gpt4_results.csv',
        'Llama3-8B': 'eval/0_shot_llama8B_results.csv'
    })
    # error_analysis('eval/3_shot_cot_w_depth_openai_o1_results.csv')
    # error_analysis('eval/3_shot_cot_w_depth_llama70B_results.csv')