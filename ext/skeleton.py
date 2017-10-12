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
# Import some POX stuff
from pox.core import core                     # Main POX object
import pox.openflow.libopenflow_01 as of      # OpenFlow 1.0 library
import pox.lib.packet as pkt                  # Packet parsing/construction
from pox.lib.addresses import EthAddr, IPAddr # Address types
import pox.lib.util as poxutil                # Various util functions
import pox.lib.revent as revent               # Event library
import pox.lib.recoco as recoco               # Multitasking library
# Create a logger for this component
log = core.getLogger()
mac_port = {}
admin_port = 3 #change this
restrict_mac = {}
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
	log.info("ola comecei carai")
def packet_in(event):
	flag = 0
	packet = event.parse()
	if str(packet.src) in restrict_mac:
		log.info("thus is " + restrict_mac[str(packet.src)])
	log.info(event.port)
	msg = of.ofp_packet_out()
	msg.data = event.ofp
	msg.idle_timeout = 10
	msg.hard_timeout = 30
	if str(packet.dst) in restrict_dst and restrict_dst[str(packet.dst)] == 4:
		log.info("dropped")
		return
	if packet.src not in mac_port:
		if packet.src in restrict_mac:
			log.info("learning" + str(packet.src) +"is in port" + str(event.ofp.in_port))
			mac_port[packet.src] = (event.ofp.in_port)
		if packet.src not in restrict_mac:
			mac_port[packet.src] = (event.ofp.in_port)
	if packet.dst in mac_port:
		log.info("send to " + str(packet.dst) + "known as " + str(mac_port[packet.dst]))
		if str(packet.src) not in restrict_mac or restrict_mac[str(packet.src)] == "2" :
			if str(packet.dst) in restrict_dst and restrict_dst[str(packet.dst)] == "2":
				print "Dropped"
			else:
				action = of.ofp_action_output(port = mac_port[packet.dst])
				msg.actions.append(action)
				if str(packet.dst) in restrict_dst and restrict_dst[str(packet.dst)] == "3":
					action = of.ofp_action_output(port = admin_port)
					msg.actions.append(action)
				event.connection.send(msg)
		if str(packet.src) in restrict_mac and restrict_mac[str(packet.src)] == "1":
			if str(packet.dst) in restrict_dst and restrict_dst[str(packet.dst)]== "1":
				action = of.ofp_action_output(port = mac_port[packet.dst])
				msg.actions.append(action)
				event.connection.send(msg)
			else:
				log.info("Dropped")
			return 
		if str(packet.src) in restrict_mac and restrict_mac[str(packet.src)] == "3":
			if str(packet.dst) in restrict_dst and restrict_dst[str(packet.dst)] == "2":
				print "Dropped"
			else:
				action = of.ofp_action_output(port = mac_port[packet.dst])
				msg.actions.append(action)
				event.connection.send(msg)
				if str(packet.dst) not in restrict_dst or restrict_dst[str(packet.dst)] != "1":
					restrict_dst[packet.dst] = "3"
		if str(packet.src) in restrict_mac and restrict_mac[str(packet.src)] == "4":
			if str(packet.dst) in restrict_dst and restrict_dst[str(packet.dst)] == "2":
				print "Dropped"
			else:
				if str(packet.dst) not in restrict_dst or restrict_dst[str(packet.dst)] != "1":
					action = of.ofp_action_output(port = admin_port)
					msg.actions.append(action)
				action = of.ofp_action_output(port = mac_port[packet.dst])
				msg.actions.append(action)
				event.connection.send(msg)
		if str(packet.src) in restrict_mac and restrict_mac[str(packet.src)] == "5":
			if str(packet.dst) in restrict_dst and restrict_dst[str(packet.dst)] == "1":
				action = of.ofp_action_output(port = mac_port[packet.dst])
				msg.actions.append(action)
				event.connection.send(msg)
			else:
				action = of.ofp_action_output(port = admin_port)
				msg.actions.append(action)
				event.connection.send(msg)
	else:
		action = of.ofp_action_output(port = of.OFPP_ALL)
		msg.actions.append(action)
		event.connection.send(msg)
def launch (bar = False):
	restriction_num = raw_input("entre com o num de restricoes")
	for i in range(0,int(restriction_num)):
		mac_port = raw_input("Entre com o macport")
		restriction = raw_input("entre com o numero da restricao para esse mac")
		restrict_mac[str(mac_port)] = restriction
	restrict_dst = raw_input("entre com o num de permissoes")
	for j in range(0,int(restrict_dst)):
		mac_port = raw_input("entre com o mac port")
		restriction = raw_input("entre com o numero de permissao")
		restrict_dst[restrict_mac] = restriction
	core.openflow.addListenerByName("ConnectionUp",_start_ev)
	core.openflow.addListenerByName("PacketIn",packet_in)
  	