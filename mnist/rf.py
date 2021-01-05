from sklearn.metrics import classification_report, matthews_corrcoef
from utils import load_mnist_pickle
from pandas import DataFrame
from sklearn.ensemble import RandomForestClassifier
import tensorflow as tf
import numpy as np
import random
import sys
import os

mccs = list()
dicts = list()
VERBOSE = 0
items = [10, 50, 250, 500]
for item in items:

    # Load the dataset
    x_train, y_train, x_test, y_test = load_mnist_pickle(id=item)
    if VERBOSE: print("Shape after loading: ", x_train.shape, y_train.shape, x_test.shape, y_test.shape)

    # Reshape to vector form
    x_train = x_train.reshape(len(x_train), 28*28)
    x_test = x_test.reshape(len(x_test), 28*28)
    if VERBOSE: print("Shape after converting to vector", x_train.shape, y_train.shape, x_test.shape, y_test.shape)

    # Revert categorical arrays on labels
    y_train = [np.argmax(label) for label in y_train]
    y_test = [np.argmax(label) for label in y_test]
    y_train = np.asarray(y_train)
    y_test = np.asarray(y_test)
    if VERBOSE: print("Shape after converting labels: ", y_train.shape, y_train.shape)

    seed_value = 0
    # 1. Set the `PYTHONHASHSEED` environment variable at a fixed value
    os.environ['PYTHONHASHSEED']=str(seed_value)
    # 2. Set the `python` built-in pseudo-random generator at a fixed value
    random.seed(seed_value)
    # 3. Set the `numpy` pseudo-random generator at a fixed value
    np.random.seed(seed_value)
    # 4. Set the `tensorflow` pseudo-random generator at a fixed value
    tf.random.set_seed(seed_value)

    # Model definition
    clf = clf = RandomForestClassifier(n_jobs=3,n_estimators=3000, criterion='gini', min_samples_split=2, max_depth=10, random_state=seed_value)

    if VERBOSE: print("Training")
    # Model training
    clf.fit(x_train, y_train)

    # Model testing
    predictions = clf.predict(x_test)

    if VERBOSE: print("Training complete", end='\n\n')

    dicts.append(classification_report(y_true=y_test, y_pred=predictions, digits=3, output_dict=True))
    mccs.append(matthews_corrcoef(y_true=y_test, y_pred=predictions))

original_stdout = sys.stdout
with open(f'results/rf.txt', 'w') as f:
    sys.stdout = f
    for index, dictionary in enumerate(dicts):
        print()
        print("items/class: ", items[index])
        dataFrame = DataFrame.from_dict(dictionary).T.round(3)
        dataFrame['support'] = dataFrame['support'].astype(int)
        dataFrame.loc['accuracy', 'support'] = 10000
        dataFrame.loc['accuracy','recall'] = '-'
        dataFrame.loc['accuracy','precision'] = '-'
        print(dataFrame)
        print("mcc: ", round(mccs[index],3))
        print()
sys.stdout = original_stdout
f.close()