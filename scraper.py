# This is a template for a Python scraper on Morph (https://morph.io)
# including some code snippets below that you should find helpful

# import scraperwiki
# import lxml.html
#
# # Read in a page
# html = scraperwiki.scrape("http://foo.com")
#
# # Find something on the page using css selectors
# root = lxml.html.fromstring(html)
# root.cssselect("div[align='left']")
#
# # Write out to the sqlite database using scraperwiki library
# scraperwiki.sqlite.save(unique_keys=['name'], data={"name": "susan", "occupation": "software developer"})
#
# # An arbitrary query against the database
# scraperwiki.sql.select("* from data where 'name'='peter'")

# You don't have to do things with the ScraperWiki and lxml libraries. You can use whatever libraries are installed
# on Morph for Python (https://github.com/openaustralia/morph-docker-python/blob/master/pip_requirements.txt) and all that matters
# is that your final data is written to an Sqlite database called data.sqlite in the current working directory which
# has at least a table called data.

import scraperwiki
import lxml.html
import lxml.etree
import json
import re
import resource
import xlrd
import cookielib, urllib2, urllib
import requests


def queryBuffer(buff):
        qparams = {}
        qparams['f'] = "json"
        qparams['where'] = ""
        qparams['geometryType'] = "esriGeometryPolygon"
        qparams['geometry'] = json.dumps(buff)
        qparams['returnGeometry'] = False;
        qparams['outFields'] = "OBJECTID,STANPAR,OWNER,PROP_ADDR,PROP_CITY,PROP_ZIP,LAND_USE,ACREAGE"
        qparams['outSR'] = 2274
        qparams['returnCountOnly'] = False
# print "qparams = " + repr(qparams)
        queryURL = "http://maps.nashville.gov/MetGIS/rest/services/Basemaps/Parcels/MapServer/0/query"
        r3 = requests.post(queryURL, data=qparams)
# print "r3.text = " + repr(r3.text)
        features = r3.json()
# print "Number of parcels returned: " + r3.text
# print "r3.url = " + repr(r3.url)
        for i in features['features']:
            scraperwiki.sqlite.save(unique_keys=["OBJECTID"],data=i['attributes'],table_name="properties")
        print repr(len(features['features'])+1) + " features saved."

def queryBufferById(buffId):
        i = 0
        qparams = {}
        qparams['f'] = "json"
        qparams['where'] = "OBJECTID IN ("
        while i < len(buffId)-1:
            qparams['where'] += "'" + repr(buffId[i]) + "',"
            i += 1
        qparams['where'] += "'" + repr(buffId[i]) + "')"
        qparams['returnGeometry'] = False;
        qparams['outFields'] = "OBJECTID,STANPAR,OWNER,PROP_ADDR,PROP_CITY,PROP_ZIP,LAND_USE,ACREAGE"
        qparams['outSR'] = 2274
        qparams['returnCountOnly'] = False
# print "qparams = " + repr(qparams)
        queryURL = "http://maps.nashville.gov/MetGIS/rest/services/Basemaps/Parcels/MapServer/0/query"
#        print "buffId = " + json.dumps(buffId)
        r3 = requests.post(queryURL, data=qparams)
#        print "qparams['where'] = " + qparams['where']
#        print "r3.text = " + repr(r3.text)
        features = r3.json()
#       print "Number of parcels returned: " + r3.text
#       print "r3.url = " + repr(r3.url)
        for i in features['features']:
            scraperwiki.sqlite.save(unique_keys=["OBJECTID"],data=i['attributes'],table_name="properties")
        print "Processed " + repr(len(features['features'])) + " features with this query."

def queryBufferCount(buff):
        qparams = {}
        qparams['f'] = "json"
        qparams['where'] = ""
        qparams['geometryType'] = "esriGeometryPolygon"
        qparams['geometry'] = json.dumps(buff)
        qparams['returnGeometry'] = False;
        qparams['outSR'] = 2274
        qparams['returnCountOnly'] = False
        qparams['returnIdsOnly'] = True
# print "qparams = " + repr(qparams)
        queryURL = "http://maps.nashville.gov/MetGIS/rest/services/Basemaps/Parcels/MapServer/0/query"
        r3 = requests.post(queryURL, data=qparams)
# print "r3.text = " + repr(r3.text)
        features = r3.json()
        print repr(len(features['objectIds'])) + " features identified."
        if len(features['objectIds']) > 500:
            j = 0
            while j < len(features['objectIds']):
                buff = features['objectIds'][j:j+49]
                print "Getting objectIds " + repr(j+1) + " thru " + repr(j+50) + "."
                queryBufferById(buff)
                j += 50
            print repr(len(features['objectIds'])) + " total features saved."
        else:
            queryBuffer(buff)
                
# print "number of features = " + repr(len(features['features']))
# return len(features['features'])
# print "number of features = " + repr(len(features['features']))
# print "Number of parcels returned: " + r3.text
# print "r3.url = " + repr(r3.url)
# for i in features['features']:
# scraperwiki.sqlite.save(unique_keys=["OBJECTID"],data=i['attributes'],table_name="properties")

def getGeoBuffer(geom,dist):
        bparams = {}
        bparams['geometries'] = json.dumps({'geometryType': "esriGeometryPolygon", 'geometries': [geom]})
# bparams['geometries'] = geom
        bparams['distances'] = dist
        #bparams['unit'] = "UNIT_FOOT"
        bparams['unit'] = 9002
        bparams['unionResults'] = False
        bparams['geodesic'] = False
        bparams['bufferSR'] = 2274
        bparams['outSR'] = 2274
        bparams['inSR'] = 2274
        bparams['f'] = "json"
# print "bparams = " + json.dumps(bparams)
        buffURL = "http://maps.nashville.gov/MetGIS/rest/services/Geometry/GeometryServer/buffer"
        r2 = requests.get(buffURL, params=bparams)
# print "r2.url = " + repr(r2.url)
# print "r2.text = " + repr(r2.text)
        buff = r2.json()
        queryBufferCount(buff['geometries'][0])
# if queryBufferCount(buff['geometries'][0]) > 500:
# queryBufferById(buff['geometries'][0])
# else:
# queryBuffer(buff['geometries'][0]

def getParcelFeature(parcelID,distance):
# test = "http://maps.nashville.gov/MetGIS/rest/services/Geometry/GeometryServer/buffer?f=json&unit=9002&unionResults=false&geodesic=false&geometries=%7B%22geometryType%22%3A%22esriGeometryPolygon%22%2C%22geometries%22%3A%5B%7B%22rings%22%3A%5B%5B%5B1728133.7991666645%2C646400.799999997%5D%2C%5B1728123.2450000048%2C646380%5D%2C%5B1728079.400000006%2C646293.599999994%5D%2C%5B1728075.900000006%2C646287.5%5D%2C%5B1728071.400000006%2C646282%5D%2C%5B1728066.200000003%2C646277.200000003%5D%2C%5B1728060.400000006%2C646273.200000003%5D%2C%5B1728054%2C646270.200000003%5D%2C%5B1728047.200000003%2C646268.099999994%5D%2C%5B1728040.200000003%2C646267.099999994%5D%2C%5B1728033.099999994%2C646267.099999994%5D%2C%5B1728026.099999994%2C646268.299999997%5D%2C%5B1728019.4008333385%2C646270.400000006%5D%2C%5B1728010.2991666645%2C646274.400000006%5D%2C%5B1728001.200000003%2C646278.299999997%5D%2C%5B1727991.900000006%2C646281.799999997%5D%2C%5B1727982.599999994%2C646285.200000003%5D%2C%5B1727973.200000003%2C646288.299999997%5D%2C%5B1727963.700000003%2C646291.099999994%5D%2C%5B1727954.099999994%2C646293.700000003%5D%2C%5B1727944.3991666734%2C646296%5D%2C%5B1727934.700000003%2C646298.200000003%5D%2C%5B1727925%2C646300%5D%2C%5B1727982.599999994%2C646423.200000003%5D%2C%5B1728133.7991666645%2C646400.799999997%5D%5D%5D%2C%22spatialReference%22%3A%7B%22wkid%22%3A2274%7D%7D%5D%7D&inSR=2274&distances=250&outSR=2274&bufferSR=2274"
# print "test = " + urllib.url2pathname(test)

    #try:
        # get feature object based on parcel ID
        spatialRef = {"wkid":2274}
        pageURL = "http://maps.nashville.gov/MetGIS/rest/services/Basemaps/Parcels/MapServer/0/query"
        params = {'where': "STANPAR='" + parcelID + "'", 'spatialRel' : 'esriSpatialRelIntersects', 'f':"json", 'outFields': "*", 'outSR': 2274, 'returnGeometry': True}
        r1 = requests.get(pageURL, params=params)
# print "r1.url = " + repr(r1.url)
# print "r1.text = " + repr(r1.text)
        feat = r1.json()
        if len(feat['features']) == 0:
            print "No features were found"
        else:
# print "feat['features'][0]['geometry'] = " + repr(feat['features'][0]['geometry'])
            getGeoBuffer(feat['features'][0]['geometry'],distance)
            #print "testing"

#getParcelFeature("11714006400",1000)
      
def getAppraisal(objectID,parcelID):
#    try:
    # print "propID = " + propID + "."
        pageURL = "http://www.padctnwebpro.com/WebproNashville/searchResults.asp?cboSearchType=Parcel&SearchVal1=" + repr(parcelID)
        cj = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        html = lxml.html.parse(opener.open(pageURL)).getroot()
        print "Response 1: \n" + lxml.etree.tostring(html)
        links = html.cssselect('a')
#        newURL = "http://www.padctnwebpro.com/WebproNashville/" + links[0].get('href')
        newURL = "http://www.padctnwebpro.com/WebproNashville/Summary-bottom.asp?Card=1"

#summary-bottom.asp?A1=2337573&A2=1
        record = lxml.html.parse(opener.open(newURL)).getroot()
        print "Response 2: \n" + lxml.etree.tostring(record)
        fields = record.cssselect('td')
        if fields[2].text_content().strip() == "Card 1 of 1":
            card = lxml.html.parse(opener.open("http://www.padctnwebpro.com/WebproNashville/RecordCard.asp")).getroot()
            data = card.cssselect('td')
            while i < len(data):
                print "data[i]: " + repr(data[i])
                i += 1
#        neighborhood = fields[49].text_content().strip()
#        apprData = {'parcelID': parcelID,
#            'neighborhood': neighborhood}
#        scraperwiki.sqlite.save(unique_keys=["parcelID"], data=apprData, table_name="Districts")
#    except:
#        print "Could not get appraisal info for parcelID " + parcelID
            
    # owner, street, parcelID, lastsaleprice, lastsaledate, totalval, landval, impval, acres, sqft, year, foundation, siding, rooms, bedrooms, fullbaths, halfbaths, fixtures

getAppraisal(1,11715004802)
