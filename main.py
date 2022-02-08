from tensorflow import keras
from tensorflow.keras.layers import Input, Dense, Dropout, Flatten, Conv2D, MaxPooling2D, BatchNormalization
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping, TensorBoard
# from PIL import Image

import pandas as pd
import numpy as np
import pickle
# import csv

def create_CNN():
  print("Creating CNN model...")
  input = Input((80, 150, 3))
  out = input
  out = Conv2D(filters=32, kernel_size=(3, 3), padding='same', activation='relu')(out)
  out = Conv2D(filters=32, kernel_size=(3, 3), activation='relu')(out)
  out = BatchNormalization()(out)
  out = MaxPooling2D(pool_size=(2, 2))(out)
  out = Dropout(0.3)(out)
  out = Conv2D(filters=64, kernel_size=(3, 3), padding='same', activation='relu')(out)
  out = Conv2D(filters=64, kernel_size=(3, 3), activation='relu')(out)
  out = BatchNormalization()(out)
  out = MaxPooling2D(pool_size=(2, 2))(out)
  out = Dropout(0.3)(out)
  out = Conv2D(filters=128, kernel_size=(3, 3), padding='same', activation='relu')(out)
  out = Conv2D(filters=128, kernel_size=(3, 3), activation='relu')(out)
  out = BatchNormalization()(out)
  out = MaxPooling2D(pool_size=(2, 2))(out)
  out = Dropout(0.3)(out)
  out = Conv2D(filters=256, kernel_size=(3, 3), activation='relu')(out)
  out = BatchNormalization()(out)
  out = MaxPooling2D(pool_size=(2, 2))(out)
  out = Flatten()(out)
  out = Dropout(0.3)(out)
  # out = Dense(10, name='digit', activation='softmax')(out)
  out = [Dense(10, name='digit1', activation='softmax')(out), 
         Dense(10, name='digit2', activation='softmax')(out), 
         Dense(10, name='digit3', activation='softmax')(out), 
         Dense(10, name='digit4', activation='softmax')(out)]
  print(out)
  model = keras.models.Model(inputs=input, outputs=out)
  model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
  model.summary()
  return model

def get_label(path):
  print("Process " + path.split('/')[-1] + " label!")
  df = pd.read_csv(path + "/label.csv", names=["image", "code"], header=None)
  # get label
  read_label = []
  label = [[] for _ in range(4)]
  for i in range(df.shape[0]):
    num = df["code"][i]
    code = np.array([[int(v) for v in list(str(num).zfill(4))]]).reshape(-1)
    one_hot_code = np.eye(10)[code]
    read_label.append(one_hot_code)
  for arr in read_label:
    for i in range(4):
      label[i].append(arr[i])
  label = [arr for arr in np.asarray(label)] # 最後要把6個numpy array 放在一個list
  return label

train_data = np.load("./data/train/train_19600.npy")
print("train data: ", train_data.shape)
valid_data = np.load("./data/valid/validate_5600.npy")
print("valid data: ", valid_data.shape)
print("---------")
train_label = pickle.load(open("./data/train/train_label.pkl", "rb"))
valid_label = pickle.load(open("./data/valid/valid_label.pkl", "rb"))
print(f"train label: {len(train_label)} {train_label[0].shape}")
print(f"valid label: {len(valid_label)} {valid_label[0].shape}")

# model_path = "./model/captcha_model.h5"
CNN_model = create_CNN()
# CNN_model = keras.models.load_model(model_path)
new_model_path = "./model/captcha_model_new_1.h5"
checkpoint = ModelCheckpoint(new_model_path, monitor='val_digit2_accuracy', verbose=1, save_best_only=True, mode='max')
earlystop = EarlyStopping(monitor='val_digit2_digit2_accuracy', patience=5, verbose=1, mode='auto')
# tensorBoard = TensorBoard(log_dir = "./logs", histogram_freq = 1)
callbacks_list = [checkpoint, earlystop] # tensorBoard
CNN_model.fit(train_data, train_label, batch_size=1, epochs=200, verbose=2, validation_data=(valid_data, valid_label), callbacks=callbacks_list)
