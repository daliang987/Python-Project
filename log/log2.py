#-*- coding: UTF-8 -*
# author:wangdaliang

import os
import getopt
import sys
import re


def usage():
    print
    print "usage: log.py [options]"
    print
    print 'Options:'
    print "  -f	--file		set the log file "
    print "  -d	--d		set the log dir "
    print "  -o	--output	set the result file path"
    print "  -k	--keyword 	find the keyword in the log. example: -k \"post 200\" or -k \"or main.jsp login.jsp\""
    print "  -e	--exclude 	find the keyword exclude the word"
    print "  -s	--split  	split the log file with MB size  example:-s 'logfile.log 50'"
    print "  -v	--verbose	show the result in the console"
    print "  -h	--help		show this help"
    print
    print "  Example:python log.py -f access20171011.log -o result.txt -k 'post 200' -v"
    print




def splitfile(fromfile, todir, msize=50):
    kilobytes = 1024
    megabytes = kilobytes * 1024
    chunksize = int(msize * megabytes)
    if not os.path.exists(todir):
        os.mkdir(todir)
    else:
        for name in os.listdir(todir):
            os.remove(os.path.join(todir, name))  # del all dir files

    partnum = 0
    with open(fromfile, 'rb') as inputfile:
        while True:
            chunk = inputfile.read(chunksize)
            if not chunk:
                break
            partnum += 1
            filename = os.path.join(todir, ('%s_%04d.log' %(fromfile, partnum)))
            with open(filename, 'wb') as outfile:
                outfile.write(chunk)
                print 'spliting the file,%s is already complted' % filename
    return partnum
    


def get_keyword(keyword, line,ignorecase,exclude):

    if ignorecase:
        line1=line.lower()
        keyword=keyword.lower()
        exclude=exclude.lower()

    if exclude:
        excludes=exclude.split(' ')
        for e in excludes:
            if line1.find(e)>=0:
                return None
            else:
                if keyword is None:
                    return line

    if keyword:
        keywords = keyword.split(' ')
        # print keywords
        andflag = True
        if keywords[0] == 'or':
            for k in keywords[1:]:
                if line1.find(k)>=0:
                    return line
                    break
        else:
            for k in keywords:
                if line1.find(k)<0:
                    andflag=False
                    break

            if andflag == True:
                return line

if __name__ == "__main__":
    logfiles = []
    output = False
    resultfile = None
    todir=None
    msize=0
    ignorecase=False
    verbose = False
    keyword=None
    exclude=None

    try:
        opts, args = getopt.getopt(sys.argv[1:], "k:e:s:d:f:o:ivh", [
            "keyword=","exclude=","split=","dir=", "file=", "output=", "ignorecase","verbose", "help"])

    except getopt.GetoptError:
        usage()
        sys.exit()

    for name, value in opts:
        # print name,'-->',value
        if name in ("-h", "--help"):
            usage()

        if name in ("-d", "--dir"):
            dir = value
            for f in os.listdir(dir):
                if f.endswith('.log'):
                    logfiles.append(os.path.join(dir,f))

        if name in ("-f", "--file"):
            file = value
            logfiles.append(file)
        if name in ("-o", "--output"):
            output = True
            resultfile = value
            result=open(resultfile,'a')
        if name in ("-v", "--verbose"):
            verbose = True
        if name in ("-k", "--keyword"):
            keyword = value
        if name in ("-e","--exclude"):
            exclude=value
			
        if name in ("-i","--ignorecase"):
			ignorecase=True

        if name in ("-s","--split"):
            todir=value.split(" ")[0]
            msize=value.split(" ")[1]
            if len(logfiles)==1:
                filenum=splitfile(logfiles[0],todir,int(msize))
                print 'file split completed,%d files created' % filenum
        

        if len(logfiles):
            for log in logfiles:
                with open(log, 'r') as flog:
                    for line in flog.readlines():
                        if verbose:
                            if get_keyword(keyword, line,ignorecase,exclude):
                                print get_keyword(keyword,line,ignorecase,exclude)

                        if output:
                            if get_keyword(keyword,line,ignorecase,exclude):
                                result.write(get_keyword(keyword, line,ignorecase,exclude))
