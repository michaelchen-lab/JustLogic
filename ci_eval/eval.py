import pandas as pd

def eval(filename):
    df = pd.read_csv(filename)[:300]

    matching = df.label == df.predicted
    print('sample size:', len(df))
    print('overall acc:', matching.value_counts(normalize=True)[True])

if __name__ == "__main__":
    eval('ci_eval/results_gpt4_folio.csv')
