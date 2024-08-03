import numpy
import math
import statistics
from tensorflow import metrics
import tensorflow as tf
from keras.models import Sequential
from keras.layers import Dense
import matplotlib.pyplot as plt
import time
import csv

@tf.function
def predict(model, input):
    return model(input)

#THIS FILE IS FOR ABLATION STUDY
print("ABLATION STUDY")

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

    #TrueForceElapsedTime, CurrXPos, CurrYPos, CurrZPos, CurrXVel, Curr.YVel, CurrZVel, PrevTrueXForce, PrevTrueYForce, PrevTrueZForce, PrevXForce, PrevYForce, PrevZForce
    inputDatum = (float(values[1]), float(values[2]), float(values[3]), float(values[4]) * 1000, float(values[5]) * 1000, float(values[6]) * 1000, float(values[10]), float(values[11]), float(values[12]))
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
    inputDatum = (float(values[1]), float(values[2]), float(values[3]), float(values[4]) * 1000, float(values[5]) * 1000, float(values[6]) * 1000, float(values[10]), float(values[11]), float(values[12]))
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


#MODEL CREATION/TRAINING  
model = Sequential()
model.add(Dense(12, input_shape=(9,), activation='relu'))
model.add(Dense(3, activation='linear'))

model.compile(loss='mean_squared_error', optimizer='adam', metrics=['mean_absolute_error'])

history = model.fit(inputTrainData, outputTrainData, epochs=75, batch_size = 5)


speedResults = list()
meanSpeed = 0.0

#SINGLE ESTIMATION TEST
singleMSEResults = list()
singleMAEResults = list()
singleMSE = 0.0
singleMAE = 0.0
singleMSESqr = 0.0
singleMAESqr = 0.0
for i in range(0,inputTestData.__len__()):
    input = numpy.asarray(inputTestData[i]).reshape(1,-1)
    startTime = time.perf_counter_ns()
    prediction = predict(model,input)
    endTime = time.perf_counter_ns()

    mean_absolute_error = metrics.mean_absolute_error(outputTestData[i],prediction).numpy()[0]
    mean_square_error = metrics.mean_squared_error(outputTestData[i],prediction).numpy()[0]

    singleMAE += mean_absolute_error
    singleMSE += mean_square_error
    
    singleMAESqr += (mean_absolute_error * mean_absolute_error)
    singleMSESqr += (mean_square_error * mean_square_error)

    singleMAEResults.append(mean_absolute_error)
    singleMSEResults.append(mean_square_error)

    elapsedMicro = float(endTime - startTime) / 1000.0
    meanSpeed += elapsedMicro
    speedResults.append(elapsedMicro)
singleMAEstddev = math.sqrt((singleMAESqr - (singleMAE * singleMAE / inputTestData.__len__())) / inputTestData.__len__())
singleMSEstddev = math.sqrt((singleMSESqr - (singleMSE * singleMSE / inputTestData.__len__())) / inputTestData.__len__())
singleMAE /= inputTestData.__len__()
singleMSE /= inputTestData.__len__()

#FEEDBACK ESTIMATION TEST
feedbackMSEResults = list()
feedbackMAEResults = list()
feedbackMSE = 0.0
feedbackMAE = 0.0
feedbackMSESqr = 0.0
feedbackMAESqr = 0.0
prevPrediction = ()
for i in range(0,inputFeedbackTestData.__len__()):
    inputCopy = inputFeedbackTestData[i]
    if i % 16 != 0: #inputCopy[0] > 3000 / 33333:
        inputCopy = (inputCopy[0], inputCopy[1], inputCopy[2], inputCopy[3], inputCopy[4], inputCopy[5], prevPrediction.numpy()[0][0], prevPrediction.numpy()[0][1], prevPrediction.numpy()[0][2])
    #else:
        #print(str(inputCopy))
    input = numpy.array(inputCopy).reshape(1,-1)
    startTime = time.perf_counter_ns()
    prediction = predict(model,input)
    endTime = time.perf_counter_ns()

    mean_absolute_error = metrics.mean_absolute_error(outputFeedbackTestData[i],prediction).numpy()[0]
    mean_square_error = metrics.mean_squared_error(outputFeedbackTestData[i],prediction).numpy()[0]

    feedbackMAE += mean_absolute_error
    feedbackMSE += mean_square_error

    feedbackMAESqr += (mean_absolute_error * mean_absolute_error)
    feedbackMSESqr += (mean_square_error * mean_square_error)

    feedbackMAEResults.append(mean_absolute_error)
    feedbackMSEResults.append(mean_square_error)

    elapsedMicro = float(endTime - startTime) / 1000.0
    meanSpeed += elapsedMicro
    speedResults.append(elapsedMicro)
    prevPrediction = prediction
feedbackMAEstddev = math.sqrt((feedbackMAESqr - (feedbackMAE * feedbackMAE / inputFeedbackTestData.__len__())) / inputFeedbackTestData.__len__())
feedbackMSEstddev = math.sqrt((feedbackMSESqr - (feedbackMSE * feedbackMSE / inputFeedbackTestData.__len__())) / inputFeedbackTestData.__len__())
feedbackMAE /= inputFeedbackTestData.__len__()
feedbackMSE /= inputFeedbackTestData.__len__()

meanSpeed /= (2 * inputTestData.__len__())
meanFrequency = 1000000.0 / meanSpeed

#RESULT OUTPUT
with open('BigVelocityNoGroundTruthTestError', 'w') as f:
    write = csv.writer(f)
    write.writerow(['Single MAE', 'Single MSE', 'Feedback MAE', 'Feedback MSE'])
    for i in range(0,singleMAEResults.__len__()):
        write.writerow([str(singleMAEResults[i]),str(singleMSEResults[i]),str(feedbackMAEResults[i]),str(feedbackMSEResults[i])])

print("Single Estimation Test MAE: " + str(singleMAE))
print("Single Estimation Test MAE StdDev: " + str(singleMAEstddev) + " " + str(statistics.stdev(singleMAEResults)))
print("Single Estimation Test MAE Median: " + str(statistics.median(singleMAEResults)))

print("Single Estimation Test MSE(Loss): " + str(singleMSE))
print("Single Estimation Test MSE StdDev: " + str(singleMSEstddev) + " " + str(statistics.stdev(singleMSEResults)))
print("Single Estimation Test MSE Median: " + str(statistics.median(singleMSEResults)))

print("Feedback Estimation Test MAE: " + str(feedbackMAE))
print("Feedback Estimation Test MAE StdDev: " + str(feedbackMAEstddev) + " " + str(statistics.stdev(feedbackMAEResults)))
print("Feedback Estimation Test MAE Median: " + str(statistics.median(feedbackMAEResults)))

print("Feedback Estimation Test MSE(Loss): " + str(feedbackMSE))
print("Feedback Estimation Test MSE StdDev: " + str(feedbackMSEstddev) + " " + str(statistics.stdev(feedbackMSEResults)))
print("Feedback Estimation Test MSE Median: " + str(statistics.median(feedbackMSEResults)))

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


""" plt.scatter(x=range(1,speedResults.__len__()+1), y=speedResults, s=0.5)
plt.title('Estimation Speed')
plt.ylabel('Speed (microseconds)')
plt.xlabel('prediction')
plt.show(block=True) """