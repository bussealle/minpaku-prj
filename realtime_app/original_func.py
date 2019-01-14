# -*- coding: utf-8 -*-
# User Defined Functions

def remove_parenthesis(text):
    text = text.replace('(','（').replace(')','）')
    before = text.find('（')
    after = text.find('）')
    if before==-1 or after==-1:
        return text
    else:
        return remove_parenthesis(text[:before] + text[after+1:])

def make_touple(row,col):
    result = []
    for r in range(1,row+1):
        for c in range(1,col+1):
            result.append((r,c))
    return result
