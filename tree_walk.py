#coding:utf-8
import os,sys

def GetPath(arg):
    for dpath, dnames, fnames in os.walk(arg):    
        path=[]
        for fname in fnames:
            if fname.endswith('.idl'):
                path.append(dpath+'/'+fname)
            if path:
                print path

if __name__ == '__main__':
    GetPath(sys.argv[1])


