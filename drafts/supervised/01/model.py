import numpy as np
from keras.optimizers import Adam, schedules, SGD
from keras.models import Sequential
from keras.layers import Dense, Conv1D, Flatten, MaxPooling1D, LSTM, Reshape, Input, BatchNormalization, ReLU, GlobalAveragePooling1D
from sklearn.preprocessing import MinMaxScaler
from functions.utils import toLstm
from keras.callbacks import ModelCheckpoint, ReduceLROnPlateau, EarlyStopping

class Model:
    def __init__(self, config, train_x, train_y):
        self.config = config
        self.scaler = MinMaxScaler()
        self.train_x = train_x
        self.train_y = train_y
        self.model = self.create_model()
        self.history = None
        self.callbacks = self.create_callbacks()
        self.loded_model = None

    def create_callbacks(self):
        return [
            ModelCheckpoint(
                "best_model.keras", save_best_only=True, monitor="val_loss"
            ),
            ReduceLROnPlateau(
                monitor="val_loss", factor=0.5, patience=20, min_lr=0.0001
            ),
            EarlyStopping(monitor="val_loss", patience=50, verbose=1),
        ]


    def create_model(self):
        learning_rate_schedule = schedules.ExponentialDecay(
            initial_learning_rate=self.config.learning_rate,
            decay_steps=self.config.decay_steps,
            decay_rate=self.config.decay_rate,
            staircase=True)

        print("self.train_x.shape: ", self.train_x.shape)
        print("x_train first row: ", self.train_x[0])
        
        input_shape = (self.train_x.shape[1], self.train_x.shape[2])
        model = Sequential()
        model.add(Input(shape=input_shape))
        model.add(Conv1D(filters=64, kernel_size=3, activation='relu', padding="same"))
        BatchNormalization()
        ReLU()
        model.add(Conv1D(filters=64, kernel_size=3, activation='relu', padding="same"))
        BatchNormalization()
        ReLU()
        model.add(Conv1D(filters=64, kernel_size=3, activation='relu', padding="same"))
        BatchNormalization()
        ReLU()
        GlobalAveragePooling1D()
        model.add(Flatten())

        """
        Sanki Dense 64 ve 32'de daha iyi sonuçlar vermişti.
        Ama tabi ki veriyi de değiştirdim. 1000 yerine tümünü aldım.
        Ama deneme yanılma ile bulunacak bir şekilde.

        ÖNEMLİİİİİ: 1000 EPOCH yetmedi

        """


        # model.add(LSTM(64, input_shape=(self.train_x.shape[1], self.train_x.shape[2]), activation='relu', return_sequences=True))
        # model.add(LSTM(32, activation='relu'))
        # model.add(Reshape((256, self.train_x.shape[1], self.train_x.shape[2])))  # Features from train_x
        # model.add(Conv1D(128, 3, activation='relu', input_shape=(1, self.train_x.shape[1], self.train_x.shape[2])))
        # model.add(MaxPooling1D(2))
        # model.add(Flatten())
        model.add(Dense(64, input_shape=(self.train_x.shape[1],), activation='softmax'))
        model.add(Dense(32, activation='relu'))
        model.add(Dense(32, activation='relu'))
        model.add(Dense(2))
        model.compile(optimizer='adam', loss='mse', metrics=['accuracy'])
        # model.compile(optimizer='adam', loss="sparse_categorical_crossentropy", metrics=["sparse_categorical_accuracy"])
        model.summary()
        return model
    
    # def prepare(self, data):
    #     scaled = self.scaler.fit_transform(data)
    #     if self.config.lstm_window_size > 1:
    #         return toLstm(scaled, self.config.lstm_window_size) 
        

    def train(self):
        self.history = self.model.fit(self.train_x, self.train_y, epochs=self.config.epochs, batch_size=self.config.batch_size, validation_split=self.config.validation_split, verbose=self.config.verbose, callbacks=self.callbacks)

    def predict(self, data):
        return self.model.predict(data)
    
    def evaluate(self, test_x, test_y):
        return self.model.evaluate(test_x, test_y)
    
    def save(self, file):
        self.model.save(file)

    def load(self, file):
        self.loded_model = self.model.load_model(file)
