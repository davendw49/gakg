import elasticsearch
import elasticsearch.helpers
import ujson
from tqdm import tqdm
import time
from nltk.corpus import stopwords
import numpy as np
import string
from nltk.stem.lancaster import LancasterStemmer
from gensim import similarities


def load_data(paper_json_path):
    print(paper_json_path)
    f1 = open(paper_json_path, "r")
    paper_dict = ujson.load(f1)
    f1.close()
    return paper_dict


def get_stop_words(lang):
    """
    get stopwords
    """
    stop_words = set(stopwords.words(lang))
    return stop_words


def get_es_conn(hosts):
    """
    connection to the elasticsearch cluster
    """
    es = elasticsearch.Elasticsearch(hosts)
    return es


def query_abs_over_wiki(abstract):
    """
    query from es with the document is wiki_entity
    """
    return {
        "track_total_hits": "true",
        "version": "true",
        "size": 1000,
        "sort": [{
            "_score": {
                "order": "desc"
            }
        }],
        "_source": {

            "includes": [
                "entity",
                "stem",
                "description"
            ]
        },
        "stored_fields": [
            "*"
        ],
        "script_fields": {},
        "docvalue_fields": [],
        "query": {
            "match": {
                "entity": abstract
            }
        },
        "highlight": {
            "pre_tags": [
                "@@"
            ],
            "post_tags": [
                "@@"
            ],
            "fields": {
                "*": {}
            },
            "fragment_size": 2147483647
        }
    }


def useless_detect(entity):
    """
    detect useless entity
    """
    fh = "~!@#$%^&*()_+-*/<>,.[]\/ "
    sz = "0123456789"
    flag = 0
    for e in entity:
        if e in fh or e in sz:
            flag += 1
    if flag == len(entity):
        return True
    else:
        return False


def check_entity_in_qa(a, b):
    """
    detect the word after stemming wether appearing continious
    """
    for i in range(len(b) - len(a) + 1):
        flag = True
        if b[i] == a[0]:
            for j in range(len(a) - 1):
                if b[i + j + 1] != a[j + 1]:
                    flag = False
            if not flag:
                continue
            return i + 1
    return False


def checkfully(entity, st_qa, stop_words):  # entity=>hit["_source"]["stem"]
    """
    check if the entity is the full highlight and meaningful entity
    """
    st_entity = entity.split(' ')
    pos = check_entity_in_qa(st_entity, st_qa)  # pos is the first list index of the matched word +1
    if not pos:
        return False
    elif entity not in stop_words:
        if useless_detect(entity):
            return False
        else:
            return pos
    else:
        return False


def get_entity_position(source, qa, st_qa, pid_abs, pos):  # entity-->hit["_source"]
    """
    get entity position
    """
    qaInAbs_pos = pid_abs.find(qa)
    enInQa_pos = 0
    qa = qa.split(' ')
    for i in range(len(qa)):
        if i < pos - 1:
            enInQa_pos += len(qa[i])
    entity_len = 0
    entity_name_in_qa = qa[pos - 1:pos - 1 + len(source['entity'].split(' '))]
    for j in range(len(entity_name_in_qa)):
        entity_len += len(entity_name_in_qa[j])
    return qaInAbs_pos + enInQa_pos + pos - 1, qaInAbs_pos + enInQa_pos + pos - 1 + entity_len + len(
        entity_name_in_qa) - 1


def e_distance(v1, v2):
    return np.sqrt(np.sum(np.square(v1 - v2)))


def sim(p, Qid, index, corpus_query):
    p_index = corpus_query[str(p)]
    Q_index = corpus_query[str(Qid)]
    sim_score = (index.vector_by_id(p_index)).multiply(index.vector_by_id(Q_index)).sum()  # 点乘计算相似度
    return float(sim_score)


def get_score_paper_entityDescription_and_entityLength(pid, mr_key, entity_Qlist, index, corpus_query):
    abs_Q_score = []
    title_Q_score = []
    mr_Q_score = []
    en_word_len = []
    en_letter_len = []
    complex_len = []
    for entity in entity_Qlist:
        Q = entity[0]
        abs_Q_score.append(sim((pid, 'abstract'), Q, index, corpus_query))
        title_Q_score.append(sim((pid, 'title'), Q, index, corpus_query))
        mr_Q_score.append(sim((pid, mr_key), Q, index, corpus_query))
        en_letter_len.append(len(entity[1]))
        en_word_len.append(len(entity[1].split(' ')))
        complex_num = 0
        for e in entity[1]:
            if e not in string.ascii_letters:
                complex_num += 1
        complex_len.append(complex_num)
    return abs_Q_score, title_Q_score, mr_Q_score, en_word_len, en_letter_len, complex_len


def print_paperkg_top3(paperkg_v2, paper_dict):
    paperkg_final = {}
    p = list(paperkg_v2.keys())[0]
    paperkg_final[p] = {}
    paperkg_final[p]['abstract'] = paper_dict[p]['abstract']
    paperkg_final[p]['title'] = paper_dict[p]['title']
    if "author" not in list(paper_dict[p].keys()):
        paperkg_final[p]['author'] = ""
    else:
        paperkg_final[p]['author'] = paper_dict[p]['author']
    for q in paperkg_v2[p].keys():
        paperkg_final[p][q] = []
        for index in range(0, len(paperkg_v2[p][q])):
            if index >= 3:
                break
            paperkg_final[p][q].append(paperkg_v2[p][q][index])

    return paperkg_final


def api_paperkg(paperkg_v2, paper_dict):
    """
    :param paperkg_v2:
    :param paper_dict:
    :return: api required format dict
    """
    results = {}
    p = list(paperkg_v2.keys())[0]

    results['paper_id'] = p
    results['abstract'] = paper_dict[p]['abstract']
    results['title'] = paper_dict[p]['title']

    if "author" not in list(paper_dict[p].keys()):
        pa = ""
    else:
        pa = paper_dict[p]['author']

    results['author'] = []
    for a in pa:
        tmp = {
            'name': a[0],
            'affiliation': a[1]
        }
        results['author'].append(tmp)

    results['kg'] = []

    for q in paperkg_v2[p].keys():
        onetail = []
        for index in range(0, len(paperkg_v2[p][q])):
            if index >= 3:
                break
            tmp_tuple = (paperkg_v2[p][q][index])
            tmp_dict = {
                'id': tmp_tuple[0][0],
                'score': tmp_tuple[1],
                'entity': tmp_tuple[0][1],
                'description': tmp_tuple[0][4],
                'spanh': int(tmp_tuple[0][2]),
                'spant': int(tmp_tuple[0][3])
            }
            onetail.append(tmp_dict)

        tmp = {
            'rel': q,
            'tail': onetail
        }
        results['kg'].append(tmp)

    return results


def paperkg_init(es, paper_dict, pid, stop_words, mode="standary"):
    """
    query the paperkg_full
    """
    paperkg = {}
    mr = paper_dict[pid]
    paperkg[pid] = {}
    filter_list = []
    if mode == "parallel":
        pass
    else:
        for q in list(mr.keys())[:-3]:  # [:-2]
            if mr[q] in filter_list:
                continue
            filter_list.append(mr[q])
            tmp_res = es.search(index='dbacestem', body=query_abs_over_wiki(mr[q]), request_timeout=600)["hits"]["hits"]
            print("-", q, len(tmp_res))
            st = LancasterStemmer()
            st_qa = []
            for word in mr[q].split(' '):
                st_qa.append(st.stem(word.replace('.', '').replace(',', '').replace('?', '').replace('!', '')))
            entity_filter = []
            for hit in tqdm(tmp_res):
                if hit["_id"] in entity_filter:
                    continue
                pos = checkfully(hit["_source"]["stem"], st_qa, stop_words)
                if pos:
                    pid_abs = paper_dict[pid]['abstract']
                    start_pos, end_pos = get_entity_position(hit["_source"], mr[q], st_qa, pid_abs, pos)
                    if q not in paperkg[pid].keys():
                        paperkg[pid][q] = []
                        paperkg[pid][q].append(
                            (hit["_id"], hit["_source"]["entity"], start_pos, end_pos, hit["_source"]["description"]))
                        entity_filter.append(hit["_id"])
                    else:
                        paperkg[pid][q].append(
                            (hit["_id"], hit["_source"]["entity"], start_pos, end_pos, hit["_source"]["description"]))
                        entity_filter.append(hit["_id"])
    return paperkg


def paperkg_manu(paperkg_v1, index, corpus_query, stop_words, abs_w, title_w, mr_w, word_len_w, letter_len_w,
                 complex_len_w):
    """
    order the paperkg entity
    """
    paperkg_score = {}
    pid = list(paperkg_v1.keys())[0]
    paperkg_score[pid] = {}
    mr_dict = paperkg_v1[pid]
    for mr_key, entity_Qlist in mr_dict.items():
        # print(mr_key)
        abs_Q_score, title_Q_score, mr_Q_score, en_word_len, en_letter_len, complex_len = get_score_paper_entityDescription_and_entityLength(
            pid, mr_key, entity_Qlist, index, corpus_query)
        final_score = list(map(
            lambda x: x[0] * abs_w + x[1] * title_w + x[2] * mr_w + x[3] * word_len_w + x[4] * letter_len_w + x[
                5] * complex_len_w,
            zip(abs_Q_score, title_Q_score, mr_Q_score, en_word_len, en_letter_len, complex_len)))
        final_score_entity = []
        for i, entity in enumerate(entity_Qlist):
            entity_name = entity[1]
            if abs_Q_score[i] == 0 or mr_Q_score[i] < 0.1:
                final_score[i] = 0
            final_score_entity.append((entity, final_score[i], abs_Q_score[i], title_Q_score[i], mr_Q_score[i],
                                       en_word_len[i], en_letter_len[i], complex_len[i]))
        paperkg_score[pid][mr_key] = sorted(final_score_entity, key=lambda s: s[1], reverse=True)  # 按分数排序
    return paperkg_score


def get_paperkg_final(paper_dict, index, corpus_query, pid, abs_w, title_w, mr_w, word_len_w, letter_len_w,
                      complex_len_w, x=0):
    """
    output the final paperkg
    """
    eshosts = ['10.10.10.10:9201']
    paperkg_final = {}
    if "('{}', '{}')".format(pid, 'title') in list(corpus_query.keys()):
        # try:
        paperkg_v1 = paperkg_init(get_es_conn(eshosts), paper_dict, pid, get_stop_words("english"))
        paperkg_v2 = paperkg_manu(paperkg_v1, index, corpus_query, get_stop_words("english"), abs_w, title_w, mr_w,
                                  word_len_w, letter_len_w, complex_len_w)
        paperkg_final = api_paperkg(paperkg_v2, paper_dict)
        # except:
        print(pid)
    else:
        print("('{}', '{}')".format(pid, 'title') + ' not in corpus!')
    return paperkg_final


def get_preload(paper_json_path, index_path, corpus_query_path):
    print('loading data!')
    start_time = time.perf_counter()
    paper_dict = load_data(paper_json_path)
    end_time = time.perf_counter()
    print('loaded paper_dict costs ' + str(end_time - start_time) + 's!')
    start_time = time.perf_counter()
    index = similarities.Similarity.load(index_path)
    with open(corpus_query_path, 'r', encoding='utf8') as fin:
        corpus_query = ujson.load(fin)
    end_time = time.perf_counter()
    print('loaded index,corpus_query costs ' + str(end_time - start_time) + 's!')
    return paper_dict, index, corpus_query
