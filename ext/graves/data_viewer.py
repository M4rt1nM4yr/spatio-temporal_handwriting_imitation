#!/usr/bin/env python3

from data_frame import DataFrame
import drawing

import matplotlib.pyplot as plt

import numpy as np

import os
import argparse



class DataDrawer():
    
    def __init__(self, dataFrame):
        self.dataFrame=dataFrame
        self.currentFrameId=0
        
        self.fig, (self.ax1, self.ax2) = plt.subplots(2,1)
        self.fig.canvas.set_window_title('Data Drawer')

        self.fig.canvas.mpl_connect('key_press_event', self.onKeyPress)


    def onKeyPress(self, event):
        if event.key == 'right' or event.key == 'd':
            self.currentFrameId = (self.currentFrameId + 1) % len(self.dataFrame)
            self.drawCurrentFrame()
        elif event.key == 'left' or event.key == 'a':
            self.currentFrameId = (self.currentFrameId - 1) % len(self.dataFrame)
            self.drawCurrentFrame()

        self.fig.canvas.flush_events()


    def splitByPenUp(self, data):

        strokes = list()
        assert(np.array_equal(data[0], [0,0,1]))

        currentStroke = list()
        for dataPoint in data[1:]:
            x = dataPoint[0]
            y = dataPoint[1]
            penUp = dataPoint[2] > 0.5

            currentStroke.append([x,y])

            if penUp:
                strokes.append(np.array(currentStroke))
                currentStroke = list()


        assert(not currentStroke)

        return strokes
        

    def drawCurrentFrame(self):
        currentFrame = self.dataFrame[self.currentFrameId]
        
        currentFrameText = drawing.decode_ascii(currentFrame.c, currentFrame.c_len)

        # Compute integrate offsets to coords
        offsets = currentFrame.x[:currentFrame.x_len]
        coords = drawing.offsets_to_coords(offsets)
    
        # Split to strokes
        offsetStrokes = self.splitByPenUp(offsets)
        coordStrokes = self.splitByPenUp(coords)

        # Reset plots
        self.ax1.cla()
        self.ax2.cla()

        # Draw data
        for offsetStroke in offsetStrokes:
            self.ax1.plot(offsetStroke[:,0], offsetStroke[:,1])
        for coordStroke in coordStrokes:
            self.ax2.plot(coordStroke[:,0], coordStroke[:,1])

        # Set title, aspect ratio, etc
        self.ax1.set_title('ID: ' + str(self.currentFrameId))
        self.ax2.set_title('<' + currentFrameText + '>')
        self.ax1.set_aspect('equal')
        self.ax2.set_aspect('equal')

        # Update window
        self.fig.canvas.draw()

    def run(self):
        self.drawCurrentFrame()

        plt.show()



def main():
 
    parser = argparse.ArgumentParser(description='Converts npz files to actual training libraries')
    parser.add_argument('dataset', help='The dataset folder.')
    args = parser.parse_args()
    print(args)

    data_cols = ['x', 'x_len', 'c', 'c_len']
    data = [np.load(os.path.join(args.dataset, '{}.npy'.format(i))) for i in data_cols]
    
    dataFrame = DataFrame(columns=data_cols, data=data)
    dataDrawer = DataDrawer(dataFrame)

    dataDrawer.run()

if __name__ == "__main__":
    main()
