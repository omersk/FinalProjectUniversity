import numpy as np
import tensorflow as tf
from pathlib import Path
import cv2
from random import shuffle
# example of random rotation image augmentation
from numpy import expand_dims
from keras.preprocessing.image import load_img
from keras.preprocessing.image import save_img
from keras.preprocessing.image import img_to_array
from keras.preprocessing.image import ImageDataGenerator
from matplotlib import pyplot

numberOfExternalRotation = 1
X = []
Y = []
NAMES = {

}


def getRotatedImages():
    # load the image
    img = load_img("resized.jpg")
    # convert to numpy array
    data = img_to_array(img)
    # expand dimension to one sample
    samples = expand_dims(data, 0)
    # create image data augmentation generator
    datagen = ImageDataGenerator(rotation_range=90)
    # prepare iterator
    it = datagen.flow(samples, batch_size=1)
    # generate samples and plot
    rotated = []
    for i in range(numberOfExternalRotation):
        # generate batch of images
        batch = it.next()
        # convert to unsigned integers for viewing
        save_img("resized.jpg", batch[0].astype('uint8'))
        rotated.append(np.asarray(cv2.imread("resized.jpg", cv2.IMREAD_UNCHANGED)))

    return rotated

i = 0
for filename in Path('data').rglob('*.jpg'):
    i += 1
    img = cv2.imread(str(filename), cv2.IMREAD_UNCHANGED)
    resized = cv2.resize(img, (150, 150), interpolation=cv2.INTER_AREA)
    cv2.imwrite("resized.jpg", resized)
    data = np.asarray(resized)
    X.append(np.asarray(resized))
    X.extend(getRotatedImages())
    thisName = str(filename).split("_")[0].split("\\")[1].split(" ")[0]
    if i == 1:
        NAMES[thisName] = 0
    if thisName in NAMES.keys():
        Y.append(np.asarray(NAMES[thisName]))
        for j in range(numberOfExternalRotation):
            Y.append(np.asarray(NAMES[thisName]))
    else:
        print(NAMES.values())
        NAMES[thisName] = max(NAMES.values()) + 1
        Y.append(np.asarray(NAMES[thisName]))
        for j in range(numberOfExternalRotation):
            Y.append(np.asarray(NAMES[thisName]))

#Z = list(zip(X, Y))
#shuffle(Z)  # WE SHUFFLE X,Y TO PERFORM RANDOM ON THE TEST LEVEL
#X, Y = zip(*Z)

X = np.asarray(X)
Y = np.asarray(Y)

model = tf.keras.models.Sequential([
    tf.keras.layers.Conv2D(64, (3, 3), activation='relu', input_shape=(150, 150, 3)),
    tf.keras.layers.MaxPooling2D(2, 2),
    tf.keras.layers.Conv2D(128, (3, 3), activation='relu'),
    tf.keras.layers.MaxPooling2D(2, 2),
    tf.keras.layers.Conv2D(256, (3, 3), activation='relu'),
    tf.keras.layers.MaxPooling2D(2, 2),
    tf.keras.layers.Conv2D(512, (3, 3), activation='relu'),
    tf.keras.layers.MaxPooling2D(2, 2),
    tf.keras.layers.Conv2D(1024, (3, 3), activation='relu'),
    tf.keras.layers.MaxPooling2D(2, 2),
    tf.keras.layers.Flatten(),
    tf.keras.layers.Dense(2048, activation='relu'),
    tf.keras.layers.Dense(len(NAMES), activation='softmax', name='pred')

])
model.compile(optimizer='adam',
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])
# -------------- OUR TENSOR FLOW NEURAL NETWORK MODEL -------------- #
print("fitting")
history = model.fit(X, Y, epochs=1, batch_size=2)
print("testing")
X_val = []
Y_val = []
for filename in Path('tIm').rglob('*.jpg'):
    img = cv2.imread(str(filename), cv2.IMREAD_UNCHANGED)
    resized = cv2.resize(img, (150, 150), interpolation=cv2.INTER_AREA)
    X_val.append(np.asarray(resized))
    thisName = str(filename).split("_")[0].split("\\")[1].split(" ")[0]
    if thisName in NAMES.keys():
        Y_val.append(np.asarray(NAMES[thisName]))
    else:
        print(NAMES.values())
        NAMES[thisName] = max(NAMES.values()) + 1
        Y_val.append(np.asarray(NAMES[thisName]))
Z_val = list(zip(X_val, Y_val))
shuffle(Z_val)  # WE SHUFFLE X_val,Y_val TO PERFORM RANDOM ON THE TEST LEVEL
X_val, Y_val = zip(*Z_val)

X_val = np.asarray(X_val)
Y_val = np.asarray(Y_val)
h = model.evaluate(X_val, Y_val)
print(h)
