from neuron import h
import math

class Current_injection(object):
    """A module for current injection"""
    def __init__(self,cell,sec_index,loc=0.5,pulse=True,current=[0],Dt=None,record=False,**pulse_param):
        """
        cell: target cell object
        sec_index: index of the target section in the section list
        loc: location on a section, between [0,1]
        pulse: If True, use pulse injection with keyword arguments in 'pulse_param'
               If False, use waveform data in vector 'current' as injection
        Dt: current vector time step size
        record: If True, enable recording current injection history
        """
        self.cell = cell
        self.sec_index = sec_index
        self.ccl = h.IClamp(self.get_section()(loc))
        self.inj_vec = self.rec_vec = None
        if pulse:
            self.setup_pulse(**pulse_param)
        else:
            self.setup_current(current,Dt)
        if record:
            self.setup_recorder()
    
    def setup_pulse(self,**pulse_param):
        """Set IClamp attributes. Argument keyword: attribute name, arugment value: attribute value"""
        for param,value in pulse_param.items():
            setattr(self.ccl,param,value)
    
    def setup_current(self,current,Dt):
        """Set current injection with the waveform in vector 'current'"""
        self.ccl.dur = 0
        self.ccl.dur = h.tstop if hasattr(h,'tstop') else 1e30
        if Dt is None:
            Dt = h.dt
        self.inj_vec = h.Vector()
        self.inj_vec.from_python(current)
        self.inj_vec.append(0)
        self.inj_vec.play(self.ccl._ref_amp,Dt)
    
    def setup_recorder(self):
        size = [round(h.tstop/h.dt)+1] if hasattr(h,'tstop') else []
        self.rec_vec = h.Vector(*size).record(self.ccl._ref_i)
    
    def get_section(self):
        return self.cell.all[self.sec_index]
    
    def get_segment(self):
        return self.ccl.get_segment()
    
    def get_segment_id(self):
        """Get the index of the injection target segment in the segment list"""
        iseg = math.floor(self.get_segment().x*self.get_section().nseg)
        return self.cell.sec_id_in_seg[self.sec_index]+iseg
