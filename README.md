# torch-tacospawn

(Unofficial) PyTorch implementation of TacoSpawn, Speaker Generation, Stanton et al., 2021.

- Speaker Generation [[arXiv:2111.05095](https://arxiv.org/abs/2111.05095)]
- Unconditional VLB-TacoSpawn implementation.

## Requirements

Tested in python 3.7.9 ubuntu conda environment, [requirements.txt](./requirements.txt)

## Usage

Download LibriTTS dataset from [openslr](https://openslr.org/60/)

To train model, run [train.py](./train.py). 

```bash
python train.py --data-dir /datasets/LibriTTS/train-clean-360
```

To start to train from previous checkpoint, `--load-epoch` is available.

```bash
python train.py \
    --data-dir /datasets/LibriTTS/train-clean-360 \
    --load-epoch 20 \
    --config ./ckpt/t1.json
```

Checkpoint will be written on `TrainConfig.ckpt`, tensorboard summary on `TrainConfig.log`.

```bash
python train.py
tensorboard --logdir ./log
```

[WIP] inference and pretrained

## [WIP] Learning Curve

## [WIP] Samples
