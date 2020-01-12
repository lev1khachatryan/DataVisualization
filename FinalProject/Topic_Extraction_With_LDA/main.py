'''
Loading numpy and pandas libraries
'''
import numpy as np
import pandas as pd


'''
Loading Gensim and nltk libraries
'''
import gensim
from gensim.utils import simple_preprocess
from gensim.parsing.preprocessing import STOPWORDS
from nltk.stem import WordNetLemmatizer, SnowballStemmer
# from nltk.stem.porter import * 
# from nltk.stem.porter import PorterStemmer


'''
Load english wards from nltk , and english stemmers
'''
import nltk
nltk.download('wordnet')
nltk.download('words')
words = set(nltk.corpus.words.words())
stemmer = SnowballStemmer("english")


'''
Load Regular expressions
'''
import re


'''
Load operator package, this will be used in dictionary sort
'''
import operator


'''
fix random state
'''
np.random.seed(42)


'''
Suppress warnings
'''
import warnings
warnings.filterwarnings("ignore")


'''
Load punctuation for data preprocesing
'''
from string import punctuation


'''
Word cloud implementation
'''
from PIL import Image
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
from matplotlib import pyplot as plt

'''
Import packages for parameter pass through command line
'''
from UsedFunctions import *
import sys, getopt



# start_date = '20190407'
# end_date   = '20190507'
# number_of_topics = 7




def main(argv):

    start_date = argv[0]
    end_date   = argv[1]
    number_of_topics = int(argv[2])


    '''
    Load data from csv file, which is in the same folder
    '''
    data = pd.read_csv('***.csv')


    '''
    Delete messages created by ***
    '''
    data = data[data.u_id != 1]


    '''
    Correct the Date column format
    '''
    data.date = data.date.str.slice(0, 10)
    data['date'] = pd.to_datetime(data['date'], format='%Y-%m-%d')


    '''
    Choose only same part from data, in this example I Chose the messages created on last month
    '''
    data = data.loc[data.date >= start_date & data.date >= start_date]


    '''
    Delete messages containing no more than 3 characters
    '''
    data = data[data.text.str.len() > 3]

    
    '''
    Group messages to appropriate conversations which we will consider as documents
    '''
    conversation = data.groupby('c_id')['text'].apply(lambda x: "%s" % ', '.join(x))
    documents = conversation.to_frame(name=None)
    
    '''
    Create a list from 'documents' DataFrame and call it 'processed_docs'
    '''

    processed_docs = []

    for doc in documents.values:
        processed_docs.append(preprocess(preprocess_document(doc[0])))
        
    '''
    Create a dictionary from 'processed_docs' containing the number of times a word appears 
    in the data set using gensim.corpora.Dictionary and call it 'dictionary'
    '''

    dictionary = gensim.corpora.Dictionary(processed_docs)
    
    '''
    OPTIONAL STEP
    Remove very rare and very common words:

    - words appearing less than 15 times
    - words appearing in more than 10% of all documents
    '''

    dictionary.filter_extremes(no_below=15, no_above=0.1, keep_n= 100000)
    

    '''
    Create the Bag-of-words model for each document i.e for each document we create a dictionary reporting how many
    words and how many times those words appear. Save this to 'bow_corpus'
    '''

    bow_corpus = [dictionary.doc2bow(doc) for doc in processed_docs]
    
    # LDA mono-core -- fallback code in case LdaMulticore throws an error on your machine
    # lda_model = gensim.models.LdaModel(bow_corpus, 
    #                                    num_topics = 10, 
    #                                    id2word = dictionary,                                    
    #                                    passes = 50)

    # LDA multicore 
    '''
    Train your lda model using gensim.models.LdaMulticore and save it to 'lda_model'
    '''

    lda_model =  gensim.models.LdaMulticore(bow_corpus, 
                                       num_topics = number_of_topics, 
                                       id2word = dictionary,                                    
                                       passes = 10,
                                       workers = 2)
    '''
    Create (num_of_conv x num_of_topic) matrix with all 0 values and call it conversation_topic
    '''

    conversation_topic = np.zeros(shape=(len(bow_corpus), number_of_topics), dtype=float)

    '''
    Fill appropriate probability of conversation i to belong topic j to conversation_topic matrix
    '''

    for i in range(len(bow_corpus)):
        prob = lda_model.get_document_topics(bow_corpus[i], per_word_topics = False)
        for k in range(len(prob)):
            conversation_topic[i, prob[k][0]] = prob[k][1]
    
    '''
    Calculate summed probabilities of each topic and call it prob_dict
    '''

    prob_dict = dict()
    for i in range(number_of_topics):
        prob_dict[i] = round(conversation_topic.sum(axis = 0)[i] / len(bow_corpus), 2)
    
    '''
    Sort prob_dict dictionary t find the most probable topic over all conversation dataset
    '''

    sorted_prob = sorted(prob_dict.items(), key=operator.itemgetter(1))

    file1 = open("Report/report.txt","w")
    file1.write("Appropriate probabilities: \n\n")
    file1.writelines(str(sorted_prob) + '\n\n\n') 
    file1.close()

    
    '''
    For each topic, we will explore the words occuring in that topic and its relative weight
    '''

    txt = ''
    for idx, topic in lda_model.print_topics(-1):
        txt += ("Topic: {} \nWords: {}\n\n".format(idx, topic ))
        
    file1 = open("Report/report.txt","a")
    file1.write("Obtained Topics: \n\n")
    file1.writelines(txt) 
    file1.close()

    '''
    Combine all preprocessed conversations to one string and call it word_cloud_messenger
    '''

    word_cloud_messenger = []

    for doc in processed_docs:
        s = " "
        word_cloud_messenger.append(s.join( doc ))

    s = " "

    word_cloud_messenger = s.join( word_cloud_messenger )
    

    '''
    Generate Picture of words, so called word cloud
    '''

    # Create stopword list:
    stopwords = set()
    stopwords.update(["doritos", "doritosdoritos", "chirp", "chirpchirp", "mexico"])

    # Generate a word cloud image
    wordcloud = WordCloud(stopwords=stopwords, 
                          background_color="white",
                          width = 800, 
                          height = 800, 
                          min_font_size = 10).generate(word_cloud_messenger)

    # Save the image in the img folder:
    wordcloud.to_file("Report/word-cloud.png")

if __name__ == "__main__":
   main(sys.argv[1:])