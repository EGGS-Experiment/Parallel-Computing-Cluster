#!/usr/bin/env python
# coding: utf-8

# # Qt_Slurm Example

# In[1]:


from qutip import *
import numpy as np
import matplotlib.pyplot as plt
from time import *
import os.path
import sys
import csv

from qt_slurm import parallel_slurm as pqt


# ### Variables

# In[ ]:


us=1e-6;
MHz=1e6;
kHz=1e3;
Hz=1;
debye=3.3e-30   #*2/3/1.5; # C/m  factor 2 is due to Bfield is 45 and 45 degree two 1/sqrt(2) away from quantization axis 
hbar=6.62607015e-34/(2*np.pi);
charge_e=1.602e-19 # C
r_0=0.55*1e-3; #meter  r0
b=1;  # ion displacement coefficient
amu=1.6605*1e-27; #kg
hcl=40*amu;
w0=2*np.pi* 1.091e6; # radian Hz natural frequency
V_c=.01 # volt on electrodes
V_b=2 # volt on electrodes
V_r=2 # volt on electrodes
scaling=1/20 # scaling the RF heating due to 3 degree off 
x0=np.sqrt(hbar/(2*hcl*w0))


# In[ ]:


num_of_divs = 5 #Number of Divisions variable necessary for Qt_Slurm to run
detunings=np.linspace(2*np.pi*0*kHz,2*np.pi*50*kHz,num_of_divs) #range to be used in detunings_func seen later


# In[ ]:


# dipole field for motion
dipole_scaling=0.715
efield_d_c=0.715*V_c/r_0
efield_d_b=0.715*V_b/r_0
efield_d_r=0.715*V_r/r_0

rabi_d_c=efield_d_c*charge_e/hbar*b*x0
rabi_d_b=efield_d_b*charge_e/hbar*b*x0
rabi_d_r=efield_d_r*charge_e/hbar*b*x0

#quadrupole field for motion

efield_q_c=V_c/r_0**2*b*x0
efield_q_b=V_b/r_0**2*b*x0
efield_q_r=V_r/r_0**2*b*x0

rabi_q_c=efield_q_c/2*charge_e/hbar*b*x0
rabi_q_b=efield_q_b/2*charge_e/hbar*b*x0
rabi_q_r=efield_q_r/2*charge_e/hbar*b*x0


#  eggs field dipole
Omega_d_b=efield_d_b*debye/(hbar);
Omega_d_r=efield_d_r*debye/(hbar);
Omega_d_c=efield_d_c*debye/(hbar);
#quadrupole
Omega_q_b=efield_q_b*debye/(hbar);
Omega_q_r=efield_q_r*debye/(hbar);
Omega_q_c=efield_q_c*debye/(hbar);

eta=np.sqrt(hbar/(2*hcl*w0))

#### floquet engineering sub-harmonic excitation
#### dqd configuration
Nmax = 40
delta=2*np.pi*70*MHz
scale=9
V_b=18*scale # volt on electrodes for bsb
V_r=48*scale # volt on electrodes for rsb
V_c=scale*0.02/17.3 #0*(0.35/40)*V_b # volt on electrodes  for carrier
w0=2*np.pi*1.4e6    #2*np.pi* 0.787e6; # radian Hz natural frequency
w0=2*np.pi*0.77e6
w0=2*np.pi*1.08e6

x0=np.sqrt(hbar/(2*hcl*w0)) 
b=1
tperiod=1e-3 # second
tau=1000*us

times = np.linspace(0,tperiod,200)

#Initialization
a = tensor(qeye(2),destroy(Nmax))
sx1 = tensor(sigmax(),qeye(Nmax))
sz1=tensor(sigmaz(),qeye(Nmax))
psi0 = tensor(basis(2,1),fock(Nmax,0))
Dtrace = tensor(basis(2,0),qeye(Nmax))
projD = Dtrace*Dtrace.dag()
n = a.dag()*a
x = (a.dag()+a)
p = 1j*(a.dag()-a)


# In[ ]:


def gammaSine2(t,args):
    return np.sin(np.pi*t/args['tau']/2)**2

def cos_c(t,args):
    if  t < args['tau']:
            return gammaSine2(t,args)*np.cos(args['w_c']*t+args['phi_c'])
    elif t >= tau and t < tperiod+tau:
            return np.cos(args['w_c']*t+args['phi_c'])
    elif t >= tperiod+tau:
            return gammaSine2(t-tperiod,args)*np.cos(args['w_c']*t+args['phi_c'])
        
def cos_c0(t,args):
    if  t < args['tau']:
            return gammaSine2(t,args)*np.cos(args['w_c0']*t+args['phi_c'])
    elif t >= tau and t < tperiod+tau:
            return np.cos(args['w_c0']*t+args['phi_c'])
    elif t >= tperiod+tau:
            return gammaSine2(t-tperiod,args)*np.cos(args['w_c0']*t+args['phi_c'])

def cos_b(t,args):
    if  t < args['tau']:
            return gammaSine2(t,args)*np.cos(args['w_b']*t+args['phi_b'])
    elif t >= tau and t < tperiod+tau:
            return np.cos(args['w_b']*t+args['phi_b'])
    elif t >= tperiod+tau:
            return gammaSine2(t-tperiod,args)*np.cos(args['w_b']*t+args['phi_b'])
def cos_b0(t,args):
    if  t < args['tau']:
            return gammaSine2(t,args)*np.cos(args['w_b0']*t+args['phi_b'])
    elif t >= tau and t < tperiod+tau:
            return np.cos(args['w_b0']*t+args['phi_b'])
    elif t >= tperiod+tau:
            return gammaSine2(t-tperiod,args)*np.cos(args['w_b0']*t+args['phi_b'])

def cos_r(t,args):
    return np.cos(args['w_r']*t + args['phi_r'])#*gammaSine2(t,args)


#Hamitonian
H0=w0*a.dag()*a+delta/2*sz1  
# internal state Hamitonian
efield_d_c=0.715*V_c/r_0
efield_d_b=0.715*V_b/r_0
efield_d_r=0.715*V_r/r_0

rabi_d_c=efield_d_c*charge_e/hbar*b*x0
rabi_d_b=efield_d_b*charge_e/hbar*b*x0
rabi_d_r=efield_d_r*charge_e/hbar*b*x0

#quadrupole field for motion

efield_q_c=V_c/r_0**2*b*x0
efield_q_b=V_b/r_0**2*b*x0
efield_q_r=V_r/r_0**2*b*x0

rabi_q_c=efield_q_c/2*charge_e/hbar*b*x0
rabi_q_b=efield_q_b/2*charge_e/hbar*b*x0
rabi_q_r=efield_q_r/2*charge_e/hbar*b*x0


#  eggs field dipole
Omega_d_b=efield_d_b*debye/(hbar);
Omega_d_r=efield_d_r*debye/(hbar);
Omega_d_c=efield_d_c*debye/(hbar);
#quadrupole
Omega_q_b=efield_q_b*debye/(hbar);
Omega_q_r=efield_q_r*debye/(hbar);
Omega_q_c=efield_q_c*debye/(hbar);

# green eggs
Hc=1*Omega_d_c*sx1
Hb=Omega_q_b*(a+a.dag())*sx1
Hr=Omega_q_r*(a+a.dag())*sx1

# motional state Hamitonian
H_c=(rabi_d_c)*(a.dag()+a)  # dipole configuration
H_b=rabi_q_b*(a.dag()+a)*(a.dag()+a) # quadrupole configuration
H_r=rabi_q_r*(a.dag()+a)*(a.dag()+a) # quadrupole configuration


# ### Function

# In[ ]:


def detuning_func(detunings):
    args_use = { 'w_c': delta+w0/3+detunings,'w_b': delta+w0/3+detunings,'w_c0': delta+2*np.pi*0.0*MHz,'w_b0': delta+2*np.pi*0.0*MHz,'w_r': delta+detunings, 'phi_r': 0*1*np.pi/2, 'phi_c': 0,'phi_b' :0, 'tau': tperiod}

    H=[H0,[H_b,cos_b],[H_c,cos_c],[H_b/10,cos_b0],[H_c/10,cos_c0]] # full green eggs hamitonian
    H=[H0,[H_b,cos_b],[H_c,cos_c],[H_b,cos_b0]] # full green eggs hamitonian

    outputc = sesolve(H,psi0,times,e_ops = [n], args = args_use,progress_bar=True,options = Options(nsteps = 1e6,max_step = tperiod/1000000,store_final_state = True))

    return outputc.expect[0][-1]


# In[ ]:


pqt.parallelize(detuning_func, detunings, num_of_divs)


# In[3]:


'''
This and the first cell that imports all modules are the only cells you need to run to queue a Slurm job
'''
pqt.execute("Qt_Slurm_Example", 5, 8, 5)


# In[ ]:




