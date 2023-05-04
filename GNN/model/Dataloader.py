from ogb.nodeproppred import DglNodePropPredDataset
import dgl
import numpy as np

def split_graph(nodes_num, train_ratio, val_ratio):

    np.random.seed(42)
    indices = np.random.permutation(nodes_num)
    train_size = int(nodes_num * train_ratio)
    val_size = int(nodes_num * val_ratio)

    train_ids = indices[:train_size]
    val_ids = indices[train_size:train_size+val_size]
    test_ids = indices[train_size+val_size:]

    return train_ids, val_ids, test_ids

def load_data(name):
    if name == 'ogbn-arxiv':
        data = DglNodePropPredDataset(name=name)
        splitted_idx = data.get_idx_split()
        train_idx, val_idx, test_idx = (
            splitted_idx["train"],
            splitted_idx["valid"],
            splitted_idx["test"],
        )
        graph, labels = data[0]
    elif name == 'amazon-children':
        graph = dgl.load_graphs('/mnt/v-wzhuang/Amazon/Books/Amazon-Books-Children.pt')[0][0]
        labels = graph.ndata['label'].numpy()
        train_idx, val_idx, test_idx = split_graph(graph.num_nodes(), 0.6, 0.2)
    elif name == 'amazon-history':
        graph = dgl.load_graphs('/mnt/v-wzhuang/Amazon/Books/Amazon-Books-History.pt')[0][0]
        labels = graph.ndata['label'].numpy()
        train_idx, val_idx, test_idx = split_graph(graph.num_nodes(), 0.6, 0.2)
    else:
        raise ValueError('Not implemetned')
    return graph, labels, train_idx, val_idx, test_idx