# -*- coding: utf-8 -*-
"""
Created on Sun Dec  2 13:11:46 2018

@author: li
"""

import re
import numpy as np
import time

# =============================================================================
#  function area

def splitChar(pattern):
    '''
    use pattern to complie every line in the txt
    split the compile output to single charactor and store in char_list
    '''
    with open(filename + '.txt', 'r') as file:
        char_list = []
        line = file.readline()
        while line:
            element_list = pattern.findall(line)
            for index in np.arange(len(element_list)):
                single_char = ''.join(element_list[index])
                char_list.extend(single_char)
            char_list.extend('\n')
            line = file.readline()
    return char_list

def splitWord(pattern):
    '''
    use pattern to complie every line in the txt
    split the compile output to single charactor and store in char_list
    '''
    with open(filename + '.txt', 'r') as file:
        char_list = []
        line = file.readline()
        while line:
            element_list = pattern.findall(line)
            char_list += element_list
            line = file.readline()
    return char_list

def freqCounter(char_list):
    '''
    use Counter to count every element in the list and return the frequency
    '''
    import collections
    counter = collections.Counter(char_list)
    return counter

def sort_freq(dic):
    '''
    sort the frequency dictionary by the value
    the value is frequency of this keyword in the text
    '''
    sorted_freq = sorted(dic.items(), key=lambda x: x[1], reverse=True)
    freq_dic = {}
    for i in np.arange(len(sorted_freq)):
        freq_dic[sorted_freq[i][0]] = sorted_freq[i][1]
    return freq_dic

def heapProcess(freq_dic):
    '''
    freq_dic: {word/char : freq}
    sorted_heap is actually the codebook
    '''
    import heapq
    # create heap
    heap = []
    # add freq and code lists into heap
    for k,v in freq_dic.items():
        heap.append([v, [k, '']]) #[freq, [word/char, str]]
    # transform list "heap" into a heap
    heapq.heapify(heap)
    # loop until every element in the heap is processed
    while len(heap) > 1:
        # pop and return the smallest item
        min1 = heapq.heappop(heap) 
        min2 = heapq.heappop(heap)
        # loop and code every word/char in the two pop heap
        # word_code_list is [word/char, code]
        for i in np.arange(len(min1[1:])):
            min1[1+i][1] = '0' + min1[1+i][1]
        for i in np.arange(len(min2[1:])):
            min2[1+i][1] = '1' + min2[1+i][1]
        # add them together and insert back
        heapq.heappush(heap, [min1[0] + min2[0]] + min1[1:] + min2[1:])
    # sort the heap
    inner_list = heapq.heappop(heap)[1:]
    sorted_heap = sorted(inner_list, key=lambda p: (len(p[1]), p))
    return sorted_heap

def codeStr(text, code_dic):
    '''
    parametres:
    text: the whole char/word/symbol in the orignal text
    code_dic: {char/word : code}
    return:
    code_str_list: the encode string by 8 bits in a list
    num: the num of supplement 0
    '''
    # get code for every char/word
    code_string = ''
    for item in text:
        code_string += code_dic[item]
    # if the lence of whole 0/1 string can not divide equally, add 0 in the end
    # also, compress the number of supplement 0
    if len(code_string) % 8 != 0:
        num = len(code_string) % 8
        code_string += (8 - num) * '0'
    else:
        num = 8
    add_0_num = 8 - num
    # store the code_string by 8 bits in a list
    code_str_list = [code_string[i:i+8] for i in range(0, len(code_string), 8)]
    return code_str_list, add_0_num

def codeArray(code_str_list, add_0_num):
    '''
    code_str_list: the encode string by 8 bits in a list
    add_0_num: supplement 0
    '''
    import array
    codearray = array.array('B')
    # transform every binary into int
    for i in np.arange(len(code_str_list)):
        c = code_str_list[i]
        codearray.append(int(c, 2))
    # store the supplement 0
    codearray.append(add_0_num)
    f = open(filename + '.bin', 'wb')
    codearray.tofile(f)
    f.close()

def buildPkl(code_dic):
    '''
    code_dic: the codebook
    '''
    import pickle
    #open the .pkl file for storing the codebook
    with open(filename + '-symbol-model.pkl', 'wb') as f:
        pickle.dump(code_dic,f)
    f.close()

def compress(text):
    start0 = time.time()
    # sort the freq
    word_freq = freqCounter(text) 
    freq_dic = sort_freq(word_freq) 
    # heap process and build codebook
    sorted_heap = heapProcess(freq_dic) 
    # transform the codebook into dic
    ele_code_dic = {}
    for lis in sorted_heap:
        ele_code_dic[lis[0]] = lis[1] 
    end0 = time.time()
    # construct the 0/1 string
    code_str_list, add_0_num = codeStr(text, ele_code_dic)
    # compress into .bin
    codeArray(code_str_list, add_0_num)
    # store codebook
    buildPkl(ele_code_dic)
    end1 = time.time()
    return end0 - start0, end1 - end0, add_0_num
# =============================================================================
#get the parametre from command line
import sys
symbolmodel = sys.argv[2] 
filename = sys.argv[3].replace('.txt', '')

# set the default parametre
if not(symbolmodel):
    symbolmodel= "char" 
else:
    symbolmodel = symbolmodel

# choode 'char' or 'word'
if symbolmodel == "char":
    pattern = re.compile(r'.')
    text = splitChar(pattern)
    sym_time, encode_time, add_0_num= compress(text)

if symbolmodel == "word":
    pattern = re.compile(r'\w+|[^\w]')
    text = splitWord(pattern)
    sym_time, encode_time, add_0_num= compress(text)

print('budil symbol models:',sym_time, 'encode:', encode_time)