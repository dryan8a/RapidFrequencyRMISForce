import numpy
import math
import statistics
import matplotlib.pyplot as plt
import time
import csv
import seaborn as sns
import pandas as pd
from IPython.display import display

x = 3

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
        window = 20
        iA20 = pd.read_csv("InaccurateAblationTestError0.012")
        iA20.insert(1,"Smooth All Force Feedback MAE", iA20["All Force Feedback MAE"].rolling(window).mean(), True)
        iA20.dropna(inplace=True)
        iA50 = pd.read_csv("InaccurateAblationTestError0.03")
        iA50.insert(1,"Smooth All Force Feedback MAE", iA50["All Force Feedback MAE"].rolling(window).mean(), True)
        iA50.dropna(inplace=True)
        iA100 = pd.read_csv("InaccurateAblationTestError0.06")
        iA100.insert(1,"Smooth All Force Feedback MAE", iA100["All Force Feedback MAE"].rolling(window).mean(), True)
        iA100.dropna(inplace=True)        
        iA200 = pd.read_csv("InaccurateAblationTestError0.12")
        iA200.insert(1,"Smooth All Force Feedback MAE", iA200["All Force Feedback MAE"].rolling(window).mean(), True)
        iA200.dropna(inplace=True)
        iA500 = pd.read_csv("InaccurateAblationTestError0.3")
        iA500.insert(1,"Smooth All Force Feedback MAE", iA500["All Force Feedback MAE"].rolling(window).mean(), True)
        iA500.dropna(inplace=True)
        concat = pd.concat([iA20.assign(Noise="20%"), iA50.assign(Noise="50%"), iA100.assign(Noise="100%"), iA200.assign(Noise="200%"), iA500.assign(Noise="500%")])

        sns.set_style("ticks")
        sns.set_context("paper")
        palette = sns.color_palette("rocket")

        #sns.relplot(data=concat, x=concat.index, y="True Force Single MAE", hue="Noise", palette=palette, kind="scatter", s=10)
        sns.relplot(data=concat, x=concat.index, y="Smooth All Force Feedback MAE", hue="Noise", palette=palette, kind="line", linewidth=1.5)
        
        plt.title("")
        plt.xlabel("Estimation Number")
        plt.xlim(0,10277)
        plt.ylabel("Absolute Error (N)")
        plt.yscale("log")
        plt.ylim(top=1.05)
        plt.axhline(y=0.06, color= "black", linestyle = 'dashed')
        plt.show()
    case 2:
        '''
        iA20Prev = pd.read_csv("InaccurateAblationTestError0.012", usecols=["Prev Force Single MAE"], names=["AE"], header=1)
        iA20True = pd.read_csv("InaccurateAblationTestError0.012", usecols=["True Force Single MAE"], names=["AE"], header=1)
        iA20All = pd.read_csv("InaccurateAblationTestError0.012", usecols=["All Force Single MAE"], names=["AE"], header=1)
        iA20 = pd.concat([iA20Prev.assign(NoiseInput="Previous Force"), iA20True.assign(NoiseInput="True Force"), iA20All.assign(NoiseInput="All Force")])

        iA50Prev = pd.read_csv("InaccurateAblationTestError0.03", usecols=["Prev Force Single MAE"], names=["AE"], header=1)
        iA50True = pd.read_csv("InaccurateAblationTestError0.03", usecols=["True Force Single MAE"], names=["AE"], header=1)
        iA50All = pd.read_csv("InaccurateAblationTestError0.03", usecols=["All Force Single MAE"], names=["AE"], header=1)
        iA50 = pd.concat([iA50Prev.assign(NoiseInput="Previous Force"), iA50True.assign(NoiseInput="True Force"), iA50All.assign(NoiseInput="All Force")])
        
        iA100Prev = pd.read_csv("InaccurateAblationTestError0.06", usecols=["Prev Force Single MAE"], names=["AE"], header=1)
        iA100True = pd.read_csv("InaccurateAblationTestError0.06", usecols=["True Force Single MAE"], names=["AE"], header=1)
        iA100All = pd.read_csv("InaccurateAblationTestError0.06", usecols=["All Force Single MAE"], names=["AE"], header=1)
        iA100 = pd.concat([iA100Prev.assign(NoiseInput="Previous Force"), iA100True.assign(NoiseInput="True Force"), iA100All.assign(NoiseInput="All Force")])
        
        iA200Prev = pd.read_csv("InaccurateAblationTestError0.12", usecols=["Prev Force Single MAE"], names=["AE"], header=1)
        iA200True = pd.read_csv("InaccurateAblationTestError0.12", usecols=["True Force Single MAE"], names=["AE"], header=1)
        iA200All = pd.read_csv("InaccurateAblationTestError0.12", usecols=["All Force Single MAE"], names=["AE"], header=1)
        iA200 = pd.concat([iA200Prev.assign(NoiseInput="Previous Force"), iA200True.assign(NoiseInput="True Force"), iA200All.assign(NoiseInput="All Force")])
        
        iA500Prev = pd.read_csv("InaccurateAblationTestError0.3", usecols=["Prev Force Single MAE"], names=["AE"], header=1)
        iA500True = pd.read_csv("InaccurateAblationTestError0.3", usecols=["True Force Single MAE"], names=["AE"], header=1)
        iA500All = pd.read_csv("InaccurateAblationTestError0.3", usecols=["All Force Single MAE"], names=["AE"], header=1)
        iA500 = pd.concat([iA500Prev.assign(NoiseInput="Previous Force"), iA500True.assign(NoiseInput="True Force"), iA500All.assign(NoiseInput="All Force")])

        df = pd.concat([iA20.assign(Noise="20%"), iA50.assign(Noise="50%"), iA100.assign(Noise="100%"), iA200.assign(Noise="200%"), iA500.assign(Noise="500%")])
        '''

        data = [["20%", "Previous Force", 0.021053519992951575], ["20%", "True Force", 0.02080679973178915],["20%", "All Force", 0.021055618557386697],
                ["50%", "Previous Force", 0.022195641001843184], ["50%", "True Force", 0.020835491940108183],["50%", "All Force", 0.0223268969843185],
                ["100%", "Previous Force", 0.025841570883649547], ["100%", "True Force", 0.020990253061681112],["100%", "All Force", 0.02605403507335384],
                ["200%", "Previous Force", 0.03693631043746085], ["200%", "True Force", 0.02161498109018607],["200%", "All Force", 0.03794760517291978],
                ["500%", "Previous Force", 0.08221798256355708], ["500%", "True Force", 0.025634497854167146],["500%", "All Force", 0.08553248307924541]]
        df = pd.DataFrame(data, columns=["Noise", "NoiseInput", "MAE"])

        sns.set_style("ticks")
        sns.set_context("paper")
        palette = sns.color_palette("hls", 3)

        sns.barplot(df, x="Noise", y="MAE", hue="NoiseInput")

        plt.title("")
        plt.xlabel("Noise (% of 0.06N)")
        plt.ylabel("Mean Absolute Error (N)")
        plt.legend(title="Noise Input")
        #plt.axhline(y=0.06, color= "black", linestyle = 'dashed')
        plt.show()
    case 3:
        noRemoval = pd.read_csv("BigVelocityTestError")
        noPosition = pd.read_csv("NoPositionBigVelocityTestError")
        noVelocity = pd.read_csv("NoVelocityTestError")
        noKinematics = pd.read_csv("NoKinematicsTestError")
        noGT = pd.read_csv("BigVelocityNoGroundTruthTestError")
        randInput = pd.read_csv("RandomizedTrainingData.txt", sep=" ", names=["ET", "PosX", "PosY", "PosZ", "VelX", "VelY", "VelZ", "TFX", "TFY", "TFZ", "PFX", "PFY", "PFZ", "OFX", "OFY", "OFZ"], skiprows= lambda x: x < (102778 * 0.9))
        df = (randInput - randInput.min())/(randInput.max() - randInput.min())
        df.loc[-1] = ["","","","","","","","","","","","","","","",""]
        df.index = df.index + 1
        df.sort_index(inplace=True)
        #df.insert(0,"", df.index)
        df = df.stack()
        df.drop([0], inplace=True)
        df.drop(index=["PosX", "PosY", "PosZ", "OFX", "OFY", "OFZ"], level=1, inplace=True)
        df = df.reset_index(level=[0,1])
        df.columns = ["Input Number","Input Type", "Input Value"]
        #aedf = pd.DataFrame(numpy.array(numpy.repeat(noPosition.dropna()["Single MAE"], 10), dtype=float)).reset_index([0])
        #aedf.columns = ["", "AE"]
        #df = pd.concat([df, aedf["AE"]], axis=1)
        
        display(df)

        sns.set_style("ticks")
        sns.set_context("paper")
        palette = sns.color_palette("hls", 10)
        sns.lmplot(data=df, x= "Input Number", y= "Input Value", hue="Input Type", palette=palette)

        plt.title("")
        plt.xlabel("Absolute Error")
        plt.ylabel("Input Value")
        plt.legend(title="Input Type")
        plt.show()