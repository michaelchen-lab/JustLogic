import json
import pandas as pd
import numpy as np

def split(dataset):
    df = pd.read_csv(dataset)
    train, validate, test = [], [], []
    for i in range(1,8):
        depth_df = df[df.depth == i]

        d_train, d_validate, d_test = np.split(depth_df.sample(frac=1, random_state=0), [int(.7*len(depth_df)), int(.85*len(depth_df))])
        train.append(d_train)
        validate.append(d_validate)
        test.append(d_test)

    train = pd.concat(train)
    validate = pd.concat(validate)
    test = pd.concat(test)

    return train, validate, test

train, validate, test = split('dataset.csv')
train.to_csv('train_dataset.csv', index=False)
validate.to_csv('validate_dataset.csv', index=False)
test.to_csv('test_dataset.csv', index=False)
