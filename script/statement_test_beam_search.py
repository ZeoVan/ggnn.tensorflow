import argparse
import random

import gzip
import pycurl
import pickle

import tensorflow as tf
from utils.data.dataset import MonoLanguageProgramData
from utils.data.dataset import load_single_program
from utils.utils import ThreadedIterator
from utils.utils import scale_attention_score_by_group
from utils.dense_ggnn import DenseGGNNModel
import os
import sys

import math
import copy
import operator
import numpy as np
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score



def fetch_data_from_github(filename):
    if not os.path.exists(os.path.dirname(filename)):
        os.makedirs(os.path.dirname(filename))
    fp = open(filename, "wb") 
    curl = pycurl.Curl()
    curl.setopt(pycurl.URL, os.path.join("https://raw.githubusercontent.com/bdqnghi/ggnn.tensorflow/master", filename))
    curl.setopt(pycurl.WRITEDATA, fp)
    curl.perform()
    curl.close()
    fp.close()   

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--workers', type=int, help='number of data loading workers', default=2)
    parser.add_argument('--train_batch_size', type=int, default=10, help='input batch size')
    parser.add_argument('--test_batch_size', type=int, default=5, help='input batch size')
    parser.add_argument('--state_dim', type=int, default=30, help='GGNN hidden state dimension size')
    parser.add_argument('--node_dim', type=int, default=100, help='node dimension size')
    parser.add_argument('--hidden_layer_size', type=int, default=200, help='size of hidden layer')
    parser.add_argument('--num_hidden_layer', type=int, default=1, help='number of hidden layer')
    parser.add_argument('--n_steps', type=int, default=10, help='propogation steps number of GGNN')
    parser.add_argument('--lr', type=float, default=0.001, help='learning rate')
    parser.add_argument('--cuda', action='store_true', help='enables cuda')
    parser.add_argument('--verbal', type=bool, default=True, help='print training info or not')
    parser.add_argument('--manualSeed', type=int, help='manual seed')
    parser.add_argument('--test_file', default="program_data/test_data/5/100_dead_code_1.java", help="test program")
    parser.add_argument('--n_classes', type=int, default=10, help='manual seed')
    parser.add_argument('--path', default="program_data/github_java_sort_function_babi", help='program data')
    parser.add_argument('--model_path', default="model", help='path to save the model')
    parser.add_argument('--n_hidden', type=int, default=50, help='number of hidden layers')
    parser.add_argument('--size_vocabulary', type=int, default=59, help='maximum number of node types')
    parser.add_argument('--log_path', default="logs/" ,help='log path for tensorboard')
    parser.add_argument('--aggregation', type=int, default=1, choices=range(0,4), help='0 for max pooling, 1 for attention with sum pooling, 2 for attention with max pooling, 3 for attention with average pooling')
    parser.add_argument('--distributed_function', type=int, default=0, choices=range(0,2), help='0 for softmax, 1 for sigmoid')
    parser.add_argument('--pretrained_embeddings_url', default="embedding/fast_pretrained_vectors.pkl.gz", help='pretrained embeddings url, there are 2 objects in this file, the first object is the embedding matrix, the other is the lookup dictionary')
    parser.add_argument('argv', nargs="+", help='filenames')
    opt = parser.parse_args()

    if len(opt.argv) == 1:
        opt.test_file = opt.argv[0]
    # Create model path folder if not exists
    opt.model_path = os.path.join(opt.model_path,"sum_softmax" + "_hidden_layer_size_" + str(opt.hidden_layer_size) + "_num_hidden_layer_"  + str(opt.num_hidden_layer)) + "_node_dim_" + str(opt.node_dim)
    
    generate_graph_files(opt)
    pb_path = generate_files(opt)
    # generate_graph_files(opt)

    stmt_ids_path = generate_statement_file(pb_path)
    opt.stmt_ids_path = stmt_ids_path
    statement_paths, stmt_ids = delete_statements(stmt_ids_path, pb_path)
   
    statement_test_file = os.path.join(opt.pb_path.split(".")[0] + "_statement_test_results.csv")
    delta_score_file = os.path.join(opt.pb_path.split(".")[0] + "_delta_score_scaled.csv")
    delta_visualization_file = os.path.join(opt.pb_path.split(".")[0] + "_statement_by_delta_visualization.html")

    # if not os.path.exists(opt.pretrained_embeddings_url):
    #     fetch_data_from_github(opt.pretrained_embeddings_url)
    with gzip.open(opt.pretrained_embeddings_url, 'rb') as fh:
        embeddings, embed_lookup = pickle.load(fh,encoding='latin1')
        opt.pretrained_embeddings = embeddings
        opt.pretrained_embed_lookup = embed_lookup

    checkfile = os.path.join(opt.model_path, 'cnn_tree.ckpt')    
    ckpt = tf.train.get_checkpoint_state(opt.model_path)
    
    test_dataset = MonoLanguageProgramData(opt, False, False, True)
    # opt.n_edge_types = test_dataset.n_edge_types
    opt.n_edge_types = 7

    ggnn = DenseGGNNModel(opt)

    
    original_file = opt.test_file

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

    
            original_softmax_values_data, _, correct_label , prediction = making_prediction(test_dataset, ggnn, sess, opt, True)
            subtree_score_dict = opt.subtree_score_dict 

           

            if os.path.exists(statement_test_file):
                os.remove(statement_test_file)

            if os.path.exists(delta_score_file):
                os.remove(delta_score_file)
            with open(statement_test_file,"a") as f:
                line = original_file + ";" + str(original_softmax_values_data[0].tolist()) + ";" + correct_label + ";" + prediction + ";"
                f.write(line)
                f.write("\n")

            delta_score_map = {}

            for i, stmt_path in enumerate(statement_paths):
                opt.test_file = stmt_path

                splits = stmt_path.split("_")
                stmt_id = splits[len(splits)-1].replace(".csv","").replace(".java","")
                score = subtree_score_dict[int(stmt_id)]

                generate_graph_files(opt)

                # if os.stat(opt.test_graph_path).st_size != 0:
                generate_files(opt)
           
                test_dataset = MonoLanguageProgramData(opt, False, False, True)
                opt.n_edge_types = test_dataset.n_edge_types
                softmax_values_data, argmax, correct_label, prediction = making_prediction(test_dataset, ggnn, sess, opt, False)
                
                

                delta = abs(original_softmax_values_data[0][int(correct_label)] - softmax_values_data[0][int(correct_label)])

                with open(statement_test_file,"a") as f:
                    line = stmt_path + ";" + str(softmax_values_data[0].tolist()) + ";" + correct_label + ";" + prediction + ";" + str(delta) + ";" + str(score)
                    f.write(line)
                    f.write("\n")

               


                subtree_ids_path =   os.path.join(pb_path.split(".")[0] + "_subtree_" + str(stmt_ids[i]) + ".csv")
                # subtree_ids = []
                delta_score_map[stmt_id] = delta
                with open(subtree_ids_path, "r") as f1:
                    data = f1.readlines()
                    for line in data:
                        subtree_id = line.replace("\n","")
                        delta_score_map[subtree_id] = delta

            delta_score_map_scaled, raw_delta_score_map = scale_attention_scores_map(delta_score_map)
            with open(delta_score_file,"a") as f2:

                for tree_id, score in delta_score_map_scaled.items():
                    line = tree_id + "," + str(score)
                    f2.write(line)
                    f2.write("\n")

            generate_visualization(pb_path, delta_score_file, delta_visualization_file)

    # print(train_dataset.bucketed)

def making_prediction(test_dataset, ggnn, sess, opt, original=False):

     # For debugging purpose
    nodes_representation = ggnn.nodes_representation
    graph_representation = ggnn.graph_representation
    logits = ggnn.logits
    softmax_values = ggnn.softmax_values
    attention_scores = ggnn.attention_scores

    batch_iterator = ThreadedIterator(test_dataset.make_minibatch_iterator(), max_queue_size=5)

    correct_labels = []
    predictions = []

    attention_scores_data = []
    softmax_values_data = []
    print("--------------------------------------")
    print('Computing training accuracy...')

    for step, batch_data in enumerate(batch_iterator):
        # print(batch_data["labels"])

        print(batch_data['labels'])
        softmax_values_data, attention_scores_data = sess.run(
            [softmax_values, attention_scores],
            feed_dict={
                ggnn.placeholders["initial_node_representation"]: batch_data["initial_representations"],
                ggnn.placeholders["num_vertices"]: batch_data["num_vertices"],
                ggnn.placeholders["adjacency_matrix"]:  batch_data['adjacency_matrix'],
                ggnn.placeholders["labels"]:  batch_data['labels']
            }
        )

        
        # print(attention_scores_data)
        # print(len(attention_scores_data[0]))
        
        correct_labels.extend(np.argmax(batch_data['labels'],axis=1))
        argmax = np.argmax(softmax_values_data,axis=1)
        predictions.extend(np.argmax(softmax_values_data,axis=1))

        print("Probability : " + str(softmax_values_data))
        print("Probability max : " + str(np.argmax(softmax_values_data,axis=1)))
        print("Correct class " + str(correct_labels))
        print("Predicted class : " + str(predictions))

    scaled_attention_path, raw_attention_path, raw_attention_score_dict = generate_attention_scores(opt, attention_scores_data[0])

    html_path = os.path.join(scaled_attention_path.split(".")[0] + ".html")
    generate_visualization(opt.pb_path,scaled_attention_path,html_path)

    if original:
        modified_attention_score_dict, subtree_score_dict = generate_subtree(opt, opt.stmt_ids_path, raw_attention_score_dict)
        opt.subtree_score_dict = subtree_score_dict
    # print(attention_path)
    # print(opt.pb_path)

    return softmax_values_data, argmax, str(correct_labels[0]), str(predictions[0])

if __name__ == "__main__":
    main()
