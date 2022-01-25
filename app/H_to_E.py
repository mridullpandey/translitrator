import sys
import psycopg2
import glob
import re
import json
import itertools
import pandas as pd
def check_language(wrd,lang = "",target_language = ""):
    try:
        wrd.encode(encoding='utf-8').decode('ascii')
        if lang == "":
            lang = 'Engish'
        if target_language == "":
            target_language = "Hindi"
    except:
        if lang == "":
            lang = 'Hindi'
        if target_language == "":
            target_language = "English"
    return lang,target_language

def find_elem_from_database(wrd,lang = "",target_language = ""):
    #language_check
    lang,target_language = check_language(wrd,lang,target_language)
    
    # find_word_from_database_using_wrd,lang,target_language_or_return_False
    
    return False

def translate(wrd):
    lang,target_language = check_language(wrd)
    tr_wrd = find_elem_from_database(wrd,lang,target_language)
    recom = []
    if tr_wrd != False:
        recom.append(tr_wrd.split(';'))
    try:
        if target_language == "English":
            recom.extend([k for k in list(map(str.title,eng_translate(wrd))) if k not in recom])
        elif target_language == "Hindi":
            recom.extend([k for k in list(map(str.title,hin_translate(wrd))) if k not in recom])
        recom.append(wrd)
        return recom
    except Exception as ex:
        #print(ex)
        return [wrd]

def eng_translate(hin):
    spec_char1 = {                     
    'ँ':{ 'an': 100, 'un':10 },
    'ं':{ 'an': 100, 'un':10 },
    'ॅ':{ 'a': 100, 'u':10 },
    '०':{ '०':100},
    '़':{'': 100},
    'ा':{'a':100, 'aa':80},
    'ि':{'i': 100,'e': 40} ,
    'ी':{'i':100, 'ee':80 , 'e': 60 },
    'ु':{'u': 100, 'oo':10},
    'ू':{'u': 100,'oo':80, 'uu': 20},
    'े':{'e':100},
    'ै':{'ai':100, 'ae':90 },          
    'ॉ':{'a': 100},     
    'ो':{'o':100},
    'ौ':{'au':100},
    '्':{'':100},
    'ृ':{'r':100, 'ra':80}    

    }
    spec_char2 = {
    'ँ':{'n':100},
    '०':{ '०':100},
    'ं':{'n':100},
    'ा':{'a':100}, 
    '़':{'':100},                          # if special char is preceded by another special char
    'ि':{'i':100},      # Revisit
    'ी':{'e':100,'ee':80, 'i':40},
    'ॅ':{ 'a': 100, 'u':10 },
    'ु':{'u':100, 'oo':20},
    'ू':{'u':100,'oo':40,'uu':20},    #Revist
    'े':{'e':100, 'ai':80, 'a':60},          #Revisit
    'ै':{'ai': 100, 'ae':90},            #Revisit
    'ॉ':'a',
    'ो':{'o':100},
    'ौ':{'au':100},                        
    '्':{'':100},
    'ृ':{'ra':100, 'r':80},
    ' ृ':{'r':100}
    }
    first = {'अ':{'a':100},
         'ऑ':{'o':100, 'au':60},    
     'आ':{'a': 100,'aa': 80},
     'इ':{'i':100,'e': 60} ,
     'ई':{'i':100, 'e':80, 'ee':60, 'ii':20},
     'उ':{'u': 100,'oo': 40},
     'ऊ':{'u': 100 ,'oo': 60,'uu':40},
     'ए':{'ae': 100},
     'ऐ':{'e':100},
     'ओ':{'o':100},
     'औ':{'au': 100},
     'क':{'ka': 100, 'ca': 60},
     
     'ख':{'kha': 100},
     'ग':{'ga':100},
     'घ':{'gh': 100},
     'च':{'cha':100},
     'छ':{'chha': 100},
     'ज':{'ja': 100},
     'झ':{'jha': 100},
     'ट':{'ta':100},
     'ठ':{'tha':100},
     'ळ':{'ttha':100},
     'ड':{'da': 100},
     'ङ': {'da':100},
     'ण':{'na':100},
     'त':{'ta': 100},
     'थ':{'tha':100},
     'द':{'da': 100},
     'ध':{'dha': 100},
     'न':{'na': 100},
     'प':{'pa': 100},
     'फ':{'pha': 100,'fa': 80},
     'ब':{'ba':100},
     'भ':{'bha':100},
     'म':{'ma':100},
     'य':{'ya': 100},
     'र':{'ra': 100},
     'ल':{'la':100},
     'व':{'va': 80, 'wa': 100},
     'श':{'sha':100},
     'स':{'sa': 100},
     'ह':{'ha': 100},
     'ष':{'sha': 100},
     'ञ': {'ya': 100},
     'ढ':{ 'dd': 100 , 'd': 60},
     'क़':{'ka': 100, 'ca': 20},
     'ख़':{'kha': 100},
     'ग़':{'ga': 100},
     'ज़':{'za': 100},
     'ड़':{'rha': 100, 'dha': 60},
     'ढ़':{'rha': 100, 'dha': 60},
     'फ़':{'fa': 100, 'pha': 80},
     'ऋ': {'ri':100}
         }
    last = {'अ':{'a':100},
     'आ':{'a':100, 'aa': 80},
     'इ':{'i': 100, 'e':80},               #Revisit
     'ई': {'e':100 , 'ee':80 , 'i': 60,'ii': 40},
     'उ':{'u':100, 'oo': 60},
     'ऊ':{'u': 100 , 'oo': 80, 'uu': 60},
     'ए':{'ye': 100},
     'ऐ':{'ae':100},
     'ओ':{'o':100},
     'औ':{'au': 100},
     'क':{'k':100, 'c':40},
     'ख':{'kh':100},
     'ग':{'g':100},
     'घ':{'gh':100},
     'च':{'ch':100},
     'छ':{'chh':100},
     'ज':{'j':100, 'g':10},
     'झ':{'jh': 100},
     'ट':{'t': 100},
     'ठ':{'th': 100},
     'ळ':{'tth':100},
     'ड':{'d': 100},
     'ङ': {'d':100},
     'ण':{'n': 100},
     'त':{'t': 100},
     'थ':{'th':100},
     'द':{'d': 100, 'dd':20},
     'ध':{'dh': 100},
     'न':{'n': 100},
     'प':{'p': 100},
     'फ':{'f': 100, 'ph': 80},
     'ब':{'b': 100},
     'भ':{'bh':100},
     'म':{'m': 100},
     'य':{'ya': 100},
     'र':{'r':100},
     'ल':{'l': 100},
     'व':{'v': 100,'w': 80},
     'श':{'sh': 100},
     'स':{'s': 100},
     'ह':{'h': 100},
     'ढ':{ 'dd': 100 , 'd': 60},
     'क़':{'k': 100, 'c': 20},
     'ख़':{'kh': 100},
     'ग़':{'g': 100},
     'ज़':{'z': 100},
     'ड़':{'rh': 100, 'dh': 60},
     'ढ़':{'rh': 100, 'dh': 60},
     'फ़':{'f': 100, 'ph': 80},
     'ष':{'sh': 100},
     'ञ': {'y': 100},
     'ऋ': {'ri':100}
    }
    exact = {
    'ए':'a', 'बी':'b', 'सी':'c', 'डी':'d', 'ई':'e','एफ':'f', 'जी':'g', 'एच':'h', 'आई':'i', 'जे':'j', 'के':'k', 'एल':'l', 
    'एम':'m', 'एन':'n', 'ओ':'o', 'पी':'p', 'क्यू':'q', 'आर':'r', 'एस':'s', 'टी':'t', 'यू':'u','वी':'v','डब्ल्यू':'w','एक्स':'x',
    'व्हाई':'y', 'ज़ेड':'z','डा':'Dr.','टैक्स':'tax','आॅफिस':'office','ऑफिस':'office'}
    str1 = ''
    lt = []
    if hin in exact:
        return exact[hin],[exact[hin]] 

    for i in range(0,len(hin)):

        try:
            if i == 0 and i!=len(hin) - 1 and hin[i] in first and hin[i+1] in spec_char1:
                lt.append(last[hin[i]])
                #print(hin[i])
            elif i == 0 and hin[i] in first:
                lt.append(first[hin[i]])
                #print(hin[i])
            elif i == len(hin) - 2 and hin[i] in last and hin[-1] in spec_char1:
                lt.append(last[hin[i]])
                #print(hin[i])
            elif i == len(hin) - 1 and hin[i] in last:
                lt.append(last[hin[i]])
                #print(hin[i])
            elif i == len(hin) - 1:
                lt.append(spec_char1[hin[i]])
                #print(hin[i])
            elif hin[i] in spec_char1 and hin[i-1] in spec_char1:
                lt.append(spec_char2[hin[i]])
                #print(hin[i])
            elif hin[i] in spec_char1:
                lt.append(spec_char1[hin[i]])
                #print(hin[i])
            elif hin[i] in last and i != len(hin) - 1 and hin[i+1] in spec_char1:
                lt.append(last[hin[i]])
                #print(hin[i])
            elif hin[i] in first:
                lt.append(first[hin[i]])
                #print(hin[i])
            else:
                lt.append([hin[i]])
                #print(hin[i])
        except:
            lt.append([hin[i]])
            #print(hin[i])

    from queue import PriorityQueue
    q = PriorityQueue()

    for i in lt[0]:
        q.put((-1*lt[0][i], i))

    for i in range(1,len(lt)):
        qtemp = PriorityQueue()
        while not q.empty():
            temp = q.get()
            for j in lt[i]:  
                qtemp.put((temp[0]+(-1 *lt[i][j]),temp[1]+j))
        c=15
        while ( not qtemp.empty() and c):
            temp2 = qtemp.get()
            q.put((temp2[0],temp2[1]))
            c-=1

    lisq = []                 
    while not q.empty():
        t = q.get()[1]
        lisq.append(t)

    return lisq

def Hindi_English_Transliteration(d,a):

        lis = sorted(d.items(), key = lambda kv:(kv[1], kv[0]),reverse = True)
        sorted_lis = []
        for i in lis:
            sorted_lis.append(i[0])

        #sorted_lis.append(a)                                                  #sort
        
        for i in eng_translate(a):
            if( i not in d):
                sorted_lis.append(i)
        return sorted_lis

def Database_Search_Hindi(a):
    
    connection = psycopg2.connect(user="postgres",
                                      password="Jarvis123",
                                      host="localhost",
                                      port="5432",
                                      database="postgres")
    cursor = connection.cursor()
    try:
        cursor.execute("""SELECT ENGLISH from Hindi_Eng_DICTIONARY where hindi = '%s';"""%a)
        d = cursor.fetchall()
        d = d[0][0]
        sorted_list = Hindi_English_Transliteration(d,a)
        return sorted_list
    
    except:
        return eng_translate(a)

lis_argv = sys.argv
df = pd.read_excel(lis_argv[1])
lis_unique=[]

if(len(lis_argv)>2):
    columns = []
    for i in lis_argv[2:]:
        a1 = int(i.split(':')[0])
        try:
            b1 = int(i.split(':')[1])
        except:
            b1 = a1
        columns.extend(list(df.columns[a1-1:b1]))
else:
    columns = list(df.columns)

lis_unique=[]
for column in columns:
    unique = list(df[column].drop_duplicates())
    lis_unique = lis_unique + unique


lis_split = []
for i in range(0,len(lis_unique)):
    lis_split.append(re.split(r'[^\u0900-\u097F\n]',str(lis_unique[i])))

flatlist = []
for elem in lis_split:
    flatlist.extend(elem)
lis_dis = set(flatlist)
lis_dis = list(lis_dis)

lis1 = []
d_new = {}
for key in lis_dis:
    

    try:

        d_new[key] = Database_Search_Hindi(key)[0]

    except:
        lis = key
        if lis not in lis1:
            lis1.append(lis)
        continue

global settemp
settemp = set()
def tran(w_list,wrd):

    for i in w_list:
        try:
            wrd = wrd.replace(i,d_new[i])
        except:
            #settemp.add((i))
            wrd = wrd.replace(i,"")
            continue
    return wrd

for column in columns:
    #print(column)
    if column == "BM_split":
        continue
    #df['BM_split'] = df[column].apply(lambda x: sorted(list(set(filter(None,re.sub("\s+"," ",re.sub("[^a-zA-Z]"," ",str(x))).strip().split(" ")))), key=len, reverse = True) if x==x else [])
    df['BM_split'] = df[column].apply(lambda x: sorted(list(set(filter(None,re.split(r'[^\u0900-\u097F\n]',str(x))))), key=len, reverse = True) if x==x else [])
    df[column +'_English'] = df[["BM_split",column]].apply(lambda x: tran(*x), axis = 1)
    del df["BM_split"]
    #del df[column]
df.to_excel(r'%s_English.xlsx'%lis_argv[1].split("\\")[-1], index= False)



