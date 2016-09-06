#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import pyo

class Composition:
    def __init__(self, update_rate, tick_nb, init_funct):
        #Rate at which events are called.
        self.update_rate = update_rate
        #Metronome ticking at the update rate.
        self.master_metro = pyo.Metro(self.update_rate)
        #Signal equal to the current position in the piece.
        self.counter = pyo.Counter(self.master_metro, min=0, max=tick_nb)
        #Calls the events at the current counter position every update tick
        self.event_tf = pyo.TrigFunc(self.master_metro, self._call_event)
        #Calls the init function as soo as .
        self.init_tf = pyo.TrigFunc(pyo.Select(self.counter, value=0), init_funct)
        #Dictionary containing lists of tuples (function_to_call, args*) at [tick_nb].
        self.structure = {}

        self.master_metro.play()

    
    def add_event(self, bar_nb, function, args):
        """Add an event to the structure. Args should be a tuple of the wanted arguments."""
        if bar_nb not in self.structure.keys():
            self.structure[bar_nb] = [(function, args)]
        else:
            self.structure[bar_nb].append((function, args))

    def _call_event(self):
        """Called every tick by event_tf, should never be called manually."""
        key = self.counter.get()
        #la structure dans le dictionnaire est une liste de tuples ayant comme premier élément une fonction et comme deuxième un tuple des arguments
        if key in self.structure.keys():
            for func in self.structure[key]:
                func[0](*func[1])
    def start(self):
        """Starts the master metronome which immediately calls the initialisation fuction"""
        self.master_metro.play()
