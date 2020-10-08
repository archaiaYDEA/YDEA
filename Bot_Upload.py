#!/usr/bin/env python
# coding: utf-8

# In[9]:


import pandas as pd
import pywikibot 
import re
import requests

site = pywikibot.Site("wikidata", "wikidata")
repo = site.data_repository()

df = pd.read_csv('Dura_Europos.csv')
df['ID']=df['ID'].astype(str)
sample=df[0:50]
df['ObjectNumber']=df['ObjectNumber'].astype(str)

### FIND ITEMS ALREADY IN WIKIDATA
URL = "https://query.wikidata.org/sparql?query= SELECT ?item ?ID WHERE {?item wdt:P8583 ?ID . SERVICE wikibase:label { bd:serviceParam wikibase:language 'en' . }} &format = JSON"
headers = {"User" : "DuraEuroposBot/0.0 (https://www.wikidata.org/wiki/User_talk:Valeriummaximum) pywikibot_data_import",
           "Accept" : "application/json"
          }
read = requests.get(URL, headers=headers)
read=read.json()

items = []
ids = []
for item in read['results']['bindings']:
    val = item['item']['value']
    val2 = item['ID']['value']
    Qid = re.sub(r'.*/','',val)
    items.append(Qid)
    ids.append(val2)
d = {'Qid': items, 'ID':ids}
wikidata_items = pd.DataFrame(d)

for artifact in sample.itertuples(index=False):
    
    ### Wikidata property claims
    prop_ID= pywikibot.Claim(repo, u'P8583') 
    prop_Collection = pywikibot.Claim(repo, u'P195')
    Inventory_qual = pywikibot.Claim(repo, u'P217')
    prop_Settlement = pywikibot.Claim(repo, u'P276')

    prop_Date = pywikibot.Claim(repo, u'P571')
    EarliestDate_qual = pywikibot.Claim(repo, u'P1319')
    LatestDate_qual = pywikibot.Claim(repo, u'P1326')
    Circa_qual = pywikibot.Claim(repo,u"P1480")

    prop_Location = pywikibot.Claim(repo, u'P189')
    prop_Instance = pywikibot.Claim(repo, u'P31')

    prop_Commons = pywikibot.Claim(repo, u'P4765')
    License_qual = pywikibot.Claim(repo, u'P6216')
    Format_qual = pywikibot.Claim(repo, u'P2701')
    Title_qual = pywikibot.Claim(repo,u'P1476')

    ### ADD URL FOR EACH CLAIM
    url_qual = pywikibot.Claim(repo, u'P854')
    prop_ID.addSource(url_qual)
    prop_Date.addSource(url_qual)
    prop_Collection.addSource(url_qual)
    prop_Location.addSource(url_qual)
    prop_Commons.addSource(url_qual)
    
    def date_normalise(x):
        if pd.isna(x.DateCertainty)==False:
            if 'circa' in x.DateCertainty:
                circa = pywikibot.ItemPage(repo, u"Q5727902")
                Circa_qual.setTarget(circa)
                prop_Date.addQualifier(Circa_qual)
        
        if pd.isna(x.EarliestDate)==False:
            val = x.EarliestDate[0:5]
            val = re.sub(r'(?<=\+|\-)(0)*?(?=[1-9])','',val)
            val=int(val)
            target = pywikibot.WbTime(year=val)
            EarliestDate_qual.setTarget(target)
            prop_Date.addQualifier(EarliestDate_qual)
        
            val = x.LatestDate[0:5]
            val = re.sub(r'(?<=\+|\-)(0)*?(?=[1-9])','',val)
            val=int(val)
            target = pywikibot.WbTime(year=val)
            LatestDate_qual.setTarget(target)
            prop_Date.addQualifier(LatestDate_qual)
    
        if x.Date=='somevalue':
             prop_Date.setSnakType('somevalue')
             claims.append(prop_Date)
        else:
            if 'Z/9' in x.Date:
                val = x.Date[0:5]
                val = re.sub(r'(?<=\+|\-)(0)*?(?=[1-9])','',val)
                val=int(val)
                target = pywikibot.WbTime(year=val)
                prop_Date.setTarget(target)
                claims.append(prop_Date)
            if 'Z/7' in x.Date:
                val = x.Date[0:5]
                val = re.sub(r'(?<=\+|\-)(0)*?(?=[1-9])','',val)
                val=int(val)
                target = pywikibot.WbTime(year=val, precision=7)
                prop_Date.setTarget(target)
                claims.append(prop_Date)  
    
    ###Check Items in Wikidata, update items, create items, create claims, iterate over addClaims, iterate over rows
    if str(artifact.ID) in ids:
        claims=[]
        val = str(artifact.ID)
        Qid = wikidata_items.loc[wikidata_items.ID==val, 'Qid'].item()
        item = pywikibot.ItemPage(repo, Qid)
        
        #SET URL REFERENCE
        url_qual.setTarget(artifact.Reference) 
               
        ###ADD Dates, SOMEVALUE, CENTURY, YEAR, QUALIFIERS (if not null)  
        if 'P571' not in item.get()['claims'].keys():
            date_normalise(artifact)
    
        ###Add Place of Excavation if not already there
        if 'P189' not in item.get()['claims'].keys():
            Dura = pywikibot.ItemPage(repo, u"Q464266")
            prop_Location.setTarget(Dura)
            claims.append(prop_Location)
        
        ### Add settlement of object if not there
        if 'P276' not in item.get()['claims'].keys():
            New_Haven = pywikibot.ItemPage(repo, u'Q49145')
            prop_Settlement.setTarget(New_Haven)
            claims.append(prop_Settlement)
        
        #Check Collection Inventory Number
        ObjNo = artifact.ObjectNumber
        ObjNo = re.sub('inv\. ', '', ObjNo)
        if 'P195' in item.get()['claims'].keys():
            for claim in item.claims['P195']:            
                if 'P217' not in claim.qualifiers: 
                    Inventory_qual.setTarget(ObjNo)
                    prop_Collection.addQualifier(Inventory_qual)
        else:
            YaleGallery = pywikibot.ItemPage(repo, u"Q1568434") 
            prop_Collection.setTarget(YaleGallery)
            Inventory_qual.setTarget(ObjNo)
            prop_Collection.addQualifier(Inventory_qual)
            claims.append(prop_Collection)
        
        #ADD IMAGE URL
        if 'P4765' not in item.get()['claims'].keys():
            if pd.isna(artifact.url)==False:
                prop_Commons.setTarget(artifact.url)
                public_domain = pywikibot.ItemPage(repo, u"Q19652")
                License_qual.setTarget(public_domain)
                prop_Commons.addQualifier(License_qual)
                title_target = pywikibot.WbMonolingualText(artifact.Title, 'en')
                Title_qual.setTarget(title_target)
                prop_Commons.addQualifier(Title_qual)
                if 'tif' in artifact.formatresource:
                    Format_qual.setTarget(pywikibot.ItemPage(repo, u"Q215106"))
                    prop_Commons.addQualifier(Format_qual)
                elif 'jpg' in artifact.formatresource:
                    Format_qual.setTarget(pywikibot.ItemPage(repo, u"Q2195"))
                    prop_Commons.addQualifier(Format_qual)
                claims.append(prop_Commons)
    
        #If not described as archaeological object, add this statement
        if 'P31' in item.get()['claims']:
            lst=[]
            for clm in item.get()['claims']['P31']:
                target = clm.getTarget()
                target=str(target)
                lst.append(target)
            if '[[wikidata:Q220659]]' not in lst:
                archaeological_artifact = pywikibot.ItemPage(repo, u"Q220659")                
                prop_Instance.setTarget(archaeological_artifact)
                prop_Instance.addSource(url_qual)
                claims.append(prop_Instance)
        else:
            archaeological_artifact = pywikibot.ItemPage(repo, u"Q220659")                
            prop_Instance.setTarget(archaeological_artifact)
            prop_Instance.addSource(url_qual)
            claims.append(prop_Instance)
                    
        #Update labels to include unique inventory numbers and IDs
        item.editLabels(labels={'en': artifact.Title + ", Yale University Art Gallery, " + artifact.ObjectNumber}, summary='Synchronizing Wikidata entry with Yale gallery records for ' + artifact.ObjectNumber)
        item.editDescriptions(descriptions={'en': "YUAG " + artifact.ID + ". Archaeological artifact excavated in Dura Europos by the Yale-French team, 1928-1937, Syria"}, summary='Synchronizing Wikidata entry with Yale gallery records for ' + artifact.ObjectNumber)
        
        for stmnt in claims:
            item.addClaim(stmnt,summary='Importing Yale gallery records for ' + artifact.ObjectNumber)
    ### else ---> CREATE NEW ITEM:

    else:
        claims=[]
        item = pywikibot.ItemPage(repo)
        item.editEntity(artifact)
        url_qual.setTarget(artifact.Reference)
        
        ###ADD YUAG ID
        prop_ID.setTarget(artifact.ID)
        claims.append(prop_ID)
        
        ###Add Location of discovery
        Dura = pywikibot.ItemPage(repo, u"Q464266")
        prop_Location.setTarget(Dura)
        claims.append(prop_Location)
        
        ###Add Collection and Inventory Number Qualifier
        ObjNo = artifact.ObjectNumber
        ObjNo = re.sub('inv\. ', '', ObjNo)
        YaleGallery = pywikibot.ItemPage(repo, u"Q1568434") 
        prop_Collection.setTarget(YaleGallery)
        Inventory_qual.setTarget(ObjNo)
        prop_Collection.addQualifier(Inventory_qual)
        claims.append(prop_Collection)
        
        #Add New Haven as Settlement of Object
        New_Haven = pywikibot.ItemPage(repo, u'Q49145')
        prop_Settlement.setTarget(New_Haven)
        claims.append(prop_Settlement)
    
        ###Add Instance of Archaeological Artifact
        archaeological_artifact = pywikibot.ItemPage(repo, u"Q220659")
        prop_Instance.setTarget(archaeological_artifact)
        prop_Instance.addSource(url_qual)
        claims.append(prop_Instance)
        
        ###ADD Dates, SOMEVALUE, CENTURY, YEAR, QUALIFIERS (if not null)
        date_normalise(artifact)
        
        #ADD IMAGE URL
        if pd.isna(artifact.url)==False:
            prop_Commons.setTarget(artifact.url)
            public_domain = pywikibot.ItemPage(repo, u"Q19652")
            License_qual.setTarget(public_domain)
            prop_Commons.addQualifier(License_qual)
            prop_Commons.addQualifier(License_qual)
            title_target = pywikibot.WbMonolingualText(artifact.Title, 'en')
            Title_qual.setTarget(title_target)
            prop_Commons.addQualifier(Title_qual)
            if 'tif' in artifact.formatresource:
                Format_qual.setTarget(pywikibot.ItemPage(repo, u"Q215106"))
                prop_Commons.addQualifier(Format_qual)
            elif 'jpg' in artifact.formatresource:
                Format_qual.setTarget(pywikibot.ItemPage(repo, u"Q2195"))
                prop_Commons.addQualifier(Format_qual)
            claims.append(prop_Commons)
        
        ###Add labels and descriptions
        new_label = {"en": artifact.Title + ", Yale University Art Gallery, " + artifact.ObjectNumber}
        new_description = {"en": "YUAG " + artifact.ID + ". Archaeological object excavated in Dura Europos by the Yale-French team, 1928-1937, Syria"}

        item.editLabels(labels=new_label, summary='Importing Yale gallery records for ' + artifact.ObjectNumber)
        item.editDescriptions(descriptions=new_description, summary='Importing Yale gallery records for ' + artifact.ObjectNumber)
        
        #add Claims
        for stmnt in claims:
            item.addClaim(stmnt,summary='Importing Yale gallery records for ' + artifact.ObjectNumber)

