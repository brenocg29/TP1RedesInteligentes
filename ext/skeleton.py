# Copyright 2013 <Your Name Here>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from enum import Enum
from pox.openflow.of_json import *

# Import some POX stuff
from pox.core import core
from pox.lib.util import dpidToStr, strToDPID, fields_of                   
import pox.openflow.libopenflow_01 as of      # OpenFlow 1.0 library
import pox.lib.packet as pkt                  # Packet parsing/construction
from pox.lib.addresses import EthAddr, IPAddr # Address types
import pox.lib.util as poxutil                # Various util functions
import pox.lib.revent as revent       
import sys;        # Event library
import pox.lib.recoco as recoco               # Multitasking library
# Create a logger for this component
log = core.getLogger()
mac_port = {}
admin_port = 3 #change this
restrict_mac = {}
switches = []
restrict_dst = {}
class Restrict(Enum):
	DROP = 1
	FORWARD = 2
	FORANDTRACK = 3
	DUPLICATE = 4
	BLOCKANDREPORT = 5
class hostType(Enum):
	SUPERUSER = 1
	DROPALL = 2
	ALWAYSDUPLICATE = 3
def _start_ev(event):
	connection = event.connection
	sock = connection.sock
	ip,port = sock.getpeername()
	print dpidToStr(event.dpid ) + "and ip is " + ip
	file = open('switches.txt','w')
	switches.append(str(ip))
	file.write("\n".join(switches))
	file.close
def packet_in(event):
	flag = 0
	packet = event.parse()
	print str (event.port) + "\n"
	msg = of.ofp_packet_out()
	msg.data = event.ofp
	source = ""
	msg.idle_timeout = 10
	msg.hard_timeout = 30
	mode = "1"
	if (packet.find(pkt.ipv4) != None or packet.find(pkt.ipv6)!=None) and mode == "1" :
		source = str(packet.next.srcip)
		destiny = str(packet.next.dstip)
	else:
		source = str(packet.src)
		destiny = str(packet.dst)
	if packet.src not in mac_port:
		if packet.src in restrict_mac:
			log.info("learning" + str(packet.src) +"is in port" + str(event.ofp.in_port))
			mac_port[packet.src] = (event.ofp.in_port)
		if packet.src not in restrict_mac:
			mac_port[packet.src] = (event.ofp.in_port)
	if packet.dst in mac_port:
		log.info("send to " + destiny + "known as " + str(mac_port[packet.dst]))
		if source not in restrict_mac or restrict_mac[source] == "2" :
			if destiny in restrict_dst and restrict_dst[destiny] == "2":
				print ("Dropped from " + source + "to " + destiny + "\n")
			else:
				action = of.ofp_action_output(port = mac_port[packet.dst])
				msg.actions.append(action)
				if destiny in restrict_dst and restrict_dst[destiny] == "3":
					action = of.ofp_action_output(port = admin_port)
					msg.actions.append(action)
				event.connection.send(msg)
		if source in restrict_mac and restrict_mac[source] == "1":
			if destiny in restrict_dst and restrict_dst[destiny]== "1":
				action = of.ofp_action_output(port = mac_port[packet.dst])
				msg.actions.append(action)
				event.connection.send(msg)
			else:
				print("Dropped from " + source + "to " + destiny + "\n")
			return 
		if source in restrict_mac and restrict_mac[source] == "3":
			if destiny in restrict_dst and restrict_dst[destiny] == "2":
				print ("Dropped from " + source +"to " + destiny + "\n")
			else:
				action = of.ofp_action_output(port = mac_port[packet.dst])
				msg.actions.append(action)
				event.connection.send(msg)
				if destiny not in restrict_dst or restrict_dst[destiny] != "1":
					restrict_dst[packet.dst] = "3"
		if source in restrict_mac and restrict_mac[source] == "4":
			if destiny in restrict_dst and restrict_dst[destiny] == "2":
				print ("Dropped from " + source + "to " + destiny + "\n")
			else:
				if destiny not in restrict_dst or restrict_dst[destiny] != "1":
					action = of.ofp_action_output(port = admin_port)
					msg.actions.append(action)
				action = of.ofp_action_output(port = mac_port[packet.dst])
				msg.actions.append(action)
				event.connection.send(msg)
		if source in restrict_mac and restrict_mac[source] == "5":
			if destiny in restrict_dst and restrict_dst[destiny] == "1":
				action = of.ofp_action_output(port = mac_port[packet.dst])
				msg.actions.append(action)
				event.connection.send(msg)
			else:
				action = of.ofp_action_output(port = admin_port)
				msg.actions.append(action)
				event.connection.send(msg)
	else:
		if (source != "1"):
			action = of.ofp_action_output(port = of.OFPP_ALL)
			msg.actions.append(action)
			event.connection.send(msg)
def launch (bar = False):
	f = open ("./rules.txt")
	print "Lendo regras e iniciando controlador\n"
	for line in f:
		aux = line.split();
		ip,rest = aux[0],aux[1]
		restrict_mac[ip] = rest
	#mode = raw_input("entre com o modo (1) Ip address se possivel (2) para endrecos MAC")
	#restriction_num = raw_input("entre com o num de restricoes ")
	#for i in range(0,int(restriction_num)):
	#	mac_port = raw_input("Entre com o macport ")
	#	restriction = raw_input("entre com o numero da restricao para esse mac ")
	#	restrict_mac[str(mac_port)] = restriction
	#restriction_num  = raw_input("entre com o num de permissoes ")
	#for j in range(0,int(restriction_num)):
	#	mac_port = raw_input("entre com o mac port ")
	#	restriction = raw_input("entre com o numero de permissao ")
	#	restrict_dst[str(mac_port)] = restriction
	#	print "olz"
	core.openflow.addListenerByName("ConnectionUp",_start_ev)
	core.openflow.addListenerByName("PacketIn",packet_in)