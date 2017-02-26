# Introduction

Set of simple tools using stem python to monitor and control tor

# Installation

	# pip install pywhois stem python-nmap
	# dpkg -i tor-monitoring-1.0.deb 

# Synopsis

* `tor-map [-q] [-o <destination] [-z <zoom>]`: open a Google map of the circuit and of each node neighboring
* `tor-circuit`: display detailed information about the circuit nodes (ip, nickname, reverse DNS, geoip output, fingerprint, whois output, nmap output)
* `tor-new`: force to create a new tor circuit
* `tor-exit <2 digit country codes>` and `tor-entry <2 digit coutry codes>`: set the exit and entry nodes country and restart tor.

