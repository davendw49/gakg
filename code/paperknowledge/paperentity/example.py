raw_path = "."
dde_paper_json_path = os.path.join(raw_path,
                                   "dde_paper_v4.json")
dde_index_path = os.path.join(raw_path, "dde/db_dde_sim")
dde_corpus_query_path = os.path.join(raw_path, "db_dde_corpus_query.json")

print(dde_corpus_query_path)

dde_paper_dict, dde_index, dde_corpus_query = get_preload(dde_paper_json_path, dde_index_path, dde_corpus_query_path)

stopwords = []
with open('stopwords.txt', 'r') as f:
    words = f.read()
    stopwords = words.splitlines()

def paper_entity_extraction(
        pid: str = Query(..., description='paper id', example='413417819')
):
    paper_dict = dde_paper_dict
    index = dde_index
    corpus_query = dde_corpus_query
    paperkg_final = get_paperkg_final(paper_dict, index, corpus_query, pid, abs_w=0.2, title_w=0.3, mr_w=0.5,
                                      word_len_w=1.0, letter_len_w=0.01, complex_len_w=1.0)
    return paperkg_final