import numpy as np
from scipy.optimize import root

class status:
    def __init__(self, success, message):
        self.success = success
        self.message = message

    def update(self, success, message):
        self.success = success
        self.message = message

    def __str__(self):
        m = 'Success Status: ' + str(self.success) + '\n' + 'Message :' + self.message
        return m

def gen_IV(param, Voc, datapoints, Ncell):
    Vt = 25.7e-3
    Rs, Rsh, Isat, Iph, eta = param
    func = lambda i: -i + Iph - Isat*(np.exp((v+i*Rs) / (eta*Ncell*Vt))-1) - (v+i*Rs)/Rsh
    V = np.linspace(0,Voc,datapoints)
    I = []
    for v in V:
        ior = root(func,0.001)
        io = ior.x[0]
        I.append(io)
    I = np.round(I, 2)
    V = np.round(V, 2)
    return dict(x=V, y=I)

def translate(G, T, I_N, Isc, param):
    kb = 1.38*10**(-23) #Boltzmann constant
    q = 1.6*10**(-19)
    Eg = 1.1
    Rs, Rsh, Isat, Iph, eta = param
    Rs_n = Rs
    alpha = Isc*0.05/100
    K = np.log((I_N-alpha*(45-25))/Isc)/np.log(800/1000)
    Isc_n = ((G/1000)**K) * (Isc + alpha*(T-25))
    Rsh_n = (1000/G)*Rsh
    Iph_n = Isc_n*(1+Rs_n/Rsh_n)
    Isat_n = Isat*(((T+273)/(25+273))**3)*np.exp((Eg*q)/(eta*kb) * (1/(273+25) - 1/(T+273)))
    return (Rs, Rsh_n, Isat_n, Iph_n, eta)

def iv_data(Ncell=72, G=1000, T=35, Voc=45.9, Isc = 9.25, Vm=37.2, Im=8.76, I_N=7.47, datapoints=100):
    
    Vt = 25.7e-3

    #Initial Guess Calculation
    etai = (2*Vm-Voc) / (Ncell*Vt*(np.log((Isc-Im)/Isc)+Im/(Isc-Im)))
    Rsi = Vm/Im - (2*Vm-Voc) / ((Isc - Im) * (np.log((Isc-Im)/Isc) + Im/(Isc-Im)))
    if (Rsi<0):
        Rsi = 0
        num = 1 + (1-Im/Isc)*(np.log(1-Im/Isc))/(1-Vm/Voc)
        den = Im/Vm + (Isc-Im)*np.log(1-Im/Isc)/(Voc-Vm)
        Rshi = num/den
    else :
        Rshi = np.sqrt(Rsi/((Isc/(etai*Ncell*Vt)*np.exp((Rsi*Isc - Voc)/(etai*Ncell*Vt)))))

    def para(X):
        eta, Rs, Rsh = X
        f = [Im - Isc + (Vm + Im*Rs - Isc*Rs)/Rsh + (Isc - (Voc - Isc)/Rsh)*np.exp((-Voc + Vm+Im*Rs)/(eta*Ncell*Vt)), Im + Vm*((-((-Voc+Isc*Rsh+Isc*Rs)/(eta*Ncell*Vt*Rsh))*(np.exp((-Voc + Vm+Im*Rs)/(eta*Ncell*Vt)))-(1/Rsh))/(1+((-Voc+Isc*Rsh+Isc*Rs)/(eta*Ncell*Vt*Rsh)*Rs*np.exp((-Voc+Vm+Im*Rs)/(eta*Ncell*Vt)))+Rs/Rsh)), 1/Rsh + ((-((-Voc+Isc*Rsh+Isc*Rs)/(eta*Ncell*Vt*Rsh))*(np.exp((-Voc + Isc*Rs)/(eta*Ncell*Vt)))-(1/Rsh))/(1+((-Voc+Isc*Rsh+Isc*Rs)/(eta*Ncell*Vt*Rsh)*Rs*np.exp((-Voc+Isc*Rs)/(eta*Ncell*Vt)))+Rs/Rsh))]
        return f

    param_sol = root(para,[etai,Rsi,Rshi])
    eta = param_sol.x[0]
    Rs = param_sol.x[1]
    Rsh = param_sol.x[2]
    if (Rs<0):
        Rs=0

    status_param = status(param_sol.success, param_sol.message)

    Isat = (Isc - (Voc - Isc*Rs)/Rsh)*(np.exp(-Voc/(eta*Ncell*Vt)));
    Iph = Isat * np.exp(Voc / (eta*Ncell*Vt)) + (Voc/Rsh);

    param_STC = (Rs, Rsh, Isat, Iph, eta)
    param_GT = translate(G, T, I_N, Isc, param_STC)

    IV_STC = gen_IV(param_STC, Voc, datapoints, Ncell)
    IV_GT = gen_IV(param_GT, Voc, datapoints,  Ncell)
    return (IV_STC, IV_GT, dict(x=[Rs], y=[Rsh]), status_param)
