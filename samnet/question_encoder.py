# Copyright (C) IBM Corporation 2020
#
# SPDX-License-Identifier: Apache-2.0

"""
question_encoder.py: Implementation of the Question Encoder 
Takes raw text as input and produces question representations
by using a combination of word embeddings and a LSTM
"""

__author__ = "T.S. Jayram"

import torch
from torch import nn


class QuestionEncoder(nn.Module):
    """
    Implementation of the ``QuestionEncoder`` of the VWM network.
    """

    def __init__(self, vocabulary_size, embedded_dim, dim):
        """
        Constructor for the ``QuestionEncoder``.
        
        :param vocabulary_size: size of dictionnary
        :type vocabulary_size: int
        
        :param embedded_dim: dimension of the word embeddings.
        :type embedded_dim: int

        :param dim: dimension of feature vectors
        :type dim: int

        """

        # call base constructor
        super(QuestionEncoder, self).__init__()

        # create bidirectional LSTM layer
        self.lstm = torch.nn.LSTM(
            input_size=embedded_dim, hidden_size=dim,
            num_layers=1, batch_first=True, bidirectional=True)

        # linear layer for projecting the word encodings from 2*dim to dim
        self.lstm_proj = torch.nn.Linear(2 * dim, dim)

        # Defines nn.Embedding for embedding of questions into float tensors.
        self.Embedding = nn.Embedding(vocabulary_size, embedded_dim, padding_idx=0)

    def forward(self, questions, questions_len):
        """
        Forward pass of the ``QuestionEncoder``.

        :param questions: tensor of the questions words, shape [batch_size x maxQuestionLength x embedded_dim].
        :type questions: torch.tensor

        :param questions_len: Unpadded questions length.
        :type questions_len: list

        :return question encodings: [batch_size x (2*dim)]
        :return: contextual_word_embedding: [batch_size x maxQuestionLength x dim] 

        """
        # get batch size
        batch_size = questions.shape[0]

        # Embeddings.
        embedded_questions = self.Embedding(questions)

        # LSTM layer: words & questions encodings
        lstm_out, (h, _) = self.lstm(embedded_questions)

        # get final words encodings using linear layer
        contextual_word_embedding = self.lstm_proj(lstm_out)

        # reshape last hidden states for questions encodings -> [batch_size x (2*dim)]
        question_encoding = h.permute(1, 0, 2).contiguous().view(batch_size, -1)

        return contextual_word_embedding, question_encoding
