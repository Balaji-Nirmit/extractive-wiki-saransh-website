from flask import Flask,render_template,request
import requests,re
from bs4 import BeautifulSoup
import spacy
from spacy.lang.en.stop_words import STOP_WORDS
from string import punctuation
from heapq import nlargest
# pip install spacy
# python -m spacy download en_core_web_sm

app = Flask(__name__,template_folder='templates', static_folder='static')


@app.route('/')
def index():
    return render_template("index.html")
@app.route('/content_image',methods=['POST','GET'])
def content_image():
  if request.method == 'POST': 
    query_ = request.form['flag'] 
    data=json_file_data_img(query_)
  return render_template("index.html",data1=data)
  
def json_file_data_img(query):
  #getting the url
  search_query=query.replace(" ","_")
  url = f'https://en.wikipedia.org/wiki/{search_query}'
  
  # Make a GET request to fetch the raw HTML content
  html_content = requests.get(url).text
  
  # Parse the html content
  soup = BeautifulSoup(html_content, "html.parser") 
  
  
  # getting images
  imagedata=[]
  all_images = soup.find_all('div',{'class':'thumbinner'})
  for image1 in all_images:
      if len(image1.find_all('div',{'class':'tsingle'}))!=0:
        tsingles=image1.find_all('div',{'class':'tsingle'})
        for tsingle in tsingles:
          thumbimage=tsingle.find('div',{'class':'thumbimage'})
          image=thumbimage.find('img')
          image=image.get('src') if image else ""
          caption=tsingle.find('div',{'class':'thumbcaption'})
          caption=caption.text if caption else " "
          image_info={
            "link":"https:"+image,
            "caption":caption
          }
          imagedata.append(image_info)
          
      else:  
        image=image1.find('img',{'class':'thumbimage'})
        image=image.get('src') if image else " "
        caption=image1.find('div',{'class':'thumbcaption'})
        caption=caption.text if caption else " "
        image_info={
          "link":"https:"+image,
          "caption":caption
        }
        imagedata.append(image_info)
  
  try:
    gallery=[]
    galarydatas=soup.find_all('li',{'class':'gallerybox'})
    for galarydata in galarydatas:
      image=galarydata.find('img')
      image=image.get('src') if image else " "
      caption=galarydata.find('div',{'class':'gallerytext'})
      caption=caption.text if caption else " "
      image_info={
          "link":"https:"+image,
          "caption":caption
        }
      gallery.append(image_info)
      imagedata=imagedata+gallery
  except:
    pass
  
  # with open("image_info.json","w") as file:
  #   json.dump(imagedata,file)
  return imagedata
  

@app.route('/content_summary',methods=['POST','GET'])
def content_summary():
  if request.method == 'POST': 
    query_ = request.form['flag'] 
    data_con=json_file_data_sum(query_)
  return render_template("index.html",data2=data_con)
  
def json_file_data_sum(query):
  #getting the url
  search_query=query.replace(" ","_")
  url = f'https://en.wikipedia.org/wiki/{search_query}'
  
  # Make a GET request to fetch the raw HTML content
  html_content = requests.get(url).text
  
  # Parse the html content
  soup = BeautifulSoup(html_content, "html.parser") 
  # Get all the paragraphs in the page
  paragraphs = soup.find_all('p')
  # content=[{"title":"-----","content_text":"  "}]
  content=[]
  heading1=""
  for para1 in paragraphs:
      heading=para1.find_previous('h2').text
      heading=re.sub(r"\[+[\w+\ ]+\]"," ",heading).upper()
      if heading1!=heading:
        try:
          data_info={
          "title":heading1,
          "content_text":summary(content_text)
          }
          content.append(data_info)
        except:
          pass
        content_text=" "
      para=para1.text
      para=re.sub(r"\[+[\w+\ ]+\]"," ",para)
      content_text=content_text+para
      heading1=heading
  
  # with open("content_info.json","w") as file:
  #   json.dump(content,file)
  return content

def summary(content):
  text=content
  stopwords=list(STOP_WORDS)
  nlp=spacy.load("en_core_web_sm")
  doc=nlp(text)
  tokens=[token.text for token in doc]
  # calculating the word frequency
  word_frequency={}
  for word in doc:
    if word.text.lower() not in stopwords and word.text.lower() not in punctuation:
      if word.text not in word_frequency.keys():
        word_frequency[word.text]=1
      else:
        word_frequency[word.text] +=1
  
  max_frequency=max(word_frequency.values())
  
  # calculating the normalised frequency
  for word in word_frequency.keys():
    word_frequency[word]=word_frequency[word]/max_frequency
  
  sentence_tokens=[sent for sent in doc.sents]
  sentence_scores={}
  
  for sent in sentence_tokens:
    for word in sent:
      if word.text in word_frequency.keys():
        if sent not in sentence_scores.keys():
          sentence_scores[sent]=word_frequency[word.text]
        else:
          sentence_scores[sent]+=word_frequency[word.text]
  
  select_len=int(len(sentence_tokens)*0.3)#taking 30%
  
  summary=nlargest(select_len,sentence_scores,key=sentence_scores.get)
  final_summary=[word.text for word in summary]
  summary=" ".join(final_summary)
  return summary

if __name__=="__main__":
  app.run(host='0.0.0.0', port=81,debug=True)
  