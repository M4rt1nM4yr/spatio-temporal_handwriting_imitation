
from functools import total_ordering
import matplotlib.pyplot as plt
import operator


@total_ordering
class LogEntry:

    def __init__(self, epoch, data):
        self.epoch = epoch
        self.data = data

    def __eq__(self, other):
        return self.epoch == other.epoch

    def __ne__(self, other):
        return not (self == other)

    def __lt__(self, other):
        return self.epoch < other.epoch

    def __repr__(self):
        return "LogEntry(" + repr(self.epoch) + ")"

    def __str__(self):
        return "LogEntry(" + str(self.epoch) + ")"


class TrainingGraphPlotter:

    def __init__(self, columnNames, figureTitle=None, maxNumberNodes=500):
        self.maxNumberNodes = maxNumberNodes
        self.columnNames = columnNames
        self.data = list()
        self.figureTitle = figureTitle

    def addOrderedDataPoint(self, epoch, data):
        """Adds a data point to the plotter.

        Important: If a datapoint gets added that has a lower epoch number than previously added datapoints,
                   the previous datapoints get deleted.
                   The common use-case for that is that if training gets interrupted and continued, it usually starts
                   at the beginning of the epoch, and the logs in that same epoch before interruption are meaningless
                   and have to be deleted.

        :param epoch: The epoch, as float, of the current data point
        :param data: The data, as dict
        """
        data_processed = dict()
        for columnName in self.columnNames:
            if columnName not in data:
                data_processed[columnName] = 0.0
            else:
                data_processed[columnName] = float(data[columnName])

        newEntry = LogEntry(epoch, data_processed)

        while self.data and self.data[-1] >= newEntry:
            self.data.pop()

        self.data.append(newEntry)

    def computeColumnAverages(self):
        logAvgs = {}

        for logColumn in self.columnNames:
            logAvgs[logColumn] = 0

        for logEntry in self.data:
            for logColumn, logColumnData in logEntry.data.items():
                logAvgs[logColumn] += logColumnData

        for logColumn in logAvgs:
            logAvgs[logColumn] /= len(self.data)

        return logAvgs

    def plot(self):

        print("Plotting " + str(len(self.data)) + " log entries ...")

        chunkSize = int(round(len(self.data) / self.maxNumberNodes))
        print("Combining to chunks of size " + str(chunkSize) + " ...")

        # Compute averages to determine plot order
        logColumnsWithAverages = self.computeColumnAverages()

        if self.figureTitle:
            plt.figure(self.figureTitle)

        # Draw from highest to lowest average to minimize the number graph hidden behind other graphs
        for logColumn, _ in reversed(sorted(logColumnsWithAverages.items(), key=operator.itemgetter(1))):
            x = list()
            y = list()
            y_max = list()
            y_min = list()

            currentMin = None
            currentMax = None
            currentYAvgCounter = 0
            currentXAvgCounter = 0
            currentNum = 0

            for logElem in self.data:
                if currentNum >= chunkSize and currentNum > 0:
                    x.append(currentXAvgCounter / currentNum)
                    y.append(currentYAvgCounter / currentNum)
                    y_min.append(currentMin)
                    y_max.append(currentMax)
                    currentMin = None
                    currentMax = None
                    currentYAvgCounter = 0
                    currentXAvgCounter = 0
                    currentNum = 0

                currentY = logElem.data[logColumn]
                if currentMin is None or currentMin > currentY:
                    currentMin = currentY
                if currentMax is None or currentMax < currentY:
                    currentMax = currentY

                currentXAvgCounter += logElem.epoch
                currentYAvgCounter += currentY
                currentNum += 1

#            for logElem in self.data:
#                x.append(logElem.epoch)
#                if logColumn not in logElem.data:
#                    y.append(0)
#                else:
#                    y.append(logElem.data[logColumn])

            [p] = plt.plot(x, y, label=logColumn)
            currentColor = p.get_color()
            plt.fill_between(x, y_min, y_max, color=currentColor, alpha=0.2, linestyle='None', linewidth=0.0)

        plt.legend()

        if self.figureTitle:
            plt.show()
