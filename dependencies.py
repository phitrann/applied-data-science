#spacy
import spacy
from spacy.pipeline import EntityRuler
from spacy.lang.en import English
from spacy.tokens import Doc

#gensim
import gensim
from gensim import corpora

#Visualization
from spacy import displacy
import pyLDAvis.gensim_models
from wordcloud import WordCloud
import plotly.express as px
import matplotlib.pyplot as plt

#Data loading/ Data manipulation
import pandas as pd
import numpy as np
import jsonlines

#nltk
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
nltk.download(['stopwords','wordnet'])

#warning
import warnings 
warnings.filterwarnings('ignore')

from spacy.cli import download

download("en_core_web_lg")

import os
import textwrap
import torch
import chromadb
import langchain
import openai
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import TextLoader, UnstructuredPDFLoader, YoutubeLoader
from langchain.embeddings import HuggingFaceEmbeddings, OpenAIEmbeddings, HuggingFaceInstructEmbeddings
from langchain.indexes import VectorstoreIndexCreator
from langchain.llms import OpenAI, HuggingFacePipeline
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.prompts import PromptTemplate
from auto_gptq import AutoGPTQForCausalLM
from transformers import AutoTokenizer, pipeline, logging, TextStreamer
from langchain.document_loaders.image import UnstructuredImageLoader