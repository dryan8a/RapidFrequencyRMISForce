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
    inputDatum = (float(values[0])/33333, float(values[1]), float(values[2]), float(values[3]), float(values[4]), float(values[5]), float(values[6]), float(values[7]), float(values[8]), float(values[9]), float(values[10]), float(values[11]), float(values[12]))
    outputDatum = (float(values[13]), float(values[14]), float(values[15]))
    if i < trainAmount:
        inputTrainData.append(inputDatum)
        outputTrainData.append(outputDatum)
    else:
        inputTestData.append(inputDatum)
        outputTestData.append(outputDatum)

orderedDatasetFile = open("TrainingData.txt", "r")
orderedDatasetLines = orderedDatasetFile.readlines()

inputFeedbackTestData = list()
outputFeedbackTestData = list()

for i in range(0,inputTestData.__len__()):
    values = orderedDatasetLines[i].split(' ')
    inputDatum = (float(values[0])/33333, float(values[1]), float(values[2]), float(values[3]), float(values[4]), float(values[5]), float(values[6]), float(values[7]), float(values[8]), float(values[9]), float(values[10]), float(values[11]), float(values[12]))
    outputDatum = (float(values[13]), float(values[14]), float(values[15]))
    inputFeedbackTestData.append(inputDatum)
    outputFeedbackTestData.append(outputDatum)

print(inputTrainData[0])
print(outputTrainData[0])

print(inputTrainData.__len__())
print(outputTrainData.__len__())
print(inputTestData.__len__())
print(outputTestData.__len__())
print(inputFeedbackTestData.__len__())
print(outputFeedbackTestData.__len__())

''' Best Configurations:
    Dense 7, Dense 3, Epochs 200, Batch size 5: loss 0.0077, accuracy 0.987, mean absolute error 0.0299, 750us/step 
    Dense 8, Dense 3, Epochs 200, Batch size 5: loss 0.0069, accuracy 0.9944, mean absolute error 0.0251, 750us/step 
'''


#MODEL CREATION/TRAINING
model = Sequential()
model.add(Dense(13, input_shape=(13,), activation='relu'))
model.add(Dense(3, activation='linear'))

model.compile(loss='mean_squared_error', optimizer='adam', metrics=['mean_absolute_error'])

history = model.fit(inputTrainData, outputTrainData, epochs=50, batch_size = 5)


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

#FEEDBACK ESTIMATION TEST
feedbackMSEResults = list()
feedbackMAEResults = list()
feedbackMSE = 0.0
feedbackMAE = 0.0
prevPrediction = ()
for i in range(0,inputFeedbackTestData.__len__()):
    inputCopy = inputFeedbackTestData[i]
    if inputCopy[0] > 3000:
        inputCopy = (inputCopy[0], inputCopy[1], inputCopy[2], inputCopy[3], inputCopy[4], inputCopy[5], inputCopy[6], inputCopy[7], inputCopy[8], inputCopy[9], prevPrediction.numpy()[0][0], prevPrediction.numpy()[0][1], prevPrediction.numpy()[0][2])
    input = numpy.array(inputCopy).reshape(1,-1)
    startTime = time.perf_counter_ns()
    prediction = predict(model,input)
    endTime = time.perf_counter_ns()

    mean_absolute_error = metrics.mean_absolute_error(outputFeedbackTestData[i],prediction).numpy()[0]
    mean_square_error = metrics.mean_squared_error(outputFeedbackTestData[i],prediction).numpy()[0]

    feedbackMAE += mean_absolute_error
    feedbackMSE += mean_square_error

    feedbackMAEResults.append(mean_absolute_error)
    feedbackMSEResults.append(mean_square_error)

    elapsedMicro = float(endTime - startTime) / 1000.0
    meanSpeed += elapsedMicro
    speedResults.append(elapsedMicro)
    prevPrediction = prediction
feedbackMAE /= inputFeedbackTestData.__len__()
feedbackMSE /= inputFeedbackTestData.__len__()

meanSpeed /= (2 * inputTestData.__len__())
meanFrequency = 1000000.0 / meanSpeed

#RESULT OUTPUT
print("Single Estimation Test MAE: " + str(singleMAE))
print("Single Estimation Test MSE(Loss): " + str(singleMSE))
print("Feedback Estimation Test MAE: " + str(feedbackMAE))
print("Feedback Estimation Test MSE(Loss): " + str(feedbackMSE))
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

plt.scatter(x=range(1,singleMAEResults.__len__()+1), y=singleMAEResults, s=0.5)
plt.title('Single Estimation Absolute Error')
plt.ylabel('absolute error')
plt.xlabel('prediction')
plt.show(block=True)

plt.scatter(x=range(1,singleMSEResults.__len__()+1), y=singleMSEResults, s=0.5)
plt.title('Single Estimation Squared Error')
plt.ylabel('squared error')
plt.xlabel('prediction')
plt.show(block=True)

plt.scatter(x=range(1,feedbackMAEResults.__len__()+1), y=feedbackMAEResults, s=0.5)
plt.title('Feedback Estimation Absolute Error')
plt.ylabel('absolute error')
plt.xlabel('prediction')
plt.show(block=True)

plt.scatter(x=range(1,feedbackMSEResults.__len__()+1), y=feedbackMSEResults, s=0.5)
plt.title('Feedback Estimation Squared Error')
plt.ylabel('squared error')
plt.xlabel('prediction')
plt.show(block=True)

plt.scatter(x=range(1,speedResults.__len__()+1), y=speedResults, s=0.5)
plt.title('Estimation Speed')
plt.ylabel('Speed (microseconds)')
plt.xlabel('prediction')
plt.show(block=True)