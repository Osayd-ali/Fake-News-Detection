# """FakeNewsDetection.ipynb

# Automatically generated by Colaboratory.

# Original file is located at
#     https://colab.research.google.com/drive/1u7zzR4n6i6cKsRJaIf84EYwToUjoTSk9

# Library imports
# """

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import nltk
import re
#from wordcloud import WordCloud

from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding,Dense,LSTM,Conv1D,MaxPool1D
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report,accuracy_score

#"""Exploring Fake Data

#"""

fake=pd.read_csv('https://raw.githubusercontent.com/laxmimerit/fake-real-news-dataset/main/data/Fake.csv')

fake['subject'].value_counts()

text=' '.join(fake['text'].tolist())

# plt.figure(figsize=(10,6))
# sns.countplot(x='subject',data=fake)
# plt.show()

#"""Word Cloud"""

#wordcloud =WordCloud().generate(text)
#plt.figure(figsize=(10,10))
#plt.imshow(wordcloud)
#plt.axis('off')
#plt.tight_layout(pad=0)

#wordcloud =WordCloud().generate(text)
#plt.figure(figsize=(10,10))
#plt.imshow(wordcloud)
#plt.axis('off')
#plt.tight_layout(pad=0)
#plt.show()

#"""Exploring Real news"""

real=pd.read_csv('https://raw.githubusercontent.com/laxmimerit/fake-real-news-dataset/main/data/True.csv')

# real.columns

# real['text'][0]

# real['subject'].value_counts()

text=' '.join(real['text'].tolist())

# """# Differences in text 

# Real news seems to have source of publication which is not present in fake news
# looking at the data:

# *   most of text contains reuter info such as "WASHINGTON (Reuters)".
# *   Some text are tweets from twitter.
# *   Few text do not contain any publication info.

# # Cleaning Data
# Removing reueters or Twitter tweet info from the text.


# * Text can be splitted only once at "-" which is always present after mentioning source of publication,this gives us publisher part and text part.
# * If we do not get text part,this means publication details were not given for that record.
# * The twitter tweets always have same source,a long text of max 259 characters.
# """

real=real.drop(8970,axis=0)

# real['text'][0]

unknown_publishers=[]
temp=[]
for index,row in enumerate(real.text.values):
  try:
    record=row.split('-',maxsplit=1)
    temp.append(record[1])
    assert(len(record[0])<120)
  except:
    unknown_publishers.append(index)

# print(temp[0])

# real['text'][0]

#len(unknown_publishers)
#real.iloc[unknown_publishers].text

publisher=[]
tmp_text=[]
text2=[]
for index,row in enumerate(real.text.values):
  if index in unknown_publishers:
    #print(row)
    tmp_text.append(row)
    text2.append(row)
    publisher.append('Unknown')
  else:
    record=row.split('-',maxsplit=1)
    publisher.append(record[0].strip())
    tmp_text.append(record[1].strip())
   # print(record[1])
    #text2.append(record[1].strip())

# tmp_text[0]

real['publisher']=publisher
real['text']=tmp_text

# real['text'][0]

#real.head()

#real.shape

empty_fake_index=[index for index,text in enumerate(fake.text.tolist()) if (str(text).strip()=="")]

# fake.iloc[empty_fake_index]

real['text']=real['title']+" "+real['text']
fake['text']=fake['title']+" "+fake['text']

real['text']=real['text'].apply(lambda x: str(x).lower())
fake['text']=fake['text'].apply(lambda x: str(x).lower())

real['class']=1
fake['class']=0

real=real[['text','class']]
fake=fake[['text','class']]

data=real.append(fake,ignore_index=True)

# real['text'][0]

#data.sample(5)

#installing from https://github.com/laxmimerit/preprocess_kgptalkie
#!pip install spacy==2.2.3
#!python -m spacy download en_core_web_sm
#!pip install beautifulsoup4==4.9.1
#!pip install textblob==0.15.3
#!pip install git+https://github.com/laxmimerit/preprocess_kgptalkie.git --upgrade --force-reinstall

#importing this package to remove special characters from our dataset
import preprocess_kgptalkie as ps

data['text']=data['text'].apply(lambda x:ps.remove_special_chars(x))
# data2=[]
# for i in data['text']:
#     if i.isalnum():
#         data2.append(i)
# data['text']=data2
#ps.remove_special_chars("this@#%$%isGreat09^&**")

#data.head()
# data['text'][0]

# """# Vectorization-Word2Vec
# word2vec is one of the most popular techniques to learn word embeddings using shallow neural network.It was developed by Tomas Mikolov in 2013 at Google. word embedding is the most popular representation of a document vocabulary.It is capable of capturing context of a word in a document.
# Semantic and syntactic similarity,relation with other words etc..
# """

#!pip install gensim

import gensim

y=data['class'].values

X=[d.split() for d in data['text'].tolist()]

# print(X[0])

DIM=100
w2v_model=gensim.models.Word2Vec(sentences=X,vector_size=DIM,window=10,min_count=1)

# len(w2v_model.wv.vocab)

w2v_model.wv.most_similar('gandhi')

tokenizer=Tokenizer()
tokenizer.fit_on_texts(X)

X=tokenizer.texts_to_sequences(X)

# tokenizer.word_index

# plt.hist([len(x) for x in X],bins=700)
# plt.show()

nos=np.array([len(x) for x in X])
# len(nos[nos>1000])

maxlen=1000
X=pad_sequences(X,maxlen)

#len(X[9])

vocab_size=len(tokenizer.word_index)+1
vocab=tokenizer.word_index

def get_weight_matrix(model):
  weight_matrix=np.zeros((vocab_size,DIM))

  for word,i in vocab.items():
    weight_matrix[i]=model.wv[word]

    return weight_matrix

embedding_vectors=get_weight_matrix(w2v_model)

# embedding_vectors.shape

model=Sequential()
model.add(Embedding(vocab_size,output_dim=DIM,weights=[embedding_vectors],input_length=maxlen,trainable=True))
model.add(LSTM(units=128))
model.add(Dense(1, activation='sigmoid'))
model.compile(optimizer='adam',loss='binary_crossentropy',metrics=['acc'])

#model.summary()

X_train,X_test,y_train,y_test=train_test_split(X,y)

model.fit(X_train,y_train,validation_split=0.3,epochs=6)

y_pred=(model.predict(X_test)>=0.5).astype(int)

accuracy_score(y_test,y_pred)

#print(classification_report(y_test,y_pred))

#X_test



inp=input("Enter news article :")
u=inp
x=[inp]
x=tokenizer.texts_to_sequences(x)
x=pad_sequences(x,maxlen=maxlen)
result=(model.predict(x)>=0.5).astype(int)
if(result==[[0]]):
  print("fake news")
else:print("real news")

#x1="South Africa asked Johnson & Johnson and Pfizer Inc. to suspend delivery of Covid-19 vaccines as it now has enough stock, an illustration of how plunging demand is undermining the country’s rollout ahead of a potential fourth wave of infections.    Africa’s most developed economy has fully protected just 35% of adults, more than six months after doses were first made available to the public. About 120,000 people received shots on Tuesday, less than half the daily peak."

  #wordcloud =WordCloud().generate(x1)
  #plt.figure(figsize=(10,10))
  #plt.imshow(wordcloud)
  #plt.axis('off')
  #plt.tight_layout(pad=0)
  #x2=[x1]

















