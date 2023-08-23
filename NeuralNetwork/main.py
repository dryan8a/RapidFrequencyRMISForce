from numpy import loadtxt
from keras.models import Sequential
from keras.layers import Dense
import matplotlib.pyplot as plt

datasetFile = open("RandomizedTrainingData.txt", "r")

datasetLines = datasetFile.readlines()

inputTrainData = list()
outputTrainData = list()
inputTestData = list()
outputTestData = list()

trainAmount = datasetLines.__len__() * 0.9

for i in range(0,datasetLines.__len__()):
    values = datasetLines[i].split(' ')
    inputDatum = (float(values[0]), float(values[1]), float(values[2]), float(values[3]), float(values[4]), float(values[5]), float(values[6]), float(values[7]), float(values[8]))
    outputDatum = (float(values[9]), float(values[10]), float(values[11]))
    if i < trainAmount:
        inputTrainData.append(inputDatum)
        outputTrainData.append(outputDatum)
    else:
        inputTestData.append(inputDatum)
        outputTestData.append(outputDatum)

#print(inputTrainData.__len__())
#print(outputTrainData.__len__())
#print(inputTestData.__len__())
#print(outputTestData.__len__())

''' Best Configurations:
    Dense 7, Dense 3, Epochs 200, Batch size 5: loss 0.0077, accuracy 0.987, mean absolute error 0.0299, 750us/step 
    Dense 8, Dense 3, Epochs 200, Batch size 5: loss 0.0069, accuracy 0.9944, mean absolute error 0.0251, 750us/step 
'''



model = Sequential()
model.add(Dense(8, input_shape=(9,), activation='relu'))
model.add(Dense(3, activation='linear'))

model.compile(loss='mean_squared_error', optimizer='adam', metrics=['accuracy', 'mean_absolute_error'])

history = model.fit(inputTrainData, outputTrainData, epochs=200, batch_size = 5)

loss, accuracy, mean_absolute_error = model.evaluate(inputTestData, outputTestData)

'''
plt.plot(history.history['accuracy'])
plt.title('model accuracy')
plt.ylabel('accuracy')
plt.xlabel('epoch')
plt.legend(['train', 'validation'], loc='upper left')
plt.show(block=True)

plt.plot(history.history['loss'])
plt.title('model loss')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['train', 'validation'], loc='upper left')
plt.show(block=True)
'''