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
import random

@tf.function
def predict(model, input):
    return model(input)

def makeNoise(StdDev):
    return (random.random() * 2 * StdDev) - StdDev

#THIS FILE IS FOR INACCURATE ABLATION STUDY
print("INACCURATE ABLATION STUDY")

goalAbsoluteError = 0.06 #based on study which indicates direct force feedback must be within 0.06
noiseRange = (0.2 * goalAbsoluteError, 0.5 * goalAbsoluteError, goalAbsoluteError, 2 * goalAbsoluteError, 5 * goalAbsoluteError)

for i in range(0,10):
    print(str(makeNoise(goalAbsoluteError)))

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
    inputDatum = (float(values[0])/33333, float(values[4]) * 1000, float(values[5]) * 1000, float(values[6]) * 1000, float(values[7]), float(values[8]), float(values[9]), float(values[10]), float(values[11]), float(values[12]))
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

    inputDatum = (float(values[0])/33333, float(values[4]) * 1000, float(values[5]) * 1000, float(values[6]) * 1000, float(values[7]), float(values[8]), float(values[9]), float(values[10]), float(values[11]), float(values[12]))
    inputFeedbackTestData.append(inputDatum)

    outputDatum = (float(values[13]), float(values[14]), float(values[15]))
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
model.add(Dense(12, input_shape=(10,), activation='relu'))
model.add(Dense(3, activation='linear'))

model.compile(loss='mean_squared_error', optimizer='adam', metrics=['mean_absolute_error'])

history = model.fit(inputTrainData, outputTrainData, epochs=50, batch_size = 5)

for noiseIndex in range(0,noiseRange.__len__()):
    print("Test " + str(noiseIndex) + ", Noise: " + str(noiseRange[noiseIndex]))

    feedbackXForce = 0.0
    feedbackYForce = 0.0
    feedbackZForce = 0.0
    prevForceInputTestData = list()
    trueForceInputTestData = list()
    allForceInputTestData = list()
    allForceInputFeedbackTestData = list()

    for i in range(0,inputTestData.__len__()):
        prevForceInputTestData.append((inputTestData[i][0], inputTestData[i][1], inputTestData[i][2], inputTestData[i][3], inputTestData[i][4], inputTestData[i][5], inputTestData[i][6], inputTestData[i][7] + makeNoise(noiseRange[noiseIndex]), inputTestData[i][8] + makeNoise(noiseRange[noiseIndex]), inputTestData[i][9] + makeNoise(noiseRange[noiseIndex])))
        trueForceInputTestData.append((inputTestData[i][0], inputTestData[i][1], inputTestData[i][2], inputTestData[i][3], inputTestData[i][4] + makeNoise(noiseRange[noiseIndex]), inputTestData[i][5] + makeNoise(noiseRange[noiseIndex]), inputTestData[i][6] + makeNoise(noiseRange[noiseIndex]), inputTestData[i][7], inputTestData[i][8], inputTestData[i][9]))
        allForceInputTestData.append((inputTestData[i][0], inputTestData[i][1], inputTestData[i][2], inputTestData[i][3], inputTestData[i][4] + makeNoise(noiseRange[noiseIndex]), inputTestData[i][5] + makeNoise(noiseRange[noiseIndex]), inputTestData[i][6] + makeNoise(noiseRange[noiseIndex]), inputTestData[i][7] + makeNoise(noiseRange[noiseIndex]), inputTestData[i][8] + makeNoise(noiseRange[noiseIndex]), inputTestData[i][9] + makeNoise(noiseRange[noiseIndex])))

        if inputFeedbackTestData[i][0] <= 3000 / 33333:
            feedbackXForce = inputFeedbackTestData[i][7] + makeNoise(noiseRange[noiseIndex])
            feedbackYForce = inputFeedbackTestData[i][8] + makeNoise(noiseRange[noiseIndex])
            feedbackZForce = inputFeedbackTestData[i][9] + makeNoise(noiseRange[noiseIndex])

        allForceInputFeedbackTestData.append((inputFeedbackTestData[i][0], inputFeedbackTestData[i][1], inputFeedbackTestData[i][2], inputFeedbackTestData[i][3], feedbackXForce, feedbackYForce, feedbackZForce, feedbackXForce, feedbackYForce, feedbackZForce))
    print(str(prevForceInputTestData[0]))
    print(str(trueForceInputTestData[0]))
    print(str(allForceInputTestData[0]))
    print(str(allForceInputFeedbackTestData[0]) + ", " + str(allForceInputFeedbackTestData[1]))
    print("Noise generated")

    #PREV FORCE SINGLE ESTIMATION TEST
    prevForceSingleMSEResults = list()
    prevForceSingleMAEResults = list()
    prevForceSingleMSE = 0.0
    prevForceSingleMAE = 0.0
    prevForceSingleMSESqr = 0.0
    prevForceSingleMAESqr = 0.0
    for i in range(0,prevForceInputTestData.__len__()):
        input = numpy.asarray(prevForceInputTestData[i]).reshape(1,-1)
        
        prediction = predict(model,input)
        
        mean_absolute_error = metrics.mean_absolute_error(outputTestData[i],prediction).numpy()[0]
        mean_square_error = metrics.mean_squared_error(outputTestData[i],prediction).numpy()[0]

        prevForceSingleMAE += mean_absolute_error
        prevForceSingleMSE += mean_square_error

        prevForceSingleMAESqr += (mean_absolute_error * mean_absolute_error)
        prevForceSingleMSESqr += (mean_square_error * mean_square_error)

        prevForceSingleMAEResults.append(mean_absolute_error)
        prevForceSingleMSEResults.append(mean_square_error)
    prevForceSingleMAEstddev = math.sqrt((prevForceSingleMAESqr - (prevForceSingleMAE * prevForceSingleMAE / prevForceInputTestData.__len__())) / prevForceInputTestData.__len__())
    prevForceSingleMSEstddev = math.sqrt((prevForceSingleMSESqr - (prevForceSingleMSE * prevForceSingleMSE / prevForceInputTestData.__len__())) / prevForceInputTestData.__len__())
    prevForceSingleMAE /= prevForceInputTestData.__len__()
    prevForceSingleMSE /= prevForceInputTestData.__len__()

    #TRUE FORCE SINGLE ESTIMATION TEST
    trueForceSingleMSEResults = list()
    trueForceSingleMAEResults = list()
    trueForceSingleMSE = 0.0
    trueForceSingleMAE = 0.0
    trueForceSingleMSESqr = 0.0
    trueForceSingleMAESqr = 0.0
    for i in range(0,trueForceInputTestData.__len__()):
        input = numpy.asarray(trueForceInputTestData[i]).reshape(1,-1)
        
        prediction = predict(model,input)
        
        mean_absolute_error = metrics.mean_absolute_error(outputTestData[i],prediction).numpy()[0]
        mean_square_error = metrics.mean_squared_error(outputTestData[i],prediction).numpy()[0]

        trueForceSingleMAE += mean_absolute_error
        trueForceSingleMSE += mean_square_error

        trueForceSingleMAESqr += (mean_absolute_error * mean_absolute_error)
        trueForceSingleMSESqr += (mean_square_error * mean_square_error)

        trueForceSingleMAEResults.append(mean_absolute_error)
        trueForceSingleMSEResults.append(mean_square_error)
    trueForceSingleMAEstddev = math.sqrt((trueForceSingleMAESqr - (trueForceSingleMAE * trueForceSingleMAE / trueForceInputTestData.__len__())) / trueForceInputTestData.__len__())
    trueForceSingleMSEstddev = math.sqrt((trueForceSingleMSESqr - (trueForceSingleMSE * trueForceSingleMSE / trueForceInputTestData.__len__())) / trueForceInputTestData.__len__())
    trueForceSingleMAE /= trueForceInputTestData.__len__()
    trueForceSingleMSE /= trueForceInputTestData.__len__()

    #ALL FORCE SINGLE ESTIMATION TEST
    allForceSingleMSEResults = list()
    allForceSingleMAEResults = list()
    allForceSingleMSE = 0.0
    allForceSingleMAE = 0.0
    allForceSingleMSESqr = 0.0
    allForceSingleMAESqr = 0.0
    for i in range(0,allForceInputTestData.__len__()):
        input = numpy.asarray(allForceInputTestData[i]).reshape(1,-1)
        
        prediction = predict(model,input)
        
        mean_absolute_error = metrics.mean_absolute_error(outputTestData[i],prediction).numpy()[0]
        mean_square_error = metrics.mean_squared_error(outputTestData[i],prediction).numpy()[0]

        allForceSingleMAE += mean_absolute_error
        allForceSingleMSE += mean_square_error

        allForceSingleMAESqr += (mean_absolute_error * mean_absolute_error)
        allForceSingleMSESqr += (mean_square_error * mean_square_error)

        allForceSingleMAEResults.append(mean_absolute_error)
        allForceSingleMSEResults.append(mean_square_error)
    allForceSingleMAEstddev = math.sqrt((allForceSingleMAESqr - (allForceSingleMAE * allForceSingleMAE / allForceInputTestData.__len__())) / allForceInputTestData.__len__())
    allForceSingleMSEstddev = math.sqrt((allForceSingleMSESqr - (allForceSingleMSE * allForceSingleMSE / allForceInputTestData.__len__())) / allForceInputTestData.__len__())
    allForceSingleMAE /= allForceInputTestData.__len__()
    allForceSingleMSE /= allForceInputTestData.__len__()

    #ALL FORCE FEEDBACK ESTIMATION TEST
    allForceFeedbackMSEResults = list()
    allForceFeedbackMAEResults = list()
    allForceFeedbackMSE = 0.0
    allForceFeedbackMAE = 0.0
    allForceFeedbackMSESqr = 0.0
    allForceFeedbackMAESqr = 0.0
    prevPrediction = ()
    for i in range(0,allForceInputFeedbackTestData.__len__()):
        inputCopy = allForceInputFeedbackTestData[i]
        if inputCopy[0] > 3000 / 33333:
            inputCopy = (inputCopy[0], inputCopy[1], inputCopy[2], inputCopy[3], inputCopy[4], inputCopy[5], inputCopy[6], prevPrediction.numpy()[0][0], prevPrediction.numpy()[0][1], prevPrediction.numpy()[0][2])
        input = numpy.array(inputCopy).reshape(1,-1)
        
        prediction = predict(model,input)

        mean_absolute_error = metrics.mean_absolute_error(outputFeedbackTestData[i],prediction).numpy()[0]
        mean_square_error = metrics.mean_squared_error(outputFeedbackTestData[i],prediction).numpy()[0]

        allForceFeedbackMAE += mean_absolute_error
        allForceFeedbackMSE += mean_square_error

        allForceFeedbackMAESqr += (mean_absolute_error * mean_absolute_error)
        allForceFeedbackMSESqr += (mean_square_error * mean_square_error)

        allForceFeedbackMAEResults.append(mean_absolute_error)
        allForceFeedbackMSEResults.append(mean_square_error)

        prevPrediction = prediction
    allForceFeedbackMAEstddev = math.sqrt((allForceFeedbackMAESqr - (allForceFeedbackMAE * allForceFeedbackMAE / allForceInputFeedbackTestData.__len__())) / allForceInputFeedbackTestData.__len__())
    allForceFeedbackMSEstddev = math.sqrt((allForceFeedbackMSESqr - (allForceFeedbackMSE * allForceFeedbackMSE / allForceInputFeedbackTestData.__len__())) / allForceInputFeedbackTestData.__len__())
    allForceFeedbackMAE /= allForceInputFeedbackTestData.__len__()
    allForceFeedbackMSE /= allForceInputFeedbackTestData.__len__()

    print("Tests finished")

    #RESULT OUTPUT
    with open('InaccurateAblationTestError' + str(noiseRange[noiseIndex]), 'w') as f:
        write = csv.writer(f)
        write.writerow(['Prev Force Single MAE', 'Prev Force Single MSE', 'True Force Single MAE', 'True Force Single MSE', 'All Force Single MAE', 'All Force Single MSE', 'All Force Feedback MAE', 'All Force Feedback MSE',])
        for i in range(0,prevForceSingleMAEResults.__len__()):
            write.writerow([str(prevForceSingleMAEResults[i]), str(prevForceSingleMSEResults[i]), str(trueForceSingleMAEResults[i]), str(trueForceSingleMSEResults[i]), str(allForceSingleMAEResults[i]), str(allForceSingleMSEResults[i]), str(allForceFeedbackMAEResults[i]), str(allForceFeedbackMSEResults[i])])

    print("Prev Force Single Estimation Test MAE: " + str(prevForceSingleMAE))
    print("Prev Force Single Estimation Test MAE StdDev: " + str(prevForceSingleMAEstddev) + " " + str(statistics.stdev(prevForceSingleMAEResults)))
    print("Prev Force Single Estimation Test MAE Median: " + str(statistics.median(prevForceSingleMAEResults)))

    print("Prev Force Single Estimation Test MSE(Loss): " + str(prevForceSingleMSE))
    print("Prev Force Single Estimation Test MSE StdDev: " + str(prevForceSingleMSEstddev) + " " + str(statistics.stdev(prevForceSingleMSEResults)))
    print("Prev Force Single Estimation Test MSE Median: " + str(statistics.median(prevForceSingleMSEResults)))

    print("True Force Single Estimation Test MAE: " + str(trueForceSingleMAE))
    print("True Force Single Estimation Test MAE StdDev: " + str(trueForceSingleMAEstddev) + " " + str(statistics.stdev(trueForceSingleMAEResults)))
    print("True Force Single Estimation Test MAE Median: " + str(statistics.median(trueForceSingleMAEResults)))

    print("True Force Single Estimation Test MSE(Loss): " + str(trueForceSingleMSE))
    print("True Force Single Estimation Test MSE StdDev: " + str(trueForceSingleMSEstddev) + " " + str(statistics.stdev(trueForceSingleMSEResults)))
    print("True Force Single Estimation Test MSE Median: " + str(statistics.median(trueForceSingleMSEResults)))

    print("All Force Single Estimation Test MAE: " + str(allForceSingleMAE))
    print("All Force Single Estimation Test MAE StdDev: " + str(allForceSingleMAEstddev) + " " + str(statistics.stdev(allForceSingleMAEResults)))
    print("All Force Single Estimation Test MAE Median: " + str(statistics.median(allForceSingleMAEResults)))

    print("All Force Single Estimation Test MSE(Loss): " + str(allForceSingleMSE))
    print("All Force Single Estimation Test MSE StdDev: " + str(allForceSingleMSEstddev) + " " + str(statistics.stdev(allForceSingleMSEResults)))
    print("All Force Single Estimation Test MSE Median: " + str(statistics.median(allForceSingleMSEResults)))

    print("All Force Feedback Estimation Test MAE: " + str(allForceFeedbackMAE))
    print("All Force Feedback Estimation Test MAE StdDev: " + str(allForceFeedbackMAEstddev) + " " + str(statistics.stdev(allForceFeedbackMAEResults)))
    print("All Force Feedback Estimation Test MAE Median: " + str(statistics.median(allForceFeedbackMAEResults)))

    print("All Force Feedback Estimation Test MSE(Loss): " + str(allForceFeedbackMSE))
    print("All Force Feedback Estimation Test MSE StdDev: " + str(allForceFeedbackMSEstddev) + " " + str(statistics.stdev(allForceFeedbackMSEResults)))
    print("All Force Feedback Estimation Test MSE Median: " + str(statistics.median(allForceFeedbackMSEResults)))
    print("")

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