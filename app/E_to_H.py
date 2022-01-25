import psycopg2
import sys
import glob
import re
import json
import itertools
from queue import PriorityQueue
import pandas as pd
dict_tr = {'क':'k;c;q','ख':'kh','ग':'g','घ':'gh','ङ':'d','च':'ch','छ':'chh','ज':'j','झ':'jh','ञ':'ny','ट':'t','ठ':'th',          'ड':'d','ढ':'dh','ण':'n','त':'t','थ':'th','द':'d','ध':'dh','न':'n','प':'p','फ':'ph;f','ब':'b','भ':'bh','म':'m',          'य':'y','र':'r','ल':'l','व':'v;w','ड़':'dh;rh','ढ़':'rh;dh','श':'sh','ष':'sh','स':'s','ह':'h'}

dict_en = {'k': ['क', 'क़'],'c': ['क'],'q': ['क', 'क़'],'kh': ['ख', 'ख़'],'g': ['ग'],'gh': ['घ'],'d': ['ङ', 'ड', 'द', 'ड़'],           'ch': ['च', 'छ'],'chh': ['छ'],'j': ['ज'],'jh': ['झ'],'ny': ['ञ', 'न्य'],'t': ['ट', 'त'],'th': ['ठ', 'थ'],           'dh': ['ढ', 'ध', 'ड़', 'ढ़'],'n': ['ण', 'न', 'ँ', 'ं'],'p': ['प'],'ph': ['फ', 'फ़'],'f': ['फ', 'फ़'],'b': ['ब'],           'bh': ['भ'],'m': ['म', 'ं'],'y': ['य'],'r': ['र'],'l': ['ल'],'v': ['व'],'w': ['व'],'rh': ['ड़', 'ढ़'],           'sh': ['श', 'ष'],'s': ['स'],'h': ['ह'],'tch': ['च'],'tion': ['शन'],'z': ['ज़', 'ज'],'ye': ['ए', 'ये'],           'yi': ['यी', 'ई'],'x': ['क्स']}
#single characters
dict_en1 = {'k': ['क', 'क़'],'c': ['क'],'q': ['क', 'क़'],'g': ['ग'],'d': ['ङ', 'ड', 'द', 'ड़'],'j': ['ज'],'t': ['ट', 'त'],            'n': ['ण', 'न', 'ँ', 'ं'],'p': ['प'],'f': ['फ', 'फ़'],'b': ['ब'],'m': ['म', 'ं'],'y': ['य'],'r': ['र'],'l': ['ल'],            'v': ['व'],'w': ['व'],'s': ['स'],'h': ['ह'],'z': ['ज़', 'ज'],'x': ['क्स']}

#double characters
dict_en2 = {'kh': ['ख', 'ख़'],'gh': ['घ'],'ch': ['च', 'छ'],'jh': ['झ'],'ny': ['ञ', 'न्य'],'th': ['ठ', 'थ'],            'dh': ['ढ', 'ध', 'ड़', 'ढ़'],'ph': ['फ', 'फ़'],'bh': ['भ'],'rh': ['ड़', 'ढ़'],'sh': ['श', 'ष'],'ye': ['ए', 'ये'],            'yi': ['यी', 'ई']}

#more than 2 characters
dict_en3 = {'chh': ['छ'], 'tch': ['च'], 'tion': ['शन']}

#dictionary for vyanjan when succeeded by another vyanjan
half = {'k': {'क्': 100, 'क़्': 20, 'क': 0, 'क़': 0},
 'c': {'क्': 100, 'क': 0},
 'q': {'क्': 10, 'क़्': 100, 'क': 0, 'क़': 0},
 'g': {'ग्': 100, 'ग': 0},
 'd': {'ड्': 100,'द्': 100,'ङ': 0,'ड': 0,'द': 0,'ड़': 0},
 'j': {'ज्': 100, 'ज': 0},
 't': {'ट्': 100, 'त्': 80, 'ट': 0, 'त': 0},
 'n': {'ण्': 60, 'न्': 80, 'ँ': 40, 'ं': 100, 'ण': 0,'न': 0},
 'p': {'प्': 100, 'प': 0},
 'f': {'फ्': 100, 'फ़्': 60, 'फ': 0, 'फ़': 0},
 'b': {'ब्': 100, 'ब': 0},
 'm': {'म्': 100, 'ं': 100, 'म': 0},
 'y': {'य्': 100, 'य': 0},
 'r': {'र्': 100, 'र': 0},
 'l': {'ल्': 100, 'ल': 0},
 'v': {'व्': 100, 'व': 0},
 'w': {'व्': 100, 'व': 0},
 's': {'स्': 100, 'स': 0},
 'h': {'ह्': 100, 'ह': 0},
 'z': {'ज़्': 100, 'ज्': 60, 'ज़': 0, 'ज': 0},
 'x': {'क्स्': 100, 'क्स': 0},
 'kh': {'ख्': 100, 'ख़्': 80, 'ख': 0, 'ख़': 0},
 'gh': {'घ्': 100, 'घ': 0},
 'ch': {'क्': 40, 'च्': 100, 'च': 0, 'छ': 0},
 'th': {'ठ्': 100, 'थ्': 80, 'ठ': 0, 'थ': 0},
 'dh': {'ढ्': 100,'ध्': 100,'ढ': 0,'ध': 0,'ड़': 0,'ढ़': 0},
 'ph': {'फ्': 100, 'फ़्': 60, 'फ': 0, 'फ़': 0},
 'bh': {'भ्': 100, 'भ': 0},
 'rh': {'ढ़': 100, 'ड़': 40},
 'sh': {'श्': 100, 'ष्': 100, 'श': 0, 'ष': 0},
 'yi': {'ई': 100, 'यी': 0},
 'tch': {'च्': 100, 'च': 0},
 'tion': {'शन्': 100, 'शन': 0},
 'chh': {'छ्': 100, 'छ': 0},
 'jh': {'झ्': 100, 'झ': 0},
 'ny': {'न्य': 100, 'ञ': 10},
 'ye': {'ये': 100, 'ए': 20}}

#dictionary for starting characters
#1 is the dictionary for vyanjans and 0 is the dictionary for combination of swars
dictf = {1: {'b': {'ब': 100},
  'c': {'क': 100, 'स': 10},
  'd': {'द': 100, 'ड': 25, 'ड़': 0},
  'f': {'फ़': 3, 'फ': 100},
  'g': {'ग': 100},
  'h': {'ह': 100},
  'j': {'ज': 100},
  'k': {'क': 100, 'क़': 0},
  'l': {'ल': 100},
  'm': {'म': 100},
  'n': {'न': 100, 'ण': 0},
  'p': {'प': 100},
  'q': {'क़': 100, 'क': 100},
  'r': {'र': 100},
  's': {'स': 100},
  't': {'ट': 26, 'त': 100},
  'v': {'व': 100},
  'w': {'व': 100},
  'x': {'क्स': 100},
  'y': {'य': 100},
  'z': {'ज़': 100, 'ज': 66},
  'bh': {'भ': 100},
  'ch': {'च': 100, 'छ': 2},
  'dh': {'ध': 100, 'ढ': 15, 'ढ़': 1, 'ड़': 0},
  'gh': {'घ': 100},
  'jh': {'झ': 100},
  'kh': {'ख': 100, 'ख़': 0},
  'ny': {'न्य': 100},
  'rh': {'ढ़': 100, 'ड़': 40},
  'ph': {'फ': 100, 'फ़': 2},
  'sh': {'श': 100, 'ष': 1},
  'th': {'थ': 72, 'ठ': 100},
  'ye': {'ए': 6, 'ये': 100},
  'yi': {'यी': 100},
  'tion': {'शन':100},
  'tch': {'च्': 100, 'च': 0},
  'chh': {'छ': 100}},
   
 0: {'a': {'अ': 100, 'आ': 25},
  'e': {'ए': 100, 'इ': 0, 'ई': 0},
  'i': {'इ': 100, 'ई': 14},
  'o': {'ओ': 100, 'ऑ': 66},
  'u': {'उ': 100, 'ऊ': 1},
  'aa': {'आ': 100},
  'ae': {'ऐ': 100, 'आए': 42, 'अए': 20, 'ए': 40},
  'ai': {'ऐ': 100, 'आई': 12},
  'ao': {'औ': 19, 'ओ': 100, 'अव': 19},
  'au': {'औ': 100, 'अऊ': 0, 'आऊ': 0, 'आउ': 0},
  'ea': {'ऐ': 14, 'ए': 97, 'ई': 100, 'एअ': 31, 'इ': 40},
  'ee': {'ई': 100, 'इ': 46, 'ए': 38},
  'ei': {'ऐ': 12, 'ई': 100, 'एई': 41, 'एइ': 39, 'इ': 14},
  'eo': {'एओ': 100, 'इओ': 50, 'एव': 50, 'ईओ': 50},
  'eu': {'एयु': 28, 'एउ': 100, 'यु': 18},
  'ia': {'इअ': 32, 'इ': 25, 'इआ': 23, 'इया': 100},
  'ie': {'ई': 50, 'इए': 100, 'आई ई': 38},
  'ii': {'ई': 100, 'ईइ': 1},
  'io': {'इओ': 100, 'आय': 11},
  'iu': {'इउ': 25, 'इु': 100, 'ईउ': 9, 'इयु': 22, 'ईयु': 16, 'इयू': 9},
  'oa': {'ओ': 100, 'ऑ': 20, 'ओआ': 60, 'ओए': 60, 'ओवा': 20, 'ओअ': 20},
  'oe': {'ओए': 100},
  'oi': {'ओई': 61, 'ओइ': 100},
  'oo': {'ऊ': 100},
  'ou': {'ओउ': 100, 'औ': 69, 'ओ': 23},
  'ua': {'उ': 100, 'उअ': 69, 'उॅ': 30, 'उआ': 13, 'ऊ': 20},
  'ue': {'उे': 100, 'उए': 19},
  'ui': {'उइ': 100, 'उी': 47, 'उि': 52, 'उई': 42, 'युई': 10},
  'uo': {'उव': 100, 'ऊआ': 5, 'उओ': 5},
  'uu': {'ऊ': 100, 'उयु': 0},
  'aaa': {'आअ': 40, 'आआ': 20, 'अआ': 40, 'आ': 100},
  'aae': {'आए': 100, 'आइ': 15, 'आय': 15},
  'aai': {'आइ': 60, 'ऐ': 20, 'आई': 100, 'अऐ': 10, 'आऐ': 10},
  'aao': {'आऊ': 6, 'आओ': 100, 'आव': 18},
  'aau': {'आउ': 66, 'आऊ': 66, 'औ': 100, 'आयु': 33, 'अअु': 33},
  'aea': {'एअ': 100, 'ओ': 100},
  'aee': {'आई': 100, 'अई': 50, 'एइए': 8, 'आऐ': 8},
  'aei': {'एइ': 100, 'अइ': 33, 'एै': 33},
  'aia': {'आया': 100, 'आइअ': 100, 'आइआ': 100},
  'aie': {'ऐे': 100},
  'aii': {'अई': 100, 'आई': 33, 'ऐइ': 25, 'ऐई': 8},
  'aio': {'आयो': 100, 'अयो': 100, 'ऐओ': 100, 'आइओ': 100},
  'aiu': {'आईउ': 100,
   'अैयू': 50,
   'आइयु': 100,
   'आइउ': 100,
   'ऐयू': 50,
   'अैयु': 100,
   'आईयु': 50,
   'ऐउ': 100,
   'ऐयु': 50},
  'aoo': {'आऊ': 100},
  'aou': {'आओ': 24, 'ओ': 50, 'औ': 100, 'अ': 12, 'ओउ': 12},
  'aua': {'औअ': 50,
   'आयुॅ': 50,
   'आै': 50,
   'औॅ': 100,
   'औा': 100,
   'औ': 100,
   'आैा': 50},
  'aue': {'औए': 100, 'औय': 20},
  'aui': {'औई': 85, 'औइ': 100},
  'auo': {'औओ': 100, 'अवो': 100},
  'auu': {'अयूू': 31, 'औयु': 100, 'औउ': 65, 'आयुु': 31, 'अुु': 31},
  'eaa': {'एआ': 100},
  'eae': {'ई': 100, 'इए': 12},
  'eai': {'ऐ': 70, 'एआई': 30, 'ई': 100},
  'eau': {'ऐयु': 100},
  'eee': {'एई': 50, 'ई': 100, 'ईए': 50},
  'eia': {'एइअ': 11, 'एया': 100},
  'eii': {'एईइ': 11, 'एई': 100},
  'eio': {'इयो': 100},
  'eiu': {'एइउ': 100},
  'eoo': {'एऊ': 100},
  'eua': {'इउ': 100},
  'tion': {'शन':100},
  'eue': {'यूए': 100},
  'iai': {'इऐ': 100, 'ईआइ': 20},
  'iau': {'इऔ': 100},
  'iea': {'आइ': 100, 'इ': 100},
  'iua': {'युए': 100},
  'iui': {'इउई': 100},
  'iuu': {'ईयु': 100, 'ईऊ': 100},
  'oaa': {'ओ.ए.अ': 25, 'ओवा': 100},
  'oai': {'ओै': 40, 'ओऐ': 100, 'ओई': 60},
  'oao': {'ओआओ': 100},
  'oau': {'ओऔ': 100, 'आओ': 100},
  'oie': {'ओइए': 100, 'ओइे': 100},
  'ooa': {'ऊ': 100},
  'ooi': {'ऊई': 100, 'उई': 50, 'ओई': 50, 'ओइ': 50},
  'ooo': {'ओऊ': 100},
  'oua': {'औ': 100},
  'uaa': {'उआ': 100},
  'uai': {'ऊऐ': 100, 'युऐ': 66},
  'uau': {'वऊ': 100},
  'uea': {'उएअ': 100, 'यूई': 100, 'युई': 100},
  'uia': {'उया': 100},
  'uii': {'उई': 100},
  'uua': {'ऊआ': 100},
  'uuu': {'उऊ': 42, 'उउउ': 100},
  'aaaa': {'आआ': 100},
  'aaao': {'आओ': 100},
  'aaie': {'आऐे': 100},
  'aaii': {'आइ': 100},
  'aaiu': {'अैयू': 100},
  'aaoo': {'आऊ': 100, 'आओ': 33},
  'aiai': {'ऐऐ': 100, 'ऐ': 100},
  'aieo': {'आइओ': 100},
  'aieu': {'ऐेयु': 100},
  'auaa': {'आैाा': 100},
  'auai': {'अयुै': 100, 'अूअी': 100},
  'eaiu': {'एैयु': 100},
  'eeai': {'ेएै': 100},
  'iuai': {'इउाई': 100},
  'iuiu': {'इउइउ': 100},
  'oooo': {'ोोू': 100},
  'aaaaa': {'अअअअअ': 100, 'आआअ': 100},
  'aieai': {'ऐेै': 100},
  'eeaiu': {'ेएैयु': 100},
  'eeeee': {'इ': 100},
  'oooooo': {'ऊऊऊ': 100},
  'aaaaaaaaa': {'आआआआआ': 100},
  'aeo': {'एओ': 100, 'आइओ': 0},
  'aeu': {'आयु': 50, 'एउ': 100, 'एऊ': 100},
  'aoa': {'आवा': 25, 'आवै': 0, 'अवा': 100},
  'aoe': {'औए': 100, 'औय': 20},
  'aoi': {'औए': 42, 'ओ': 100},
  'eao': {'ईओ': 42, 'एओ': 100},
  'eea': {'इआ': 100, 'ई': 100},
  'eei': {'ई': 100, 'अई': 100},
  'eeo': {'ईओ': 100},
  'eeu': {'ईऊ': 100, 'इउ': 0},
  'eie': {'इए': 25, 'ई': 100},
  'eoa': {'ऐवा': 100, 'एओ': 25, 'एओए': 0},
  'eoe': {'इवे': 25, 'एवे': 100, 'एओए': 0, 'ऐवे': 0},
  'eoi': {'एवी': 100, 'ऐवी': 25, 'इवी': 0, 'इओआई': 0},
  'eou': {'एवु': 100, 'इओ': 0},
  'eui': {'युई': 100, 'यूई': 33, 'यूइ': 33, 'ई': 0},
  'euo': {'यूओ': 100, 'ओ': 25},
  'euu': {'ईऊ': 40, 'एऊ': 100, 'ऊ': 60},
  'iaa': {'इआ': 100},
  'iae': {'इए': 100, 'ईए': 25},
  'iao': {'ईओ': 66, 'याओ': 100},
  'iee': {'ई': 100, 'इए': 25},
  'iei': {'आई': 66, 'ई': 100},
  'ieo': {'इयो': 25, 'ईयो': 100},
  'ieu': {'ईयू': 100, 'येऊ': 25},
  'iia': {'आईआईए': 0, 'इया': 25, 'ईया': 100},
  'iie': {'ईए': 100, 'ईये': 25},
  'iii': {'ई': 100, 'आई': 0},
  'iio': {'ईओ': 25, 'ईयो': 100},
  'iiu': {'ईऊ': 100, 'इउ': 0},
  'ioa': {'इवा': 100},
  'ioe': {'इवे': 100, 'एओए': 25},
  'ioi': {'इवी': 100, 'योई': 25},
  'ioo': {'ईऊ': 100, 'इउ': 0},
  'iou': {'इवू': 100},
  'iue': {'ईवे': 100, 'इवे': 25, 'इये': 0},
  'iuo': {'यूओ': 66, 'ईओ': 0, 'ईवो': 100},
  'oae': {'ओए': 100},
  'oea': {'ओई': 100, 'ओइ': 42},
  'oee': {'ओई': 100, 'ओइ': 11},
  'oei': {'ओई': 100, 'ओइ': 11},
  'oeo': {'ओयो': 100, 'ओएओ': 0},
  'oeu': {'ओयु': 100, 'वेऊ': 25, 'ओएओ': 0},
  'oia': {'ओया': 100, 'वीया': 25},
  'oii': {'ओई': 100},
  'oio': {'ओयो': 100, 'ओएओ': 0},
  'oiu': {'ओयु': 100, 'ओयू': 25},
  'ooe': {'ऊए': 100, 'ऊई': 25},
  'oou': {'ओऊ': 100, 'ओउ': 11},
  'oue': {'ओए': 100},
  'oui': {'ओइ': 100, 'ऊई': 25, 'वुई': 0},
  'ouo': {'ओऊओ': 0, 'ओ': 100},
  'ouu': {'ओऊ': 100},
  'uae': {'ऊए': 100, 'ऊई': 40, 'उए': 60},
  'uao': {'वओ': 0, 'ऊआ': 25, 'उओ': 100},
  'uee': {'उई': 100, 'ऊए': 0},
  'uei': {'उई': 100, 'ऊए': 0},
  'ueo': {'उयो': 100, 'ऊ': 0},
  'ueu': {'उएऊ': 0, 'यू': 42, 'ऊ': 100},
  'uie': {'उई': 100, 'उये': 25},
  'uio': {'उयो': 100},
  'uiu': {'ऊइउ': 100},
  'uoa': {'उवा': 100},
  'uoe': {'उवे': 25, 'ऊवे': 100},
  'uoi': {'उवी': 25, 'ओई': 100},
  'uoo': {'उऊ': 25, 'उवो': 100},
  'uou': {'उओ': 100},
  'uue': {'ऊए': 100},
  'uui': {'ऊई': 100, 'उई': 50, 'ओई': 50, 'ओइ': 50},
  'uuo': {'ऊओ': 100}}}

#Dictionary for characters in the middle
dictm = {1: {'b': {'ब': 100},
  'c': {'क': 100, 'स': 10},
  'd': {'द': 100, 'ड': 15, 'ड़': 4, 'ङ': 0},
  'f': {'फ': 100, 'फ़': 4},
  'g': {'ग': 100},
  'h': {'ह': 100},
  'j': {'ज': 100},
  'k': {'क': 100, 'क़': 0},
  'l': {'ल': 100},
  'm': {'म': 100},
  'n': {'न': 100, 'ण': 42},
  'p': {'प': 100},
  'q': {'क़': 75, 'क': 100},
  'r': {'र': 100},
  's': {'स': 100},
  't': {'त': 100, 'ट': 100},
  'v': {'व': 100},
  'w': {'व': 100},
  'x': {'क्स': 100},
  'y': {'य': 100},
  'z': {'ज़': 100, 'ज': 96},
  'bh': {'भ': 100},
  'ch': {'च': 100, 'छ': 0},
  'dh': {'ध': 100, 'ढ़': 6, 'ढ': 10, 'ड़': 50},
  'gh': {'घ': 100},
  'jh': {'झ': 100},
  'kh': {'ख': 100, 'ख़': 0},
  'ny': {'न्य': 100, 'ण्य': 5, 'ंय': 11},
  'ph': {'फ': 100, 'फ़': 4},
  'rh': {'ढ़': 85, 'ड़': 100},
  'sh': {'श': 100, 'ष': 20},
  'th': {'ठ': 56, 'थ': 100},
  'ye': {'ए': 9, 'ये': 100},
  'yi': {'ई': 7, 'यी': 100},
  'chh': {'छ': 100},
   'tion': {'शन':100},
  'tch': {'च': 100}},

 0: {'a': {'': 100, 'ा': 100, 'ै': 0},
  'e': {'े': 100, '': 25},
  'i': {'ि': 100, 'ी': 100},
  'o': {'ो': 100},
  'u': {'ु': 100, 'ू': 12},
  'aa': {'ा': 100},
  'ae': {'ाए': 100, 'ै': 11, 'ए': 77},
  'ai': {'ै': 100, 'ाई': 16},
  'ao': {'ाओ': 100, 'ो': 23, 'ौ': 10, 'ओ': 48, 'ाव': 74},
  'au': {'ौ': 100, 'ाउ': 25},
  'ea': {'े': 54, 'ी': 27, 'ेआ': 100},
  'ee': {'ी': 100, 'ि': 9},
  'ei': {'े': 51, 'ेई': 72, 'ेइ': 100},
  'eo': {'ेओ': 100, 'ेव': 77, 'ियो': 44},
  'eu': {'ेउ': 100, 'ेयु': 28},
  'ia': {'ीया': 60, 'िआ': 46, 'ीअ': 86, 'ीआ': 40, 'िया': 100},
  'ie': {'िए': 100, 'ीए': 69, 'ाई': 62},
  'ii': {'ी': 100, 'ि': 25},
  'io': {'िओ': 100, 'ियो': 33, 'ीओ': 33},
  'iu': {'िउ': 65, 'ीउ': 65, 'ियु': 100, 'ीयु': 12},
  'oa': {'ो': 33, 'ोआ': 100},
  'oe': {'ोए': 100, 'ो': 41, 'ोइ': 25},
  'oi': {'ोइ': 100, 'ोई': 56},
  'oo': {'ू': 100},
  'ou': {'ौ': 100, 'ोउ': 26},
  'ua': {'ुआ': 100, 'ु': 5, 'ू': 5},
  'ue': {'ुए': 100},
  'ui': {'ुइ': 25, 'ुई': 100, 'ूइ': 25, 'ूई': 100},
  'uo': {'ुओ': 100, 'ुआ': 5},
  'uu': {'ुउ': 0, 'ूउ': 0, 'ुयु': 5, 'ू': 100},
  'aaa': {'ा': 21, 'आ': 100, 'ाआ': 21},
  'aae': {'ाए': 100, 'ाई': 5, 'ाइ': 5},
  'aai': {'ाइ': 16, 'ाई': 100, 'ाऐ': 50},
  'aao': {'ाओ': 100, 'ाऊ': 5},
  'aau': {'ाऊ': 100, 'ाउ': 33, 'औ': 66, 'ाअु': 0, 'ाऔ': 66, 'आव': 66},
  'aea': {'ई': 75, 'ाई': 75, 'इ': 0, 'एय': 100},
  'aee': {'ई': 100, 'ाई': 42, 'इ': 0, 'ी': 0},
  'aei': {'े': 33,'ई': 100,'ाई': 100,'ए': 16,'ेइ': 66,'ाइ': 0,'इ': 16,'ैइ': 0},
  'aeo': {'ेओ': 100},
  'aeu': {'ाएउ': 42, 'ेयु': 100, 'ईउ': 42},
  'aia': {'य': 0, 'या': 100, 'इआ': 14, 'ै': 0, 'य्या': 28},
  'aie': {'ाइ': 10, 'ैए': 100, 'ाईए': 24},
  'aii': {'ाई': 80, 'ैइ': 20, 'ई': 100},
  'aio': {'ैओ': 100, 'ाईओ': 100, 'ायो': 100},
  'aiu': {'ैयु': 100, 'ैयू': 75, 'ाईउ': 7, 'ाइउ': 5, 'ईउ': 12, 'ैउ': 62},
  'aoi': {'ओइ': 100, 'ाई': 100, 'ोई': 100},
  'aoo': {'ाऊ': 100, 'ऊ': 66},
  'aou': {'ावु': 25,'ऑउ': 16, 'ाओउ': 0, 'ौ': 100,'ाओ': 5,'ओउ': 5,'ोऊ': 5,'ोउ': 5,'ाउ': 5},
  'aua': {'ौआ': 100, 'ौ': 58, 'ाउ': 8},
  'aue': {'ौए': 100, 'ाउे': 11},
  'aui': {'ौई': 100, 'ौइ': 25},
  'auo': {'ौओ': 100, 'उओ': 8, 'ौऊ': 8, 'ऊओ': 33},
  'auu': {'ाउु': 0, 'ौउ': 100, 'ाऊ': 100},
  'eaa': {'ेआ': 100, 'िआ': 40},
  'eae': {'ेए': 100},
  'eai': {'इऐ': 100},
  'eao': {'ीओ': 100, 'ेव': 100},
  'eau': {'्यू': 100,'्यु': 25,'ेआउ': 0,'ेअऊ': 0, 'ेयू': 25,'ियु': 25,'ाउ': 0,'ीउ': 0,'ो': 75},
  'eea': {'ीए': 25, 'ीआ': 100},
  'eee': {'ी': 100, 'ीए': 11},
  'eei': {'िई': 100, 'ी': 100, 'ीई': 100},
  'eeu': {'ीउ': 33, 'ीयु': 100},
  'eia': {'ेया': 66, 'िया': 100},
  'eie': {'ेइए': 11, 'ी': 100},
  'eii': {'ेई': 66, 'ी': 100},
  'eiu': {'ेईयु': 100},
  'eoa': {'ेवा': 100, 'ीवा': 100},
  'eoe': {'ेवे': 100, 'ेओए': 25},
  'eoo': {'ेऊ': 100},
  'eou': {'ेओ': 100, 'ेऊ': 100, ' ेव': 50, 'ेओउ': 0},
  'eua': {'ेयूआ': 66, 'ेउआ': 100},
  'eue': {'ेयुए': 100, 'ेउे': 60, 'ियु': 40},
  'eui': {'ेउी': 100},
  'iaa': {'िआ': 100, 'ीआ': 100},
  'iae': {'िए': 100, 'ीए': 100},
  'iai': {'ीऐ': 100, 'िऐ': 100},
  'iau': {'ियाउ': 0,'िऔ': 100,'ीआउ': 10,'िआउ': 30,'ियाऊ': 0,'ीअु': 0,'िअउ': 0,'ीउ': 60},
  'iea': {'ीए': 80, 'िएअ': 0, 'िए': 20, 'िऐ': 0, 'िया': 100},
  'iee': {'िए': 0, 'ी': 100, 'ीई': 0, 'ीए': 11},
  'iei': {'िएइ': 5, 'िऐ': 100, 'ीइ': 5},
  'ieo': {'िव': 100},
  'ieu': {'ियू': 100},
  'iia': {'ीआ': 100, 'ीया': 0},
  'iie': {'िइए': 100, 'िए': 100},
  'iii': {'ीईइ': 0, 'ी': 100},
  'iiu': {'ीउ': 100, 'ीऊ': 100},
  'tion': {'शन':100},
  'ioa': {'िओआ': 0, 'िवा': 100},
  'ioe': {'ोए': 100},
  'ioi': {'ीओइ': 100, 'ओइ': 100},
  'ioo': {'िऊ': 100, 'ीऊ': 66},
  'iou': {'िओउ': 0,
   'ीयु': 0,
   'िउ': 40,
   'ियू': 60,
   'िय': 0,
   'ी': 0,
   'िओ': 100,
   'ीय': 0},
  'iua': {'िउआ': 100, 'िउ': 17, 'ीउ': 17},
  'iue': {'ियुए': 25, 'िउए': 100},
  'iui': {'ीउई': 66, 'िउई': 100},
  'iuo': {'िउओ': 25, 'ुओ': 100},
  'iuu': {'ियु': 28, 'ीयू': 100, 'ियू': 100, 'िऊ': 57},
  'oaa': {'ोआ': 100, 'ौ': 0},
  'oae': {'ोए': 100},
  'oai': {'ोऐ': 100},
  'oao': {'ोआओ': 100},
  'oau': {'ोआउ': 0, 'औ': 100, 'ोऔ': 25, 'ोअयु': 0},
  'oea': {'ोए़': 100, 'ोएआ': 0, 'ोयअ': 0, 'ोइ़': 50, 'ोऐ': 16},
  'oee': {'ोई': 100},
  'oei': {'ोए': 25, 'ोएइ': 0, 'ोई': 100},
  'oeo': {'ोएओ': 100},
  'oia': {'िया': 100},
  'oie': {'ोइए': 16, 'ोईए': 16, 'ोइ': 33, 'ोई': 100},
  'oii': {'ोई': 100, 'वई': 0},
  'oiu': {'ोइउ': 90, 'ोईउ': 90, 'ोईयु': 21, 'ीयू': 100},
  'ooa': {'ूअ': 11, 'ूआ': 100, 'ू': 0},
  'ooe': {'ूए': 100, 'ूई': 25},
  'ooi': {'ूइ': 25, 'ूई': 100},
  'ooo': {'ूओ': 16, 'ोऊ': 50, 'ू': 100},
  'oou': {'ूउ': 11, 'ोऊ': 100},
  'oua': {'ोवा': 100, 'ौ': 0, 'ोऊआ': 0, 'ौआ': 100},
  'oue': {'ौए': 100},
  'oui': {'ौइ': 20, 'ौई': 100, 'ुई': 60, 'ोइ': 20},
  'ouu': {'ोऊ': 100},
  'uaa': {'ुआ': 100, 'ुअ': 11},
  'uae': {'ुऐ': 100, 'ुअए': 11},
  'uai': {'ुआइ': 8, 'ुऐ': 100, 'ुआई': 8, 'ुई': 50},
  'uao': {'ुआओ': 100},
  'uau': {'ुआउ': 0, 'ुआऊ': 50, 'ुऔ': 100, 'ूऔ': 100},
  'uea': {'ुइ़': 50, 'ुए': 100, 'ो': 50},
  'uee': {'ि': 14, 'ुई': 100, 'ी': 100, 'ुवी': 71},
  'uei': {'िव': 25, 'ुइ': 100, 'ुएइ': 0},
  'ueu': {'उ': 100, 'ु': 49},
  'uia': {'ुई': 100, 'ुइआ': 0, 'ुवाई': 0, 'ुइ': 100},
  'uie': {'ुइए': 0, 'ुईए': 0, 'ुई': 100, 'ुइ': 42},
  'uii': {'ुई': 100},
  'uio': {'ुइओ': 0, 'िओ': 100, 'ीओ': 100},
  'uiu': {'ुईउ': 0, 'ुइऊ': 42, 'ुयु': 100},
  'uoe': {'ुओए': 0, 'ो': 66, 'ोए': 100},
  'uoi': {'ुओइ': 0, 'ोइ': 66, 'ोई': 100},
  'uoo': {'ुऊ': 25, 'ू': 100},
  'uua': {'ू': 5, 'ुऊ': 5, 'ूआ': 100},
  'uue': {'ूए': 100, 'ुए': 25},
  'uui': {'ूई': 100},
  'uuu': {'ु': 0, ' ू': 100},
  'aaaa': {'आआ': 100},
     #ADDED
  'aaao': {'ाओ': 100},
  'aaie': {'ाऐे': 100},
  'aaiu': {'ैयू': 100},
  'aiai': {'ऐऐ': 100, 'ऐ': 100},
  'aieo': {'ाइओ': 100},
  'aieu': {'ैयू': 100},
  'auaa': {'ौआ': 100},
  'auai': {'ौ': 100, 'अूअी': 100},
  'eaiu': {'ैयु': 100},
  'eeai': {'ेएै': 100},
  'iuai': {'िउाई': 100},
  'iuiu': {'िउइउ': 100},
  'oooo': {'ोोू': 100},
  'aaaaa': {'ा': 100, 'आआअ': 100},
  'aieai': {'ै': 100},
  'eeaiu': {'ेएैयु': 100},
  'eeeee': {'ी': 100},
  'oooooo': {'ू': 100},
  'aaaaaaaaa': {'ा': 100},
     #ADDED
  'aaai': {'ाऐ': 100},
  'aaee': {'ाइ': 100, 'ाऐ': 100, 'ाई': 100},
  'aaie': {'ऐे': 100},
  'aaii': {'ाई': 100},
  'aaoo': {'ाऊ': 100},
  'aaua': {'ाउआ': 100},
  'aauu': {'ाऊ': 100},
  'aeiu': {'ैइउ': 100},
  'aeoo': {'ाएऊ': 100},
  'aiaa': {'ैआ': 100},
  'aoa': {'ावा': 100, 'ाओ': 25, 'ाओआ': 0},
  'aoe': {'वे': 100, 'ावे': 100, 'ाओए': 0},
  'eeo': {'ीओ': 100, 'ीयो': 66},
  'eio': {'ेयो': 100},
  'eoi': {'ेवी': 100},
  'euo': {'्विओ': 100, 'ओ': 100, '्यूओ': 100, '्यो': 100},    
  'euu': {'ेऊ': 100, ' ीऊ': 25},
  'iao': {'िऔ': 100},
  'iio': {'ीओ': 100, 'ीयो': 66},
  'oeu': {'ोेऊ': 100},
  'oio': {'ोयो': 100},
  'ouo': {'ौओ': 100, 'वो': 25},
  'ueo': {'ुयो': 100},
  'uoa': {'ुवा': 100, 'ुओ': 25},
  'uou': {'ुओ': 100, 'ूओ': 25},
  'uuo': {'ूओ': 100, 'ूवो': 12, 'ुवो': 12}}}

#dictionary for characters in the end
dictl = {1: {'b': {'ब': 100},
  'c': {'क': 100},
  'd': {'ड़': 4, 'द': 100, 'ड': 11, 'ङ': 0},
  'f': {'फ़': 9, 'फ': 100},
  'g': {'ग': 100},
  'h': {'ह': 100},
  'j': {'ज': 100},
  'k': {'क': 100, 'क़': 0},
  'l': {'ल': 100},
  'm': {'म': 100, 'ं': 0},
  'n': {'न': 100, 'ं': 14, 'ँ': 0, 'ण': 28},
  'p': {'प': 100},
  'q': {'क': 29, 'क़': 100},
  'r': {'र': 100},
  's': {'स': 100},
  't': {'त': 100, 'ट': 14},
  'v': {'व': 100},
  'w': {'व': 100},
  'x': {'क्स': 100},
  'y': {'य': 100},
  'z': {'ज़': 100, 'ज': 100},
  'bh': {'भ': 100},
  'ch': {'च': 100, 'छ': 1},
  'dh': {'ध': 100, 'ड़': 9, 'ढ़': 55, 'ढ': 20},
  'gh': {'घ': 100},
  'jh': {'झ': 100},
  'kh': {'ख': 100, 'ख़': 0},
  'ny': {'न्य': 100},
  'ph': {'फ': 100, 'फ़': 17},
  'rh': {'ढ़': 100, 'ड़': 33},
  'sh': {'श': 100, 'ष': 17},
  'th': {'थ': 100, 'ठ': 6},
  'ye': {'ये': 100, 'ए': 42},
  'yi': {'ई': 16, 'यी': 100},
  'chh': {'छ': 100},
  'tch': {'च्': 100, 'च': 0},
  'tion': {'शन': 100}},
 0: {'a': {'ा': 100, '': 11},
  'e': {'े': 100, '': 20},
  'i': {'ी': 100, 'ि': 100},
  'o': {'ो': 100},
  'u': {'ु': 100, 'ू': 35},
  'aa': {'ा': 100, 'आ': 0},
  'ae': {'ाए': 66, 'ए': 100},
  'ai': {'ाई': 33, 'ई': 100, 'ाइ': 0, ' ै': 33},
  'ao': {'ाओ': 100, 'ओ': 16, 'ाव': 50},
  'au': {'ौ': 100, 'ाऊ': 66, 'यु': 0},
  'ea': {'ेआ': 100},
  'ee': {'ी': 100, 'ेए': 0},
  'ei': {'ेई': 100, 'ेइ': 28, 'ी': 14},
  'eo': {'ेव': 100, 'ेओ': 25},
  'eu': {'ेउ': 33, 'ेयु': 0, 'ु': 8, 'ेऊ': 100},
  'ia': {'िया': 100, 'िआ': 40, 'ीया': 60},
  'ie': {'ी': 100, 'िए': 25},
  'ii': {'ी': 100, 'िई': 0, 'ीई': 0, 'ई': 42},
  'io': {'िओ': 100, 'ीओ': 100, 'ियो': 100, 'ीयो': 100},
  'iu': {'िउ': 0,'ीउ': 0,'िऊ': 25,'ियु': 50,'ियू': 100,'ीयु': 25,'ीऊ': 25,'ीयू': 25},
  'oa': {'ोआ': 100, 'ोवा': 100},
  'oe': {'ोए': 100, 'ो': 42},
  'oi': {'ोई': 100, 'ोइ': 19},
  'oo': {'ू': 100},
  'ou': {'ू': 14, 'ौ': 100, 'ोयु': 0, 'ोऊ': 14, 'ोउ': 7, 'ो': 7, 'ॉउ': 0},
  'ua': {'ुआ': 100},
  'ue': {'ुए': 100, 'ुई': 12, 'ुइ': 12},
  'ui': {'ुई': 100, 'ुइ': 13},
  'uo': {'ुओ': 100, 'ुऑ': 11},
  'uu': {'ु': 0, 'ू': 100},
  'aaa': {'ा': 21, 'आ': 100, 'ाआ': 21},
  'aae': {'ाए': 100, 'ाई': 5, 'ाइ': 5},
  'aai': {'ाइ': 16, 'ाई': 100, 'ाऐ': 50},
  'aao': {'ाओ': 100, 'ाऊ': 5},
  'aau': {'ाऊ': 100, 'ाउ': 33, 'औ': 66, 'ाअु': 0, 'ाऔ': 66, 'आव': 66},
  'aea': {'ई': 75, 'ाई': 75, 'इ': 0, 'एय': 100},
  'aee': {'ई': 100, 'ाई': 42, 'इ': 0, 'ी': 0},
  'aei': {'े': 33,'ई': 100,'ाई': 100,'ए': 16,'ेइ': 66,'ाइ': 0,'इ': 16,'ैइ': 0},
  'aeo': {'ेओ': 100},
  'aeu': {'ाएउ': 42, 'ेयु': 100, 'ईउ': 42},
  'aia': {'य': 0, 'या': 100, 'इआ': 14, 'ै': 0, 'य्या': 28},
  'aie': {'ाइ': 10, 'ैए': 100, 'ाईए': 24},
  'aii': {'ाई': 80, 'ैइ': 20, 'ई': 100},
  'aio': {'ैओ': 100, 'ाईओ': 100, 'ायो': 100},
  'aiu': {'ैयु': 100, 'ैयू': 75, 'ाईउ': 7, 'ाइउ': 5, 'ईउ': 12, 'ैउ': 62},
  'aoi': {'ओइ': 100, 'ाई': 100, 'ोई': 100},
  'aoo': {'ाऊ': 100, 'ऊ': 66},
  'aou': {'ावु': 25,'ऑउ': 16,'ाओउ': 0,'ौ': 100,'ाओ': 5,'ओउ': 5,'ोऊ': 5,'ोउ': 5,'ाउ': 5},
  'aua': {'ौआ': 100, 'ौ': 58, 'ाउ': 8},
  'aue': {'ौए': 100, 'ाउे': 11},
  'aui': {'ौई': 100, 'ौइ': 25},
  'auo': {'ौओ': 100, 'उओ': 8, 'ौऊ': 8, 'ऊओ': 33},
  'auu': {'ाउु': 0, 'ौउ': 100, 'ाऊ': 100},
  'eaa': {'ेआ': 100, 'िआ': 40},
  'eae': {'ेए': 100},
  'eai': {'इऐ': 100},
  'eao': {'ीओ': 100, 'ेव': 100},
  'eau': {'्यू': 100,'्यु': 25,'ेआउ': 0,'ेअऊ': 0,'ेयू': 25,'ियु': 25,'ाउ': 0,'ीउ': 0,'ो': 75},
  'eea': {'ीए': 25, 'ीआ': 100},
  'eee': {'ी': 100, 'ीए': 11},
  'eei': {'िई': 100, 'ी': 100, 'ीई': 100},
  'eeu': {'ीउ': 33, 'ीयु': 100},
  'eia': {'ेया': 66, 'िया': 100},
  'eie': {'ेइए': 11, 'ी': 100},
  'eii': {'ेई': 66, 'ी': 100},
  'eiu': {'ेईयु': 100},
  'eoa': {'ेवा': 100, 'ीवा': 100},
  'eoe': {'ेवे': 100, 'ेओए': 25},
  'eoo': {'ेऊ': 100},
  'eou': {'ेओ': 100, 'ेऊ': 100, 'ेव': 50, 'ेओउ': 0},
  'eua': {'ेयूआ': 66, 'ेउआ': 100},
  'eue': {'ेयुए': 100, 'ेउे': 60, 'ियु': 40},
  'eui': {'ेउी': 100},
  'iaa': {'िआ': 100, 'ीआ': 100},
  'iae': {'िए': 100, 'ीए': 100},
  'iai': {'ीऐ': 100, 'िऐ': 100},
  'iau': {'ियाउ': 0,'िऔ': 100,'ीआउ': 10,'िआउ': 30,'ियाऊ': 0,'ीअु': 0,'िअउ': 0,'ीउ': 60},
  'iea': {'ीए': 80, 'िएअ': 0, 'िए': 20, 'िऐ': 0, 'िया': 100},
  'iee': {'िए': 0, 'ी': 100, 'ीई': 0, 'ीए': 11},
  'iei': {'िएइ': 5, 'िऐ': 100, 'ीइ': 5},
  'ieo': {'िव': 100},
  'ieu': {'ियू': 100},
  'iia': {'ीआ': 100, 'ीया': 0},
  'iie': {'िइए': 100, 'िए': 100},
  'iii': {'ीईइ': 0, 'ी': 100},
  'iiu': {'ीउ': 100, 'ीऊ': 100},
  'ioa': {'िओआ': 0, 'िवा': 100},
  'ioe': {'ोए': 100},
  'ioi': {'ीओइ': 100, 'ओइ': 100},
  'ioo': {'िऊ': 100, 'ीऊ': 66},
  'iou': {'िओउ': 0,'ीयु': 0,'िउ': 40,'ियू': 60,'िय': 0,'ी': 0,'िओ': 100,'ीय': 0},
  'iua': {'िउआ': 100, 'िउ': 17, 'ीउ': 17},
  'iue': {'ियुए': 25, 'िउए': 100},
  'iui': {'ीउई': 66, 'िउई': 100},
  'iuo': {'िउओ': 25, 'ुओ': 100},
  'iuu': {'ियु': 28, 'ीयू': 100, 'ियू': 100, 'िऊ': 57},
  'oaa': {'ोआ': 100, 'ौ': 0},
  'oae': {'ोए': 100},
  'oai': {'ोऐ': 100},
  'oao': {'ोआओ': 100},
  'oau': {'ोआउ': 0, 'औ': 100, 'ोऔ': 25, 'ोअयु': 0},
  'oea': {'ोए़': 100, 'ोएआ': 0, 'ोयअ': 0, 'ोइ़': 50, 'ोऐ': 16},
  'oee': {'ोई': 100},
  'oei': {'ोए': 25, 'ोएइ': 0, 'ोई': 100},
  'oeo': {'ोएओ': 100},
  'oia': {'िया': 100},
  'oie': {'ोइए': 16, 'ोईए': 16, 'ोइ': 33, 'ोई': 100},
  'oii': {'ोई': 100, 'वई': 0},
  'oiu': {'ोइउ': 90, 'ोईउ': 90, 'ोईयु': 21, 'ीयू': 100},
  'ooa': {'ूअ': 11, 'ूआ': 100, 'ू': 0},
  'ooe': {'ूए': 100, 'ूई': 25},
  'ooi': {'ूइ': 25, 'ूई': 100},
  'ooo': {'ूओ': 16, 'ोऊ': 50, 'ू': 100},
  'oou': {'ूउ': 11, 'ोऊ': 100},
  'oua': {'ोवा': 100, 'ौ': 0, 'ोऊआ': 0, 'ौआ': 100},
  'oue': {'ौए': 100},
  'oui': {'ौइ': 20, 'ौई': 100, 'ुई': 60, 'ोइ': 20},
  'ouu': {'ोऊ': 100},
  'uaa': {'ुआ': 100, 'ुअ': 11},
  'uae': {'ुऐ': 100, 'ुअए': 11},
  'uai': {'ुआइ': 8, 'ुऐ': 100, 'ुआई': 8, 'ुई': 50},
  'uao': {'ुआओ': 100},
  'uau': {'ुआउ': 0, 'ुआऊ': 50, 'ुऔ': 100, 'ूऔ': 100},
  'uea': {'ुइ़': 50, 'ुए': 100, 'ो': 50},
  'uee': {'ि': 14, 'ुई': 100, 'ी': 100, 'ुवी': 71},
  'uei': {'िव': 25, 'ुइ': 100, 'ुएइ': 0},
  'ueu': {'उ': 100, 'ु': 49},
  'uia': {'ुई': 100, 'ुइआ': 0, 'ुवाई': 0, 'ुइ': 100},
  'uie': {'ुइए': 0, 'ुईए': 0, 'ुई': 100, 'ुइ': 42},
  'uii': {'ुई': 100},
  'uio': {'ुइओ': 0, 'िओ': 100, 'ीओ': 100},
  'uiu': {'ुईउ': 0, 'ुइऊ': 42, 'ुयु': 100},
  'uoe': {'ुओए': 0, 'ो': 66, 'ोए': 100},
  'uoi': {'ुओइ': 0, 'ोइ': 66, 'ोई': 100},
  'uoo': {'ुऊ': 25, 'ू': 100},
  'uua': {'ू': 5, 'ुऊ': 5, 'ूआ': 100},
  'uue': {'ूए': 100, 'ुए': 25},
  'uui': {'ूई': 100},
  'uuu': {'ु': 0, ' ू': 100},
  'aoa': {'ावा': 100, 'ाओ': 25, 'ाओआ': 0},
  'aoe': {'वे': 100, 'ावे': 100, 'ाओए': 0},
  'eeo': {'ीओ': 100, 'ीयो': 66},
  'eio': {'ेयो': 100},
  'eoi': {'ेवी': 100},
  'euo': {'्विओ': 100, 'ओ': 100, '्यूओ': 100, '्यो': 100},
  'euu': {'ेऊ': 100, ' ीऊ': 25},
  'iao': {'िऔ': 100},
  'iio': {'ीओ': 100, 'ीयो': 66},
  'oeu': {'ोेऊ': 100},
  'oio': {'ोयो': 100},
  'ouo': {'ौओ': 100, 'वो': 25},
  'ueo': {'ुयो': 100},
  'uoa': {'ुवा': 100, 'ुओ': 25},
  'tion': {'शन':100},
  'uou': {'ुओ': 100, 'ूओ': 25},
  'uuo': {'ूओ': 100, 'ूवो': 12, 'ुवो': 12},
  'aaao': {'ाओ': 100},
  'aaie': {'ाऐे': 100},
  'aaiu': {'ैयू': 100},
  'aiai': {'ऐऐ': 100, 'ऐ': 100},
  'aieo': {'ाइओ': 100},
  'aieu': {'ैयू': 100},
  'auaa': {'ौआ': 100},
  'auai': {'ौ': 100, 'अूअी': 100},
  'eaiu': {'ैयु': 100},
  'eeai': {'ेएै': 100},
  'iuai': {'िउाई': 100},
  'iuiu': {'िउइउ': 100},
  'oooo': {'ोोू': 100},
  'aaaaa': {'ा': 100, 'आआअ': 100},
  'aieai': {'ै': 100},
  'eeaiu': {'ेएैयु': 100},
  'eeeee': {'ी': 100},
  'oooooo': {'ू': 100},
  'aaaaaaaaa': {'ा': 100},
     #ADDED
  'aaai': {'ाऐ': 100},
  'aaee': {'ाइ': 100, 'ाऐ': 100, 'ाई': 100},
  'aaie': {'ऐे': 100},
  'aaii': {'ाई': 100},
  'aaoo': {'ाऊ': 100},
  'aaua': {'ाउआ': 100},
  'aauu': {'ाऊ': 100},
  'aeiu': {'ैइउ': 100},
  'aeoo': {'ाएऊ': 100},
  'aiaa': {'ैआ': 100},  }}
#Dictionary for single characters
exact_hin = {'a': 'ए','b': 'बी','c': 'सी','d': 'डी','e':'ई','f':'एफ','g':'जी','h':'एच','i':'आई','j':'जे','k':'के','l':'एल', 'm': 'एम','n': 'एन','o': 'ओ','p': 'पी','q': 'क्यू','r': 'आर','s': 'एस','t': 'टी','u': 'यू','v': 'वी','w': 'डब्ल्यू','x': 'एक्स',         'y': 'व्हाई','z': 'ज़ेड','Dr.': 'डा','tax': 'टैक्स','office': 'ऑफिस','smt':'श्रीमती'}


def wrd_break(w):
    #Function for breaking an english word about vyanjan
    w = w.lower()
    w1 = []
    xt = ()
    for i in dict_en3:
        xt += tuple((m.start(),len(i)) for m in re.finditer(i, w))
    for i in dict_en2:
        xt += tuple((m.start(),len(i)) for m in re.finditer(i, w))
    for i in dict_en1:
        xt += tuple((m.start(),len(i)) for m in re.finditer(i, w))
   
    yt = tuple((i,i+j) for i,j in xt)
    yt = sorted(list(yt),key = lambda x: x[0])
    
    if len(yt)>0:
        fin = [yt[0]]                                           #consonent
                                                   
        for i in yt[1:]:        
            if i[0]>=fin[-1][1]:
                fin.append(i)
                                                                  
        bin = [1]*len(fin)                                      #no df consonents in that string
        fin1 = fin.copy()
        if fin[0][0] != 0:
            fin1.insert(0,(0,fin[0][0]))
            bin.insert(0,0)
        
        prev = fin[0]
        for i in fin[1:]:
            if i[0]>prev[1]:
                ind = fin1.index(i)
                fin1.insert(ind,(prev[1],i[0]))
                bin.insert(ind,0)
            
            prev = i
        if fin[-1][1] < len(w):
            fin1.append((fin[-1][1],len(w)))
            bin.append(0)
        fin2 = []
        cnt = -1
        for i in fin1:
            cnt = cnt + 1
            
            if( i[1] - i[0] > 3 and w[i[0]:i[1]] != 'tion'):  #not in dictm or dictf or dictl or half
                p = i[0]
                curr_len = i[1]-i[0]
                while(p<i[1]):
                    fin2.append((p,min(p+2,i[1])))
                    if(p!=i[0]):
                        bin.insert(len(fin2)-1,0)
                    p = p + 2    
                
            else:
                fin2.append(i);
                
        for i in bin:
            #print(i)
            fin1 = []        
            fin1 = fin2
        for i in fin1:
            w1.append(w[i[0]:i[1]])
       
        return w1,bin
    return [w,[0]]

def hin_translate(w):
    #Function for translating the split characters from english to hindi
    w,b = wrd_break(w) #List of characters split about vyanjan
    temw = []
    finw = []
    temw1 = []
    #finw.append(dictf[b[0]][w[0]])
    for i in range(len(b)-1):
        if b[i+1] == 1 and b[i] == 1:
            finw.append(half[w[i]])
        elif i == 0:
            finw.append(dictf[b[i]][w[i]])
        else:
            finw.append(dictm[b[i]][w[i]])
    
    finw.append(dictl[b[-1]][w[-1]])
    q = PriorityQueue()
    #print(finw)
    for i in finw[0]:
        q.put((-1*finw[0][i], i))
    
    for i in range(1,len(finw)):
        qtemp = PriorityQueue()
        while not q.empty():
            temp = q.get()
            for j in finw[i]:  
                qtemp.put((temp[0]+(-1 *finw[i][j]),temp[1]+j))
          
        q1= PriorityQueue()
        q = q1
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

def Eng_Hindi_Transliteration(d,a):
    
    lis = sorted(d.items(), key = lambda kv:kv[1],reverse = True)
    sorted_lis = []
    for i in lis:
        sorted_lis.append(i[0])

    #sorted_lis.append(a)

    for i in hin_translate(a):
        if( i not in d):
            sorted_lis.append(i)
    
    return sorted_lis

def Database_Search_English(a):
    a = a.capitalize()
    
    connection = psycopg2.connect(user="postgres",                             #Make Changes Here
                                      password="DdA9s1kxHm65vw8i",
                                      host="34.131.254.179",
                                      port="5432",
                                      database="mridul_db")
    cursor = connection.cursor()
    try:
        cursor.execute("""SELECT HINDI from ENG_HINDI_DICTIONARY_new1 where english = '%s';"""%a)
        d = cursor.fetchall()
        d = d[0][0]
        sorted_list = Eng_Hindi_Transliteration(d,a)
        return sorted_list
    
    except:
        
        return hin_translate(a) 


# #file = str(input())
# lis_argv = sys.argv
# #print(lis_argv[1:])
# df = pd.read_excel(lis_argv[1])
# lis_unique=[]

# if(len(lis_argv)>2):
#     columns = []
#     for i in lis_argv[2:]:
#         a1 = int(i.split(':')[0])
#         try:
#             b1 = int(i.split(':')[1])
#         except:
#             b1 = a1
#         columns.extend(list(df.columns[a1-1:b1]))
# else:
#     columns = list(df.columns)
        
# for column in columns:
#     unique = list(df[column].drop_duplicates())
#     lis_unique = lis_unique + unique


# lis_split = []
# for i in range(0,len(lis_unique)):
#     #lis_split.append(re.split(r"[^a-zA-Z]",str(lis_unique[i])))
#     lis_split.append(re.sub("\s+"," ",re.sub("[^a-zA-Z]"," ",str(lis_unique[i]))).strip().split(" "))

# flatlist = []
# for elem in lis_split:
#     flatlist.extend(elem)
# lis_dis = set(flatlist)
# lis_dis = list(lis_dis)


# for i in range(0,len(lis_dis)):
#     lis_dis[i] = lis_dis[i].lower()

  
# lis_dis_lower = set(lis_dis)


# d_new = {}

# for key in lis_dis_lower:
    
#     try:

#         d_new[key] = Database_Search_English(key)[0]

#     except:
#         continue
        
# global settemp
# settemp = set()
# def tran(w_list,wrd):

#     for i in w_list:
#         try:
#             wrd = wrd.replace(i,d_new[i.lower()])
#         except:
#             #settemp.add((i))
#             wrd = wrd.replace(i,"")
#             continue
#     return wrd

# for column in columns:
#     #print(column)
#     if column == "BM_split":
#         continue
#     df['BM_split'] = df[column].apply(lambda x: sorted(list(set(filter(None,re.sub("\s+"," ",re.sub("[^a-zA-Z]"," ",str(x))).strip().split(" ")))), key=len, reverse = True) if x==x else [])
    
#     df[column +'_Hindi'] = df[["BM_split",column]].apply(lambda x: tran(*x), axis = 1)
#     del df["BM_split"]
    
# df.to_excel(r'%s_Hindi.xlsx'%lis_argv[1].split("\\")[-1], index= False)



    
        





















