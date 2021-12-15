from nltk.corpus import stopwords
from nltk.cluster.util import cosine_distance
import numpy as np
import networkx as nx

class Summer:
    def __init__(self, article):
        self.article = article

    def _process_sentences(self, article):
        sentences = []

        for sentence in article:
            sentences.append(sentence.replace("[^a-zA-Z]", " ").split(" "))
        
        return sentences

    def _sentence_similarity(self, a, b, stop_words=None):
        if stop_words is None:
            stop_words = []

        a = [w.lower() for w in a]
        b = [w.lower() for w in b]

        all_words = list(set(a + b))

        v1 = [0] * len(all_words)
        v2 = [0] * len(all_words)

        for w in a:
            if w in stop_words:
                continue
            v1[all_words.index(w)] += 1

        for w in b:
            if w in stop_words:
                continue
            v2[all_words.index(w)] += 1

        return 1 - cosine_distance(v1, v2)
    
    def _build_similarity_matrix(self, sentences, stop_words):
        similarity_matrix = np.zeros((len(sentences), len(sentences)))

        for i in range(len(sentences)):
            for j in range(len(sentences)):
                if i == j: # Case same sentence
                    continue
                similarity_matrix[i][j] = \
                    self._sentence_similarity(sentences[i], sentences[j], stop_words)

        return similarity_matrix
    
    def generate_summary(self, top_n=5):
        stop_words = stopwords.words('english')
        summary = []

        article = self._process_sentences(self.article)

        similarity_matrix = self._build_similarity_matrix(article, stop_words)
        similarity_graph = nx.from_numpy_array(similarity_matrix)

        scores = nx.pagerank(similarity_graph)

        ranked_sentences = sorted([(scores[i], s) for i, s in enumerate(article)], reverse=True)

        for i in range(top_n):
            summary.append(" ".join(ranked_sentences[i][1]))

        return " ".join(summary)
