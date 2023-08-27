from numpy import loadtxt
import numpy
from tensorflow import metrics
import tensorflow as tf
from keras.models import Sequential
from keras.layers import Dense
import matplotlib.pyplot as plt
import time

@tf.function
def predict(model, input):
    return model(input)

#DATA LOADING
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

print(inputTrainData.__len__())
print(outputTrainData.__len__())
print(inputTestData.__len__())
print(outputTestData.__len__())

''' Best Configurations:
    Dense 7, Dense 3, Epochs 200, Batch size 5: loss 0.0077, accuracy 0.987, mean absolute error 0.0299, 750us/step 
    Dense 8, Dense 3, Epochs 200, Batch size 5: loss 0.0069, accuracy 0.9944, mean absolute error 0.0251, 750us/step 
'''


#MODEL CREATION/TRAINING
model = Sequential()
model.add(Dense(8, input_shape=(9,), activation='relu'))
model.add(Dense(3, activation='linear'))

model.compile(loss='mean_squared_error', optimizer='adam', metrics=['mean_absolute_error'])

history = model.fit(inputTrainData, outputTrainData, epochs=5, batch_size = 5)


speedResults = list()
meanSpeed = 0.0

#SINGLE ESTIMATION TEST
singleMSEResults = list()
singleMAEResults = list()
singleMSE = 0.0
singleMAE = 0.0
for i in range(0,inputTestData.__len__()):
    input = numpy.asarray(inputTestData[i]).reshape(1,-1)
    startTime = time.perf_counter_ns()
    prediction = predict(model,input)
    endTime = time.perf_counter_ns()

    mean_absolute_error = metrics.mean_absolute_error(outputTestData[i],prediction).numpy()[0]
    mean_square_error = metrics.mean_squared_error(outputTestData[i],prediction).numpy()[0]

    singleMAE += mean_absolute_error
    singleMSE += mean_square_error

    singleMAEResults.append(mean_absolute_error)
    singleMSEResults.append(mean_square_error)

    elapsedMicro = float(endTime - startTime) / 1000.0
    meanSpeed += elapsedMicro
    speedResults.append(elapsedMicro)
singleMAE /= inputTestData.__len__()
singleMSE /= inputTestData.__len__()



meanSpeed /= inputTestData.__len__()
meanFrequency = 1000000.0 / meanSpeed

#RESULT OUTPUT
print("Single Estimation Test MAE: " + str(singleMAE))
print("Single Estimation Test MSE(Loss): " + str(singleMSE))

print("Test Prediction Mean Speed: " + str(meanSpeed))
print("Test Prediction Frequency: " + str(meanFrequency))

plt.plot(history.history['loss'])
plt.title('Training Mean Squared Error (Loss)')
plt.ylabel('mean squared error')
plt.xlabel('epoch')
plt.show(block=True)

plt.plot(history.history['mean_absolute_error'])
plt.title('Training Mean Absolute Error')
plt.ylabel('mean absolute error')
plt.xlabel('epoch')
plt.show(block=True)

plt.scatter(x=range(1,singleMAEResults.__len__()+1), y=singleMAEResults, s=1)
plt.title('Single Estimation Absolute Error')
plt.ylabel('absolute error')
plt.xlabel('prediction')
plt.show(block=True)

plt.scatter(x=range(1,singleMSEResults.__len__()+1), y=singleMSEResults, s=1)
plt.title('Single Estimation Squared Error')
plt.ylabel('squared error')
plt.xlabel('prediction')
plt.show(block=True)

plt.scatter(x=range(1,singleMSEResults.__len__()+1), y=speedResults, s=1)
plt.title('Estimation Speed')
plt.ylabel('Speed (microseconds)')
plt.xlabel('prediction')
plt.show(block=True)