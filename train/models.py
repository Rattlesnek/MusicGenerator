"""
Bachelor's thesis: Generation of guitar tracks utilizing knowledge of song structure
Author: Adam Pankuch
"""
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Input, Conv2D, MaxPool2D, Flatten, Dense
import numpy as np
import glob
import os
from reverse_pianoroll import pianoroll_to_pretty_midi


class Model:
    """
    Base model class.
    """
    def __init__(self, input_length, output_length):
        """Constructs instance."""
        self.model = None
        self.input_length = input_length
        self.output_length = output_length

    def createModel(self):
        """Creates the model."""
        raise NotImplementedError()
        # implement in child class!

    def generateBatches(self, path, batch_size, sample_spacing):
        """Generates train / test batches."""
        raise NotImplementedError()
        # implement in child class!

    def predict(self, seed, predict_length, threshold):
        """Generates a track from a seed."""
        assert seed.shape == (48, self.input_length), 'Wrong input seed dimensions!'
        # implement in child class!

    def loadAndPrepareSeed(self, filepath):
        """Loads and preprocesses seed."""
        song = np.load(filepath)['arr_0']
        # prepare seed for prediction
        seed = song[40:88, :self.input_length]
        return seed

    def generateMidi(self, seedPath, predict_length, threshold=0.5):
        """Generates midi from a seed."""
        seed = self.loadAndPrepareSeed(seedPath)
        generated = self.predict(seed, predict_length, threshold)
        pianoroll = self.createPianoroll(generated)
        midi = pianoroll_to_pretty_midi(pianoroll, fs=20)
        return midi

    @staticmethod
    def openArchivePerSong(path):
        """Batch generator utility function."""
        for file in glob.glob(os.path.join(path, '*.npz')):
            songs = np.load(file).values()
            for song in songs:
                yield song

    @staticmethod
    def infiniteSongLoop(path):
        """Batch generator utility function."""
        while True:
            for song in Model.openArchivePerSong(path):
                yield song

    @staticmethod
    def createPianoroll(generated):
        """Creates pianoroll from generated output"""
        generated = np.where(generated == 1, 100, generated)
        generated = np.pad(generated, ((40,40), (0,0)))
        return generated


class Model_1Dout(Model):
    """
    Base class for CNN models with 1 column vector of pianoroll as an output.
    """
    def __init__(self, input_length):
        """Constructs instance."""
        super().__init__(input_length, 1)

    def generateBatches(self, path, batch_size=200, sample_spacing=1):
        """Generates train / test batches."""
        generate_songs = self.infiniteSongLoop(path)
        song, idx = None, 0
        x_batch, y_batch = None, None

        i = 0
        while True:
            if x_batch is None:
                x_batch = np.zeros((batch_size, self.input_length, 48, 1), dtype=np.float)
                y_batch = np.zeros((batch_size, 48), dtype=np.float)

            if song is None:
                song = next(generate_songs)
                song_t = np.transpose(song[40:88, ::])
                idx = 0

            if idx + self.input_length >= song.shape[1]:
                song = None
                continue         
            
            x_batch[i, ::, ::, 0] = song_t[idx:(idx + self.input_length), ::]
            y_batch[i, ::] = song_t[idx + self.input_length, ::]
            
            idx += sample_spacing
            i += 1
            if i == batch_size:
                yield x_batch, y_batch
                x_batch, y_batch = None, None
                i = 0

    def predict(self, seed, predict_length, threshold=0.5):
        """Generates a track from a seed."""
        super().predict(seed, predict_length, threshold)
        
        track = np.transpose(seed)
        result = np.copy(track)
        for _ in range(predict_length):
            new = self.model.predict(track[np.newaxis, ::, ::, np.newaxis])
            new = (new >= threshold).astype('float')
            result = np.concatenate((result, new), axis=0)
            track = result[-self.input_length:]
        return np.transpose(result)


class Model_2Dout(Model):
    """
    Base class for CNN models with 2D pianoroll as an output.
    """
    def __init__(self, input_length, output_length, output_overlap):
        """Constructs instance."""
        super().__init__(input_length, output_length)
        self.output_overlap = output_overlap
        self.createModel()

    def generateBatches(self, path, batch_size=200, sample_spacing=1):
        """Generates train / test batches."""
        generate_songs = self.infiniteSongLoop(path)
        song, idx = None, 0
        x_batch, y_batch = None, None

        i = 0
        while True:
            if x_batch is None:
                x_batch = np.zeros((batch_size, self.input_length, 48, 1), dtype=np.float)
                y_batch = np.zeros((batch_size, self.output_length, 48, 1), dtype=np.float)

            if song is None:
                song = next(generate_songs)
                song_t = np.transpose(song[40:88, ::])
                idx = 0

            if idx + self.input_length + self.output_length - self.output_overlap >= song.shape[1]:
                song = None
                continue         
            
            x_batch[i, ::, ::, 0] = song_t[idx:(idx + self.input_length), ::]
            y_batch[i, ::, ::, 0] = song_t[(idx + self.input_length - self.output_overlap):(idx + self.input_length + self.output_length - self.output_overlap), ::]
            
            idx += sample_spacing
            i += 1
            if i == batch_size:
                yield x_batch, y_batch
                x_batch, y_batch = None, None
                i = 0

    def predict(self, seed, predict_length, threshold=0.5):
        """Generates a track from a seed."""
        super().predict(seed, predict_length, threshold)
        assert predict_length % (self.output_length - self.output_overlap) == 0, 'Wrong predict length!'

        track = np.transpose(seed)
        result = np.copy(track)
        for _ in range(predict_length // (self.output_length - self.output_overlap)):
            new = self.model.predict(track[np.newaxis, ::, ::, np.newaxis])
            new = new[0, -(self.output_length - self.output_overlap):, ::, 0]
            new = (new >= threshold).astype('float')
            result = np.concatenate((result, new), axis=0)
            track = result[-self.input_length:, ::]
        return np.transpose(result)


class Model_CNN_2Din_1Dout(Model_1Dout):
    """
    Example of classic CNN with 1D output.
    """
    def __init__(self, input_length):
        """Constructs instance."""
        super().__init__(input_length)
        # create model by default
        self.createModel()

    def createModel(self):
        """Creates the model."""
        model = Sequential()
        model.add(Input(shape=(self.input_length, 48, 1)))

        model.add(Conv2D(32, (5, 5), activation='relu', padding='same'))
        model.add(MaxPool2D(pool_size=(2, 1)))

        model.add(Conv2D(32, (5, 5), activation='relu'))
        model.add(MaxPool2D(pool_size=(2, 1)))

        model.add(Conv2D(32, (5, 5), activation='relu'))
        model.add(Flatten())
        model.add(Dense(48, activation='sigmoid'))
        # save to self
        self.model = model

