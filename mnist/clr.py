import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' # ignore tf warnings about cuda
from keras.layers import Conv2D, MaxPooling2D, Dense, Flatten
from keras.metrics import CategoricalAccuracy
from sklearn.metrics import classification_report, matthews_corrcoef
from keras.losses import CategoricalCrossentropy
from keras.callbacks import EarlyStopping, LearningRateScheduler
from keras.models import Sequential
from keras.optimizers import Adam
from pandas import DataFrame
import tensorflow as tf
import numpy as np
import random
import sys

from mnistloader import load_mnist, mnist_preprocess
from utils import make_graphs, print_to_file

GLOBAL_EPOCHS = 50

def scheduler(epoch, lr):
    lrmin=0.00001
    lrmax=0.001
    step_size=10
    max_iter=GLOBAL_EPOCHS
    delta=10
    clr = lrmin + ((lrmax-lrmin)*(1.-np.fabs((epoch/step_size)-(2*np.floor(epoch/(2*step_size)))-1.)))
    clr_decay = clr/(1.+((delta-1.)*(epoch/max_iter)))
    return clr_decay

VERBOSE = 0
if not VERBOSE: print("Change verbose to 1 to see messages.")

last_epochs = list()
mccs = list()
dicts = list()
histories = list()
items = [10, 50, 250, 500]
patiences = [10, 8, 6, 5]
for index, item in enumerate(items):

    # Load the dataset
    x_train, y_train, x_test, y_test = load_mnist(items_per_class=item) # 10 items per class means a dataset size of 100
    if VERBOSE: print("Shape after loading: ", x_train.shape, y_train.shape, x_test.shape, y_test.shape)

    # Pre process images
    x_train, y_train, x_test, y_test = mnist_preprocess(x_train, y_train, x_test, y_test)
    if VERBOSE: print("Shape after pre processing: ", x_train.shape, y_train.shape, x_test.shape, y_test.shape)
    
    if VERBOSE: print(f"Training set size: {len(x_train)}")
    if VERBOSE: print(f"Test set size: {len(x_test)}", end='\n\n')

    seed_value = 0
    # 1. Set the `PYTHONHASHSEED` environment variable at a fixed value
    os.environ['PYTHONHASHSEED']=str(seed_value)
    # 2. Set the `python` built-in pseudo-random generator at a fixed value
    random.seed(seed_value)
    # 3. Set the `numpy` pseudo-random generator at a fixed value
    np.random.seed(seed_value)
    # 4. Set the `tensorflow` pseudo-random generator at a fixed value
    tf.random.set_seed(seed_value)

    epochs = GLOBAL_EPOCHS
    batch_size = 32
    learning_rate = 0.001
    patience = patiences[index]
    num_classes = y_test.shape[1]
    # build model
    model = Sequential()
    model.add(Conv2D(filters=64, kernel_size=(7,7), input_shape=(28, 28, 1), activation='relu', padding='same'))
    model.add(MaxPooling2D(pool_size=(4,4), padding='same'))
    model.add(Conv2D(filters=128, kernel_size=(5,5), activation='relu', padding='same'))
    model.add(Conv2D(filters=64, kernel_size=(5,5), activation='relu', padding='same'))
    model.add(Conv2D(filters=64, kernel_size=(5,5), activation='relu', padding='same'))
    model.add(Conv2D(filters=32, kernel_size=(7,7), activation='relu', padding='same'))
    model.add(Conv2D(filters=128, kernel_size=(5,5), activation='relu', padding='same'))
    model.add(Flatten())
    model.add(Dense(units = 32, activation='relu'))
    model.add(Dense(units = 32, activation='relu'))
    model.add(Dense(num_classes, activation='softmax'))
    
    model.compile(loss=CategoricalCrossentropy(), optimizer=Adam(lr=learning_rate), metrics=[CategoricalAccuracy()])

    if VERBOSE: model.summary()

    earlyStop = EarlyStopping(monitor='val_loss', mode='min', patience=patience, verbose=VERBOSE)
    history = model.fit(x_train, y_train, 
                        validation_data=(x_test, y_test), 
                        epochs=epochs, 
                        batch_size=batch_size, 
                        verbose=VERBOSE, 
                        callbacks=[earlyStop,LearningRateScheduler(scheduler)])

    histories.append(history)

    predictions = model.predict(x_test)
    y_test = np.argmax(y_test, axis=1)
    predictions = np.argmax(predictions, axis=1)
    
    dicts.append(classification_report(y_true=y_test, y_pred=predictions, digits=3, output_dict=True))
    mccs.append(matthews_corrcoef(y_true=y_test, y_pred=predictions))
    last_epochs.append(len(history.history['loss']))

print_to_file(dicts, mccs, items, epochs, batch_size, learning_rate, patiences, last_epochs, model, 'clr')
make_graphs(histories, items, 'clr')