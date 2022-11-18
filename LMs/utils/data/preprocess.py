import gc
import os
import time

import dgl
import numpy as np
import pandas as pd
import torch as th
from transformers import AutoTokenizer
import time
import utils.function as uf
from utils.function.dgl_utils import sample_nodes
from utils.settings import *
from tqdm import tqdm
from copy import deepcopy
from torch_sparse import SparseTensor
from torch_geometric.utils import to_undirected, dropout_adj


def tokenize_text(cf):
    # = Tokenization on FSequence
    full_dict = deepcopy(cf.model_conf)
    full_dict['dataset'] = '_'.join(full_dict['dataset'].split('_')[:2])
    full_cf = cf.__class__(SN(**full_dict)).init()
    d = full_cf.data
    if not d.is_processed('token'):
        if cf.local_rank <= 0:
            # ! Load full-graph
            print(f'Processing data on LOCAL_RANK #{cf.local_rank}...')
            g_info = load_graph_info(full_cf)
            print(f'Loaded graph structure, start tokenization...')
            _tokenize_ogb_arxiv_datasets(d, g_info.labels)
            print(f'Tokenization finished on LOCAL_RANK #{cf.local_rank}')
        else:
            # If not main worker (i.e. Local_rank!=0), wait until data is processed and load
            print(f'Waiting for tokenization on LOCAL_RANK #{cf.local_rank}')
            while not d.is_processed('token'):
                time.sleep(2)  # Check if processed every 2 seconds
            print(f'Detected processed data, LOCAL_RANK #{cf.local_rank} start loading!')
            time.sleep(5)  # Wait for file write for 5 seconds
    else:
        cf.log(f'Found processed {cf.dataset}.')


def plot_length_distribution(node_text, tokenizer, g):
    sampled_ids = np.random.permutation(g.nodes())[:10000]
    get_text = lambda n: node_text.iloc[n]['text'].tolist()
    tokenized = tokenizer(get_text(sampled_ids), padding='do_not_pad').data['input_ids']
    node_text['text_length'] = node_text.apply(lambda x: len(x['text'].split(' ')), axis=1)
    pd.Series([len(_) for _ in tokenized]).hist(bins=20)
    import matplotlib.pyplot as plt
    plt.show()


def tokenize_graph(cf):
    # = Tokenization on Full Graph
    full_dict = deepcopy(cf.model_conf)
    full_cf = cf.__class__(SN(**full_dict)).init()
    d = full_cf.data
    if not d.is_processed('token'):
        if cf.local_rank <= 0:
            # ! Load full-graph
            print(f'Processing data on LOCAL_RANK #{cf.local_rank}...')
            g_info = load_graph_info(full_cf)
            print(f'Loaded graph structure, start tokenization...')
            if d.ogb_name == 'ogbn-arxiv':
                _tokenize_ogb_arxiv_datasets(d, g_info.labels)
            else:
                raise NotImplementedError
            print(f'Tokenization finished on LOCAL_RANK #{cf.local_rank}')
        else:
            # If not main worker (i.e. Local_rank!=0), wait until data is processed and load
            print(f'Waiting for tokenization on LOCAL_RANK #{cf.local_rank}')
            while not d.is_processed('token'):
                time.sleep(2)  # Check if processed every 2 seconds
            print(f'Detected processed data, LOCAL_RANK #{cf.local_rank} start loading!')
            time.sleep(5)  # Wait for file write for 5 seconds
    else:
        cf.log(f'Found processed {cf.dataset}.')

def load_ogb_graph_structure_only(cf):
    from ogb.nodeproppred import DglNodePropPredDataset
    data = DglNodePropPredDataset(cf.data.ogb_name, root=uf.init_path(cf.data.raw_data_path))
    g, labels = data[0]
    split_idx = data.get_idx_split()
    labels = labels.squeeze().numpy()
    return g, labels, split_idx




def load_graph_info(cf):
    d = cf.data
    # ! Process Full Graph
    if not d.is_processed('g_info'):
        # Load OGB
        if cf.local_rank <= 0:
            g, labels, split_idx = load_ogb_graph_structure_only(cf)
            # Process and save supervision
            splits = {**{f'{_}_x': split_idx[_].numpy() for _ in ['train', 'valid', 'test']}, 'labels': labels}
            is_gold = np.zeros((g.num_nodes()), dtype=bool)
            val_test = np.zeros((g.num_nodes()), dtype=bool)
            g, splits = _subset_graph(g, cf, splits)
            is_gold[splits['train_x']] = True
            val_test[splits['valid_x']] = True
            val_test[splits['test_x']] = True
            g_info = SN(splits=splits, labels=labels, is_gold=is_gold, n_nodes=g.num_nodes(), val_test=val_test)
            if d.subset_ratio < 1:
                g_info.IDs = g.ndata['_ID'].numpy()
                g_info.labels = g_info.labels[g_info.IDs]
                g_info.is_gold = g_info.is_gold[g_info.IDs]
                g_info.val_test = g_info.val_test[g_info.IDs]
            d.save_g_info(g_info)
            del g
        else:
            # If not main worker (i.e. Local_rank!=0), wait until data is processed and load
            print(f'Waiting for feature processing on LOCAL_RANK #{cf.local_rank}')
            while not d.is_processed('g_info'):
                time.sleep(2)  # Check if processed every 2 seconds
            print(f'Detected processed feature, LOCAL_RANK #{cf.local_rank} start loading!')
            time.sleep(5)  # Wait f
    g_info = uf.pickle_load(d._g_info_file)
    return g_info


def _tokenize_ogb_arxiv_datasets(d, labels, chunk_size=50000):
    def merge_by_ids(meta_data, node_ids, categories):
        meta_data.columns = ["ID", "Title", "Abstract"]
        # meta_data.drop([0, meta_data.shape[0] - 1], axis=0, inplace=True)  # Drop first and last in Arxiv full dataset processing
        meta_data["ID"] = meta_data["ID"].astype(np.int64)
        meta_data.columns = ["mag_id", "title", "abstract"]
        data = pd.merge(node_ids, meta_data, how="left", on="mag_id")
        data = pd.merge(data, categories, how="left", on="label_id")
        return data

    def read_ids_and_labels(data_root):
        category_path_csv = f"{data_root}/mapping/labelidx2arxivcategeory.csv.gz"
        paper_id_path_csv = f"{data_root}/mapping/nodeidx2paperid.csv.gz"  #
        paper_ids = pd.read_csv(paper_id_path_csv)
        categories = pd.read_csv(category_path_csv)
        categories.columns = ["ID", "category"]  # 指定ID 和 category列写进去
        paper_ids.columns = ["ID", "mag_id"]
        categories.columns = ["label_id", "category"]
        paper_ids["label_id"] = labels
        return categories, paper_ids  # 返回类别和论文ID

    def process_raw_text_df(meta_data, node_ids, categories):

        data = merge_by_ids(meta_data.dropna(), node_ids, categories)
        data = data[~data['title'].isnull()]
        text_func = {
            'TA': lambda x: f"Title: {x['title']}. Abstract: {x['abstract']}",
            'T': lambda x: x['title'],
        }
        # Merge title and abstract
        data['text'] = data.apply(text_func[d.process_mode], axis=1)
        data['text'] = data.apply(lambda x: ' '.join(x['text'].split(' ')[:d.cut_off]), axis=1)
        return data['text']

    from ogb.utils.url import download_url, extract_zip
    # Get Raw text path
    assert d.ogb_name in ['ogbn-arxiv', 'ogbn-papers100M']
    print(f'Loading raw text for {d.ogb_name}')
    raw_text_path = download_url(d.raw_text_url, d.data_root)
    print('d.hf_model', d.hf_model)
    tokenizer = AutoTokenizer.from_pretrained(d.hf_model)

    if d.hf_model in ['gpt2','gpt2-medium','gpt2-large','gpt2-xl']:
        print('Adding pad token')
        tokenizer.padding_side = 'left'
        tokenizer.pad_token = tokenizer.eos_token
        # tokenizer.add_special_tokens({'pad_token': '[PAD]'})
    token_info = {k: np.memmap(d.info[k].path, dtype=d.info[k].type, mode='w+', shape=d.info[k].shape)
                  for k in d.token_keys}
    categories, node_ids = read_ids_and_labels(d.data_root)
    for meta_data in tqdm(pd.read_table(raw_text_path, header=None, chunksize=chunk_size, skiprows=[0])):
        text = process_raw_text_df(meta_data, node_ids, categories)
        print(text.index, text)
        tokenized = tokenizer(text.tolist(), padding='max_length', truncation=True, max_length=512,  return_token_type_ids=True).data
        for k in d.token_keys:
            token_info[k][text.index] = np.array(tokenized[k], dtype=d.info[k].type)
    uf.pickle_save('processed', d._processed_flag['token'])
    return
