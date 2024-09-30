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
        else:
            print(l)
            print(type(l))
    df['num_predicted'] = num_predicted
    return df

def eval(filename):
    df = pd.read_csv(filename)[:300]
    if 'justlogic' in filename:
        df = get_num_label_and_predicted(df)
        matching = df.num_label == df.num_predicted
    else:
        matching = df.label == df.predicted
    print(matching[:10])
    print('sample size:', len(df))
    print('overall acc:', matching.value_counts(normalize=True)[True])

if __name__ == "__main__":
    eval('ci_eval/ci_results_proofwriter.csv')
