#!/usr/bin/env python
# -*- coding: utf8 -*-
# -*- coding: cp850 -*
from stem import CircStatus
from stem.control import Controller
import geoip2.database
import socket
import whois
from ipwhois import IPWhois



reader = geoip2.database.Reader('/root/docs/GeoLite2-City.mmdb')

with Controller.from_port(port = 9051) as controller:
    controller.authenticate()
    for circ in sorted(controller.get_circuits()):
        if circ.status != CircStatus.BUILT:
            continue

    print("")
    print("Circuit %s (%s)\n" % (circ.id, circ.purpose))

    node_num=1
    for i, entry in enumerate(circ.path):
        div = '+' if (i == len(circ.path) - 1) else '|'
        fingerprint, nickname = entry
        desc = controller.get_network_status(fingerprint, None)
        address = desc.address if desc else 'unknown'
        response=reader.city(address)
        try:
            socket.gethostbyaddr(address)
        except socket.herror:
            host='?'
        else:
            host=socket.gethostbyaddr(address)[0]

        #    org = whois.whois(host)['org']
        num_it=23
        column1 = ["IP","NICKNAME","REVERSE DNS","GEOLOCALIZATION","FINGERPRINT"]
        column2 = [address,nickname,host,str(response.country.name)+' ('+str(response.location.latitude)+', '+ str(response.location.longitude)+')',fingerprint]
        print '\n--------- Node '+str(node_num)+' ------------\n'
        for c1, c2 in zip(column1, column2):
            print "%-22s %s" % (c1, c2)
        print "WHOIS OUTPUT"
        # Organization name with whois query
        for key in ['range','description','postal_code','city','address','state','asn_country_code' ]:
            try:
                field=str(IPWhois(address).lookup_whois()['nets'][0][key])
            except:
                continue
            else:
                if field != 'None':
                    print " "*num_it+str(field).replace('\n','\n'+' '*num_it).replace(' - ','-')
        node_num=node_num+1

#print response.city
