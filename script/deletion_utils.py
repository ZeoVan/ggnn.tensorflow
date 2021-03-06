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


def generate_graph_file(test_file_path):
    fbs_path = test_file_path.split(".")[0] + ".fbs"
    graph_path = test_file_path.split(".")[0] + ".txt"

    if not os.path.exists(fbs_path):

        fbs_cmd = "docker run --rm -v $(pwd):/e -it yijun/fast -S -G " + test_file_path + " " + fbs_path
        os.system(fbs_cmd)

    if not os.path.exists(graph_path):
        ggnn_cmd = "docker run -v $(pwd):/e --entrypoint ggnn -it yijun/fast " + fbs_path + " " + test_file_path.split(".")[0] + "_train.txt" + " " + graph_path
        print(ggnn_cmd)
        os.system(ggnn_cmd)
    
    
    return graph_path

def generate_statements_file(pb_path, statement_type, output_path):
    
    if not os.path.exists(output_path):
        generate_stmt_cmd = "docker run --rm -v $(pwd):/e -it yijun/fast --node_types=" + statement_type + " " + pb_path + " " + "temp.pb" + " > " + output_path
        print(generate_stmt_cmd)
        os.system(generate_stmt_cmd)
    # return stmt_ids_path

def generate_pb_file(test_file_path):
    print("Generating pb with src_path : " + test_file_path)
    pb_path = os.path.join(test_file_path.split(".")[0] + ".pb")
    if not os.path.exists(pb_path):
        cmd = "docker run --rm -v $(pwd):/e -it yijun/fast -p " + test_file_path + " " + pb_path
        os.system(cmd)
    return pb_path

def generate_subtrees(pb_path, stmt_ids):

    subtrees_dict = {}
    for stmt_id in stmt_ids:
        subtree_ids_path =   os.path.join(pb_path.split(".")[0] + "_subtree_" + str(stmt_id) + ".csv")
        generate_subtree_ids_cmd = "docker run -v $(pwd):/e yijun/fast -CA " +  str(stmt_id) + " " + pb_path + " > " + subtree_ids_path        
        os.system(generate_subtree_ids_cmd)
        
        subtree_ids = []
        with open(subtree_ids_path,"r") as f1:
            data = f1.readlines()
            for line in data:
                subtree_id = int(line.replace("\n",""))
                subtree_ids.append(subtree_id)

        subtrees_dict[int(stmt_id)] = subtree_ids

    return subtrees_dict
            
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

def generate_component_ids(pb_path):
    # Create model path folder if not exists
    
    # generate_graph_files(opt)
    # print(stmt_ids_path)

    single_stmt_ids_path = os.path.join(pb_path.split(".")[0] + "_expr_stmt_ids.txt")
    generate_statements_file(pb_path, "statements_single.csv",single_stmt_ids_path)

    condition_stmt_ids_path = os.path.join(pb_path.split(".")[0] + "_condition_stmt_ids.txt")
    generate_statements_file(pb_path, "statements_condition.csv",condition_stmt_ids_path)

    all_stmt_ids_path = os.path.join(pb_path.split(".")[0] + "_stmt_ids.txt")
    if os.path.exists(all_stmt_ids_path):
        os.remove(all_stmt_ids_path)

    stmt_ids = []
    with open(single_stmt_ids_path,"r") as f:
        data = f.readlines()
        for line in data:
            stmt_ids.append(line.replace("\n",""))

    with open(condition_stmt_ids_path,"r") as f1:
        data = f1.readlines()
        for line in data:
            stmt_ids.append(line.replace("\n",""))

    with open(all_stmt_ids_path,"w") as f2:
        for stmt_id in stmt_ids:
            f2.write(str(stmt_id))
            f2.write("\n")
        
    return stmt_ids

def scale_attention_scores(attention_scores_map):
    attention_scores_sorted = sorted(attention_scores_map.items(), key=operator.itemgetter(1))
    attention_scores_sorted.reverse()

    node_ids = []
    attention_scores = []
    raw_attention_scores_dict = {}
    for element in attention_scores_sorted:
        node_ids.append(element[0])
        attention_scores.append(element[1])
        raw_attention_scores_dict[element[0]] = element[1]
    scaled_attention_scores = scale_attention_score_by_group(attention_scores)

    scaled_attention_scores_dict = {}
    for i, score in enumerate(scaled_attention_scores):
        key = str(node_ids[i])
        scaled_attention_scores_dict[key] = float(score)

    return scaled_attention_scores_dict, raw_attention_scores_dict

def generate_attention_scores(test_file_path, attention_scores):
    attention_scores_map = {}
    for i, score in enumerate(attention_scores):
        attention_scores_map[i] = float(score)


    scaled_attention_scores_dict, raw_attention_scores_dict = scale_attention_scores(attention_scores_map)

    scaled_attention_scores_path = os.path.join(test_file_path.split(".")[0] + "_scaled.csv")

    with open(scaled_attention_scores_path,"w") as f:
        for k, v in scaled_attention_scores_dict.items():
            f.write(str(k) + "," + str(v))
            f.write("\n")

    raw_attention_scores_path = os.path.join(test_file_path.split(".")[0] + "_raw.csv")

    with open(raw_attention_scores_path,"w") as f:
        for k, v in raw_attention_scores_dict.items():
            f.write(str(k) + "," + str(v))
            f.write("\n")
     
    return scaled_attention_scores_path, raw_attention_scores_path, raw_attention_scores_dict

def compute_components_attention_score(subtrees_dict, raw_attention_scores_dict):
    # print(subtrees_dict)
    print(raw_attention_scores_dict)
    component_scores_dict = {}
    for component_id, subtree_ids in subtrees_dict.items():
        component_scores_dict[component_id] = 0
        for subtree_id in subtree_ids:
            component_scores_dict[component_id] += raw_attention_scores_dict[subtree_id]
    return component_scores_dict



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

    # Load pretrained embeddings
    with gzip.open(opt.pretrained_embeddings_url, 'rb') as fh:
        embeddings, embed_lookup = pickle.load(fh,encoding='latin1')
        opt.pretrained_embeddings = embeddings
        opt.pretrained_embed_lookup = embed_lookup

    # Generate necessary files
    opt.model_path = os.path.join(opt.model_path,"sum_softmax" + "_hidden_layer_size_" + str(opt.hidden_layer_size) + "_num_hidden_layer_"  + str(opt.num_hidden_layer)) + "_node_dim_" + str(opt.node_dim)
    opt.test_graph_path = generate_graph_file(opt.test_file)
    opt.pb_path = generate_pb_file(opt.test_file)

    # Generate statement id and subtree ids
    component_ids = generate_component_ids(opt.pb_path)
    subtrees_dict = generate_subtrees(opt.pb_path, component_ids)

    # Init the model
    checkfile = os.path.join(opt.model_path, 'cnn_tree.ckpt')    
    ckpt = tf.train.get_checkpoint_state(opt.model_path)
    test_dataset = MonoLanguageProgramData(opt, False, False, True)
    # opt.n_edge_types = test_dataset.n_edge_types
    opt.n_edge_types = 7
    ggnn = DenseGGNNModel(opt)
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

            prediction_results = making_prediction(test_dataset, ggnn, sess, opt, True)
            
            component_attention_scores_dict = compute_components_attention_score(subtrees_dict, prediction_results["raw_attention_scores_dict"])
            
            components_attention_scores_path = os.path.join(opt.pb_path.split(".")[0] + "_component_ids.csv")

            with open(components_attention_scores_path,"w") as f:
                for k, v in component_attention_scores_dict.items():
                    f.write(str(k) + "," + str(v))
                    f.write("\n")

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

        correct_labels.extend(np.argmax(batch_data['labels'],axis=1))
        argmax = np.argmax(softmax_values_data,axis=1)
        predictions.extend(np.argmax(softmax_values_data,axis=1))

        print("Probability : " + str(softmax_values_data))
        print("Probability max : " + str(np.argmax(softmax_values_data,axis=1)))
        print("Correct class " + str(correct_labels))
        print("Predicted class : " + str(predictions))


    scaled_attention_scores_path, raw_attention_scores_path, raw_attention_scores_dict = generate_attention_scores(opt.test_file, attention_scores_data[0])
    prediction_results = {}
    prediction_results["scaled_attention_scores_path"] = scaled_attention_scores_path
    prediction_results["raw_attention_scores_path"] = raw_attention_scores_path
    prediction_results["raw_attention_scores_dict"] = raw_attention_scores_dict
    prediction_results["softmax_values_data"] = softmax_values_data
    prediction_results["predicted_label"] = argmax[0]
    prediction_results["correct_label"] = np.argmax(batch_data['labels'],axis=1)
    
    return prediction_results

if __name__ == "__main__":
    main()
