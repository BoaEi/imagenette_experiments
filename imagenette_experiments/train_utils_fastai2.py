# AUTOGENERATED! DO NOT EDIT! File to edit: 02_train_utils_fastai2.ipynb (unless otherwise specified).

__all__ = ['get_dls', 'get_learn']

# Cell
from fastai2.vision.all import *
from model_constructor.net import *
from fastscript.core import Param

# Cell
# import math
# import torch
# from torch.optim.optimizer import Optimizer, required
# import itertools as it

# Cell
def get_dls(size=128, woof=1, bs=64, sh=0., workers=None):
#     if size<=224: path = URLs.IMAGEWOOF_320 if woof else URLs.IMAGENETTE_320
    if size<=224: path = URLs.IMAGEWOOF if woof else URLs.IMAGENETTE_320
    else        : path = URLs.IMAGEWOOF     if woof else URLs.IMAGENETTE
    source = untar_data(path)
    if workers is None: workers = min(8, num_cpus())
    batch_tfms = [Normalize.from_stats(*imagenet_stats)]
    if sh: batch_tfms.append(RandomErasing(p=0.3, max_count=3, sh=sh))
    dblock = DataBlock(blocks=(ImageBlock, CategoryBlock),
                       splitter=GrandparentSplitter(valid_name='val'),
                       get_items=get_image_files, get_y=parent_label,
                       item_tfms=[RandomResizedCrop(size, min_scale=0.35), FlipItem(0.5)],
                       batch_tfms=batch_tfms)
    return dblock.dataloaders(source, path=source, bs=bs, num_workers=workers)


# Cell
def get_learn(
    gpu:   Param("GPU to run on", int)=None,
    woof:  Param("Use imagewoof (otherwise imagenette)", int)=1,
#     lr:    Param("Learning rate", float)=1e-2,
    size:  Param("Size (px: 128,192,256)", int)=128,
    sqrmom:Param("sqr_mom", float)=0.99,
    mom:   Param("Momentum", float)=0.9,
    eps:   Param("epsilon", float)=1e-6,
    epochs:Param("Number of epochs", int)=5,
    bs:    Param("Batch size", int)=64,
    mixup: Param("Mixup", float)=0.,
    opt:   Param("Optimizer (adam,rms,sgd,ranger)", str)='ranger',
    model='xresnet50',
#     arch:  Param("Architecture", str)='xresnet50',
    sh:    Param("Random erase max proportion", float)=0.,
    sa:    Param("Self-attention", int)=0,
    sym:   Param("Symmetry for self-attention", int)=0,
    beta:  Param("SAdam softplus beta", float)=0.,
    act_fn:Param("Activation function", str)='Mish',
    fp16:  Param("Use mixed precision training", int)=0,
    pool:  Param("Pooling method", str)='AvgPool',
    dump:  Param("Print model; don't train", int)=0,
    runs:  Param("Number of times to repeat training", int)=1,
    meta:  Param("Metadata (ignored)", str)=''
):
    "Training of Imagenette."

    #gpu = setup_distrib(gpu)
    if gpu is not None: torch.cuda.set_device(gpu)
    if   opt=='adam'  : opt_func = partial(Adam, mom=mom, sqr_mom=sqrmom, eps=eps)
    elif opt=='rms'   : opt_func = partial(RMSprop, sqr_mom=sqrmom)
    elif opt=='sgd'   : opt_func = partial(SGD, mom=mom)
    elif opt=='ranger': opt_func = partial(ranger, mom=mom, sqr_mom=sqrmom, eps=eps, beta=beta)

    dls = get_dls(size, woof, bs, sh=sh)
#     if not gpu: print(f'epochs: {epochs}; lr: {lr}; size: {size}; sqrmom: {sqrmom}; mom: {mom}; eps: {eps}')
    if model=='xresnet50':
        m,act_fn,pool = [globals()[o] for o in ('xresnet50',act_fn,pool)]
        model = m(c_out=10, act_cls=act_fn, sa=sa, sym=sym, pool=pool)
    else: model = model()
    learn = Learner(dls, model, opt_func=opt_func, \
                metrics=[accuracy,top_k_accuracy], loss_func=LabelSmoothingCrossEntropy())
    if fp16: learn = learn.to_fp16()
#         cbs = MixUp(mixup) if mixup else []
    return learn
