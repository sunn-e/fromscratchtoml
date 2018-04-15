#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2017 Mohit Rathore <mrmohitrathoremr@gmail.com>
# Copyright (C) 2017 Dikshant Gupta <dikshant2210@gmail.com>
# Licensed under the GNU General Public License v3.0 - https://www.gnu.org/licenses/gpl-3.0.en.html

import unittest

import torch as ch
import fromscratchtoml as fs2ml
import torch.utils.data

from fromscratchtoml.test.toolbox import _tempfile, _test_data_path

import logging

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class TestNN(unittest.TestCase):
    def setUp(self):
        # sets up a basic input dataset which implements a XOR gate.
        x = ch.Tensor([[0, 0], [0, 1], [1, 0], [1, 1]])
        y = ch.Tensor([[1, 0], [0, 1], [0, 1], [1, 0]])
        self.train_data = torch.utils.data.TensorDataset(x, y)

    def model_equal(self, m1, m2):
        # compares two fs2ml.nn models by comparing their weights and biases
        for wt1, wt2 in zip(m1.layerwise_weights, m2.layerwise_weights):
            self.assertTrue(torch.equal(wt1, wt2))

        for b1, b2 in zip(m1.layerwise_biases, m2.layerwise_biases):
            self.assertTrue(torch.equal(b1, b2))

    def test_consistency(self):
        # tests for model's load save consistency.
        old_nw = fs2ml.nn.NetworkMesh([2, 5, 2], seed=100)
        old_nw.SGD(train_data=self.train_data, epochs=15, batch_size=4, lr=3)

        fname = _tempfile("model.fs2ml")
        old_nw.save_model(fname)

        new_nw = fs2ml.nn.NetworkMesh()
        new_nw.load_model(fname)
        self.model_equal(old_nw, new_nw)

    def test_persistence(self):
        # ensure backward compatiblity and persistence of the model.
        model = fs2ml.nn.NetworkMesh([2, 5, 2], seed=100)
        model.SGD(train_data=self.train_data, epochs=15, batch_size=4, lr=3)

        saved_model = fs2ml.nn.NetworkMesh()
        saved_model.load_model(_test_data_path("xor_15_4_3_100.ch"))

        # self.model_equal(model, saved_model)

    def test_inconsistency(self):
        # ensure that NotImplementedError is raised when the netowrk architecture
        # is not defined.
        model = fs2ml.nn.NetworkMesh()
        with self.assertRaises(NotImplementedError):
            model.SGD(train_data=self.train_data, epochs=15, batch_size=4, lr=3)

    def test_model_sanity(self):
        # test when y is a list of integers (as in torch's dataloader implementation) our
        # model is still sane.
        X = ch.Tensor([[0, 0], [0, 1], [1, 0], [1, 1]])
        Y = [0, 1, 1, 0]
        self.train_data_new = [(x, y) for x, y in zip(X, Y)]
        model = fs2ml.nn.NetworkMesh([2, 5, 2], seed=100)
        model.SGD(train_data=self.train_data_new, epochs=15, batch_size=4, lr=3, test_data=self.train_data_new)