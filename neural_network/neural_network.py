""" Implements a multi-layer perceptron.

@author Gabriel Nogueira (Talendar)
"""

import numpy as np


class NeuralNetwork:
    """ Basic implementation of a multi-layer perceptron, the standard feedforward neural network. """

    def __init__(self, layers_size=None, layers_activation="sigmoid", weights_multiplier=1):
        """ Constructor.

        :param layers_size: list containing the sizes of the layers. The layers activation functions will be the default one.
        """
        self.layers = []
        if layers_size is not None:
            self.layers.append(NeuralLayer(layers_size[0], input_count=0, activation="input_layer"))
            for s in layers_size[1:]:
                input_count = self.layers[-1].size
                self.layers.append(NeuralLayer(s, input_count, layers_activation, weights_multiplier=weights_multiplier))

    def predict(self, x):
        """ Wrapper for the feedforward function that uses the network's current weights and bias.

        :param x: column vector containing the features of the sample. If an out of shape numpy array is fed, this function
        won't work properly due to errors in matrix multiplications.
        :return:
        """
        weights = [l.weights for l in self.layers[1:]]
        bias = [l.bias for l in self.layers[1:]]

        return self.feedforward(weights, bias, x)

    def feedforward(self, weights, bias, x):
        """ Feeds the data to the network.

        :param weights: list with the weights matrix for each layer (excluding the input layer).
        :param bias: list with the bias vector for each layer (excluding the input layer).
        :param x: column vector containing the features of the sample. If an out of shape numpy array is fed, this function
        won't work properly due to errors in matrix multiplications.
        :return: a vector (numpy array) containing the output of each neuron of the output layer.
        """
        a = self.colvector(x)
        for i, l in enumerate(self.layers[1:]):
            w, b = weights[i], bias[i]
            a = l.activate(np.dot(w, a) + b)

        return a

    @staticmethod
    def colvector(v):
        """ Turns a numpy array into a column vector. """
        v2 = v.copy()
        v2.shape = (len(v), 1)
        return v2

    def get_weights(self):
        return [layer.weights.copy() for layer in self.layers[1:]]

    def set_weights(self, weights):
        for i, layer in enumerate(self.layers[1:]):
            layer.weights = weights[i].copy()

    def save(self, out_pathname):
        with open(out_pathname, "w") as file:
            for layer in self.layers:
                file.write(
                    "LAYER_ACTIVATION %s\n" % layer.activation +
                    "SIZE %d\n" % layer.size +
                    "INPUT_COUNT %d\n" % layer.input_count +
                    "WEIGHTS_MULTIPLIER %.2f\n" % layer.weights_multiplier
                )

                if layer.activation != "input_layer":
                    to_write = ""
                    for row in layer.weights:
                        for item in row:
                            to_write += str(item) + " "
                        to_write += "\n"

                    for b in layer.bias:
                        to_write += str(b[0]) + " "

                    file.write(to_write + "\n")

                if layer != self.layers[-1]:
                    file.write("\n")

    @staticmethod
    def load(in_pathname):
        with open(in_pathname, "r") as file:
            net = NeuralNetwork()

            line = file.readline()
            while line != "":
                activation = line.replace("\n", "").split(" ")[1]
                size = int(file.readline().replace("\n", "").split(" ")[1])
                input_count = int(file.readline().replace("\n", "").split(" ")[1])
                weights_multiplier = float(file.readline().replace("\n", "").split(" ")[1])

                layer = NeuralLayer(size, input_count, activation, weights_multiplier)

                weights = []
                line = file.readline()

                while line != "\n" and line != "":
                    weights.append(line.replace("\n", "").split(" ")[:-1])
                    line = file.readline()

                if len(weights) > 0:
                    for i in range(len(weights) - 1):
                        for j in range(len(weights[i])):
                            layer.weights[i][j] = float(weights[i][j])

                    for i, b in enumerate(weights[-1]):
                        layer.bias[i][0] = float(b)

                net.layers.append(layer)
                line = file.readline()

            return net


class NeuralLayer:
    """ Represents a feedforward layer in a neural network. """

    def __init__(self, size, input_count, activation="sigmoid", weights_multiplier=1.0):
        self.size = size
        self.input_count = input_count
        self.activation = activation
        self.weights_multiplier = weights_multiplier

        if activation.lower() == "input_layer":
            self.weights, self.bias = None, None
        else:
            self.weights = np.random.uniform(low=-1, high=1, size=(size, input_count)) * self.weights_multiplier
            self.bias = np.random.uniform(low=-1, high=1, size=(size, 1)) * self.weights_multiplier

    def activate(self, z):
        if self.activation.lower() == "input_layer":
            raise ValueError("Tried to activate the neurons from the input layer!")

        if self.activation.lower() == "sigmoid":
            return 1 / (1 + np.exp(-z))

        if self.activation.lower() == "relu":
            return np.maximum(z, 0)

        if self.activation.lower() == "linear":
            return z

        raise NameError("Activation function of type \"%s\" is not defined!" % str(self.activation))
