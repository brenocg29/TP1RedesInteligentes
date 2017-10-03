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

"""
A skeleton POX component

You can customize this to do whatever you like.  Don't forget to
adjust the Copyright above, and to delete the Apache license if you
don't want to release under Apache (but consider doing so!).

Rename this file to whatever you like, .e.g., mycomponent.py.  You can
then invoke it with "./pox.py mycomponent" if you leave it in the
ext/ directory.

Implement a launch() function (as shown below) which accepts commandline
arguments and starts off your component (e.g., by listening to events).

Edit this docstring and your launch function's docstring.  These will
show up when used with the help component ("./pox.py help --mycomponent").
"""
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
admin_port = 0 #change this
restrict_mac = {}
class Restrict(Enum):
	DROP = 1
	FORWARD = 2
	FORANDTRACK = 3
	DUPLICATE = 4
	BLOCKANDREPORT = 5
def _start_ev(event):
	log.info("ola comecei carai")
def packet_in(event):
	packet = event.parse()
	if str(packet.src) in restrict_mac:
		log.info("thus is " + restrict_mac[str(packet.src)])
	log.info(event.port)
	msg = of.ofp_packet_out()
	msg.data = event.ofp	
	if event.port == 3:
		log.info("dropped")
	else:
		if packet.src not in mac_port:
			if packet.src in restrict_mac:
				#TODO take action
				log.info("learning" + str(packet.src) +"is in port" + str(event.ofp.in_port))
				mac_port[packet.src] = (event.ofp.in_port)
			if packet.src not in restrict_mac:
				mac_port[packet.src] = (event.ofp.in_port)

		if packet.dst in mac_port:
			log.info("send to " + str(packet.dst) + "known as" + str(mac_port[packet.dst]))
			#take action in conformity to each packet restriction
			if str(packet.src) not in restrict_mac or restrict_mac[str(packet.src)]== "2" :
				action = of.ofp_action_output(port = mac_port[packet.dst])
				msg.actions.append(action)
				event.connection.send(msg)
			if str(packet.src) in restrict_mac and restrict_mac[str(packet.src)] == "1":
				log.info("Dropped")
				return 
			if str(packet.src) in restrict_mac and restrict_mac[str(packet.src)] == "4":
				action = of.ofp_action_output(port = admin_port)
				msg.actions.append(action)
				action = of.ofp_action_output(port = mac_port[packet.dst])
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
	print restrict_mac["00:00:00:00:00:02"]
	core.openflow.addListenerByName("ConnectionUp",_start_ev)
	core.openflow.addListenerByName("PacketIn",packet_in)
  	