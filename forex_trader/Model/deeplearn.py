from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.utils import class_weight
import tensorflow as tf

import pandas as pd
import numpy as np

class neuralnet( BaseEstimator, TransformerMixin):
    def __init__(self, nodes , activation, layer_type, epochs):
        super().__init__()
        self.epochs = epochs
        self.construct(nodes, activation, layer_type)
        self.compile()

    def construct(self, nodes, activation, layer_types):
        final_list = []
        for node, activation, layer_type in zip(nodes, activation, layer_types):
            if layer_type == "dense":
                final_list.append(tf.keras.layers.Dense(int(node), activation=activation))
            elif layer_type == "dropout":
                final_list.append(tf.keras.layers.Dropout(float(node)))
        self.model = tf.keras.models.Sequential(final_list)

    def compile(self):
        self.model.compile(optimizer=tf.keras.optimizers.Adam(
                                learning_rate=0.00001
                            ),
                            loss='binary_crossentropy',
                            metrics=['precision', "recall"]
        )

    def create_class_weights(self, y):
        weights = class_weight.compute_class_weight('balanced', classes=np.unique(y), y=y)
        class_weights = dict(enumerate(weights))
        return class_weights

    def fit(self, X, y):
        class_weights = self.create_class_weights(y)
        self.model.fit(X, y, epochs=self.epochs)
        return self

    def predict_proba(self, X):
        pred =  self.model.predict(X)
        return pred[:,0]
    
    def predict(self, X):
        pred_proba =  self.model.predict(X)[:,0]
        pred = [1 if p > 0.5 else 0 for p in pred_proba]
        return pred
