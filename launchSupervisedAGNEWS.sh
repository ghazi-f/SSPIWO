#!/usr/bin/env bash

# Unweighted experiments
python sent_train.py --losses "S" --test_name "AGNEWS/Supervised/0.001small1" --supervision_proportion 0.001 --batch_size 32 --grad_accu 1 --max_len 64 --device "cuda:1" --dev_index 1 --dataset ag_news --result_csv agnews.csv
python sent_train.py --losses "S" --test_name "AGNEWS/Supervised/0.001small2" --supervision_proportion 0.001 --batch_size 32 --grad_accu 1 --max_len 64 --device "cuda:1" --dev_index 2 --dataset ag_news --result_csv agnews.csv
python sent_train.py --losses "S" --test_name "AGNEWS/Supervised/0.001small3" --supervision_proportion 0.001 --batch_size 32 --grad_accu 1 --max_len 64 --device "cuda:1" --dev_index 3 --dataset ag_news --result_csv agnews.csv
python sent_train.py --losses "S" --test_name "AGNEWS/Supervised/0.001small4" --supervision_proportion 0.001 --batch_size 32 --grad_accu 1 --max_len 64 --device "cuda:1" --dev_index 4 --dataset ag_news --result_csv agnews.csv
python sent_train.py --losses "S" --test_name "AGNEWS/Supervised/0.001small5" --supervision_proportion 0.001 --batch_size 32 --grad_accu 1 --max_len 64 --device "cuda:1" --dev_index 5 --dataset ag_news --result_csv agnews.csv
python sent_train.py --losses "S" --test_name "AGNEWS/Supervised/0.003small1" --supervision_proportion 0.003 --batch_size 32 --grad_accu 1 --max_len 64 --device "cuda:1" --dev_index 1 --dataset ag_news --result_csv agnews.csv
python sent_train.py --losses "S" --test_name "AGNEWS/Supervised/0.003small2" --supervision_proportion 0.003 --batch_size 32 --grad_accu 1 --max_len 64 --device "cuda:1" --dev_index 2 --dataset ag_news --result_csv agnews.csv
python sent_train.py --losses "S" --test_name "AGNEWS/Supervised/0.003small3" --supervision_proportion 0.003 --batch_size 32 --grad_accu 1 --max_len 64 --device "cuda:1" --dev_index 3 --dataset ag_news --result_csv agnews.csv
python sent_train.py --losses "S" --test_name "AGNEWS/Supervised/0.003small4" --supervision_proportion 0.003 --batch_size 32 --grad_accu 1 --max_len 64 --device "cuda:1" --dev_index 4 --dataset ag_news --result_csv agnews.csv
python sent_train.py --losses "S" --test_name "AGNEWS/Supervised/0.003small5" --supervision_proportion 0.003 --batch_size 32 --grad_accu 1 --max_len 64 --device "cuda:1" --dev_index 5 --dataset ag_news --result_csv agnews.csv
python sent_train.py --losses "S" --test_name "AGNEWS/Supervised/0.01small1" --supervision_proportion 0.01 --batch_size 32 --grad_accu 1 --max_len 64 --device "cuda:1" --dev_index 1 --dataset ag_news --result_csv agnews.csv
python sent_train.py --losses "S" --test_name "AGNEWS/Supervised/0.01small2" --supervision_proportion 0.01 --batch_size 32 --grad_accu 1 --max_len 64 --device "cuda:1" --dev_index 2 --dataset ag_news --result_csv agnews.csv
python sent_train.py --losses "S" --test_name "AGNEWS/Supervised/0.01small3" --supervision_proportion 0.01 --batch_size 32 --grad_accu 1 --max_len 64 --device "cuda:1" --dev_index 3 --dataset ag_news --result_csv agnews.csv
python sent_train.py --losses "S" --test_name "AGNEWS/Supervised/0.01small4" --supervision_proportion 0.01 --batch_size 32 --grad_accu 1 --max_len 64 --device "cuda:1" --dev_index 4 --dataset ag_news --result_csv agnews.csv
python sent_train.py --losses "S" --test_name "AGNEWS/Supervised/0.01small5" --supervision_proportion 0.01 --batch_size 32 --grad_accu 1 --max_len 64 --device "cuda:1" --dev_index 5 --dataset ag_news --result_csv agnews.csv
python sent_train.py --losses "S" --test_name "AGNEWS/Supervised/0.03small1" --supervision_proportion 0.03 --batch_size 32 --grad_accu 1 --max_len 64 --device "cuda:1" --dev_index 1 --dataset ag_news --result_csv agnews.csv
python sent_train.py --losses "S" --test_name "AGNEWS/Supervised/0.03small2" --supervision_proportion 0.03 --batch_size 32 --grad_accu 1 --max_len 64 --device "cuda:1" --dev_index 2 --dataset ag_news --result_csv agnews.csv
python sent_train.py --losses "S" --test_name "AGNEWS/Supervised/0.03small3" --supervision_proportion 0.03 --batch_size 32 --grad_accu 1 --max_len 64 --device "cuda:1" --dev_index 3 --dataset ag_news --result_csv agnews.csv
python sent_train.py --losses "S" --test_name "AGNEWS/Supervised/0.03small4" --supervision_proportion 0.03 --batch_size 32 --grad_accu 1 --max_len 64 --device "cuda:1" --dev_index 4 --dataset ag_news --result_csv agnews.csv
python sent_train.py --losses "S" --test_name "AGNEWS/Supervised/0.03small5" --supervision_proportion 0.03 --batch_size 32 --grad_accu 1 --max_len 64 --device "cuda:1" --dev_index 5 --dataset ag_news --result_csv agnews.csv
python sent_train.py --losses "S" --test_name "AGNEWS/Supervised/0.1small1" --supervision_proportion 0.1 --batch_size 32 --grad_accu 1 --max_len 64 --device "cuda:1" --dev_index 1 --dataset ag_news --result_csv agnews.csv
python sent_train.py --losses "S" --test_name "AGNEWS/Supervised/0.1small2" --supervision_proportion 0.1 --batch_size 32 --grad_accu 1 --max_len 64 --device "cuda:1" --dev_index 2 --dataset ag_news --result_csv agnews.csv
python sent_train.py --losses "S" --test_name "AGNEWS/Supervised/0.1small3" --supervision_proportion 0.1 --batch_size 32 --grad_accu 1 --max_len 64 --device "cuda:1" --dev_index 3 --dataset ag_news --result_csv agnews.csv
python sent_train.py --losses "S" --test_name "AGNEWS/Supervised/0.1small4" --supervision_proportion 0.1 --batch_size 32 --grad_accu 1 --max_len 64 --device "cuda:1" --dev_index 4 --dataset ag_news --result_csv agnews.csv
python sent_train.py --losses "S" --test_name "AGNEWS/Supervised/0.1small5" --supervision_proportion 0.1 --batch_size 32 --grad_accu 1 --max_len 64 --device "cuda:1" --dev_index 5 --dataset ag_news --result_csv agnews.csv
python sent_train.py --losses "S" --test_name "AGNEWS/Supervised/0.3small1" --supervision_proportion 0.3 --batch_size 32 --grad_accu 1 --max_len 64 --device "cuda:1" --dev_index 1 --dataset ag_news --result_csv agnews.csv
python sent_train.py --losses "S" --test_name "AGNEWS/Supervised/0.3small2" --supervision_proportion 0.3 --batch_size 32 --grad_accu 1 --max_len 64 --device "cuda:1" --dev_index 2 --dataset ag_news --result_csv agnews.csv
python sent_train.py --losses "S" --test_name "AGNEWS/Supervised/0.3small3" --supervision_proportion 0.3 --batch_size 32 --grad_accu 1 --max_len 64 --device "cuda:1" --dev_index 3 --dataset ag_news --result_csv agnews.csv
python sent_train.py --losses "S" --test_name "AGNEWS/Supervised/0.3small4" --supervision_proportion 0.3 --batch_size 32 --grad_accu 1 --max_len 64 --device "cuda:1" --dev_index 4 --dataset ag_news --result_csv agnews.csv
python sent_train.py --losses "S" --test_name "AGNEWS/Supervised/0.3small5" --supervision_proportion 0.3 --batch_size 32 --grad_accu 1 --max_len 64 --device "cuda:1" --dev_index 5 --dataset ag_news --result_csv agnews.csv
python sent_train.py --losses "S" --test_name "AGNEWS/Supervised/1.0small1" --supervision_proportion 1.0 --batch_size 32 --grad_accu 1 --max_len 64 --device "cuda:1" --dev_index 1 --dataset ag_news --result_csv agnews.csv
python sent_train.py --losses "S" --test_name "AGNEWS/Supervised/1.0small2" --supervision_proportion 1.0 --batch_size 32 --grad_accu 1 --max_len 64 --device "cuda:1" --dev_index 2 --dataset ag_news --result_csv agnews.csv
python sent_train.py --losses "S" --test_name "AGNEWS/Supervised/1.0small3" --supervision_proportion 1.0 --batch_size 32 --grad_accu 1 --max_len 64 --device "cuda:1" --dev_index 3 --dataset ag_news --result_csv agnews.csv
python sent_train.py --losses "S" --test_name "AGNEWS/Supervised/1.0small4" --supervision_proportion 1.0 --batch_size 32 --grad_accu 1 --max_len 64 --device "cuda:1" --dev_index 4 --dataset ag_news --result_csv agnews.csv
python sent_train.py --losses "S" --test_name "AGNEWS/Supervised/1.0small5" --supervision_proportion 1.0 --batch_size 32 --grad_accu 1 --max_len 64 --device "cuda:1" --dev_index 5 --dataset ag_news --result_csv agnews.csv
