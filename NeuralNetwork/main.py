from numpy import loadtxt
from keras.models import Sequential
from keras.layers import Dense

datasetFile = open("RandomizedTrainingData.txt", "r")

datasetLines = datasetFile.readlines()

inputData = list()
desiredOutputData = list()

for line in datasetLines:
    values = line.split(' ')
    inputDatum = (int(values[0]), int(values[1]), int(values[2]), int(values[3]), int(values[4]), int(values[5]), float(values[6]), float(values[7]), float(values[8]))
    outputDatum = (float(values[9]), float(values[10]), float(values[11]))
    inputData.append(inputDatum)
    desiredOutputData.append(outputDatum)




