########################### PARAMETERS ##############################
# anuc  : standard atomic weight (mass number averaged over isotopes)
# zatom : number of protons (atomic number)
# rho   : density / g cm-3
# emr   : 
# hcut  :
# radl  : radiation length / m
# bnref : nuclear interaction length / g cm-2 
# csref : 
# cprob :
#####################################################################

materials = {
# Berylium
  'BE': {
        'ID': 1,
        'exenergy': 63.7e-9,
        'anuc': 9.01,         
        'zatom': 4.00,
        'rho': 1.848,
        'emr': 0.22,
        'hcut': 0.02,
        'radl': 0.353,
        'bnref': 74.7,
        'csref': [0.271, 0.192, 0, 0, 0, 0.0035e-2],
        'cprob': [0, 0, 0, 0, 0, 1]
        },

# Aluminium
  'AL': {
        'ID': 2,
        'exenergy': 166.0e-9,
        'anuc': 26.98,
        'zatom': 13.00,
        'rho': 2.70,
        'emr': 0.302,
        'hcut': 0.02,
        'radl': 0.089,
        'bnref': 120.3,
        'csref': [0.643, 0.418, 0, 0, 0, 0.0340e-2],
        'cprob': [0, 0, 0, 0, 0, 1]
        },

# Copper
  'CU': {
        'ID': 3,
        'exenergy': 322.0e-9,
        'anuc': 63.55,
        'zatom': 29.00,
        'rho': 8.96,
        'emr': 0.366,
        'hcut': 0.01,
        'radl': 0.0143,
        'bnref': 217.8,
        'csref': [1.253, 0.769, 0, 0, 0, 0.1530e-2],
        'cprob': [0, 0, 0, 0, 0, 1]
        },

# Tungsten
  'W': {
        'ID': 4,
        'exenergy': 727.0e-9,
        'anuc': 183.85,
        'zatom': 74.00,
        'rho': 19.30,
        'emr': 0.5208318900309039, # 0.520,
        'hcut': 0.01,
        'radl': 0.0035,
        'bnref': 420.4304986267596, # 440.3
        'csref': [2.765, 1.591, 0, 0, 0, 0.7680e-2],
        'cprob': [0, 0, 0, 0, 0, 1]
        },

# Lead
  'PB': {
        'ID': 5,
        'exenergy': 823.0e-9,
        'anuc': 207.19,
        'zatom': 82.00,
        'rho': 11.35,
        'emr': 0.542,
        'hcut': 0.01,
        'radl': 0.0056,
        'bnref': 455.3,
        'csref': [3.016, 1.724, 0, 0, 0, 0.9070e-2],
        'cprob': [0, 0, 0, 0, 0, 1]
        },

# Carbon
  'C': {
        'ID': 6,
        'exenergy': 78.0e-9,
        'anuc': 12.01,
        'zatom': 6.00,
        'rho': 1.67,
        'emr': 0.25,
        'hcut': 0.02,
        'radl': 0.2557,
        'bnref': 70.0,
        'csref': [0.337, 0.232, 0, 0, 0, 0.0076e-2],
        'cprob': [0, 0, 0, 0, 0, 1]
        },

# Carbon2
  'C2': {
        'ID': 7,
        'exenergy': 78.0e-9,
        'anuc': 12.01,
        'zatom': 6.00,
        'rho': 4.52,
        'emr': 0.25,
        'hcut': 0.02,
        'radl': 0.094,
        'bnref': 70.0,
        'csref': [0.337, 0.232, 0, 0, 0, 0.0076e-2],
        'cprob': [0, 0, 0, 0, 0, 1]
        },

# Silicon
  'Si': {
        'ID': 8,
        'exenergy': 173.0e-9,
        'anuc': 28.08,
        'zatom': 14.00,
        'rho': 2.33,
        'emr': 0.441,
        'hcut': 0.02,
        'radl': 1,
        'bnref': 120.14,
        'csref': [0.664, 0.430, 0, 0, 0, 0.0390e-2],
        'cprob': [0, 0, 0, 0, 0, 1]
        },

# Germanium
  'Ge': {
        'ID': 9,
        'exenergy': 350.0e-9,
        'anuc': 72.63,
        'zatom': 32.00,
        'rho': 5.323,
        'emr': 0.605,
        'hcut': 0.02,
        'radl': 1,
        'bnref': 226.35,
        'csref': [1.388, 0.844, 0, 0, 0, 0.1860e-2],
        'cprob': [0, 0, 0, 0, 0, 1]
        },    

# 
  'MoGR': {
        'ID': 10,
        'exenergy': 87.1e-9,
        'anuc': 13.53,
        'zatom': 6.65,
        'rho': 2.500,
        'emr': 0.25,
        'hcut': 0.02,
        'radl': 0.1193,
        'bnref': 76.7,
        'csref': [0.362, 0.247, 0, 0, 0, 0.0094e-2],
        'cprob': [0, 0, 0, 0, 0, 1]
        },   

# 
  'CuCD': {
        'ID': 11,
        'exenergy': 152.9e-9,
        'anuc': 25.24,
        'zatom': 11.90,
        'rho': 5.40,
        'emr': 0.308,
        'hcut': 0.02,
        'radl': 0.0316,
        'bnref': 115.0,
        'csref': [0.572, 0.370, 0, 0, 0, 0.0279e-2],
        'cprob': [0, 0, 0, 0, 0, 1]
        },  

# Molybdium Graphite
  'Mo': {
        'ID': 12,
        'exenergy': 424.0e-9,
        'anuc': 95.96,
        'zatom': 42.00,
        'rho': 10.22,
        'emr': 0.481,
        'hcut': 0.02,
        'radl': 0.0096,
        'bnref': 273.9,
        'csref': [1.713, 1.023, 0, 0, 0, 0.2650e-2],
        'cprob': [0, 0, 0, 0, 0, 1]
        },     

# 
  'Glid': {
        'ID': 13,
        'exenergy': 320.8e-9,
        'anuc': 63.15,
        'zatom': 28.80,
        'rho': 8.93,
        'emr': 0.418,
        'hcut': 0.02,
        'radl': 0.0144,
        'bnref': 208.7,
        'csref': [1.246, 0.765, 0, 0, 0, 0.1390e-2],
        'cprob': [0, 0, 0, 0, 0, 1]
        },   

# 
  'Iner': {
        'ID': 14,
        'exenergy': 682.2e-9,
        'anuc': 166.70,
        'zatom': 67.70,
        'rho': 18.00,
        'emr': 0.578,
        'hcut': 0.02,
        'radl': 0.00385,
        'bnref': 392.1,
        'csref': [2.548, 1.473, 0, 0, 0, 0.5740e-2],
        'cprob': [0, 0, 0, 0, 0, 1]
        },        

# Vacuum  
  'VA': {
        'ID': 15,
        'exenergy': 0,
        'anuc': 0,
        'zatom': 0,
        'rho': 0,
        'emr': 0,
        'hcut': 0,
        'radl': 1.0e1,
        'bnref': 0,
        'csref': [0, 0, 0, 0, 0, 0],
        'cprob': [0, 0, 0, 0, 0, 1]
        },        

# Black Absorber
  'BL': {
        'ID': 16,
        'exenergy': 1.0e10, # c1e10 
        'anuc': 0,
        'zatom': 0,
        'rho': 0,
        'emr': 0,
        'hcut': 0,
        'radl': 1.0e1,
        'bnref': 0,
        'csref': [0, 0, 0, 0, 0, 0],
        'cprob': [0, 0, 0, 0, 0, 1]
        },    
  
}
