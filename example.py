#!/usr/bin/env python
# -*- coding: utf-8 -*-


# Minimalist Composer In A Box
#
# Steve Reich styled music generator (based on music for 18 musicians)
from __future__ import division
import pyo
from sequencer import *
import random
from synths import *
import copy
from composition import *
s = pyo.Server().boot()
class MCIAB(Composition):
    def __init__(self, nbchords, update_time=(60/96)*3,tick_nb=100000):
        Composition.__init__(self, update_time, tick_nb, self.play)

        #major scale
        self.scale = [0,2,4,5,7,9,11]
        #whole range of the composition
        self.notes = [(note + i * 12) for i in range(3,8) for note in self.scale]
        #adds a high c.
        self.notes.append(96)
        # synths.
        self.bass = [BassClarSynth(Sequence([Note(0,1/16,1)]), amp=0)]
        self.chord = [[PianoSynth(Sequence([Note(0,1/8,1)])) for i in range(8)], [MarimbaSynth(Sequence([Note(0,1/16,0),Note(0,1/16)]), amp=0) for i in range(8)]]
        self.pattern = [VoiceSynth(Sequence([Note(0,1,0)]), amp=0), VoiceSynth(Sequence([Note(0,1,0)]), amp=0), PianoSynth(Sequence([Note(0,1,0)]), amp=0), BassClarSynth(Sequence([Note(0,1,0)]), amp=0)]
        self.melody = [VoiceSynth(Sequence([Note(0,1,0)]), amp=0), BassClarSynth(Sequence([Note(0,1,0)]), amp=0)]
        self.transition = VibeSynth(Sequence([Note(0,1,0)]), amp=0)
        self.pulses = VoiceSynth(Sequence([Note(0,1,0)]), amp=0)
        #list of generated chords.
        self.chords = []
        # list of 1 and 0s representing silence and notes
        self.rythm = [0,0,0,0,1,1,1,1,1,1,1,1]
        random.shuffle(self.rythm)

        #Very primitive chord generator but it works well in the context.
        for i in range(nbchords):
            self.chords.append([])
            self.chords[i].append(random.choice(self.notes[:8]))
            choice = random.choice(self.notes[:8])
            for j in range(7):
                choice = random.choice(self.notes[8:])
                while choice in self.chords[i]:
                    choice = random.choice(self.notes[8:])
                self.chords[i].append(choice)


        bar_count = self.generate_intro(nbchords)
        bar_count = self.generate_sections(bar_count)
        self.generate_intro(nbchords, bar_count, True)

        #Starts everything.

        self.master_metro.play()

    def play(self):
        outs = []
        for bss in self.bass:
            bss.sequence.play()
            outs.append(bss.get_out())
        for chrdi in self.chord:
            for chrd in chrdi:
                chrd.sequence.play()
                outs.append(chrd.get_out())
        for pat in self.pattern:
            pat.sequence.play()
            outs.append(pat.get_out())
        for mel in self.melody:
            mel.sequence.play()
            outs.append(mel.get_out())
        self.transition.sequence.play()
        outs.append(self.transition.get_out())
        self.pulses.sequence.play()
        outs.append(self.pulses.get_out())
        for out in outs:
            out.out()

    def change_chord(self, bar, chord):
        for i in range(8):
            notes = [ ( [Note(chord[i], 1/8)] ,) ,  ( [Note(chord[i], 1/16, 0) ,Note(chord[i], 1/16)], ) ]

            for j in range(2):
                self.add_event(bar, self.chord[j][i].set_notes, notes[j])

    def generate_sections(self, current_bar):

        #randomly places pulses
        def pulses(init_bar, final_bar, chord):
            already_used = 0
            if init_bar < final_bar-6:
                for i in range(random.randint(0,2)):
                    start = random.randint(init_bar, final_bar-6)
                    while start in range(already_used, already_used+6):
                        start = random.randint(init_bar, final_bar-6)
                    self.add_event(start, self.bass[0].set_notes, ([Note(random.choice(chord[:3]), 1/16)],))
                    self.add_event(start, self.pulses.set_notes, ([Note(random.choice(chord[3:]), 1/16)],) )
                    self.add_event(start, self.bass[0].set_amp, (1, self.update_rate*2))
                    self.add_event(start, self.pulses.set_amp, (1, self.update_rate*2))
                    self.add_event(start+3, self.bass[0].set_amp, (0, self.update_rate*2))
                    self.add_event(start+3, self.pulses.set_amp, (0, self.update_rate*2))

        def pattern_incr(current_bar, current_pattern):
            bar = current_bar
            one_indexes = [i for i in range(12) if self.rythm[i] == 1]
            random.shuffle(one_indexes)

            current_amps = [0 for i in range(12)]

            self.add_event(bar, self.pattern[2].set_amp, (5, self.update_rate/2))
            self.add_event(bar, self.pattern[2].set_pan, (random.random(), 0))
            self.add_event(bar+1, self.pattern[2].set_pan, (random.random(), self.update_rate*5))
            for i in range(8):
                current_amps[one_indexes[i]] = 1
                pattern = current_pattern[2]

                for j in range(12):
                    pattern[j].amp = current_amps[j]

                self.add_event(bar, self.pattern[2].set_notes, (copy.deepcopy(pattern),))
                bar+=2
            self.add_event(bar, self.pattern[2].set_amp, (0, self.update_rate*2))
            bar += 2
            return bar

        def reverse_pattern(current_bar, chord):
            bar = current_bar
            zero_indexes = [i for i in range(12) if self.rythm[i] == 0]
            random.shuffle(zero_indexes)
            current_amps = [0 for i in range(12)]
            full_pattern = self.generate_pattern(chord, 1)
            self.add_event(bar, self.pattern[3].set_amp, (2, self.update_rate/2))
            self.add_event(bar, self.pattern[3].set_pan, (random.random(), 0))
            self.add_event(bar+1, self.pattern[3].set_pan, (random.random(), self.update_rate*3))
            for i in range(4):
                current_amps[zero_indexes[i]] = 1

                pattern = full_pattern[0]
                for j in range(12):
                    pattern[j].amp = current_amps[j]

                self.add_event(bar, self.pattern[3].set_notes, (copy.deepcopy(pattern),))

                bar+=2
            self.add_event(bar, self.pattern[3].set_amp, (0, self.update_rate*2))
            bar+=2
            return bar
        #event creator function.
        def generate_events(current_bar, chord, next_chord):
            # first bar of the section
            init_bar = current_bar

            self.change_chord(current_bar,chord)
            #generates and plays the pattern for the section.
            current_patterns = self.generate_pattern(chord, 3)
            for i in range(2):
                self.add_event(current_bar, self.pattern[i].set_notes, (current_patterns[i],))
                self.add_event(current_bar, self.pattern[i].set_amp, (4, self.update_rate/2))
                self.add_event(current_bar+2, self.pattern[i].set_amp, (3, self.update_rate*1.5))
            current_bar+=2
            #possible processes for the section
            choices = [
                (pattern_incr, current_patterns),
                (reverse_pattern, chord),
                ]
            # one process randomly.
            choice = random.choice(choices)
            current_bar = choice[0](current_bar, choice[1])

            # last bar of the section
            final_bar = current_bar

            # insert pulses randomly 0 to 2 times in the section.
            pulses(init_bar, final_bar, chord)
            if next_chord != None:
                self.add_event(current_bar, self.transition.set_notes, ([Note(chord[5], 3/4)],))
                self.add_event(current_bar, self.transition.set_amp, (0.7, 0))
                self.add_event(current_bar+2, self.transition.set_notes, ([Note(next_chord[5], 3/4)],))
                self.add_event(current_bar+3, self.transition.set_amp, (0, 0))
                current_bar +=2
            else:
                for i in range(2):
                    self.add_event(current_bar, self.pattern[i].set_amp, (0, self.update_rate*2))
                    current_bar +=2
            return current_bar
        #generates the sections
        for i in range(len(self.chords)):
            if i+1 in range(len(self.chords)):
                next_chord = self.chords[i+1]
            else:
                next_chord = None
            current_bar = generate_events(current_bar, self.chords[i], next_chord)
            self.alter_rythm()
        return current_bar
    def generate_pattern(self, chord, number=1):
        indexes = [random.randint(2,7-(number-1)) for i in range(12)]
        melody = [ [ Note( (chord[indexes[i] - j]%12)+72, 1/16, self.rythm[i] ) for i in range(12) ] for j in range(number)]
        return melody

    def alter_rythm(self):
        choice = random.randint(0,99)
        if choice < 15:
            return
        elif choice < 85:
            # shifts all by one.
            last = self.rythm[0]
            self.rythm = [self.rythm[i] for i in range(1,12)]
            self.rythm.append(last)
        elif choice >85:
            # reverses the array.
            self.rythm = self.rythm[-1::-1]
    def generate_intro(self, nbchords, current_bar=1, isoutro=False):
        current_chord = self.chords[0]
        if not isoutro:
            # Absolute intro.
            self.change_chord(current_bar, current_chord)
            # set the pans for the chords.
            for i in range(8):
                pans = [0.05, 0.95]
                for j in range(2):
                    if j == 1:
                        self.add_event(current_bar+2, self.chord[j][i].set_amp, (1.2,self.update_rate*2))
                        self.add_event(current_bar+2, self.chord[j][i].set_pan, (0.95, self.update_rate))
                    self.add_event(current_bar, self.chord[j][i].set_pan, (0.05, self.update_rate))
            current_bar +=4

        def generate_events(count, current_bar):
            #exclude the first chord of the chord change.
            if count !=0 or isoutro:
                self.change_chord(current_bar, current_chord)
            current_bar += 2
            index = random.randint(5,6)
            for i in range(2):
                self.add_event(current_bar, self.pattern[i].set_notes, ([Note((current_chord[index+i]%12)+60, 1/16 )] ,) )
                self.add_event(current_bar, self.pattern[i].set_amp, (1.3, self.update_rate))
            current_bar +=2
            for i in range(2):
                self.add_event(current_bar, self.pattern[i].set_amp, (0, self.update_rate))
            index = 0
            self.add_event(current_bar, self.bass[0].set_notes, ([Note(current_chord[index], 1/16 )],) )
            self.add_event(current_bar, self.bass[0].set_amp, (1, self.update_rate))
            current_bar +=2
            self.add_event(current_bar, self.bass[0].set_amp, (0, self.update_rate))
            current_bar +=2
            return current_bar
        for i in range(nbchords):
            current_chord = self.chords[i]
            current_bar = generate_events(i, current_bar)
            if isoutro:
                #fadeout on the chords.
                current_bar +=7
                for i in range(8):
                    for j in range(2):
                        self.add_event(current_bar, self.chord[j][i].set_amp, (0,self.update_rate*3))
        return current_bar

c = MCIAB(8)
c.start()
s.setAmp(0.4)

s.start()
s.gui(locals())
