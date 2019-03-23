import argparse
import random

import pickle

import tensorflow as tf
from utils.data.dataset import MonoLanguageProgramData
from utils.utils import ThreadedIterator
from utils.dense_ggnn import DenseGGNNModel
import os
import sys

import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument('--workers', type=int, help='number of data loading workers', default=2)
parser.add_argument('--train_batch_size', type=int, default=10, help='input batch size')
parser.add_argument('--test_batch_size', type=int, default=5, help='input batch size')
parser.add_argument('--state_dim', type=int, default=30, help='GGNN hidden state dimension size')
parser.add_argument('--node_dim', type=int, default=100, help='node dimension size')
parser.add_argument('--n_steps', type=int, default=10, help='propogation steps number of GGNN')
parser.add_argument('--epochs', type=int, default=150, help='number of epochs to train for')
parser.add_argument('--lr', type=float, default=0.001, help='learning rate')
parser.add_argument('--cuda', action='store_true', help='enables cuda')
parser.add_argument('--verbal', type=bool, default=True, help='print training info or not')
parser.add_argument('--manualSeed', type=int, help='manual seed')
parser.add_argument('--n_classes', type=int, default=10, help='manual seed')
parser.add_argument('--path', default="program_data/github_java_sort_function_babi", help='program data')
parser.add_argument('--model_path', default="model", help='path to save the model')
parser.add_argument('--n_hidden', type=int, default=50, help='number of hidden layers')
parser.add_argument('--size_vocabulary', type=int, default=59, help='maximum number of node types')
parser.add_argument('--training', action="store_true",help='is training')
parser.add_argument('--testing', action="store_true",help='is testing')
parser.add_argument('--training_percentage', type=float, default=1.0 ,help='percentage of data use for training')
parser.add_argument('--log_path', default="logs/" ,help='log path for tensorboard')
parser.add_argument('--checkpoint_every', type=int, default=100 ,help='check point to save model')
parser.add_argument('--pretrained_embeddings_url', default="embedding/fast_pretrained_vectors.pkl", help='pretrained embeddings url, there are 2 objects in this file, the first object is the embedding matrix, the other is the lookup dictionary')

opt = parser.parse_args()


# Create model path folder if not exists
if not os.path.exists(opt.model_path):
    os.mkdir(opt.model_path)

def main(opt):
    with open(opt.pretrained_embeddings_url, 'rb') as fh:
        embeddings, embed_lookup = pickle.load(fh,encoding='latin1')

        opt.pretrained_embeddings = embeddings
        opt.pretrained_embed_lookup = embed_lookup

    
    checkfile = os.path.join(opt.model_path, 'cnn_tree.ckpt')   
    ckpt = tf.train.get_checkpoint_state(opt.model_path)
    
    train_dataset = MonoLanguageProgramData(opt)
    opt.n_edge_types = train_dataset.n_edge_types

    ggnn = DenseGGNNModel(opt)

    # For debugging purpose
    nodes_representation = ggnn.nodes_representation
    graph_representation = ggnn.graph_representation
    logits = ggnn.logits
    softmax_values = ggnn.softmax_values

    loss_node = ggnn.loss

    optimizer = tf.train.AdamOptimizer(opt.lr)
    train_step = optimizer.minimize(loss_node)

    saver = tf.train.Saver(save_relative_paths=True, max_to_keep=5)
    init = tf.global_variables_initializer()
   
    with tf.Session() as sess:
        sess.run(init)

        if ckpt and ckpt.model_checkpoint_path:
            print("Continue training with old model")
            print("Checkpoint path : " + str(ckpt.model_checkpoint_path))
            saver.restore(sess, ckpt.model_checkpoint_path)
            for i, var in enumerate(saver._var_list):
                print('Var {}: {}'.format(i, var))

        for epoch in range(1,  opt.epochs + 1):
            batch_iterator = ThreadedIterator(train_dataset.make_minibatch_iterator(), max_queue_size=5)
            for step, batch_data in enumerate(batch_iterator):
                # print(batch_data["labels"])

                _ , err, softmax_values_data = sess.run(
                    [train_step, loss_node, softmax_values],
                    feed_dict={
                        ggnn.placeholders["initial_node_representation"]: batch_data["initial_representations"],
                        ggnn.placeholders["num_vertices"]: batch_data["num_vertices"],
                        ggnn.placeholders["adjacency_matrix"]:  batch_data['adjacency_matrix'],
                        ggnn.placeholders["labels"]:  batch_data['labels']
                    }
                )

                print("Epoch:", epoch, "Step:",step,"Loss:", err)
                if step % opt.checkpoint_every == 0:
                    # save state so we can resume later
                    saver.save(sess, checkfile)
                    # shutil.rmtree(savedmodel_path)
                    print('Checkpoint saved, epoch:' + str(epoch) + ', step: ' + str(step) + ', loss: ' + str(err) + '.')
                # print(out[0])


    # print(train_dataset.bucketed)
  

    
if __name__ == "__main__":
    main(opt)

