# -*- coding: utf-8 -*-
"""
Created on Fri Nov 30 16:22:50 2018

@author: li
"""
import pickle
import numpy as np
import time
import sys
start = time.time()

# =============================================================================
# function area

def bin2str(file_data):
    '''
    transform the int back to 0/1 string
    for every int, if the lence of its bits are less than 8, add 0
    use the add_0_num to remove the supplement 0 when compress
    code_str: the 0/1 string
    '''
    code_str = ''
    add_0_num = file_data[-1]
    for i in file_data[:-1]:
        code_bin = bin(i)[2:] # remove '0b' beforehand
        if len(code_bin) != 8:
            code_bin = '0' * (8-len(code_bin)) + code_bin
        code_str += code_bin
    return code_str[:-add_0_num] # remove 0
# =============================================================================
 
filename = sys.argv[1].replace('.bin', '')
f = open(filename+ '.bin', 'rb')
file_data = f.read()
f.close()
with open(filename + '-symbol-model.pkl', 'rb') as f:
    code_dic = pickle.load(f)
code_to_word = {v:k for k,v in code_dic.items()}
code_str= bin2str(file_data) # get the whole 0/1 string
index = 0
letter = ''
lence = len(code_str)
# loop when there is no more useful element in the code_str
# ignore the supplement 0
while index < lence:
    # there is no lence of single code longer than 20
    # code_to_word: {code: word/char}
    for i in range(20):
        if code_str[index:index + i + 1] in code_to_word.keys():
            letter += code_to_word[code_str[index:index + i + 1]]
            index += i + 1
            break

f = open(filename + '-decompressed.txt', 'w')
f.write(letter)
f.close()

end = time.time()
print('decode:',end - start)
