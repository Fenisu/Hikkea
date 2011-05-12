'''
API made to access mal-api and use the funcions
'''

import json, urllib, urllib2

MALAPIURL = 'http://mal-api.com/'

def search(stype, string):
    '''
    Here it searches the given string using the mal-api and returns
    a dictionary with the found results.
    '''
    response = urllib2.urlopen(MALAPIURL + stype + '/search?q=' + \
                               urllib.quote(string))
    results = json.loads(response.read())
    foundanime = {}
    for i in results:
        foundanime[i['title']] = i['id']
    return foundanime

def retrieve_anime(animeid):
    '''
    Here is where all the information about the anime is retrieved.
    The key to match the anime is the ID.
    '''
    response = urllib2.urlopen(MALAPIURL + 'anime/' + str(animeid))
    html = response.read()
    result = json.loads(html)
    data = {}
    data['title'] = result['title']
    data['malid'] = result['id']
    data['type'] = result['type']
    data['episodes'] = result['episodes']
    data['description'] = result['synopsis']
    data['genres'] = result['genres']
    data['score'] = result['members_score']
    data['thumb'] = result['image_url']
    if result['sequels'] != '':
        dataseq = {}
        for seq in result['sequels']:
            dataseq['title'] = seq['title']
            dataseq[seq['title']] = seq['anime_id']
    if result['prequels'] != '':
        datapreq = {}
        for preq in result['prequels']:
            datapreq['title'] = preq['title']
            datapreq[preq['title']] = preq['anime_id']
    if result['side_stories'] != '':
        dataside = {}
        for side in result['side_stories']:
            dataside['title'] = side['title']
            dataside[side['title']] = side['anime_id']
    return [data['title'], data['episodes'], data['description'], data['malid']]

def retrieve_manga(mangaid):
    '''
    Here is where all the information about the anime is retrieved.
    The key to match the anime is the ID.
    '''
    response = urllib2.urlopen(MALAPIURL + 'manga/' + str(mangaid))
    html = response.read()
    result = json.loads(html)
    data = {}
    data['title'] = result['title']
    data['malid'] = result['id']
    data['type'] = result['type']
    data['episodes'] = result['episodes']
    data['description'] = result['synopsis']
    data['genres'] = result['genres']
    data['score'] = result['members_score']
    data['thumb'] = result['image_url']
    return data
