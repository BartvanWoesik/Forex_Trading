import pandas as pd
import numpy as np
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Dense ,  Dropout, Conv1D, LSTM
import tensorflow as tf

from tensorflow.keras import optimizers
from scipy.stats import zscore
import logging



class ConvModel():

    def __init__(self, data):
        self.optimizer = tf.keras.optimizers.Adam(
            learning_rate=0.1,
            beta_1=0.9,
            beta_2=0.999,
            epsilon=1e-07,
            amsgrad=False,
            weight_decay=None,
            clipnorm=None,
            clipvalue=None,
            global_clipnorm=None,
            use_ema=False,
            ema_momentum=0.99,
            ema_overwrite_frequency=None,
            jit_compile=True,
            name='Adam'
        )
        self.model = Sequential()
        self.data = data


    def create_model(self):
        logging.info(f'Create model')
        self.model.add(Conv1D(64, 3 , activation = 'relu',input_shape = (data.X[0].shape)))
        self.model.add(LSTM(units = 1028, activation = 'relu'))
        self.model.add(Conv1D(64,1, activation = 'relu'))
        self.model.add(Dropout(rate = 0.01))
        self.model.add(Dropout(rate = 0.01))
        self.model.add(Dense(units = 256, activation = 'relu'))
        self.model.add(Dense(units =512, activation = 'relu'))
        self.model.add(Dropout(rate = 0.01))
        self.model.add(Dense(units = 128, activation = 'relu'))
        self.model.add(Dense(units = 64, activation = 'relu'))
        self.model.add(Dense(units = 3, activation = 'sigmoid'))

        self.model.compile(loss = 'mse', optimizer='adam', metrics='accuracy')
    
    def fit(self):
        logging.info('Fit model using x_train and y_train')
        self.model.fit(self.data.X_train, self.data.y_train, epochs=200, batch_size=32000)
    
    def predict(self):
        logging.info('Predict using X_test')
        return self.model.predict(self.data.X_test)
    