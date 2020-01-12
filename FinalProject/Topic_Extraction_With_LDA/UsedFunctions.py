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



def preprocess_word(word):
    """ 
    Word preprocessing 
  
    This function will preprocess particular word 
  
    Parameters: 
    word: string
  
    Returns: 
    string: will return initial string input but preprocessed ,
            so from input string will delete all punctuation and repeated symbols.
    """
    
    
    # Remove punctuation
    word = ''.join(c for c in word if c not in punctuation)
    
    # Convert more than 2 letter repetitions to 2 letter
    # funnnnny --> funny
    word = re.sub(r'(.)\1+', r'\1\1', word)
    
    return word

def is_valid_word(word):
    """ 
    Word checking
  
    This function will check if word starts with alphabet 
  
    Parameters: 
    word: string
  
    Returns: 
    Boolean: Is valid or not , True means that word is valid
    """
    
    
    # Check if word begins with an alphabet
    return (re.search(r'^[a-zA-Z][a-z0-9A-Z\._]*$', word) is not None)

def handle_emojis(document):
    """ 
    Emoji classifier
  
    This function will replace emojis with EMO_POS or EMO_NEG , depending on its meaning 
  
    Parameters: 
    document: string
  
    Returns: 
    string: initial string input replaced emojis by their meaning, 
            for example :) will replaced with EMO_POS but ): will replaced with EMO_NEG
    """
    
    
    # Smile -- :), : ), :-), (:, ( :, (-:, :')
    document = re.sub(r'(:\s?\)|:-\)|\(\s?:|\(-:|:\'\))', ' EMO_POS ', document)
    
    # Laugh -- :D, : D, :-D, xD, x-D, XD, X-D
    document = re.sub(r'(:\s?D|:-D|x-?D|X-?D)', ' EMO_POS ', document)
    
    # Love -- <3, :*
    document = re.sub(r'(<3|:\*)', ' EMO_POS ', document)
    
    # Wink -- ;-), ;), ;-D, ;D, (;,  (-;
    document = re.sub(r'(;-?\)|;-?D|\(-?;)', ' EMO_POS ', document)
    
    # Sad -- :-(, : (, :(, ):, )-:
    document = re.sub(r'(:\s?\(|:-\(|\)\s?:|\)-:)', ' EMO_NEG ', document)
    
    # Cry -- :,(, :'(, :"(
    document = re.sub(r'(:,\(|:\'\(|:"\()', ' EMO_NEG ', document)
    
    return document

def preprocess_document(document, use_stemmer = False):
    """ 
    Text preprocessing
  
    This function will preprocess the input text 
  
    Parameters: 
    document: string (we can put the entire string row , for instance in our case I will pass conversation)
    use_stemmer: Boolean (If True I will use stemmer as well as all other processes)
  
    Returns: 
    string: processed input string
    """
    
    
    def lemmatize_stemming(text):
        return stemmer.stem(WordNetLemmatizer().lemmatize(text, pos='v'))

    processed_document = []
    
    # Convert to lower case
    document = document.lower()
    
    # Replaces URLs with the word URL
    document = re.sub(r'((www\.[\S]+)|(https?://[\S]+))', ' URL ', document)
    
    # Replace @handle with the word USER_MENTION
    document = re.sub(r'@[\S]+', 'USER_MENTION', document)
    
    # Replaces #hashtag with hashtag
    document = re.sub(r'#(\S+)', r' \1 ', document)
    
    # Replace 2+ dots with space
    document = re.sub(r'\.{2,}', ' ', document)
    
    # Strip space, " and ' from document
    document = document.strip(' "\'')
    
    # Replace emojis with either EMO_POS or EMO_NEG
    document = handle_emojis(document)
    
    # Replace multiple spaces with a single space
    document = re.sub(r'\s+', ' ', document)
    words = document.split()

    for word in words:
        word = preprocess_word(word)
        if is_valid_word(word):
            if use_stemmer:
                word = lemmatize_stemming(word)
            if word not in gensim.parsing.preprocessing.STOPWORDS and len(word) > 3:
                processed_document.append(word)
            
    processed_internal_state = ' '.join(processed_document)
    
    processed_internal_state = re.sub(r'\b\w{1,3}\b', '', processed_internal_state)
    
    processed_internal_state = ' '.join(processed_internal_state.split())

    return processed_internal_state

def preprocess(preprocessed_document):
    """ 
    tokenize and combine already preprocessed document
  
    This function will tokenize document and will combine document such a way ,
    that we can containing the number of times a word appears in the training set 
    using gensim.corpora.Dictionary
  
    Parameters: 
    preprocessed_document: string (particular document obtained from preprocess_document function)
  
    Returns: 
    list: tokenized documents in approprite form
    """
    
    
    result=[]
    
    for token in gensim.utils.simple_preprocess(preprocessed_document) :
        result.append(token)
            
    return result
