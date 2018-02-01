# encoding=utf-8
from urlparse import urlparse
from xml.dom.minidom import parse
import xml.dom.minidom
import httplib
import sys
import getopt
import json
import time


def usage():
    print
    print 'python soaptest.py [options]'
    print
    print '-u --url     input the wcm url'
    print '-f --file    input the wcm url list file'
    print '-o --output  set the result file'
    print
    print 'python testsoap.py -u http://192.168.51.63:8080/wcm -o a.txt'
    print 'python testsoap.py -f wcm.txt -o a.txt'


def outputtxt(filename, result):
    with open(filename, 'a') as f:
        f.write(result)


def getSoap(url_str, service):
    try:
        url = urlparse(url_str)
        host = url.hostname
        port = url.port
        conn = httplib.HTTPConnection(host, port, timeout=5)
        conn.request('GET', '/wcm/services/%s?wsdl' % service)
        resp = conn.getresponse()
        # print resp.status
        xmltext = resp.read()
        return xmltext
    except Exception, e:
        print str(e)
        return str(e)


def setValue(valueType):
    if valueType == 'soapenc:string':
        return 'html'
    elif valueType == 'soapenc:base64Binary':
        return 'dHJzIHRlc3QgZmlsZQ=='
    elif valueType == 'xsd:boolean':
        return 'false'
    elif valueType == 'xsd:int':
        return '2'
    else:
        return 'cid:1262397780768'


def formatSoap(xmltext):
    try:
        reqtext = {}
        DOMTree = xml.dom.minidom.parseString(xmltext)
        wsdl_definitionsion = DOMTree.documentElement
        # if wsdl_definitionsion.hasAttribute("targetNamespace"):
            # print "SOAP NAME : %s" % wsdl_definitionsion.getAttribute("targetNamespace")

        messages = wsdl_definitionsion.getElementsByTagName("wsdl:message")

        for soapmethod in messages:
            if soapmethod.hasAttribute("name") and soapmethod.getAttribute('name').endswith('Request'):
                methodname = soapmethod.getAttribute("name")
                soapstr = '''<soapenv:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:impl="http://impl.service.trs.com">\n<soapenv:Header/>\n<soapenv:Body>\n'''

                if methodname:
                    soapstr += '<impl:%s soapenv:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">\n' % soapmethod.getAttribute('name')[
                                                                                                                                         0:-7]

                parts = soapmethod.getElementsByTagName('wsdl:part')

                for part in parts:
                    if part.hasAttribute('name') and part.hasAttribute('type'):
                        soapstr += '<%s xsi:type="%s" xmlns:soapenc="http://schemas.xmlsoap.org/soap/encoding/">%s</%s>\n' % (
                            part.getAttribute('name'), part.getAttribute('type'), setValue(part.getAttribute('type')), part.getAttribute('name'))

                soapstr += "</impl:%s>\n" % soapmethod.getAttribute('name')[0:-7]
                soapstr += "</soapenv:Body>\n"
                soapstr += "</soapenv:Envelope>"

                reqtext[methodname] = soapstr
        return reqtext
    except Exception, e:
        print str(e)
        return str(e)


def SoapServiceTest(url_str, service, reqstr):
    try:
        url = urlparse(url_str)
        host = url.hostname
        port = url.port
        conn = httplib.HTTPConnection(host, port, timeout=5)
        conn.request('POST', '/wcm/services/%s' %
                     service, reqstr, headers={'SOAPAction': '""'})
        resp = conn.getresponse()
        # print resp.status

        if resp.status != 401:
            return 'danger'
        else:
            return 'safe'
    except Exception, e:
        print str(e)
        return str(e)


if __name__ == "__main__":

    opts, args = getopt.getopt(sys.argv[1:], "hf:u:o:")
    output = ""
    all_url = []

    if len(sys.argv) < 2:
        usage()

    for name, value in opts:
        if name in ("-f", "--file"):
            all_url = open(value, 'r').readlines()
        if name in ("-u", "--url"):
            all_url.append(value)
        if name in ("-o", "--output"):
            output = value

    services = ['trswcm:UploadService', 'trswcm:ImportService', 'trswcm:GetChannelInfoService',
    'trswcm:GetSOAPInfoService', 'trswcm:SOAPService', 'trswcm:InfoViewService',
    'trswcm:EPressImporte', 'trswcm:ImportServiceViaFtp', 'trswcm:WCMOnlineService', 'urn:FileService', 'trswcm:MetaDataImportService']

    try:
        for url_str in all_url:
            print url_str
            url = urlparse(url_str)
            for service in services:
                print
                print '%s://%s%s/wcm/services/%s' % (url.scheme, url.hostname, ':' + str(url.port) if url.port else ':80', service)
                print '-' * 45
                if output:
                    outputtxt(output, '\n%s://%s%s/wcm/services/%s\n' % (url.scheme, url.hostname, ':' + str(url.port) if url.port else ':80', service))
                    outputtxt(output, '-' * 45 + '\n')

                xmltext=getSoap(url_str, service)
                if xmltext.find('wsdl:definitions') > 0:
                    reqtext=formatSoap(xmltext)
                    for methodname, txt in reqtext.items():
                        # print txt
                        print '|%-30s |%10s |' % (methodname[0:-7], SoapServiceTest(url_str, service, txt))
                        print '-' * 45
                        if output:
                            outputtxt(output, '|%-30s |%10s |\n' %
                                      (methodname[0:-7], SoapServiceTest(url_str, service, txt)))
                            outputtxt(output, '-' * 45 + '\n')
                else:
                    print xmltext
                    if output:
                        outputtxt(output, xmltext + '\n')
                        outputtxt(output, '-' * 45 + '\n')
            print
            print '#' * 80
            print
            if output:
                outputtxt(output, '\n')
                outputtxt(output, '#' * 80 + '\n')
    except Exception as e:
        print str(e)
