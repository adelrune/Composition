# coding:utf-8
from __future__ import division
from pyo import TrigFunc, midiToHz, Sig, Trig, Metro
import time as Time
class Sequence:
    """Sequence of midi notes and rythms """

    def __init__(self, notes = [], tempo=96):
        self.signal = Sig(0)
        self.notes = notes
        self.tempo = tempo
        self.index = 0
        self.trigger = Trig()
        self.time = Sig(0)
        self.amp = Sig(0)
    def append(self, note):
            self.notes.append(note)
            
    def set_notes(self, notes):
        prop = 0
        
        #self.index = len(self.notes)-1
        while self.index != 0:
            prop +=1
        self._metro.stop()
        self.notes = notes
        self.index = 0
        self._metro.setTime(self.notes[self.index].time(self.tempo))
        self.amp = Sig(self.notes[self.index].amp)
        
        self._metro.play()
        
    def next(self):
        self.amp = Sig(self.notes[self.index].amp)
        self._metro.time = self.notes[self.index].time(self.tempo)
        if self.amp.get() != 0:
            self.trigger.play()
            self.signal.setValue(self.notes[self.index].frequency())
            self.time.setValue(self.notes[self.index].time(self.tempo))
        self.index = (self.index + 1) % len(self.notes)

    def play(self):
        self._metro = Metro(self.notes[0].time(self.tempo))
        self._func_caller = TrigFunc(self._metro, self.next)
        self._metro.play()
        self.amp = Sig(1)
        return self
    def stop(self):
        self._metro.stop()

class Note:
    def __init__(self, note, duration, amp=1):
        self.note = note
        self.duration = duration
        self.amp = amp
    def frequency(self):
        return midiToHz(self.note)

    def time(self, tempo):
        return 60/(tempo / self.duration / 4)
