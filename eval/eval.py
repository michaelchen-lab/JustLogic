import pandas as pd

def eval(filename):
    df = pd.read_csv(filename, encoding = "ISO-8859-1")
    df.dropna(subset=['predicted'], inplace=True)
    print(len(df))
    # df.replace({True: 'Correct', False: 'Incorrect'})

    matching = df.label == df.predicted
    print('sample size:', len(df))
    print('overall acc:', matching.value_counts(normalize=True)[True])

    # for ans in pd.unique(df.label):
    #     ans_df = df[df.label == ans]
    #     matching = ans_df.label == ans_df.predicted
    #     print(ans)
    #     print('acc:', matching.value_counts(normalize=True))
    
    # print(df[df.label == 'true'])

def majority_baseline(filename):
    df = pd.read_csv(filename)
    print(df.label.value_counts(normalize=True))

if __name__ == "__main__":
    # eval('context_independent_eval\ci_independent_results.csv')
    eval('eval/3_shot_cot_w_depth_gpt4_results.csv')