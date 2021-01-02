# -*- coding: utf-8 -*-
"""Homework2.1.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1XVb7R2uNR6SjgcLcfS-zT9lQDPv0_vO2

Import libraries
"""

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
import tensorflow as tf
import tensorflow.keras as keras

import random
import numpy as np
import sklearn.metrics 
from sklearn import datasets
from sklearn.model_selection import train_test_split, cross_val_score, ShuffleSplit, GridSearchCV
from sklearn import svm
from sklearn.naive_bayes import GaussianNB
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.utils.multiclass import unique_labels
import matplotlib.pyplot as plt


print("Libraries imported.")

"""Load Dataset from Drive


"""

from google.colab import drive
drive.mount('/content/drive')

"""Installing and using split-folders to create a training and a validation set"""

# Commented out IPython magic to ensure Python compatibility.
# %pip install split-folders tqdm

import splitfolders

splitfolders.ratio('/content/drive/MyDrive/ML/Homework2/Data set', \
                   output='/content/drive/MyDrive/ML/Homework2/Splitted_Dataset',\
                   seed=1337, ratio=(.7, .3), group_prefix=None)

"""Checking that the splitting has been correctly executed"""

import shutil

original_dataset_dir = '/content/drive/MyDrive/ML/Homework2/Splitted_Dataset'

train_dir = os.path.join(original_dataset_dir, 'train')
validation_dir = os.path.join(original_dataset_dir, 'val')
test_dir = os.path.join(original_dataset_dir, 'test')

if not os.path.exists(os.path.join(original_dataset_dir, 'test')):
  os.mkdir(test_dir)

folders = ['Caddies','Lollipops','Macaroni_&_Cheese_box','Melons',\
           'carving_knife_fork','juice_carton','plastic_food_container',\
           'water_glasses']

# Copying the first 4 images of each folder in the test_dir

'''
for f in folders:
  src = os.path.join(train_dir, f)
  fnames = os.listdir(src)
  i = 0
  for fname in fnames:
    src = os.path.join(train_dir, f)
    dst = os.path.join(original_dataset_dir, 'test')
    if i != 4:
      src = os.path.join(src, fname)
      dst = os.path.join(dst, fname)
      shutil.move(src, dst)
      i += 1
'''

tot_train = 0
tot_val = 0
tot_test = len(os.listdir(test_dir))

for f in folders:
  tot_train = tot_train + len(os.listdir(train_dir + '/' + f))
  tot_val = tot_val + len(os.listdir(validation_dir + '/' + f))
  
print('total training images: '  + str(tot_train))
print('total validation images: ' + str(tot_val))
print('total test images: ' + str(tot_test))

"""Data Preprocessing"""

'''
1) Read the picture files.
2) Decode the JPEG content to RGB grids of pixels.
3) Convert these into floating-point tensors.
4) Rescale the pixel values (between 0 and 255) to the [0, 1] interval (as you know,
   neural networks prefer to deal with small input values).
'''

from keras.preprocessing.image import ImageDataGenerator

train_datagen = ImageDataGenerator(rescale=1./255)
validation_datagen = ImageDataGenerator(rescale=1./255)

train_generator = train_datagen.flow_from_directory(train_dir,\
                                                    target_size=(150, 150),\
                                                    batch_size=32,\
                                                    class_mode='categorical')

validation_generator = validation_datagen.flow_from_directory(validation_dir,\
                                                        target_size=(150, 150),\
                                                        batch_size=32,\
                                                        class_mode='categorical')


for data_batch, labels_batch in train_generator:
  print('data batch shape:', data_batch.shape)
  print('labels batch shape:', labels_batch.shape)
  break

"""Instantiating the Convnet"""

from keras import layers
from keras import models

model = models.Sequential()
model.add(layers.Conv2D(32, (3, 3), activation='relu',\
                        input_shape=(150, 150, 3)))
model.add(layers.MaxPooling2D((2, 2)))
model.add(layers.Conv2D(64, (3, 3), activation='relu'))
model.add(layers.MaxPooling2D((2, 2)))
model.add(layers.Conv2D(128, (3, 3), activation='relu'))
model.add(layers.MaxPooling2D((2, 2)))
model.add(layers.Conv2D(128, (3, 3), activation='relu'))
model.add(layers.MaxPooling2D((2, 2)))
model.add(layers.Flatten())
model.add(layers.Dense(512, activation='relu'))
# 8 and softmax, why?
model.add(layers.Dense(8, activation='softmax'))

model.summary()

"""Configuring the model for training"""

from keras import optimizers
model.compile(optimizer='adam',\
              loss='categorical_crossentropy',\
              metrics=['accuracy'])

"""Fitting the model"""

# steps_per_epoch = int(number_of_train_samples / batch_size)
# val_steps = int(number_of_val_samples / batch_size)
history = model.fit(train_generator,steps_per_epoch=190,epochs=10,\
                              validation_data=validation_generator,validation_steps=82)

"""Saving the model"""

model.save('/content/drive/MyDrive/ML/Homework2/convnet1.h5')

"""Displaying curves of loss and accuracy"""

acc = history.history['accuracy']
val_acc = history.history['val_accuracy']
loss = history.history['loss']
val_loss = history.history['val_loss']
epochs = range(1, len(acc) + 1)
plt.plot(epochs, acc, 'bo', label='Training acc')
plt.plot(epochs, val_acc, 'b', label='Validation acc')
plt.title('Training and validation accuracy')
plt.legend()
plt.figure()
plt.plot(epochs, loss, 'bo', label='Training loss')
plt.plot(epochs, val_loss, 'b', label='Validation loss')
plt.title('Training and validation loss')
plt.legend()
plt.show()

"""### Using data augmentation

Setting up a data augmentation configuration
"""

datagen = ImageDataGenerator(rotation_range=40,width_shift_range=0.2,\
                             height_shift_range=0.2,shear_range=0.2,\
                             zoom_range=0.2,horizontal_flip=True,\
                             fill_mode='nearest')

"""Displaying some randomly augmented training images"""

from keras.preprocessing import image

for f in folders:
  train_dirs = os.path.join(train_dir, f)
  fnames = [os.path.join(train_dirs, fname) for
            fname in os.listdir(train_dirs)]

img_path = fnames[3] 
img = image.load_img(img_path, target_size=(150, 150))

x = image.img_to_array(img) 
x = x.reshape((1,) + x.shape)

i=0
for batch in datagen.flow(x, batch_size=1):
  plt.figure(i)
  imgplot = plt.imshow(image.array_to_img(batch[0]))
  i += 1
  if i % 4 == 0:
    break
plt.show()

"""Defining a new convnet that includes dropout"""

from keras import layers
from keras import models

# To fight overfitting, we add a Dropout layer to the model
model2 = models.Sequential()
model2.add(layers.Conv2D(32, (3, 3), activation='relu',\
                        input_shape=(150, 150, 3)))
model2.add(layers.MaxPooling2D((2, 2)))
model2.add(layers.Conv2D(64, (3, 3), activation='relu'))
model2.add(layers.MaxPooling2D((2, 2)))
model2.add(layers.Conv2D(128, (3, 3), activation='relu'))
model2.add(layers.MaxPooling2D((2, 2)))
model2.add(layers.Conv2D(128, (3, 3), activation='relu'))
model2.add(layers.MaxPooling2D((2, 2)))
model2.add(layers.Flatten())
model2.add(layers.Dropout(0.2))
model2.add(layers.Dense(512, activation='relu'))
model2.add(layers.Dense(8, activation='softmax'))

model2.summary()

model2.compile(optimizer='adam',\
              loss='categorical_crossentropy',\
              metrics=['accuracy'])

"""Training the convnet using data-augmentation generators"""

#'old' with dropout -> stop at 22
from keras import optimizers

train_datagen = ImageDataGenerator(rescale=1./255,rotation_range=40,\
                                   width_shift_range=0.2,height_shift_range=0.2,\
                                   shear_range=0.2,zoom_range=0.2,\
                                   horizontal_flip=True,)
test_datagen = ImageDataGenerator(rescale=1./255)
# We aren't augmenting validation data

train_generator = train_datagen.flow_from_directory(train_dir,\
                                                    target_size=(150, 150),\
                                                    batch_size=32,\
                                                    class_mode='categorical')
validation_generator = test_datagen.flow_from_directory(validation_dir,\
                                                         target_size=(150, 150),\
                                                         batch_size=32,\
                                                         class_mode='categorical')
 
history = model2.fit(train_generator,steps_per_epoch=190,epochs=22,validation_data=validation_generator,validation_steps=82)

"""save the model"""

model2.save('/content/drive/MyDrive/ML/Homework2/convnet2_softmax.h5')

"""load the model"""

model2 = models.load_model('/content/drive/MyDrive/ML/Homework2/convnet2_softmax.h5')

acc = history.history['accuracy']
val_acc = history.history['val_accuracy']
loss = history.history['loss']
val_loss = history.history['val_loss']
epochs = range(1, len(acc) + 1)
plt.plot(epochs, acc, 'bo', label='Training acc')
plt.plot(epochs, val_acc, 'b', label='Validation acc')
plt.title('Training and validation accuracy')
plt.legend()
plt.figure()
plt.plot(epochs, loss, 'bo', label='Training loss')
plt.plot(epochs, val_loss, 'b', label='Validation loss')
plt.title('Training and validation loss')
plt.legend()
plt.show()

"""### Blind Test"""

fnames = os.listdir(test_dir)
img_tensors = list()
for fname in fnames:
  try:
    img_path = os.path.join(test_dir,fname)
    img = image.load_img(img_path, target_size=(150, 150))
    img_tensor = image.img_to_array(img)
    img_tensor = np.expand_dims(img_tensor, axis=0) 
    img_tensor /= 255.
    img_tensors.append(img_tensor)
  except FileNotFoundError:
    print(img_path + ' not found')

print(len(img_tensors))

"""Displaying a test picture"""

plt.imshow(img_tensors[0][0])
plt.show()

"""Instantiating a model from an input tensor and a list of output tensors"""

layer_outputs = [layer.output for layer in model2.layers[:8]] 
activation_model = models.Model(inputs=model2.input, outputs=layer_outputs)

"""Running the model in predict mode

"""

import numpy as np

for i in range(len(img_tensors)):
  prediction = model2.predict(img_tensors[i])
  plt.imshow(img_tensors[i][0])
  plt.show()
  print(folders[np.argmax(prediction)])