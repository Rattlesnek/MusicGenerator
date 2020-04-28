from tensorflow.keras.callbacks import ModelCheckpoint, LambdaCallback
import numpy as np
import glob
import os

import models
import utils

####
# Data class containing all paths
####
class Paths:

    def __init__(self, *, rootDir, trainPath, testPath, testSongPath, testGenerateSavePath, checkpointBasePath, checkpointName):
        self.rootDir = rootDir
        self.trainPath = self.joinToRootDir(trainPath) 
        self.testPath = self.joinToRootDir(testPath) 
        self.testSongPath = self.joinToRootDir(testSongPath) 
        self.testGenerateSavePath = self.joinToRootDir(testGenerateSavePath) 
        self.checkpointBasePath = self.joinToRootDir(checkpointBasePath)
        self.checkpointPath = os.path.join(self.joinToRootDir(checkpointBasePath), checkpointName)

    def joinToRootDir(self, path):
        return os.path.join(self.rootDir, path)

    def createSavePaths(self):
        if not os.path.isdir(self.testGenerateSavePath):
            os.makedirs(self.testGenerateSavePath)
        if not os.path.isdir(self.checkpointBasePath):
            os.makedirs(self.checkpointBasePath)


####
# Train facility class dedicated to training of all the models
####
class TrainFacility:

    def __init__(self, modelCompound, paths):
        self.modelCompound = modelCompound
        self.paths = paths

    def compile(self, loss='binary_crossentropy', metrics=['accuracy'], optimizer='adam'):
        self.modelCompound.model.compile(loss=loss, metrics=metrics, optimizer=optimizer)

    def fit(self, epochs=1000, batch_size=200, steps_per_epoch=10000, validation_steps=1000, sample_spacing=1):
        """
        Files in train: 7840
        Batch size: 200, sample space: 1
        Average length of a pianoroll is: 400 (source: my analysis jupyter notebook)
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
        checkpoint_callback = ModelCheckpoint(self.paths.checkpointPath, monitor='val_accuracy', verbose=1)
        print_callback = LambdaCallback(on_epoch_end=self.onEpochEnd)
        return [checkpoint_callback, print_callback]

    def onEpochEnd(self, epoch, logs):
        # execute only on every second epoch
        if epoch % 2 != 0:
            return

        save_path = os.path.join(self.paths.testGenerateSavePath, "epoch_" + str(epoch))
        # create directory for this epoch
        if not os.path.isdir(save_path):
            print('create save path')
            os.mkdir(save_path)

        print(' -- Generating songs after epoch:', epoch)
        for filepath in glob.glob(self.paths.testSongPath + '/*.npz'):
            # PREPARE INPUT
            seed = self.modelCompound.loadAndPrepareSeed(filepath)
            # PREDICTION
            pred_output = self.modelCompound.predict(seed, 480)
            
            save_name = save_path + '/GEN-epoch-' + str(epoch) + '_' + os.path.basename(filepath)[:-4]
            utils.Utils.plotAndSaveOutput(save_name, pred_output)
            utils.Utils.savePianoroll(save_name, pred_output)
        print(' -- Generating songs finished')


