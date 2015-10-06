# coding:utf-8
from __future__ import division
import pyo
import time
from sequencer import *

class BaseSynth:
    def __init__(self, sequence, amp=1, pan=0.5):
        self.sequence = sequence
        self.trig = self.sequence.trigger
        self.dur = self.sequence.time
        self.freq = self.sequence.signal
        self.amp = pyo.Sig(amp)
        self.master_amp = pyo.Port(pyo.Denorm(self.amp), init=amp, risetime=0, falltime=0)
        self.pan = pyo.Sig(pan)
        self.master_pan = pyo.Port(pyo.Denorm(self.pan), init=pan, risetime=0, falltime=0)
    def out(self):
        self.stream = self.last_audio_object.out()
    def get_out(self):
        return self.last_audio_object
    def set_amp(self, value, time):
        self.master_amp.setRiseTime(time)
        self.master_amp.setFallTime(time)
        self.amp.setValue(value)
        return self
    def set_pan(self, value, time):
        self.master_pan.setRiseTime(time)
        self.master_pan.setFallTime(time)
        self.pan.setValue(value)
        return self 
    def set_notes(self, notes):
        self.sequence = Sequence(notes).play()
        self.trig = self.sequence.trigger
        self.dur = self.sequence.time
        self.freq = self.sequence.signal
        
class MarimbaSynth(BaseSynth):
    """Approximation de marimba à peu près décente."""
    def __init__(self, sequence, amp=1, pan=0.5):
        BaseSynth.__init__(self, sequence, amp, pan)
        self.env = pyo.CosTable([(0,0.0000),(353,1.0000),(4166,0.6528),(8000,0.0000)])
        self.env_reader = pyo.TrigEnv(self.trig, self.env, dur=pyo.Max(self.dur, comp=0.3125))
        self.sine_freqs = []
        for i in range(-1,1):
            self.sine_freqs.extend([self.freq*(1+0.001*i), self.freq*2*(1+0.002*i), self.freq*3*(1+0.002*i),self.freq*5*(1+0.002*i)]) 
            
        self.osc = pyo.Sine(freq=self.sine_freqs, mul=[self.env_reader, self.env_reader*0.2, self.env_reader*0.2, self.env_reader*0.1]*3)
         
        self.trans_env = pyo.CosTable([(0,0.0000),(123,0.0777),(812,0.0570),(2083,0.0052),(8000,0.0000)])
        self.trans_env_reader = pyo.TrigEnv(self.trig, self.trans_env, dur=0.25)
        self.trans = pyo.Noise(mul=self.trans_env_reader)
        self.trans_filter = pyo.Biquad(self.trans, freq=1690)
        self.trans_resonator = pyo.Biquad(self.trans_filter, q=31, freq=self.freq*4)
        self.panner = pyo.Pan((self.trans_resonator+self.osc).mix(0), mul=(0.1)*self.master_amp, pan=self.master_pan)
        self.last_audio_object = self.panner
    def set_notes(self, notes):
        BaseSynth.set_notes(self,notes)
        self.trans_env_reader.input=self.trig
        self.env_reader.input=self.trig
        sine_freqs = []
        for i in range(-1,1):
            sine_freqs.extend([self.freq*(1+0.001*i), self.freq*2*(1+0.002*i), self.freq*3*(1+0.002*i),self.freq*5*(1+0.002*i)]) 
        
        self.osc.freq = sine_freqs
        self.trans_resonator.freq = self.freq*4
        self.env_reader.dur = pyo.Max(self.dur, comp=0.3125)
class PianoSynth(BaseSynth):
    """Bon, on s'entend que ça sonne pas comme un piano mais on va dire que ça fait la job."""
    def __init__(self, sequence, amp=1, pan=0.5):
        BaseSynth.__init__(self, sequence, amp, pan)
        self.env = pyo.CosTable([(0,0.0000),(123,0.9896),(2701,0.4870),(6479,0.2746),(8192,0.0000)])
        self.env_reader = pyo.TrigEnv(self.trig, self.env, dur=pyo.Max(self.dur, comp=0.3125))
        sine_freqs = []
        for i in range(-1,1):
            freqs = [self.freq*j*(1+0.008*i) for j in range(1,8)]
            sine_freqs.extend(freqs) 
        harm_amps = [1,0.3,0.4,0.2,0.1,0.04,0.04,0.03,0.02]
        self.osc = pyo.Sine(freq=sine_freqs, mul=[self.env_reader*harm_amps[i] for i in range(8)])
         
        self.trans_env = pyo.ExpTable([(0,0.3938),(8192,0.0000)])
        self.trans_env_reader = pyo.TrigEnv(self.trig, self.trans_env, dur=0.25)
        self.trans = pyo.Noise(mul=self.trans_env_reader)
        self.trans_filter = pyo.Biquad(self.trans, freq=1690)
        self.trans_resonator = pyo.Delay(pyo.Denorm(self.trans_filter), feedback=0.90, delay=(self.freq**-1))
        self.chorus = pyo.Chorus(self.trans_resonator, depth=0.13, feedback=0.84)
        self.master_filter = pyo.Biquad((self.chorus+self.osc).mix(0), freq=3900)
        self.panner = pyo.Pan(self.master_filter, mul=(0.1)*self.master_amp, pan=self.master_pan)
        self.last_audio_object = self.panner
    def set_notes(self, notes):
        BaseSynth.set_notes(self,notes)
        self.trans_env_reader.input=self.trig
        self.env_reader.input=self.trig
        sine_freqs = []
        for i in range(-1,1):
            freqs = [self.freq*j*(1+0.008*i) for j in range(1,8)]
            sine_freqs.extend(freqs) 
        self.osc.freq = sine_freqs
        self.trans_resonator.delay = self.freq**-1
        self.env_reader.dur = pyo.Max(self.dur, comp=0.3125)
class BassClarSynth(BaseSynth):
    """Approximation de clarinette basse."""
    def __init__(self, sequence, amp=1, pan=0.5):
        BaseSynth.__init__(self, sequence, amp, pan)
        self.env = pyo.CosTable([(0,0.0000),(953,1.0000),(5737,0.7254),(8192,0.0000)])
        self.env_reader = pyo.TrigEnv(self.trig, self.env, dur=pyo.Max(self.dur, comp=0.3125))
        self.osc = pyo.LFO(type=2, freq=pyo.Noise().range(0.7*self.freq,1.3*self.freq), mul=0.5*self.env_reader)
        self.pre_filter = pyo.Biquad(self.osc, freq=191)
        self.disto_env = pyo.CosTable([(0,0.0000),(2118,0.2694),(8192,0.0000)])
        self.disto_env_reader = pyo.TrigEnv(self.trig, self.disto_env, dur=self.dur, add=0.7)
        self.disto = pyo.Disto(self.pre_filter, drive=self.disto_env_reader, mul=0.3)
        self.freq_env = pyo.CosTable([(0,0.0000),(1553,0.4767),(8192,0.0000)])
        self.freq_env_reader = pyo.TrigEnv(self.trig, self.freq_env, dur=self.dur, add=1000, mul=200) 
        self.res_filter = pyo.Biquad(pyo.BrownNoise(mul=self.env_reader), q=6, freq=self.freq_env_reader, mul=0.9, type=2)
        self.panner = pyo.Pan(self.disto+self.res_filter, mul=self.master_amp, pan=self.master_pan)
        self.last_audio_object = self.panner
    def set_notes(self, notes):
        BaseSynth.set_notes(self,notes)
        self.osc.freq = pyo.Noise().range(0.7*self.freq,1.3*self.freq)
        self.env_reader.input=self.trig
        self.env_reader.dur = pyo.Max(self.dur, comp=0.3125)
        self.disto_env_reader.dur = self.dur
        self.freq_env_reader.dur = self.dur
        self.disto_env_reader.input = self.trig
        self.freq_env_reader.input = self.trig
class VoiceSynth(BaseSynth):
    """approximation peu réeussie de voix féminine prononçant le son "dou"."""
    def __init__(self, sequence, amp=1, pan=0.5):
        BaseSynth.__init__(self, sequence, amp, pan)
        self.formant = [235,459,1105,2735,4115]
        self.env = pyo.CosTable([(0,0.0000),(1200,0.9793),(7062,0.7772),(8000,0.0000)])
        self.env_reader = pyo.TrigEnv(self.trig, self.env, dur=self.dur)
        self.source = pyo.LFO(freq=self.freq,mul=self.env_reader)
        self.eq = pyo.EQ(self.source ,freq=[self.freq], boost=20)
        self.ffilter = pyo.SVF(self.eq, type=0.5, freq=self.formant, q=10, mul=0.1)
        self.trans_env = pyo.CosTable([(0,0.0000),(388,0.3731),(2630,0.0518),(7821,0.0000),(8000,0.0000)])
        self.trans_env_reader = pyo.TrigEnv(self.trig, self.trans_env, dur=0.25)
        self.trans = pyo.Noise(mul=self.trans_env_reader)
        self.trans_filter = pyo.Biquad(self.trans, freq=400)
        self.trans_resonator = pyo.Biquad(self.trans_filter, q=31, freq=self.freq*2, mul=0.2)
        self.panner = pyo.Pan(pyo.Compress((self.ffilter+self.trans_resonator).mix(0), mul=self.master_amp,), pan=self.master_pan)
        self.last_audio_object = self.panner
    def set_notes(self, notes):
        BaseSynth.set_notes(self,notes)
        self.env_reader.input=self.trig
        self.env_reader.dur = self.dur
        self.trans_env_reader.input=self.trig
        self.eq.freq = self.freq
        self.source.freq = self.freq
        self.trans_resonator.freq = self.freq*2
class VibeSynth(BaseSynth):
    """Synthé vaguement vibraphonesque."""
    def __init__(self, sequence, amp=1, pan=0.5):
        BaseSynth.__init__(self, sequence, amp, pan)
        self.env = pyo.CosTable([(0,0.0000),(335,0.9948),(6920,0.6218),(8192,0.0000)])
        self.env_reader = pyo.TrigEnv(self.trig, self.env, dur=self.dur)
        self.index_env = pyo.CosTable([(0,0.0000),(158,0.7668),(7662,0.0933),(8000,0.0000)])
        self.index_env_reader = pyo.TrigEnv(self.trig, self.index_env, dur=self.dur, mul=7)
        self.trans_env = pyo.CosTable([(0,0.0000),(317,1.0000),(1430,0.1347),(8000,0.0000)])
        self.trans_env_reader = pyo.TrigEnv(self.trig, self.trans_env, dur=0.25)
        self.trans = pyo.Lorenz(mul=self.trans_env_reader, chaos=1, pitch=0.265)
        self.source = pyo.FM(mul=self.env_reader,index=self.index_env_reader,ratio=2, carrier=self.freq)
        self.panner = pyo.Pan((self.source + self.trans).mix(0), mul=self.master_amp, pan=self.master_pan)
        self.last_audio_object = self.panner
    def set_notes(self, notes):
        BaseSynth.set_notes(self,notes)
        self.source.carrier = self.freq
        self.env_reader.input=self.trig
        self.env_reader.dur = self.dur
        self.index_env_reader.input=self.trig
        self.index_env_reader.dur = self.dur
        self.trans_env_reader.input = self.trig
        
#Tests.        
if __name__ == "__main__":
    
    
    def play_test():
        seqs = [Sequence([Note(56,1/8)]).play(), Sequence([Note(63,1/8)]).play(), Sequence([Note(68,1/8)]).play(), Sequence([Note(67,1/8)]).play()]
        seq3 = Sequence([Note(44,1/16)]).play()
        seqs2 = [Sequence([Note(56,1/16,0),Note(56,1/16)]).play(), Sequence([Note(63,1/16,0),Note(63,1/16)]).play(), Sequence([Note(68,1/16,0),Note(68,1/16)]).play(), Sequence([Note(67,1/16,0),Note(67,1/16)]).play()]
        seqs4 = [Sequence([Note(80,1/16)]).play(),Sequence([Note(79,1/16)]).play()]
        seqs5 = [Sequence([Note(70,1/2),Note(70,1/2),Note(68,1/2)]),Sequence([Note(74,1/2),Note(74,1/2),Note(72,1/2)])]
        #seqs = [Sequence([Note(67,1/8),Note(58,1/5)]).play()]
        #seqs2 = [Sequence([Note(56,1/16,0),Note(56,1/16)]).play()]
        p = [PianoSynth(sequence=seq, amp=0.7).out() for seq in seqs]
        m = [MarimbaSynth(sequence=seq, amp=0).out() for seq in seqs2]
        b = BassClarSynth(seq3, amp=0).out()
        v = [VoiceSynth(sequence=seq, amp=0, pan=1).out() for seq in seqs4]
        vibs = [VibeSynth(sequence=seq, amp=0.03).out() for seq in seqs5]
        for seq in seqs5:
            seq.play()
        s.setAmp(0.5)
        s.recstart("demo_mciab.wav")
        time.sleep(3)
        for vib in vibs:
            vib.sequence.stop()
        for ps in p:
            ps.set_pan(0.93, 4)
        time.sleep(2)
        for ms in m:
            ms.set_pan(0.07, 2)
            ms.set_amp(0.7, 5)
        time.sleep(4)
        b.set_amp(0.1,5)
        time.sleep(7)
        for vs in v:
            vs.set_amp(1.6,5)
            vs.set_pan(0.3,3)
        b.set_amp(0,3)
        time.sleep(7)
        for vs in v:
            vs.set_amp(0.0, 2)
        for ps in p:
            ps.set_amp(0.0, 2)
        for ms in m:
            ms.set_amp(0.0, 2)
        time.sleep(9)
        
        
    s = pyo.Server().boot()
    s.start()
    s.setAmp(0.8)
    play_test()
    s.gui(locals)
