import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
plt.style.use('ggplot')
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import NMF, LatentDirichletAllocation, TruncatedSVD
from sklearn.feature_extraction import text
from sklearn.manifold import TSNE
from mpl_toolkits.mplot3d import Axes3D
from time import time
import pickle


def topic_extraction(df, col_name):
    """
    Two algorithms for topic extraction -
    NMF and LatentDirichletAllocation(LDA).
    Need to tie in with K-means clustering

    input - dataframe, column name of data to be analyzed
    output - new dataframe, nmf labels, lda labels, tfidf, and tf arrays
    """
    rec_stop = (
        ['cup', 'cups', 'tablespoon', 'tablespoons', 'teaspoon', 'teaspoons',
         'pounds', 'ounces', 'grams', 'gram', 'kilograms', 'kilogram', 'liter',
         'liters', 'sliced', 'diced', 'minced', 'finely', 'coarsely',
         'roughly', 'cut', 'peeled', 'chopped']
       )
    my_stop_words = text.ENGLISH_STOP_WORDS.union(rec_stop)
    tfidf_vectorizer = TfidfVectorizer(max_df=0.95, min_df=2,
                                       max_features=200,
                                       analyzer='word',
                                       stop_words=my_stop_words)
    tfidf = tfidf_vectorizer.fit_transform(df[col_name])
    tf_vectorizer = CountVectorizer(max_df=0.95, min_df=2,
                                    max_features=200,
                                    stop_words=my_stop_words)
    tf = tf_vectorizer.fit_transform(df[col_name])

    nmf = NMF(n_components=6, random_state=1,
            alpha=.1, l1_ratio=.5)
    tfidf_feature_names = tfidf_vectorizer.get_feature_names()
    nmf_w = nmf.fit_transform(tfidf)
    nmf_h = nmf.components_
    labels = nmf_w.argmax(axis=1)
    df['labels2'] = labels # this was the right code to get labels/clusters
    print("\nTopics in NMF model:")
    print_top_words('nmf', nmf, tfidf_feature_names)
    """uncomment to LDA topics"""
    lda = LatentDirichletAllocation(n_components=6, max_iter=5,
                                learning_method='online',
                                learning_offset=50.,
                                random_state=0,
                                n_jobs=-1)
    mod = lda.fit(tf)
    comp = mod.fit_transform(tf)
    lda_labels = comp.argmax(axis=1)
    df['lda_topics2'] = lda_labels
    print("\nTopics in LDA model:")
    tf_feature_names = tf_vectorizer.get_feature_names()
    print_top_words( 'lda', lda, tf_feature_names)
    return df, labels, lda_labels, tfidf, tf


def print_top_words(model_name, model, feature_names, n_top_words=20):
    filepath = 'data/{}_topics.pkl'.format(model_name)
    topic_dict = {}
    for topic_idx, topic in enumerate(model.components_):
        print("Topic #{}:".format(topic_idx))
        print(" ".join([feature_names[i]
                        for i in topic.argsort()[:-n_top_words - 1:-1]]))
        topic_dict[topic_idx] = " ".join([feature_names[i]
                        for i in topic.argsort()[:-n_top_words - 1:-1]])
    # with open(filepath, 'wb') as f:
    #     pickle.dump(topic_dict, f, pickle.HIGHEST_PROTOCOL)
    print('End')


def clustering_algorithm(tfidf, labels):
    """
    t-SNE dimensionality reduction of either tfidf or tf for plotting purposes
    input - matrix (tfidf or tf)
    output - x, y, z coordinates
    """
    svd = TruncatedSVD(algorithm='randomized', random_state=42)
    X_new = svd.fit_transform(tfidf)
    tsne_mod = TSNE(n_components=3, verbose=1, random_state=0, perplexity=40)
    coords = tsne_mod.fit_transform(X_new)
    x, y, z = coords[:, 0], coords[:, 1], coords[:, 2]
    return x, y, z


def plotting(x, y, z, labels, cluster_type):

    """
    NMF or LDA labels used to identify points in scatter
    plot of t-SNE analysis of recipe text
    """
    fig = plt.figure(figsize=(15, 15))
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(x, y, z, zdir='z', c=labels, s=20, cmap='Dark2', alpha=0.4)
    title = 'TSNE of Recipe Ingredients - {} labels(6)'.format(cluster_type)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.grid(False)
    plt.show()
    # plt.savefig('data/title_tsne.png')

if __name__ == '__main__':
    df = pd.read_csv('data/food52_scraped_data.csv')
    df.dropna(inplace=True)
    df, labels, lda_labels, tfidf, tf = topic_extraction(df, 'recipe')
    x, y, z = clustering_algorithm(tfidf, labels)
    plotting(x, y, z, labels, 'NMF')
    # x2, y2, z2 = clustering_algorithm(tf, lda_labels)
    # plotting(x2, y2, z2, lda_labels, 'Latent Dirichlet Allocation')
