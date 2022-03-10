import json
import io
import numpy as np
import pandas as pd

import xtrack as xt
import xpart as xp

from temp_load_db import temp_load_colldb

print('Load file...')
with open('./HL_LHC_v1p5_clean_feb2022/HL_LHC_v1p5_line.json') as fid:
    dct = json.load(fid)
print('Build line...')
line = xt.Line.from_dict(dct)
#line = line.cycle(name_first_element='ip3')

# Attach reference particle (a proton a 7 TeV)
line.particle_ref = xp.Particles(mass0 = xp.PROTON_MASS_EV, p0c=7e12)

# Build tracker
tracker = xt.Tracker(line=line)

# Switch on RF (needed to twiss)
line['acsca.a5l4.b1'].voltage = 16e6
line['acsca.a5l4.b1'].frequency = 1e6

colldb = temp_load_colldb('HL_LHC_v1p5_clean_feb2022/CollDB_HL_relaxed_b1.data')

for kk in colldb.keys():
    assert kk in line.element_names

# Assumes marker in the the line is at the center of the active length
inputcolldf = pd.DataFrame.from_dict(colldb).transpose()\
                     .rename(columns={'length': 'active_length'})
inputcolldf['inactive_length_at_start'] = 1e-2
inputcolldf['inactive_length_at_end'] = 1e-2

parameters_to_be_extracted_from_twiss = (
    'x y px py betx bety alfx alfy gamx gamy dx dpx dy dpy mux muy'.split())
locations = ['at_center_active_part', 'at_start_active_part', 'at_start_element']

temp_dfs = []
for ll in locations:
    cols = pd.MultiIndex.from_tuples(
       [(ll, nn) for nn in ['s'] + parameters_to_be_extracted_from_twiss])
    newdf = pd.DataFrame(index=inputcolldf.index, columns=cols)
    temp_dfs.append(newdf)

colldf = temp_dfs[0]
for dd in temp_dfs[1:]:
    colldf = colldf.join(dd)

for cc in inputcolldf.columns[::-1]: #Try to get a nice ordering...
    colldf.insert(0, column=cc, value=inputcolldf[cc])

colldf['length'] = (colldf['active_length']
                    + colldf['inactive_length_at_start']
                    + colldf['inactive_length_at_end'])
colldf['name'] = colldf.index

colldf['at_center_active_part', 's'] = line.get_s_position(colldf['name'].to_list())
colldf['at_start_active_part', 's'] = (
    colldf['at_center_active_part', 's'] - colldf['active_length']/2)
colldf['at_start_element', 's'] = (
    colldf['at_start_active_part', 's'] - colldf['inactive_length_at_start'])

s_twiss = []
for ll in locations:
    s_twiss.extend(colldf[ll]['s'].to_list())

n_coll = len(colldf)
assert len(s_twiss) == len(locations) * n_coll

print('Start twiss')
tw = tracker.twiss(at_s=s_twiss)

for ill, ll in enumerate(locations):
    for nn in parameters_to_be_extracted_from_twiss:
        colldf[ll, nn] = tw[nn][ill*n_coll:(ill+1)*n_coll]



