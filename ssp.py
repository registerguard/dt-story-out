import requests, json, csv, os, shutil
from lxml import etree
from bs4 import BeautifulSoup
from datetime import datetime
from pytz import timezone
from scripts import *

# Global vars
cwd = os.getcwd()
rgfiles = '/Volumes/newsweb\$/'
photoSubcats = "32058824,32067956,32058769,32058823,32058773,32058730,32058735,32058827,32058745,31994432,32058749,32058736,32058195,32058817,32068003,32058784,32058756"
#videoSubcats = "31994433,32058759,32058196,32003307,32058816,32042463,32042459,32058748,31994425,32058825,32042583,32042464,32058820,32058774,32042460,32003311,32058826,32058162"
items = 999
pacific = timezone('America/Los_Angeles')
startDate = pacific.localize(datetime(2018,1,1,0,0,1))
endDate = pacific.localize(datetime(2018,2,28,11,59,59))

def getAlbum(sspalbum):
    # raw_input for items ???
    payload = {'id': sspalbum}
    url = 'http://slideshow.registerguard.com/slideshowpro/api/ncs/index.php'
    try:
        r = requests.get(url, params=payload)
    except:
        print('bad request: {0}?id={1}'.format(url, sspalbum))
    try:
        album = r.json()
        return album
    except:
        print('bad json: {0}?id={1}'.format(url, sspalbum))

def writeGalleryXML(stories):
    for story in stories:
        if (story['sspid'] != 'NULL'):
            # Do date checking
            dt = getDatetime(story['published'])
            if (startDate <= dt <= endDate):
                print("Getting {0}: {1}".format(story['headline'],story['path']))
                gallery = etree.Element('gallery')
                # Gallery story metadata
                uniqueid = etree.SubElement(gallery,'uniqueid')
                uniqueid.text = story['id']
                title = etree.SubElement(gallery,'title')
                title.text = etree.CDATA(story['headline'])
                date = etree.SubElement(gallery,'date')
                date.text = dt.strftime('%Y-%m-%dT%H:%M:%S%z')
                # Create folder structure
                dtDIR = dt.strftime('%Y/%m/%d')
                filePath = '{0}/gallery/{1}/'.format(cwd, dtDIR)
                createFolders(filePath)
                # Come back to XML
                category = etree.SubElement(gallery,'category')
                category.text = story['section']
                taxonomy = etree.SubElement(gallery,'taxonomy')
                taxonomy.text = story['catid']
                description = etree.SubElement(gallery,'description')
                description.text = etree.CDATA(story['excerpt'])
                # Move into images
                try:
                    album = getAlbum(story['sspid'])
                except:
                    print('bad ssp - story: {0} --- {1}'.format(story['headline'], story['id']))
                #print(story['sspid'])
                images = etree.SubElement(gallery, 'images')
                for pic in album:
                    image = etree.SubElement(images, 'image')
                    title = etree.SubElement(image,'title')
                    title.text = etree.CDATA(pic['id'])
                    # Make sure caption is clean
                    caption = etree.SubElement(image,'caption')
                    captionTEMP = pic['description']
                    captionTEMP = captionTEMP.replace('\n','').replace('\r','').replace('\t','')
                    caption.text = etree.CDATA(captionTEMP)
                    # Make sure credit is clean
                    credit = etree.SubElement(image,'credit')
                    creditTEMP = pic['byline']
                    creditTEMP = creditTEMP.replace('\n','').replace('\r','').replace('\t','')
                    credit.text = etree.CDATA(pic['byline'])
                    filename = etree.SubElement(image,'filename')
                    filename.text = etree.CDATA(pic['filename'])
                    getImage(pic['original'], filePath)
                    # print(etree.tostring(images, pretty_print=True))
                # Move into exporting to file
                # print(etree.tostring(gallery, pretty_print=True))
                out = etree.ElementTree(gallery)
                outFILE = '{0}/{1}-{2}.xml'.format(filePath, dt.strftime('%Y%m%d'), story['id'])
                out.write(outFILE, pretty_print=True, xml_declaration=True, encoding='utf-8')

def writeVideoXML(stories):
    for story in stories:
        if (story['video'] != 'NULL'):
            #print("Getting {0}: {1}".format(story['headline'],story['path']))
            print("Video XML has not been configured yet.")

def main(subcats, items):
    print("Starting program...")

    # Get stories from DT API (subcat id list, number to return)
    print("Getting {0} stories...".format(items))
    stories = getStories(subcats,items)
    #print(stories)

    # Write those stories to a CSV (stories var, name of output csv)
    #storyCSV(stories,'test.csv')
    
    ### Write XML
    writeGalleryXML(stories)
    #writeVideoXML(stories)

# Write out to XML
main(photoSubcats, items)




