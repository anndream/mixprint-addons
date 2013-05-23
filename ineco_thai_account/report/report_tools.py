# -*- encoding: utf-8 -*-
import os
#from osv import osv
#import xmlrpclib
#import cStringIO as StringIO

#jy_serv = xmlrpclib.ServerProxy("http://localhost:9999/")

def safe_unicode(obj, *args):
    """ return the unicode representation of obj """
    try:
        return unicode(obj, *args)
    except UnicodeDecodeError:
        # obj is byte string
        ascii_text = str(obj).encode('string_escape')
        return unicode(ascii_text)

def safe_str(obj):
    """ return the byte string representation of obj """
    try:
        return str(obj)
    except UnicodeEncodeError:
        # obj is unicode
        return unicode(obj).encode('utf-8')

def decode_vals(vals): #need to format for str and unicode object-
    dc={}
    for k,v in vals.items():
        k,v = unicode(k),safe_unicode(v) # key and value must the same type str,str
        dc[k]=v
    return dc

def pdf_fill(orig_pdf, vals):
    vals=decode_vals(vals)
    orig_pdf_abs=os.path.join(os.getcwd(),orig_pdf)
    tmp=os.tempnam()
    #print 'filling pdf',orig_pdf,tmp,vals
    #jy_serv.pdf_fill(orig_pdf_abs,tmp,vals)
    arg = ''
    for key in vals.keys():
        arg = arg + "%s='%s' " % (key, vals[key])
    cmd = "%s/openerp/addons/ineco_thai_account/report/fillpdf.py %s %s %s" % (os.getcwd(), orig_pdf_abs, tmp, arg)
    print cmd
    os.system(cmd)
    pdf=file(tmp).read()
    os.unlink(tmp)
    return pdf
