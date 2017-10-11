# -*- coding: utf-8 -*-

"""
Neural Network Model
神经网络模型

"""


import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optimizer
from torch.autograd import Variable

USER_VECTOR_SIZE=10
PRODUCT_VECTOR_SIZE=10


class NeuralNetwork(nn.Module):

    def __init__(self):

        super(NeuralNetwork, self).__init__()

        self.user_merchandise_layer = nn.Linear(512, 512)
        self.user_self_layer = nn.Linear(USER_VECTOR_SIZE, 128)

        self.merchandise_description_layer = nn.Linear(512, 512)
        self.merchandise_self_layer = nn.Linear(PRODUCT_VECTOR_SIZE, 128)

        self.user_layer = nn.Linear(640, 512)

        self.merchandise_layer = nn.Linear(640, 512)

        self.hidden_layer_1 = nn.Linear(1024, 1024)
        self.hidden_layer_2 = nn.Linear(1024, 512)
        self.hidden_layer_3 = nn.Linear(512, 64)
        self.out = nn.Linear(64, 2)

    def forward(self, product_vector, user_vector, user_desc_vector, product_desc_vector):

        user_desc = F.relu(self.user_merchandise_layer(user_desc_vector))
        user_self = F.relu(self.user_self_layer(user_vector))
        merchandise_desc = F.relu(self.merchandise_description_layer(product_desc_vector))
        merchandise_self = F.relu(self.merchandise_self_layer(product_vector))

        user_layer = F.leaky_relu(
            self.user_layer(torch.cat([user_desc, user_self])),
            negative_slope=0.2
        )

        merchandise_layer = F.leaky_relu(
            self.merchandise_layer(torch.cat([merchandise_desc, merchandise_self])),
            negative_slope=0.2
        )

        hidden = F.leaky_relu(
            self.hidden_layer_1(torch.cat([user_layer, merchandise_layer])),
            negative_slope=0.5
        )

        hidden = F.leaky_relu(
            self.hidden_layer_2(hidden),
            negative_slope=0.5
        )

        hidden = F.leaky_relu(
            self.hidden_layer_3(hidden),
            negative_slope=0.5
        )

        output = F.softmax(
            self.out(hidden)
        )

        return output


def save_model(network, path):

    torch.save(network, path)
    print("Save Model to File: %s" % path)


def load_model(path):

    network = torch.load(path)

    return network


def output(network, user_self_vector, user_desc_vector, product_self_vector, product_desc_vector):
    user_self_vector = Variable(torch.FloatTensor(user_self_vector))
    user_desc_vector = Variable(torch.FloatTensor(user_desc_vector))
    product_desc_vector = Variable(torch.FloatTensor(product_desc_vector))
    product_self_vector = Variable(torch.FloatTensor(product_self_vector))

    prob = network(
        product_vector=product_self_vector,
        user_vector=user_self_vector,
        user_desc_vector=user_desc_vector,
        product_desc_vector=product_desc_vector
    )

    return prob


def train(trainset, epoch, user_feature, product_feature):

    learning_rate = 0.0001

    network = NeuralNetwork()

    training_optimizer = optimizer.Adam(lr=learning_rate, params=network.parameters())

    loss_criterion = torch.nn.CrossEntropyLoss()

    for i in range(epoch):
        for data in trainset:
            person_id = data[0]
            product_id = data[1]
            label = data[-1]

            user_self_vector, user_desc_vector = user_feature[person_id]

            product_self_vector, product_desc_vector = product_feature[product_id]

            label = Variable(torch.LongTensor([label]))

            prob = output(
                network,
                user_self_vector,
                user_desc_vector,
                product_self_vector,
                product_desc_vector
            )
            loss = loss_criterion(prob, label)

            if i % 10:
                print("Sample: %s: Loss: %s" % (i+1, loss.data[0]))

            training_optimizer.zero_grad()
            loss.backward()
            training_optimizer.step()
        save_model(network, '../model_param/neural_network_param_%s' % i)


def test(testset, user_feature, product_feature, model_path):

    network = load_model(model_path)

    result = []
    labels = []

    for data in testset:
        person_id = data[0]
        product_id = data[1]
        label = data[-1]

        user_self_vector, user_desc_vector = user_feature[person_id]

        product_self_vector, product_desc_vector = product_feature[product_id]

        prob = output(
            network,
            user_self_vector,
            user_desc_vector,
            product_self_vector,
            product_desc_vector
        )

        labels.append(label)
        result.append(prob)

    return labels, result


def predict(predict_set, user_feature, product_feature, model_path):

    network = load_model(model_path)
    result = []

    for data in predict_set:
        person_id = data[0]
        product_id = data[1]

        user_self_vector, user_desc_vector = user_feature[person_id]

        product_self_vector, product_desc_vector = product_feature[product_id]

        prob = output(
            network,
            user_self_vector,
            user_desc_vector,
            product_self_vector,
            product_desc_vector
        )

        result.append(prob)

    return result

