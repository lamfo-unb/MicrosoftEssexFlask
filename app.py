from flask import Flask
import requests
from bs4 import BeautifulSoup
import time
import sys
#open text file in read mode
text_file = open("api.txt", "r")
#read whole file to a string
api = text_file.read()
#close file
text_file.close()
sys.path.append('../')
from MicrosoftEssexBinary.Production_Cleaner import *
from MicrosoftEssexBert.bert import *
import warnings
warnings.filterwarnings("ignore")






# def classificador_Nagata(corpo_do_texto): centenas de vezes em paralelo
#     return classificação

def factcheck(texto):
    try:
        # print(texto)
        texto_original = texto
        for poi in range(10):
            try:
                query = "https://factchecktools.googleapis.com/v1alpha1/claims:search?query=PESQUISA&key=API"
                query = query.replace("PESQUISA",texto).replace(" ","%20").replace("API",api)
                query = requests.get(query, timeout=2.50)
                json = query.json()["claims"]
            except:
                if len(texto)>10:
                    texto = texto[:-10]

        lista_textos = []
       

        try:
            result, probbert = bert(texto_original)
            if int(result) == 0:
                lista_textos.append("<h2>Verdict: LOOKS FALSE </h2>")
            elif int(result) == 1:
                lista_textos.append("<h2>Verdict: LOOKS MISLEADING </h2>")
            else:
                lista_textos.append("<h2>Verdict: LOOKS TRUE </h2>")
        except:
            print("error bert")

        
        try:
            if probbert < 0.5:
                result = classify(texto_original)
                if int(result) == 0:
                    lista_textos.append("<h2>Verdict: LOOKS FALSE </h2>")
                else:
                    lista_textos.append("<h2>Verdict: LOOKS TRUE </h2>")
        except:
            print("error binary")


        
        try:
            for i in range(len(json)):
                texto = "<h3>"+ json[i]["text"] + "</h3>"
                try:
                    texto +=" Information Author: " + json[i]["claimant"]
                except:
                    print(list(json[i]))
                
                texto +=". Reviewer: " + json[i]["claimReview"][0].get("publisher").get("name")
                texto +="""<p><a href='""" + json[i]["claimReview"][0].get("url") + """'onclick="window.open('""" +json[i]["claimReview"][0].get("url") + """'),'_top'" > Read the full review</a></p>"""

                texto +=" <b>Verdict: " + json[i]["claimReview"][0].get("textualRating") + "</b>"
                rating = json[i]["claimReview"][0].get("textualRating")
                lista_textos.append(texto)

        except:
            print("no info from google")
    except Exception as e:
        print(e)
        lista_textos = ["Website not suported", " <br>"]
    return " <br><br>".join(lista_textos)

app = Flask(__name__)

@app.route("/<string:name>")
def home(name):
    # print(str(name))
    # making requests instance
    reqs = requests.get(str(name).replace("<https>","https://").replace("<barra>","/"))
    
    # using the BeaitifulSoup module
    soup = BeautifulSoup(reqs.text, 'html.parser')
    
    # displaying the title
    print("Title of the website is : ")
    texto = ""
    for title in soup.find_all('title'):
        texto = texto + title.get_text() + " "

    texto = texto.replace("The Washington Post"," ")
    texto = texto.replace("search menu menu The Washington Post profile profile Next articles The Washington Post share comment comment"," ")
    print(texto)

    return factcheck(texto)
app.run(port = 5000)
