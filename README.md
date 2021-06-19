<div style="text-align:center">
<img src="https://big-cheng.com/gakg/logo.png" alt="gakg-logo" width="600"/>
<h2>GAKG: A Multimodal Geoscience Academic Knowledge Graph 😈</h2>
</div>

# Overview

GAKG is a multimodal Geoscience Academic Knowledge Graph (GAKG) framework by fusing papers' illustrations, text, and bibliometric data. To our knowledge, GAKG is currently the largest and most comprehensive geoscience academic knowledge graph, consisting more than 68 million triples. Figure 1 shows the overview of GAKG. And if you want to explore the entire GAKG, view [https://gakg.acemap.info](https://gakg.acemap.info).

<div style="text-align:center">
<img src="https://big-cheng.com/gakg/overview.png" alt="gakg-logo" width="800"/>
<h6>Figure 1. Overview of Multimodal GeoScience Academic Knowledge Graph (GAKG) </h6>
</div>

In order to better serve the data mining and knowledge discovery communities, GAKG preserves several datasets and GAKG-oriented resources.

|No.|Resource Name|Resource Type|Link|
|:-:|:-:|:-:|:-:|
|1|GAKG Datasets|data dump|[https://gakg.acemap.info/download](https://gakg.acemap.info/download)|
|2|GA16K|Knowledge Representation Benchmark|[info](#krl), `/benchmarks/GA16K/`|
|3|GPCN|Geoscience Papers Citation Network|[info](#sn), [ftp](https://dataset.acemap.info/gakg/gpcn.tar.gz)|
|4|GACN|Geoscience Authors Cooperation Network|[info](#sn), [ftp](https://dataset.acemap.info/gakg/gacn.tar.gz)|
|5|GAKG SPARQL Endpoint|Query Endpoint|[GAKG Snorql](https://snorql.acemap.cn/)|
|6|Pipeline Supplements|models and codes|[Google Drive]()|


<h2 id="sn">Community Detection</h2>

-  Statistics

|dataset|node|edge|num. lcc|clustering|triangle|daglongest|
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
|GPCN|842,121|16,034,510|1,450|0.0699|38,789,469|176|
|GPCN-lwcc|838,219|16,031,892|1|0.0701|38,789,345|176|
|GACN|860,280|5,381,861|32,609|0.690|43,502,542|15|
|GACN-lc|752,718|5,231,507|1|0.700|43,332,307|15|

- Baselines

|Baseline|Source Code|Paper|
|:-:|:-:|:-:|
|Louvain|https://sites.google.com/site/findcommunities/|Fast unfolding of communities in large networks [1]|
|Map Equation|https://www.mapequation.org/code.html|Maps of random walks on complex networks reveal community structure [2]|
|LPA|https://github.com/zhuo931077127/LPA-algorithm-Demo|Near linear time algorithm to detect community structures in large-scale networks [3]|

The entire benchmarks also can be accessed from [google drive](https://drive.google.com/drive/folders/1Bfx7StqMXwEeDaH9GqSyWKe32iaP0ked?usp=sharing) 

<h2 id="krl">Knowledge Representation Learning</h2>

-  Statistics

|Benchmark|Entities Type|Relations TypeS|Triples|
|:-:|:-:|:-:|:-:|
|GA16K|10|16,363|151,662|
|WN18|18|40,943|141,442|
|FB15K|1,345|14,951|483,142|

- Baselines

|Baseline|Source Code|Paper|
|:-:|:-:|:-:|
|RESCAL|https://github.com/mnick/rescal.py|A Three-Way Model for Collective Learning on Multi-Relational Data [4]|
|TransE|https://github.com/zqhead/TransE|Translating Embeddings for Modeling Multi-relational Data [5]|
|TransH|https://github.com/zqhead/TransH|Knowledge Graph Embedding by Translating on Hyperplanes [6]|
|SimplE|https://github.com/baharefatemi/SimplE|SimplE Embedding for Link Prediction in Knowledge Graphs [7]|
|RotatE|https://github.com/DeepGraphLearning/KnowledgeGraphEmbedding|RotatE: Knowledge Graph Embedding by Relational Rotation in Complex Space [8]|

<h2 id="pkg">Paper Knowledge Extraction</h2>

The pipeline of Paper Knowledge Extraction is in folder `/code/paperknowledge/`

- BERT-based QA (`/code/paperknowledge/bertQA`)

    - run single QA, with parameters: *train_batch_size，learning_rate*
    ```bash
    python run_squad.py --do_predict
    ```

    - run batch QA, with parameters: *start file, end file, and year*
    ```bash
    CUDA_VISIBLE_DEVICES=1 python run_test.py 116 125 2015
    ```

    - `/code/paperknowledeg/bertQA/model` can be download via [google drive](https://drive.google.com/drive/folders/1Map0STLr3ScCtqRJTawg_Vlu6xXzt17U?usp=sharing)

- Paper Knowledge Entities Extraction (`/code/paperknowledge/paperentity`)

    - run
    ```bash
    python example.py
    ```

    - `/code/paperknowledge/paperentity/dde` and related files can be download via [google drive](https://drive.google.com/drive/folders/1L9_CJtmvrzfaYIcpzyuGf4-2Wzu274jn?usp=sharing)

## Citation

We now have a [paper](#) under review on CIKM-Resource Track:
```bibtex
@inproceedings{GAKG,
    title = "GAKG: A Multimodal Geoscience Academic Knowledge Graph",
    author = "Cheng Deng, Yuting Jia, Chong Zhang, Jingyao Tang, Hui Xu, Luoyi Fu, Weinan Zhang, Haisong Zhang, Xinbing Wang, Chenghu Zhou",
}
```

## To-do

- [ ] ***Coming soon:*** Python Package gakg

[1]: https://iopscience.iop.org/article/10.1088/1742-5468/2008/10/P10008/meta
[2]: https://www.pnas.org/content/105/4/1118/
[3]: https://journals.aps.org/pre/abstract/10.1103/PhysRevE.76.036106

[4]: https://icml.cc/2011/papers/438_icmlpaper.pdf
[5]: https://papers.nips.cc/paper/2013/file/1cecc7a77928ca8133fa24680a88d2f9-Paper.pdf
[6]: https://persagen.com/files/misc/wang2014knowledge.pdf
[7]: https://arxiv.org/pdf/1802.04868.pdf
[8]: https://arxiv.org/pdf/1902.10197.pdf

