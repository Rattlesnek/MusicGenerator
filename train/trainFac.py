"""
Bachelor's thesis: Generation of guitar tracks utilizing knowledge of song structure
Author: Adam Pankuch
"""
from tensorflow.keras.callbacks import ModelCheckpoint, LambdaCallback
import numpy as np
import pylab as plt
import glob
import os
import models


class Paths:
    """
    Data class containing all paths important for training.
    """
    def __init__(self, *, rootDir, trainPath, testPath, testSongPath, testGenerateSavePath, checkpointBasePath, checkpointName):
        """Constructs instance."""
        self.rootDir = rootDir
        self.trainPath = self.joinToRootDir(trainPath) 
        self.testPath = self.joinToRootDir(testPath) 
        self.testSongPath = self.joinToRootDir(testSongPath) 
        self.testGenerateSavePath = self.joinToRootDir(testGenerateSavePath) 
        self.checkpointBasePath = self.joinToRootDir(checkpointBasePath)
        self.checkpointPath = os.path.join(self.joinToRootDir(checkpointBasePath), checkpointName)

    def joinToRootDir(self, path):
        """Concatenates root dir path with an other path."""
        return os.path.join(self.rootDir, path)

    def createSavePaths(self):
        """Creates directories in case they do not exist."""
        if not os.path.isdir(self.testGenerateSavePath):
            os.makedirs(self.testGenerateSavePath)
        if not os.path.isdir(self.checkpointBasePath):
            os.makedirs(self.checkpointBasePath)


class TrainFacility:
    """ 
    Class which handles training of models.
    """
    def __init__(self, modelCompound, paths):
        """Constructs instance."""
        self.modelCompound = modelCompound
        self.paths = paths

    def compile(self, loss='binary_crossentropy', metrics=['accuracy'], optimizer='adam'):
        """Compiles the model."""
        self.modelCompound.model.compile(loss=loss, metrics=metrics, optimizer=optimizer)

    def fit(self, epochs=1000, batch_size=200, steps_per_epoch=10000, validation_steps=1000, sample_spacing=1):
        """Trains model with given train parameters.

        Note:
            Files in train: 7840
            Batch size: 200, sample space: 1
            Average length of a pianoroll is: 400 (source: pianoroll_analysis jupyter notebook)
            Number of train samples in one song is then: 400 - 120 = 280 
            280 * 7840 / 200 = 10976 ~= 10000

            Files in test: 800
            Batch size: 200, sample space: 1
            280 * 800 / 200 = 1120
        """
        history = self.modelCompound.model.fit(self.modelCompound.generateBatches(self.paths.trainPath, batch_size, sample_spacing), 
                        epochs=epochs, 
                        steps_per_epoch=steps_per_epoch, # 7840 files in train 
                        validation_data=self.modelCompound.generateBatches(self.paths.testPath, batch_size, sample_spacing),
                        validation_steps=validation_steps, # 800 files in test
                        callbacks=self.createCallbacks())
        return history

    def createCallbacks(self):
        """Defines callbacks for training."""
        checkpoint_callback = ModelCheckpoint(self.paths.checkpointPath, monitor='val_accuracy', verbose=1)
        print_callback = LambdaCallback(on_epoch_end=self.onEpochEnd)
        return [checkpoint_callback, print_callback]

    def onEpochEnd(self, epoch, logs):
        """Generates test songs (called on every end of epoch)."""
        # execute only on every second epoch
        if epoch % 2 != 0:
            return

        save_path = os.path.join(self.paths.testGenerateSavePath, "epoch_" + str(epoch))
        # create directory for this epoch
        if not os.path.isdir(save_path):
            os.mkdir(save_path)

        print(' -- Generating songs after epoch:', epoch)
        for filepath in glob.glob(self.paths.testSongPath + '/*.npz'):
            # PREPARE INPUT
            seed = self.modelCompound.loadAndPrepareSeed(filepath)
            # PREDICTION
            pred_output = self.modelCompound.predict(seed, 480, 0.1)
            
            save_name = save_path + '/GEN-epoch-' + str(epoch) + '_' + os.path.basename(filepath)[:-4]
            TrainFacility.plotAndSaveOutput(save_name, pred_output)
        print(' -- Generating songs finished')
    
    @staticmethod
    def plotAndSaveOutput(save_name, track):
        """Plots and saves the output of a network"""
        assert track.shape[0] == 48, 'Wrong input track dimensions!'
        # plot whole output
        fig = plt.figure()
        plt.imshow(track)
        plt.savefig(save_name + '.png', dpi=1200, bbox_inches='tight')
        plt.close(fig)
        # plot shorter output
        fig = plt.figure()
        plt.imshow(track[::, :240])
        plt.savefig(save_name + '_shorter.png', dpi=1200, bbox_inches='tight')
        plt.close(fig)

