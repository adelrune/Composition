from __future__ import division
import pyo
from sequencer import *
from random import *
from synths import *
from composition import *
s = pyo.Server(sr=44100).boot()

marimba_seqs = [
    [Note((12/7 * randint(1, 8)) + choice([48,60]), 1/8* (1/randint(1,3)), randint(0, 1)) for i in range(randint(6,13))] for j in range(3)
]
marimba = MarimbaSynth(Sequence(marimba_seqs[0], 100))

def init():
    marimba.sequence.play()
    marimba.get_out().out()

compo = Composition(60/200, 100000, init)
compo.add_event(12, marimba.set_notes, (marimba_seqs[1],))
compo.add_event(24, marimba.set_notes, (marimba_seqs[2],))



s.start()
compo.start()
s.gui(locals())
