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
        else:
            print(l)
            print(type(l))
    df['num_predicted'] = num_predicted
    return df

def get_acc_over_depth_calc(df): # alt method
    acc_over_depth = {}
    for i in range(1,8):
        print(i)
        depth_df = df[df.depth == i]
        print(depth_df.num_label.value_counts(normalize=True))

        label_acc = []
        for label in range(1,4):
            depth_label_df = depth_df[depth_df.num_label == label]
            matching = depth_label_df.num_label == depth_label_df.num_predicted
            label_acc.append(matching.value_counts(normalize=True)[True])
        acc_over_depth[i] = sum(label_acc) / 3
    
    return acc_over_depth

def get_acc_over_depth(filenames):
    colors = ['#AF8D1E', '#1E40AF', '#AF1E89', '#ef4444', '#34d399']
    for name, filename in filenames.items():
        df = get_dataframe(filename)
        df = get_num_label_and_predicted(df)

        acc_over_depth = {}
        for depth in df.depth.unique():
            matching = df[df.depth == depth].num_label == df[df.depth == depth].num_predicted
            acc_over_depth[depth] = matching.value_counts(normalize=True)[True]
        # acc_over_depth = get_acc_over_depth_calc(df)
        plt.plot(acc_over_depth.keys(), acc_over_depth.values(), label=name, color=colors[0])
        colors = colors[1:]
    # human = [0.777777778,0.555555556,0.777777778,0.666666667,0.777777778,0.722222222,0.833333333]
    # plt.plot(acc_over_depth.keys(), human, label='human')

    plt.title('Acc. over Reasoning Depth')
    plt.xlabel('Reasoning Depth')
    plt.ylabel('Accuracy')
    plt.legend()
    plt.savefig('statistics/acc_over_depth.png', dpi=800)
    plt.show()

def get_acc_over_arg_form(filenames):
    colors = ['#1EAF44', '#1E40AF', '#AF1E89', '#ef4444', '#34d399']
    forms = ['Modus Ponens', 'Modus Tonens', 'Hypothetical Syllogism', 'Disjunctive Syllogism', 'Reductio Ad Absurdum', 'Constructive Dilemma', 'Disjunction Elimination']
    short_forms = ['MP', 'MT', 'HS', 'DS', 'RAA', 'CD', 'DE']
    all_acc_over_form = {'Form': short_forms}
    for name, filename in filenames.items():
        df = get_dataframe(filename)
        df = get_num_label_and_predicted(df)

        acc_over_form = {}
        for f in forms:
            form_df = df[df.arg.str.contains(f)]
            form_df = form_df[form_df.depth < 2]
            matching = form_df.num_label == form_df.num_predicted
            acc_over_form[f] = matching.value_counts(normalize=True)[True]
        all_acc_over_form[name] = list(acc_over_form.values())
    print(all_acc_over_form)
    results_df = pd.DataFrame.from_dict(all_acc_over_form)
    # results_df.plot(x='Form', y=list(filenames.keys()), kind='bar', rot=0, color=colors).legend(
    #     loc='center', bbox_to_anchor=(0.25, 0.87)
    # )
    results_df.plot(x='Form', y=list(filenames.keys()), kind='bar', rot=0, color=colors).legend(
        loc='lower right'
    )
    # plt.xticks(rotation=90, ha='right')
    plt.title('Acc. over Argument Form (Depth=1)')
    plt.ylabel('Accuracy')
    plt.ylim((0.0,1.0))

    plt.savefig('statistics/acc_over_arg_form.png', dpi=800)
    plt.show()
    #     plt.bar(acc_over_form.keys(), acc_over_form.values(), label=name)
    # plt.legend()
    # plt.show()


if __name__ == "__main__":
    all_colors = ['#1E40AF', '#AF1E89', '#AF8D1E', '#1EAF44']
    get_acc_over_depth({
        'OpenAI o1-preview': 'eval/3_shot_cot_w_depth_openai_o1_results.csv',
        # 'GPT-4o': 'eval/3_shot_cot_w_depth_gpt4o_results.csv',
        # 'GPT-4': 'eval/3_shot_cot_w_depth_gpt4_results.csv',
        'Llama3-70B': 'eval/3_shot_cot_w_depth_llama70B_results.csv',
        'Llama3-8B': 'eval/3_shot_cot_w_depth_llama8B_results.csv'
    })