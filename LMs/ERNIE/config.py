from lm_utils import *


class ERNIE(LMConfig):

    def __init__(self, args=None):
        super(ERNIE, self).__init__(args)
        self.model = 'ERNIE'
        self._post_init(args)

    para_prefix = {**LMConfig.para_prefix}
    args_to_parse = list(para_prefix.keys())
    meta_data = {
        'ERNIE':
            SN(
                hf_model='nghuyong/ernie-2.0-base-en',
                hidden_dim=768,
                max_bsz=SN(  # Batch size for different device
                    train={12: 8, 16: 12, 24: 16, 32:18},
                    inf={12: 150, 16: 200, 24: 300, 32: 200},
                ),
                prt_lm={  # Initial LM configs
                    'arxiv': SN(
                        model='FtV1',
                        cmd='--lr=2e-05 --eq_batch_size=48 --weight_decay=0.01 --dropout=0.1 --att_dropout=0.1 --cla_dropout=0.1 --cla_bias=T --epochs=4 --warmup_epochs=0.2 --eval_patience=30482',
                        max_n_gpus=4, ),
                    'products': SN(
                        model='FtV1',
                        cmd='--lr=2e-05 --eq_batch_size=192 --weight_decay=0.01 --dropout=0.1 --att_dropout=0.3 --cla_dropout=0.2 --cla_bias=T --warmup_epochs=0.2 --eval_patience=65308 --epochs=4 --label_smoothing_factor=0.1 --warmup_epochs=0.6',
                        max_n_gpus=8,
                    )
                },
            ),
    }

