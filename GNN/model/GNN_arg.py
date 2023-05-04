import argparse

def args_init():
    argparser = argparse.ArgumentParser(
        "GNN(GCN,GIN,GraphSAGE,GAT) on OGBN-Arxiv/Amazon-Books/and so on. Node Classification tasks",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    argparser.add_argument(
        "--cpu",
        action="store_true",
        help="CPU mode. This option overrides --gpu.",
    )
    argparser.add_argument("--gpu", type=int, default=0, help="GPU device ID.")
    argparser.add_argument(
        "--n-runs", type=int, default=10, help="running times"
    )
    argparser.add_argument(
        "--n-epochs", type=int, default=1000, help="number of epochs"
    )
    argparser.add_argument(
        "--lr", type=float, default=0.005, help="learning rate"
    )
    argparser.add_argument(
        "--n-layers", type=int, default=3, help="number of layers"
    )
    argparser.add_argument(
        "--num-mlp-layers", type=int, default=2, help="number of mlp layers"
    )
    argparser.add_argument(
        "--n-hidden", type=int, default=256, help="number of hidden units"
    )
    argparser.add_argument(
        "--input-drop", type=float, default=0.1, help="input drop rate"
    )
    argparser.add_argument(
        "--learning-eps", type=bool, default=True, help="If True, learn epsilon to distinguish center nodes from neighbors;"
                                                        "If False, aggregate neighbors and center nodes altogether."
    )
    argparser.add_argument(
        "--neighbor-pooling-type", type=str, default='mean', help="how to aggregate neighbors (sum, mean, or max)"
    )
    argparser.add_argument("--wd", type=float, default=0, help="weight decay")
    argparser.add_argument(
        "--log-every", type=int, default=20, help="log every LOG_EVERY epochs"
    )
    argparser.add_argument(
        "--use_PLM", type=str, default=None, help="Use LM embedding as feature"
    )
    argparser.add_argument(
        "--model_name", type=str, default='GCN', help="Which GNN be implemented"
    )
    argparser.add_argument(
        "--data_name", type=str, default='ogbn-arxiv', help="The datasets to be implemented."
    )
    return argparser