import numpy
import math
import statistics
import matplotlib.pyplot as plt
import time
import csv
import seaborn as sns
import pandas as pd

x = 0

match x:
    case 0:
        noPos = pd.read_csv("NoPositionBigVelocityTestError")

        sns.set_style("whitegrid")
        sns.set_context("paper", font_scale=1.5)

        sns.scatterplot(data= noPos, x=noPos.index, y="Feedback MAE", s= 4, c= "blue")

        plt.title("No Position Network Feedback Estimation Error")
        plt.xlabel("Estimation Number")
        plt.xlim(0,10277)
        plt.ylabel("Absolute Error")
        plt.yscale("log")
        plt.ylim(0.0006,0.8)
        plt.axhline(y=0.06, color= "red", linestyle = 'dashed')
        plt.show()
    case 1:
        print("hello")