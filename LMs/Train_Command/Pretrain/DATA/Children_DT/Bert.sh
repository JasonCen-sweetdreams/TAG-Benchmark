CUDA_VISIBLE_DEVICES=0,1 /usr/bin/env python sweep/dist_runner.py LMs/Train_Command/train_DPK.py --PrtMode=Deepwalk  --att_dropout=0.1 --cla_dropout=0.1 --dataset=Children_DT --dropout=0.1 --epochs=5 --eq_batch_size=180 --per_device_bsz=90 --grad_steps=1 --lr=5e-05 --model=Bert --warmup_epochs=1 --gpus=0,1 --cache_dir=/mnt/v-wzhuang/TAG/Prt/DeepWalk/Amazon/Children/Bert/Base/
CUDA_VISIBLE_DEVICES=0,1 /usr/bin/env python sweep/dist_runner.py LMs/Train_Command/train_DPK.py --PrtMode=Deepwalk  --att_dropout=0.1 --cla_dropout=0.1 --dataset=Children_DT --dropout=0.1 --epochs=5 --eq_batch_size=180 --per_device_bsz=90 --grad_steps=1 --lr=5e-05 --model=Deberta --warmup_epochs=1 --gpus=0,1 --cache_dir=/mnt/v-wzhuang/TAG/Prt/DeepWalk/Amazon/Children/Deberta/Base/
CUDA_VISIBLE_DEVICES=0,1 /usr/bin/env python sweep/dist_runner.py LMs/Train_Command/train_DPK.py --PrtMode=Deepwalk  --att_dropout=0.1 --cla_dropout=0.1 --dataset=Children_DT --dropout=0.1 --epochs=5 --eq_batch_size=180 --per_device_bsz=90 --grad_steps=1 --lr=5e-05 --model=RoBerta --warmup_epochs=1 --gpus=0,1 --cache_dir=/mnt/v-wzhuang/TAG/Prt/DeepWalk/Arxiv/Children/RoBerta/Base/
CUDA_VISIBLE_DEVICES=0,1 /usr/bin/env python sweep/dist_runner.py LMs/Train_Command/train_DPK.py --PrtMode=Deepwalk  --att_dropout=0.1 --cla_dropout=0.1 --dataset=Children_DT --dropout=0.1 --epochs=5 --eq_batch_size=180 --per_device_bsz=90 --grad_steps=1 --lr=5e-05 --model=Electra-base --warmup_epochs=1 --gpus=0,1 --cache_dir=/mnt/v-wzhuang/TAG/Prt/DeepWalk/Arxiv/Children/Electra/Base/