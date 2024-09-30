import pandas as pd

def eval(filename):
    df = pd.read_csv(filename, encoding = "ISO-8859-1")
    df.dropna(subset=['predicted'], inplace=True)
    # df = df[df.depth == 1]

    # true, false, uncertain
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

    # df['label'] = df['label'].astype('str')
    # df['label'] = df.label.str.lower()
    # df['predicted'] = df['predicted'].astype('str') 
    # df['label'] = df.label.str.lower()
    # # df.replace({True: 'Correct', False: 'Incorrect'})

    print(df.iloc[0])

    matching = df.num_label == df.num_predicted
    print(matching[:10])
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