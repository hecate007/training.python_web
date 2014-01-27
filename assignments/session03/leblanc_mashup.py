#!/usr/bin/env python

import json
import requests
import sys

googApiKey = r'AIzaSyDIcFETDCpeaAScHDu-1b4qZ-a6rRhXiyk'

class Location(object):
    def __init__(self,name,lat,lon,address='N\A'):
        self.name = name
        self.address = address
        self.lat = lat
        self.lon = lon

def getSkiResorts(location='united states'):
    api_url = 'https://maps.googleapis.com/maps/api/place/textsearch/json'    
    print 'looking for ski resorts in %s' % location
    location = location.replace(' ','+')
    
    parameters = {
        'sensor':'false',
        'types':'establishment|lodging',
        'query':'ski+resort+%s' % location,
        'key':googApiKey}
    
    resp = requests.get(api_url,params=parameters)
    data = json.loads(resp.text)
    resorts = []
    if data['status'] == 'OK':
        for result in data['results']:
            tmpName = result['name']
            tmpLat = result['geometry']['location']['lat']
            tmpLon = result['geometry']['location']['lng']
            tmpAddr = result['formatted_address']
            if tmpName and tmpLat and tmpLon:
                resorts.append(Location(tmpName,tmpLat,tmpLon,tmpAddr))
            
    return resorts
    
    
def getDistance(orgLat,orgLon,destLat,destLon):
    api_url = 'http://maps.googleapis.com/maps/api/directions/json'
    m_to_ft = 3.281
    
    parameters = {
        'sensor':'false',
        'origin':'%s,%s'%(orgLat,orgLon),
        'destination':'%s,%s' % (destLat,destLon)}
    
    resp = requests.get(api_url,params=parameters)
    data = json.loads(resp.text)
    distance = None
    if data['status'] == 'OK':
        meters = data['routes'][0]['legs'][0]['distance']['value']
        distance = meters * m_to_ft
    
    return distance
    
def findClosestHospital(lat,lon):
    api_url = 'https://maps.googleapis.com/maps/api/place/textsearch/json'
    miles_to_ft = 5280
    
    parameters = {
        'sensor':'false',
        'types':'establishment',
        'location':'%s,%s'%(lat,lon),
        'query':'hospital',
        'radius':'16000',
        'key':googApiKey}
    
    resp = requests.get(api_url,params=parameters)
    data = json.loads(resp.text)
    hospital = None
    distance = None
    if data['status'] == 'OK':
        for result in data['results']:
            tmpName = result['name']
            tmpLat = result['geometry']['location']['lat']
            tmpLon = result['geometry']['location']['lng']
            tmpAddr = result['formatted_address']
            tmpDist = getDistance(lat,lon,tmpLat,tmpLon)
            if tmpName and tmpLat and tmpLon and tmpDist:
                if not distance or tmpDist < distance:
                    hospital = Location(tmpName,tmpLat,tmpLon,tmpAddr)
                    distance = tmpDist
    
    if distance:
        if distance > miles_to_ft:
            distance = '%.2f miles' % float(distance / miles_to_ft)
        else:
            distance = '%d feet' % distance
    
    return hospital,distance
        


if __name__ == '__main__':
    if len(sys.argv) == 2:
        location = sys.argv[1]
    else:
        location = 'united states'
    
    output = []
    for resort in getSkiResorts(location):
        hospital,dist = findClosestHospital(resort.lat,resort.lon)
        output.append('Ski Resort:')
        output.append('\tName: %s' % resort.name)
        output.append('\tAddress: %s' % resort.address)
        output.append('\tLat: %s  Lon: %s' % (resort.lat,resort.lon))
        if hospital:
            output.append('\tClosest Hospital:')        
            output.append('\t\tName: %s' % hospital.name)
            output.append('\t\tAddress: %s' % hospital.address)
            if dist:
                output.append('\t\tDistance: %s' % dist)
            else:
                output.append('\t\tDistance: N\A')
        else:
            output.append('\tClosest Hospital: N\A')
        output.append('\r\n')
    print 'results'
    print
    print '\r\n'.join(output)
