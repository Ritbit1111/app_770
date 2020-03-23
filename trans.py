# -*- coding: utf-6 -*-
"""
Created on Fri Sep  6 06:38:59 2019

@author: Ritesh
"""

import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt 
import bokeh
import flask

df = pd.read_csv('Day1/Inv10-CB9-S4-Module1 5-8-2018 02-16 PM.csv')

df_iv = df.iloc[47:149]
df_iv.columns = ['Voltage', 'Current', 'Power']
df_iv.index = range(100)
V_measured = np.round(df_iv.Voltage.astype(float), 2)
I_measured = np.round(df_iv.Current.astype(float), 2)
P_measured = df_iv.Power.astype(float)
df_iv = pd.DataFrame({'Voltage': V_measured, 'Current': I_measured, 'Power':P_measured})
Pmax_measured = 0; index_measured=0
for i, P in enumerate(P_measured):
    if P>Pmax_measured:
        Pmax_measured = P
        index_measured = i
#print (df_iv.head())

plt.plot(df_iv.Voltage, df_iv.Current, label='Measured')

#print (df_iv.tail())
#%%

Gm = np.round(float(df.iloc[19, 1])) #Solsensor Irradiance
Tm = np.round(float(df.iloc[20, 1])) #Solsensor Temp
Tamb = np.round(float(df.iloc[21, 1]))
print (f'Irradiance:  {Gm}\nTemperature: {Tm}\n')

#%%
V = df_iv.Voltage.iloc[60:100]
I = df_iv.Current.iloc[60:100]
coeff_measured_V = np.polyfit(I, V, 1)      # (Fitting I = mV + c)
Voc_measured = np.round(coeff_measured_V[1], 2)        # This is c
#%%

#%%
V = df_iv.Voltage.iloc[0:5]
I = df_iv.Current.iloc[0:5]
coeff_measured_I = np.polyfit(V, I, 1)      # (Fitting I = mV + c)
Isc_measured = np.round(coeff_measured_I[1], 2)          # This is c
#%%
shunt_orig = np.round(-1/coeff_measured_I[0], 2);
series_orig = np.round(-coeff_measured_V[0], 2); 
plt.plot([Voc_measured, 0], [0,Isc_measured], 'bo')

plt.plot([0, V_measured[0]], [Isc_measured, I_measured[0]], 'bo--')
plt.plot([V_measured[99], Voc_measured], [I_measured[99], 0], 'bo--')

alpha=0.065; 
beta=-0.36; 
gamma=-0.5; 
Voc_Nameplate=36.7; 
Isc_Nameplate=8.40; 
Vmp_Nameplate=29.1; 
Imp_Nameplate=7.90; 
Pmp_Nameplate=230.0; 
FF_Nameplate = ((Vmp_Nameplate*Imp_Nameplate)/(Voc_Nameplate*Isc_Nameplate))*100; #Fill Factor at STC from Name Plate......
deltaT=(25-Tm);

VSTC=np.round(V_measured+((beta/100)*(Voc_Nameplate)*deltaT), 2);
ISTC=np.round(I_measured+(Isc_measured*((1000/Gm)-1))+((alpha/100)*(Isc_Nameplate)*deltaT), 2);
PSTC=VSTC*ISTC
Pmax_STC = 0; index_STC=0
for i, P in enumerate(PSTC):
    if P>Pmax_STC:
        Pmax_STC = P
        index_STC = i
#%%
'''Extraploating V and I to get Voc and Isc at STC'''
coeff_STC_V = np.polyfit(ISTC[60:100], VSTC[60:100], 1)      # (Fitting I = mV + c)
Voc_STC= np.round(coeff_STC_V[1], 2)

coeff_STC_I = np.polyfit(VSTC[0:5], ISTC[0:5], 1)      # (Fitting I = mV + c)
Isc_STC = np.round(coeff_STC_I[1], 2)
#%%
shunt_STC = np.round(-1/coeff_STC_I[0], 2);
series_STC = np.round(-coeff_STC_V[0], 2); 
plt.plot(VSTC, ISTC, label='STC Corrected')
#plt.plot([0, Voc_STC], [Isc_STC, 0], 'ro')
plt.plot([0, VSTC[0]], [Isc_STC, ISTC[0]], 'ro--')
plt.plot([VSTC[99], Voc_STC], [ISTC[99], 0], 'ro--')
print ("\nMeasured Voc, Isc : {} V, {} A\nVoc, Isc at STC   : {} V, {} A".format(Voc_measured, Isc_measured, Voc_STC, Isc_STC))
print ('Maximum Power measured: {} W\nMaximum Power points measured : {} V, {} A'.format(Pmax_measured, V_measured[index_measured],  I_measured[index_measured]))

print ('Maximum Power at STC: {} W\nMaximum Power points at STC : {} V, {} A'.format(Pmax_STC, VSTC[index_STC],  ISTC[index_STC]))
print ("Measured Series and Shunt Resistance : {}, {} \nSeries and Shunt Resistance at STC   : {}, {}".format(series_orig,shunt_orig,series_STC,shunt_STC))
plt.legend()
#plt.grid(True)
plt.xlabel('Voltage (V)')
plt.ylabel('Current (I)')
plt.show()
#%%
'''SIDT Correction'''

'''STEP 1'''
V_SIDT = V_measured
I_SIDT = I_measured * (1000/Gm)
P_SIDT = V_SIDT * I_SIDT
Pmax_SIDT = 0; index_SIDT=0
for i, P in enumerate(P_SIDT):
    if P>Pmax_SIDT:
        Pmax_SIDT = P
        index_SIDT= i
plt.plot(V_measured, I_measured, label='Measured')
plt.plot(V_SIDT, I_SIDT, label='SIDT')


#%%
'''Extraploating V_SIDT and I_SIDT to get Voc_SIDT and Isc_SIDT at STC'''
coeff_SIDT_V = np.polyfit(I_SIDT[40:100], V_SIDT[40:100], 1)      # (Fitting I = mV + c)
Voc_SIDT= np.round(coeff_SIDT_V[1], 2)

coeff_SIDT_I = np.polyfit(V_SIDT[0:5], I_SIDT[0:5], 1)      # (Fitting I = mV + c)
Isc_SIDT = np.round(coeff_SIDT_I[1], 2)
#%%

'''STEP 2'''
Isc_STC2 =  Isc_SIDT + (alpha/100)*Isc_Nameplate * deltaT
Voc_STC2 =  Voc_SIDT + (beta/100)*Voc_Nameplate * deltaT
Pmp_STC2 =  Pmax_SIDT + (gamma/100)*Pmp_Nameplate * deltaT
print ("STC(SIDT corrected) Voc, Isc : {} V, {} A ".format(Voc_STC2, Isc_STC2))
plt.plot([0, Voc_SIDT], [Isc_SIDT, 0], 'ro')
plt.plot([0, Voc_STC2], [Isc_STC2, 0], 'go', label='STC')
plt.xlabel('Voltage (V)')
plt.ylabel('Current (I)')
#plt.grid(True)
plt.legend()
plt.show()
#%%
