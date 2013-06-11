# -*- encoding: utf-8 -*-
from report.interface import report_int
from report_tools import pdf_fill
from openerp.osv import fields, osv

import pooler
from num2word import num2word_th
import datetime

def fmt_tin(tin):
    return "%s %s%s%s%s %s%s%s%s %s"%(tin[0],tin[1],tin[2],tin[3],tin[4],tin[5],tin[6],tin[7],tin[8],tin[9])

def fmt_pin(pin):
    return "%s %s%s%s%s %s%s%s%s%s %s%s %s"%(pin[0],pin[1],pin[2],pin[3],pin[4],pin[5],pin[6],pin[7],pin[8],pin[9],pin[10],pin[11],pin[12])

def set_satang(vals):
    for key in vals.keys():
        if key.startswith("tax"):
            amt=vals[key]
            vals[key]=int(amt)
            vals[key.replace("tax","st")]=int(amt*100.0)%100

def fmt_thaidate(date):
    dt=datetime.datetime.strptime(date,"%Y-%m-%d")
    return "%2d/%d/%d"%(dt.day,dt.month,dt.year+543) 


class report_custom(report_int):
    def create(self,cr,uid,ids,datas,context={}):
        print "WHT PND3 Report"      
        pool=pooler.get_pool(cr.dbname)
        lang=pool.get("res.lang").browse(cr,uid,1)      
        user=pool.get("res.users").browse(cr,uid,uid)
        vouch = pool.get("ineco.wht.pnd").browse(cr,uid,ids[0])          
        company = vouch.company_id
        
        year=int(vouch.date_pnd[0:4])+543
        month=int(vouch.date_pnd[5:7]) - 1
        day=int(vouch.date_pnd[8:10])
                        
        daynow = datetime.datetime.now().day
        monthnow  = datetime.datetime.now().month
        yearnow = int(datetime.datetime.now().year)+543
               
        typepnd = 0
        section3 = ""
        section48 = ""
        section50 = ""
        attachpnd = ""
        
        if vouch.type_normal == True:
            typepnd = 0
        else:
            typepnd = 1
        if  vouch.section_3 == True:
            section3 = "Yes"
        if  vouch.section_48 == True:
            section48 = "Yes"
        if  vouch.section_50 == True:
            section50 = "Yes"        
        if  vouch.attach_pnd == True:
            attachpnd = "Yes"             

        vals={
            "Text2":company.ineco_tax,
            "Text4":company.ineco_branch,
            "Text5":company.ineco_company_name,
            "Text6":company.ineco_building,
            "Text7":company.ineco_room_no,
            "Text8":company.ineco_class,
            "Text9":company.ineco_village,
            "Text10":company.ineco_no,
            "Text11":company.ineco_moo,
            "Text12":company.ineco_alley,
            "Text13":company.ineco_road,
            "Text14":company.ineco_district,
            "Text15":company.ineco_amphoe,
            "Text16":company.ineco_province,
            "Text17":company.ineco_zip,
            "Text18":company.ineco_phone,
            "Text19":vouch.attach_count,
            "Text22":year,
            "Text46":vouch.attach_no,
            "Text51.2":lang.format("%.2f",vouch.total_amount,grouping=True).replace("."," "),
            "Text51.3":lang.format("%.2f",vouch.total_tax,grouping=True).replace("."," "),
            "Text51.4":lang.format("%.2f",vouch.add_amount,grouping=True).replace("."," "),
            "Text51.5":lang.format("%.2f",vouch.total_tax_send,grouping=True).replace("."," "),
            "Text55":"      "+ company.ineco_position,
            "Text54":"      "+ company.ineco_name,
            "Text56":daynow,  
            "Text57":"    "+ str(monthnow),  
            "Text58":yearnow,   
            "'Check Box6'": section3,
            "'Check Box7'": section48,
            "'Check Box8'": section50,
            "'Check Box36'": attachpnd,
            "'Radio Button23'":month ,
            "'Radio Button19'":typepnd ,
        }

        pdf=pdf_fill("openerp/addons/ineco_thai_account/report/pdf/wht_pnd3.pdf",vals)
        return (pdf, "pdf")

report_custom("report.wht.pnd3")
