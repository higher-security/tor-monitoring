#!/usr/bin/env python
# -*- coding: utf8 -*-
# -*- coding: cp850 -*
import fileinput
import time
from stem import CircStatus
from stem.control import Controller
import geoip2.database
import os
from time import gmtime, strftime
import shutil
import io
import webbrowser
import numpy as np
from json import load
from urllib2 import urlopen



# VARIABLES TO BE SET

map_template='/tmp/map-template.html'
directory_for_maps='/tmp'
zoom_circuit=3
zoom_node=13
reader = geoip2.database.Reader('/usr/lib/GeoLite2-City.mmdb')


# WRITE TEMPLATE FILE

MAP_TEMPLATE='''<script type="text/javascript">
var locations = [
];

var map = new google.maps.Map(document.getElementById(''), {
center: new google.maps.LatLng(0,0),
zoom: 3,
mapTypeId: google.maps.MapTypeId.HYBRID
});
var markerBounds = new google.maps.LatLngBounds();
var infowindow = new google.maps.InfoWindow();

var marker, i;

for (i = 0; i < locations.length; i++){
marker = new google.maps.Marker({
position: new google.maps.LatLng(locations[i][1], locations[i][2]),
map: map,
});

google.maps.event.addListener(marker, "click", (function(marker, i){
return function() {
infowindow.setContent(locations[i][0]);
markerBounds.extend(locations);
infowindow.open(map, marker);
}
})(marker, i));
}
</script>'''


circuit_lat=[]
circuit_lon=[]

# WRITE MAP TEMPLATE IF NON-EXISTANT

if not (os.path.isfile(map_template)):
    with open(map_template,'w') as output:
        output.write(MAP_TEMPLATE)

address=load(urlopen('http://jsonip.com'))['ip']
response=reader.city(address)

local_lat=str(response.location.latitude)
local_lon=str(response.location.longitude)

with Controller.from_port(port = 9051) as controller:
    controller.authenticate()

    for circ in sorted(controller.get_circuits()):
        if circ.status != CircStatus.BUILT:
            continue
    circuit_directory=directory_for_maps+"/circuit_"+circ.id+"_"+strftime("%Y-%m-%d_%H:%M:%S", gmtime())
    os.makedirs(circuit_directory)
    map_all=circuit_directory+"/all.html"
    map_circuit=circuit_directory+"/circuit.html"
    map_nodes = [circuit_directory+"/node0.html",circuit_directory+"/node1.html",circuit_directory+"/node2.html",circuit_directory+"/node3.html"]

# GENERAL CIRCUIT

    with open(map_template, "r") as inp, open(map_circuit, "w") as output:
        for line in inp:
            l = line.strip()
            if l.endswith("locations = ["):
                output.write(format(l))
                # Add local coordinates
                string='\n[\''+response.country.name+'\', '+local_lat+', '+local_lon+', 1 ] ,'
                output.write(string)
                for i, entry in enumerate(circ.path):
                    div = '+' if (i == len(circ.path) - 1) else '|'
                    fingerprint, nickname = entry
                    desc = controller.get_network_status(fingerprint, None)
                    address = desc.address if desc else 'unknown'
                    response = reader.city(address)
                    circuit_lat.append(response.location.latitude)
                    circuit_lon.append(response.location.longitude)
                    string='\n[\''+response.country.name+'\', '+str(response.location.latitude)+', '+str(response.location.longitude)+', 1 ] ,\n'
                    output.write(string)
            elif l.startswith("zoom:"):
                string="zoom: "+str(zoom_circuit)+", \n"
                output.write(string)
            elif l.startswith("center:"):
                output.write("{}\n".format(l))
                string="center: new google.maps.LatLng("+str(np.mean(circuit_lat))+","+str(np.mean(circuit_lon))+") , \n"
                output.write(string)
            elif l.startswith("title:"):
                    string="\ntitle: \"circ_"+str(circ.id)+"_"+strftime("%Y-%m-%d_%H-%M-%S", gmtime())
                    output.write(string)
            elif l.startswith("var map = new google.maps.Map"):
                string="var map = new google.maps.Map(document.getElementById('"+'circuit'+"'), {"
                output.write(string)
            elif l.startswith("marker = new google.maps.Marker"):
                string="label: { text: i.toString() },\n"
                output.write("{}\n".format(l))
                output.write(string)
            else:
                output.write("{}\n".format(l))

# MAP OF EACH NODE

# NODE 0 (LOCAL)

node_num=0
with open(map_template , "r") as inp, open(map_nodes[node_num], "w") as output:
    for line in inp:
        l = line.strip()
        if l.endswith("locations = ["):
            output.write("{}\n".format(l))
            string='\n[\''+response.country.name+'\', '+str(response.location.latitude)+', '+str(response.location.longitude)+', 1 ] ,\n'
            output.write(string)
        elif l.startswith("center:"):
            string="center: new google.maps.LatLng("+str(response.location.latitude)+', '+str(response.location.longitude)+") , \n"
            output.write(string)
        elif l.startswith("zoom:"):
            string="zoom: "+str(zoom_node)+", \n"
            output.write(string)
        elif l.startswith("title:"):
            string="\ntitle: \"circ_"+str(circ.id)+"_"+node+"_"+str(node_num)+"_"+strftime("%Y-%m-%d_%H-%M-%S", gmtime())
            output.write("{}\n".format(l))
        elif l.startswith("var map = new google.maps.Map"):
            string="var map = new google.maps.Map(document.getElementById('node"+str(node_num)+"'), {"
            output.write(string)
        elif l.startswith("marker = new google.maps.Marker"):
            string="label: { text: '"+str(node_num)+"' },\n"
            output.write("{}\n".format(l))
            output.write(string)
        else:
            output.write("{}\n".format(l))

# OTHER NODES

with Controller.from_port(port = 9051) as controller:
    controller.authenticate()

    for circ in sorted(controller.get_circuits()):
        if circ.status != CircStatus.BUILT:
            continue
        node_num=1
    for i, entry in enumerate(circ.path):
        div = '+' if (i == len(circ.path) - 1) else '|'
        fingerprint, nickname = entry
        desc = controller.get_network_status(fingerprint, None)
        address = desc.address if desc else 'unknown'
        response = reader.city(address)
        with open(map_template , "r") as inp, open(map_nodes[node_num], "w") as output:
            for line in inp:
                l = line.strip()
                if l.endswith("locations = ["):
                    output.write("{}\n".format(l))
                    string='\n[\''+response.country.name+'\', '+str(response.location.latitude)+', '+str(response.location.longitude)+', 1 ] ,\n'
                    output.write(string)
                elif l.startswith("center:"):
                    string="center: new google.maps.LatLng("+str(response.location.latitude)+', '+str(response.location.longitude)+") , \n"
                    output.write(string)
                elif l.startswith("zoom:"):
                    string="zoom: "+str(zoom_node)+", \n"
                    output.write(string)
                elif l.startswith("title:"):
                    string="\ntitle: \"circ_"+str(circ.id)+"_"+node+"_"+node_num+"_"+strftime("%Y-%m-%d_%H-%M-%S", gmtime())
                    output.write("{}\n".format(l))
                elif l.startswith('var map = new google.maps.Map'):
                    string="var map = new google.maps.Map(document.getElementById('node"+str(node_num)+"'), {"
                    output.write(string)
                elif l.startswith("marker = new google.maps.Marker"):
                    string="label: { text: '"+str(node_num)+"' },\n"
                    output.write("{}\n".format(l))
                    output.write(string)
                else:
                    output.write("{}\n".format(l))
        node_num+=1

# CREATE MOSAIC MAP

with open(map_all, "w") as f2:
    f2.write('''<html>
<head>
<meta name="viewport" content="initial-scale=1.0, user-scalable=no">
<meta charset="utf-8">
<script src="http://maps.google.com/maps/api/js?key=AIzaSyD8O_AHvbfS0TsYL8v7WCjteWQ572dTgBc" type="text/javascript"></script>
</head>
<div id="circuit" style="width:50%; height:50%; float:left"><body>
''')
    with open(map_circuit , "r") as f:
        f2.write(f.read())
        f2.write('</body></div>\n<div id=\"node1\" style="width:50%; height:50%; float:right; background-image: url("empty.gif"); "><body>\n')
    with open(map_nodes[1], "r") as f:
        f2.write(f.read())
        f2.write('</body></div>\n<div  id=\"node2\" style="width:50%; height:50%; float:left"><body>\n')
    with open(map_nodes[2], "r") as f:
        f2.write(f.read())
        f2.write('</body></div>\n<div  id=\"node3\" style="width:50%; height:50%; float:right"><body>\n')
    with open(map_nodes[3], "r") as f:
        f2.write(f.read())
        f2.write('</body></div></html>')
    print map_circuit

# CREATE CIRCUIT MAP

with open(map_circuit, "r+") as f:
    content = f.read()
    f.seek(0,0)
    f.write('''<html>
<head>
<meta name="viewport" content="initial-scale=1.0, user-scalable=no">
<meta charset="utf-8">
<script src="http://maps.google.com/maps/api/js?key=AIzaSyD8O_AHvbfS0TsYL8v7WCjteWQ572dTgBc" type="text/javascript"></script>
</head>
<div id="circuit" style="height: 100%; width: 100%;"><body>
'''.rstrip('\r\n') + '\n'+content)
with open(map_circuit, "a+") as f:
    f.write('</div></body></html>')

# CREATE NODE MAPS

for i in range(0,4):
    with open(map_nodes[i], "r+") as f:
        content = f.read()
        f.seek(0,0)
        f.write('''<html>
<head>
<meta name="viewport" content="initial-scale=1.0, user-scalable=no">
<meta charset="utf-8">
<script src="http://maps.google.com/maps/api/js?key=AIzaSyD8O_AHvbfS0TsYL8v7WCjteWQ572dTgBc" type="text/javascript"></script>
</head>
<div id="node'''+str(i)+'''" style="height: 100%; width: 100%;"><body>
'''.rstrip('\r\n') + '\n'+content)
    with open(map_nodes[i], "a+") as f:
        f.write('</div></body></html>')
        print map_nodes[i]

webbrowser.open_new_tab(map_circuit)
time.sleep(0.3)
webbrowser.open_new_tab(map_nodes[0])
time.sleep(0.3)
webbrowser.open_new_tab(map_nodes[1])
time.sleep(0.3)
webbrowser.open_new_tab(map_nodes[2])
time.sleep(0.3)
webbrowser.open_new_tab(map_nodes[3])
time.sleep(0.3)
webbrowser.open_new_tab(map_all)
