import numpy
import math
import statistics
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import time
import csv
import seaborn as sns
import pandas as pd
from IPython.display import display

x = 4

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
        window = 500
        iA0feedback = pd.read_csv("OrderedNoPositionBigVelocityTestError", usecols=["Feedback MAE"])
        iA0feedback.insert(1, "Smooth True Force MAE", iA0feedback["Feedback MAE"].rolling(window).mean(), True)
        iA0feedback.dropna(inplace=True)
        iA20feedback = pd.read_csv("OrderedInaccurateAblationTestError0.012", usecols=["All Force Feedback MAE"])
        iA20feedback.insert(1,"Smooth True Force MAE", iA20feedback["All Force Feedback MAE"].rolling(window).mean(), True)
        iA20feedback.dropna(inplace=True)
        iA50feedback = pd.read_csv("OrderedInaccurateAblationTestError0.03", usecols=["All Force Feedback MAE"])
        iA50feedback.insert(1,"Smooth True Force MAE", iA50feedback["All Force Feedback MAE"].rolling(window).mean(), True)
        iA50feedback.dropna(inplace=True)
        iA100feedback = pd.read_csv("OrderedInaccurateAblationTestError0.06", usecols=["All Force Feedback MAE"])
        iA100feedback.insert(1,"Smooth True Force MAE", iA100feedback["All Force Feedback MAE"].rolling(window).mean(), True)
        iA100feedback.dropna(inplace=True)        
        iA200feedback = pd.read_csv("OrderedInaccurateAblationTestError0.12", usecols=["All Force Feedback MAE"])
        iA200feedback.insert(1,"Smooth True Force MAE", iA200feedback["All Force Feedback MAE"].rolling(window).mean(), True)
        iA200feedback.dropna(inplace=True)
        iA500feedback = pd.read_csv("OrderedInaccurateAblationTestError0.3", usecols=["All Force Feedback MAE"])
        iA500feedback.insert(1,"Smooth True Force MAE", iA500feedback["All Force Feedback MAE"].rolling(window).mean(), True)
        iA500feedback.dropna(inplace=True)
        feedback = pd.concat([iA0feedback.assign(Noise="0%"), iA20feedback.assign(Noise="20%"), iA50feedback.assign(Noise="50%"), iA100feedback.assign(Noise="100%"), iA200feedback.assign(Noise="200%"), iA500feedback.assign(Noise="500%")])
        display(feedback)

        iA0single = pd.read_csv("OrderedNoPositionBigVelocityTestError", usecols=["Single MAE"])
        iA0single.insert(1, "Smooth True Force MAE", iA0single["Single MAE"].rolling(window).mean(), True)
        iA0single.dropna(inplace=True)
        iA20single = pd.read_csv("OrderedInaccurateAblationTestError0.012", usecols=["True Force Single MAE"])
        iA20single.insert(1,"Smooth True Force MAE", iA20single["True Force Single MAE"].rolling(window).mean(), True)
        iA20single.dropna(inplace=True)
        iA50single = pd.read_csv("OrderedInaccurateAblationTestError0.03", usecols=["True Force Single MAE"])
        iA50single.insert(1,"Smooth True Force MAE", iA50single["True Force Single MAE"].rolling(window).mean(), True)
        iA50single.dropna(inplace=True)
        iA100single = pd.read_csv("OrderedInaccurateAblationTestError0.06", usecols=["True Force Single MAE"])
        iA100single.insert(1,"Smooth True Force MAE", iA100single["True Force Single MAE"].rolling(window).mean(), True)
        iA100single.dropna(inplace=True)        
        iA200single = pd.read_csv("OrderedInaccurateAblationTestError0.12", usecols=["True Force Single MAE"])
        iA200single.insert(1,"Smooth True Force MAE", iA200single["True Force Single MAE"].rolling(window).mean(), True)
        iA200single.dropna(inplace=True)
        iA500single = pd.read_csv("OrderedInaccurateAblationTestError0.3", usecols=["True Force Single MAE"])
        iA500single.insert(1,"Smooth True Force MAE", iA500single["True Force Single MAE"].rolling(window).mean(), True)
        iA500single.dropna(inplace=True)
        single = pd.concat([iA0single.assign(Noise="0%"), iA20single.assign(Noise="20%"), iA50single.assign(Noise="50%"), iA100single.assign(Noise="100%"), iA200single.assign(Noise="200%"), iA500single.assign(Noise="500%")])
        display(single)

        concat = pd.concat([feedback.assign(Test="Feedback Estimation"), single.assign(Test="Single Estimation")])

        sns.set_style("ticks")
        sns.set_context("paper")
        palette = sns.color_palette("rocket")

        #sns.relplot(data=concat, x=concat.index, y="True Force Single MAE", hue="Noise", palette=palette, kind="scatter", s=10)
        g = sns.relplot(data=concat, x=concat.index, y="Smooth True Force MAE", hue="Noise", palette=palette, kind="line", style="Test", linewidth=1.2, aspect=3, height=3)
        
        plt.title("")
        plt.xlabel("Estimation Number")
        #g.set_titles("{col_name} Test")
        plt.xlim(0,10277)
        plt.ylabel("Absolute Error (N)")
        plt.yscale("log")
        plt.ylim(top=0.4)
        #plt.legend(bbox_to_anchor=(1,1))
        #plt.axhline(y=0.06, color= "black", linestyle = 'dashed')
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
        palette = sns.color_palette("crest", 3)

        print(palette.as_hex())

        sns.barplot(df, x="Noise", y="MAE", hue="NoiseInput", palette = palette)

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
        print(df["ET"].max())
        print(df["ET"].min())
        #df.to_csv("normalizedRandTraining.csv")
        df.loc[-1] = ["","","","","","","","","","","","","","","",""]
        df.index = df.index + 1
        df.sort_index(inplace=True)
        #df.insert(0,"", df.index)
        df = df.stack()
        df.drop([0], inplace=True)
        df.drop(index=["PosX", "PosY", "PosZ", "OFX", "OFY", "OFZ"], level=1, inplace=True)
        df = df.reset_index(level=[0,1])
        df.columns = ["Input Number","Input Type", "Input Value"]
        df["Input Number"] = df["Input Number"].astype("float64")
        df["Input Value"] = df["Input Value"].astype("float64")
        aedf = pd.DataFrame(numpy.repeat(noPosition.dropna()["Single MAE"], 10)).reset_index([0])
        #aedf.columns = ["", "AE"]
        df = pd.concat([df, aedf["Single MAE"]], axis=1)
        
        display(df)

        sns.set_style("ticks")
        sns.set_context("paper")
        etPal = sns.color_palette("Greys",1,as_cmap=False)
        velPal = sns.color_palette("Greens_d",3,as_cmap=False)
        tfxPal = sns.color_palette("Blues_d", 3, as_cmap=False)
        pfxPal = sns.color_palette("Reds_d", 3, as_cmap=False)
        
        palette = numpy.vstack((numpy.vstack((numpy.vstack((etPal,velPal)),tfxPal)),pfxPal))
        #palette = mcolors.LinearSegmentedColormap.from_list("my_palette", colors)

        g = sns.FacetGrid(data=df, hue="Input Type", palette=palette, height=4, aspect=3)
        #g.map(plt.scatter, "Single MAE", "Input Value", s=15, alpha=.7)
        ax = g.map(sns.regplot, "Input Value", "Single MAE", ci=None, robust=1, line_kws={"linewidth":3}, scatter_kws={"s":0.3, "alpha":0.5})
        #g.map(sns.residplot, "Single MAE", "Input Value", lowess=True)

        plt.axhline(y=0.06, color= "black", linestyle = 'dashed', label=r'$\tau_F$')

        
        handles, labels = ax.ax.get_legend_handles_labels()


        plt.title("")
        plt.ylabel("Absolute Error (N)")
        plt.ylim(0.00055, 1.05)
        plt.yscale("log")
        plt.xlabel("Normalized Input Value")
        plt.xlim(-0.003,1.003)
        plt.legend(title="Input Type", handles= handles, labels= labels, markerscale=4, loc="upper left", bbox_to_anchor=(1,1))
        
        plt.show()
    case 4:
        input = pd.read_csv("TrainingData.txt", sep=" ", names=["ET", "PosX", "PosY", "PosZ", "VelX", "VelY", "VelZ", "TFX", "TFY", "TFZ", "PFX", "PFY", "PFZ", "OFX", "OFY", "OFZ"], skiprows= lambda x: x > (102778 * 0.1 - 1))
        input.insert(1,"TFMag", numpy.sqrt(numpy.power(input["PFX"],2) + numpy.power(input["PFY"],2) + numpy.power(input["PFZ"],2)))
        inputClean = input[input["TFMag"] != 0]
        #inputdf = pd.concat([pd.DataFrame(input["TFX"].rename("True Force")).assign(Axis="X"), pd.DataFrame(input["TFY"].rename("True Force")).assign(Axis="Y"), pd.DataFrame(input["TFZ"].rename("True Force")).assign(Axis="Z")])
        display(inputClean)

        window = 1
        feedback = pd.read_csv("OrderedNoPositionBigVelocityTestError", usecols=["Feedback MAE"])
        feedback.insert(1, "True Force MAE", feedback["Feedback MAE"].rolling(window).mean(), True)
        feedback.dropna(inplace=True)
        feedbackdf = pd.concat([inputClean["TFMag"], feedback], axis=1)

        single = pd.read_csv("OrderedNoPositionBigVelocityTestError", usecols=["Single MAE"])
        single.insert(1, "True Force MAE", single["Single MAE"].rolling(window).mean(), True)
        single.dropna(inplace=True)
        singledf = pd.concat([inputClean["TFMag"], single], axis=1)
 

        #xdf = pd.concat([singleXdf.assign(Test="Single Estimation"), feedbackXdf.assign(Test="Feedback Estimation")])
        #ydf = pd.concat([singleYdf.assign(Test="Single Estimation"), feedbackYdf.assign(Test="Feedback Estimation")])
        #zdf = pd.concat([singleZdf.assign(Test="Single Estimation"), feedbackZdf.assign(Test="Feedback Estimation")])

        #display(xdf)


        sns.jointplot(data=singledf, x="TFMag", y="True Force MAE", kind="kde", fill=True, cmap="Blues")
        plt.ylabel("Single Absolute Error (N)")
        plt.ylim(0.0005, 1.05)
        plt.yscale("log")
        plt.xlabel("Ground Truth Force Magnitude (N)")
        plt.show()

        sns.jointplot(data=feedbackdf, x="TFMag", y="True Force MAE", kind="kde", fill=True, cmap="Greens")
        plt.ylabel("Feedback Absolute Error (N)")
        plt.ylim(0.0005, 1.05)
        plt.yscale("log")
        plt.xlabel("Ground Truth Force Magngitude (N)")
        plt.show()