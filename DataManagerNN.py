import logging
import pickle
import random
import Constants
import numpy as np
from database import database
from Generated.DatabaseClasses import *


class DataManagerNN:

    def __init__(self, db_manager):
        self.logger = logging.getLogger(__name__)

        self.db_manager = db_manager
        self.sizes = []
        self.num_layers = 0
        self.biases = np.empty(0)
        self.weights = np.empty(0)

    def get_pickled_inputs(self):
        self.logger.debug("Attempting to get inputs file")
        pickle_file = open(Constants.NN_INPUTS_FILENAME, 'rb')
        input_array = pickle.load(pickle_file)
        pickle_file.close()
        self.logger.info("Got inputs file")
        return input_array

    def train_network(self):
        self.logger.debug("Attempting to train network")
        input_array = self.get_pickled_inputs()

        self.logger.debug("Reshaping input data")
        input_data_inputs = [np.reshape(x[0], (8, 1)) for x in input_array]
        input_data_results = [np.reshape(x[1], (8, 1)) for x in input_array]

        total_size = len(input_data_inputs)
        validation_size = int(total_size * 0.15)
        testing_size = validation_size
        combined_size = validation_size + testing_size

        self.logger.debug("Creating training data with size: " +
                          str(total_size - combined_size))
        training_data = list(zip(input_data_inputs[:-combined_size],
                                 input_data_results[:-combined_size]))

        self.logger.debug("Creating validation data with size: " +
                          str(validation_size))
        validation_data = list(zip(input_data_inputs[-combined_size:-testing_size],
                                   input_data_results[-combined_size:-testing_size]))

        self.logger.debug("Creating testing data with size: " +
                          str(testing_size))
        test_data = list(zip(input_data_inputs[-testing_size:], input_data_results[-testing_size:]))

        self.logger.info("Starting Network")
        # net = Network([8, 20, 8])
        # net.SGD(training_data, 30, 10, 3.0, test_data=test_data)
        self.initialize_network([8, 20, 8])
        self.sgd(training_data=training_data,
                 epochs=30,
                 mini_batch_size=10,
                 learning_rate=1.0,
                 lambda_val=0.0,
                 evaluation_data=validation_data,
                 monitor_training_cost=False,
                 monitor_training_accuracy=False,
                 monitor_evaluation_cost=False,
                 monitor_evaluation_accuracy=True)
        return

    def initialize_network(self, sizes):
        self.sizes = sizes
        self.num_layers = len(sizes)
        self.biases = [np.random.randn(y, 1) for y in self.sizes[1:]]
        self.weights = [np.random.randn(y, x)/np.sqrt(x)
                        for x, y in zip(self.sizes[:-1], self.sizes[1:])]

    def feed_forward(self, activation):
        for bias, weight in zip(self.biases, self.weights):
            activation = self.sigmoid(np.dot(weight, activation) + bias)
        return activation

    def total_cost(self, data, lambda_val):
        cost = 0.0
        for x, y in data:
            a = self.feed_forward(x)
            # temp_cost = 0.5*np.linalg.norm(a-y)**2
            temp_cost = np.sum(np.nan_to_num(-y * np.log(a) - (1 - y) * np.log(1 - a)))
            cost += temp_cost/len(data)
        cost += 0.5*(lambda_val/len(data))*sum(np.linalg.norm(w)**2 for w in self.weights)
        return cost

    def accuracy(self, data):
        # if convert:
        #     results = [(np.argmax(self.feedforward(x)), np.argmax(y))
        #                for (x, y) in data]
        # else:
        #     results = [(np.argmax(self.feedforward(x)), y)
        #                for (x, y) in data]
        # return sum(int(x==y) for (x, y) in results)
        eval_results = []
        for test_data in data:
            eval_results.append((self.feed_forward(test_data[0]), test_data[1]))
        correct_results = 0
        points_arr = [12, 8, 1.6 * 10, 0.5, 0.5, 2, 2, 1.6 * 10]
        for eval_in, eval_out in eval_results:
            in_total = 0.0
            out_total = 0.0
            for i in range(len(eval_in)):
                in_total += eval_in[i] * points_arr[i]
                out_total += eval_out[i] * points_arr[i]
            if abs(in_total - out_total) < 2:
                correct_results += 1
        return correct_results

    def back_propagation(self, x, y):
        bias_gradient = [np.zeros(b.shape) for b in self.biases]
        weight_gradient = [np.zeros(w.shape) for w in self.weights]
        activation = x
        activations = [x]
        zs = []
        for b, w in zip(self.biases, self.weights):
            z = np.dot(w, activation)+b
            zs.append(z)
            activation = self.sigmoid(z)
            activations.append(activation)
        delta = activations[-1] - y
        # delta = (activations[-1] - y) * self.sigmoid_prime(zs[-1])
        bias_gradient[-1] = delta
        weight_gradient[-1] = np.dot(delta, activations[-2].transpose())
        for l in range(2, self.num_layers):
            z = zs[-l]
            sp = self.sigmoid_prime(z)
            delta = np.dot(self.weights[-l+1].transpose(), delta) * sp
            bias_gradient[-l] = delta
            weight_gradient[-l] = np.dot(delta, activations[-l-1].transpose())
        return bias_gradient, weight_gradient

    def update_mini_batch(self, mini_batch, learning_rate, lambda_val, n):
        bias_gradient = [np.zeros(b.shape) for b in self.biases]
        weight_gradient = [np.zeros(w.shape) for w in self.weights]
        for x, y in mini_batch:
            delta_bias_gradient, delta_weight_gradient = self.back_propagation(x, y)
            bias_gradient = [bg+dbg for bg, dbg in zip(bias_gradient, delta_bias_gradient)]
            weight_gradient = [wg+dwg for wg, dwg in zip(weight_gradient, delta_weight_gradient)]
        self.weights = [(1-learning_rate*(lambda_val/n))*w-(learning_rate/len(mini_batch))*wg
                        for w, wg in zip(self.weights, weight_gradient)]
        self.biases = [b-(learning_rate/len(mini_batch))*bg
                       for b, bg in zip(self.biases, bias_gradient)]

    def sgd(self, training_data, epochs, mini_batch_size, learning_rate, lambda_val=0.0, evaluation_data=None,
            monitor_training_cost=False,
            monitor_training_accuracy=False,
            monitor_evaluation_cost=False,
            monitor_evaluation_accuracy=False):
        self.logger.info("Attempting Stochastic Gradient Descent")
        if evaluation_data:
            eval_count = len(evaluation_data)
        else:
            eval_count = 0
        self.logger.debug("Evaluation data size: " + str(eval_count))
        training_count = len(training_data)
        self.logger.debug("Training data size: " + str(training_count))
        evaluation_cost, evaluation_accuracy, training_cost, training_accuracy = [], [], [], []
        self.logger.debug("Running for " +
                          str(epochs) +
                          " epochs with mini batch size of " +
                          str(mini_batch_size))
        for j in range(epochs):
            self.logger.info("Beginning epoch #" + str(j))
            random.shuffle(training_data)
            mini_batches = [
                training_data[k:k+mini_batch_size]
                for k in range(0, training_count, mini_batch_size)]
            for mini_batch in mini_batches:
                self.update_mini_batch(
                    mini_batch, learning_rate, lambda_val, len(training_data))
            self.logger.info("Completed epoch #" + str(j))
            if monitor_training_cost:
                self.logger.debug("Calculating total cost of training data")
                cost = self.total_cost(training_data, lambda_val)
                training_cost.append(cost)
                self.logger.info("Training Cost: " + str(cost))
            if monitor_training_accuracy:
                self.logger.debug("Calculating accuracy of training data")
                accuracy = self.accuracy(training_data)
                training_accuracy.append(accuracy)
                percent = float(accuracy)/float(training_count)
                percent *= 100
                self.logger.info("Training Accuracy: " +
                                 str(accuracy) +
                                 " / " +
                                 str(training_count) +
                                 " = " +
                                 str(int(percent)) +
                                 "%")
            if monitor_evaluation_cost:
                self.logger.debug("Calculating total cost of evaluation data")
                cost = self.total_cost(evaluation_data, lambda_val)
                evaluation_cost.append(cost)
                self.logger.info("Evaluation Cost: " + str(cost))
            if monitor_evaluation_accuracy:
                self.logger.debug("Calculating accuracy of evaluation data")
                accuracy = self.accuracy(evaluation_data)
                evaluation_accuracy.append(accuracy)
                percent = float(accuracy)/float(eval_count)
                percent *= 100
                self.logger.info("Evaluation Accuracy: " +
                                 str(accuracy) +
                                 " / " +
                                 str(eval_count) +
                                 " = " +
                                 str(int(percent)) +
                                 "%")
        return evaluation_cost, evaluation_accuracy, training_cost, training_accuracy

    def sigmoid(self, z):
        with np.errstate(all='raise'):
            try:
                # temp = np.array(z, dtype=np.float256)
                return_val = 1.0/(1.0+np.exp(-z))
            except RuntimeWarning as e:
                self.logger.error("Runtime Warning in Sigmoid")
                raise e
            else:
                return return_val

    def sigmoid_prime(self, z):
        return self.sigmoid(z)*(1-self.sigmoid(z))
