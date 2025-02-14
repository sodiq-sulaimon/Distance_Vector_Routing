# Distance Vector project for CS 6250: Computer Networks
#
# This defines a DistanceVector (specialization of the Node class)
# that can run the Bellman-Ford algorithm. The TODOs are all related 
# to implementing BF. Students should modify this file as necessary,
# guided by the TODO comments and the assignment instructions. This 
# is the only file that needs to be modified to complete the project.
#
# Student code should NOT access the following members, otherwise they may violate
# the spirit of the project:
#
# topolink (parameter passed to initialization function)
# self.topology (link to the greater topology structure used for message passing)
#
# Copyright 2017 Michael D. Brown
# Based on prior work by Dave Lillethun, Sean Donovan, Jeffrey Randow, new VM fixes by Jared Scott and James Lohse.

from Node import *
from helpers import *


class DistanceVector(Node):
    
    def __init__(self, name, topolink, outgoing_links, incoming_links):
        """ Constructor. This is run once when the DistanceVector object is
        created at the beginning of the simulation. Initializing data structure(s)
        specific to a DV node is done here."""

        super(DistanceVector, self).__init__(name, topolink, outgoing_links, incoming_links)
        
        # TODO: Create any necessary data structure(s) to contain the Node's internal state / distance vector data
        self.distance_vector = {}
        self.distance_vector[self.name] = 0

    def send_initial_messages(self):
        """ This is run once at the beginning of the simulation, after all
        DistanceVector objects are created and their links to each other are
        established, but before any of the rest of the simulation begins. You
        can have nodes send out their initial DV advertisements here. 

        Remember that links points to a list of Neighbor data structure.  Access
        the elements with .name or .weight """

        # TODO - Each node needs to build a message and send it to each of its neighbors
        # HINT: Take a look at the skeleton methods provided for you in Node.py

        # build the distance vector
        if (self.outgoing_links):
            for link in self.outgoing_links:
                self.distance_vector[link.name] = link.weight

        # send message to neighbors
        for link in self.incoming_links:
            self.send_msg((self.name, self.distance_vector), link.name)

    def process_BF(self):
        """ This is run continuously (repeatedly) during the simulation. DV
        messages from other nodes are received here, processed, and any new DV
        messages that need to be sent to other nodes as a result are sent. """

        # Implement the Bellman-Ford algorithm here.  It must accomplish two tasks below:
        # TODO 1. Process queued messages       
        cost_updated = False

        for msg in self.messages:  
            sender_name, sender_vector = msg

            for node in sender_vector:
                cost_to_neighbor = self.get_outgoing_neighbor_weight(sender_name)[1] # get_outgoing_neighbor_weight returns a tuple (name, weight)
                neighbor_cost_to_node = int(sender_vector[node])
                new_cost = cost_to_neighbor + neighbor_cost_to_node

                if node in self.distance_vector and node != self.name:
                    if cost_to_neighbor <= -99 or neighbor_cost_to_node <= -99:
                        if self.distance_vector[node] > -99: # the link was valid before but now invalid, update required
                            self.distance_vector[node] = -99
                            cost_updated = True
                        else:
                            self.distance_vector[node] = -99 # the link was pointing to infinity already, no update required
                    else:
                        if new_cost < int(self.distance_vector[node]):
                            self.distance_vector[node] = new_cost
                            cost_updated = True

                elif node not in self.distance_vector and node != self.name:
                    self.distance_vector[node] = new_cost
                    cost_updated = True
        # Empty queue
        self.messages = []

        # TODO 2. Send neighbors updated distances   
        if cost_updated:
            for link in self.incoming_links:
                self.send_msg((self.name, self.distance_vector), link.name)

    def log_distances(self):
        """ This function is called immedately after process_BF each round.  It 
        prints distances to the console and the log file in the following format (no whitespace either end):
        
        A:(A,0) (B,1) (C,-2)
        
        Where:
        A is the node currently doing the logging (self),
        B and C are neighbors, with vector weights 1 and 2 respectively
        NOTE: A0 shows that the distance to self is 0 """
        
        # TODO: Use the provided helper function add_entry() to accomplish this task (see helpers.py).
        # An example call that which prints the format example text above (hardcoded) is provided.        
        # add_entry("A", "(A,0) (B,1) (C,-2)")  
        log_entries = [f"({key},{value})" for key, value in self.distance_vector.items()]
        entry = " ".join(log_entries)
        add_entry(self.name, entry)