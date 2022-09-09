import json
import numpy    as np
import matplotlib.pyplot as plt

import xobjects as xo
import xtrack   as xt
import xpart    as xp
import xcoll    as xc



# Make a context and get a buffer
context = xo.ContextCpu()         # For CPU
# context = xo.ContextCupy()      # For CUDA GPUs
# context = xo.ContextPyopencl()  # For OpenCL GPUs
buffer = context.new_buffer()



# Load from json
with open('machines/lhc_run3_b1.json', 'r') as fid:
    loaded_dct = json.load(fid)
line = xt.Line.from_dict(loaded_dct)

line['acsca.d5l4.b1'].frequency = 400e6
line['acsca.c5l4.b1'].frequency = 400e6
line['acsca.b5l4.b1'].frequency = 400e6
line['acsca.a5l4.b1'].frequency = 400e6
line['acsca.a5r4.b1'].frequency = 400e6
line['acsca.b5r4.b1'].frequency = 400e6
line['acsca.c5r4.b1'].frequency = 400e6
line['acsca.d5r4.b1'].frequency = 400e6

df_imported = line.check_aperture()


# Patch aperture model
aperture_for_octupoles = line['mo.22r1.b1_mken_aper'].copy()
aperture_for_mqwa = line['mqwa.e5l3.b1_mken_aper'].copy()

for nn in ['mo.28r3.b1', 'mo.32r3.b1']:
    line.insert_element(index=nn, element=aperture_for_octupoles,
                        name=nn+'_aper_patch')

for nn in ['mqwa.f5l7.b1..1', 'mqwa.f5l7.b1..2', 'mqwa.f5l7.b1..3',
           'mqwa.f5l7.b1..4', 'mqwa.f5r7.b1..1', 'mqwa.f5r7.b1..2',
           'mqwa.f5r7.b1..3', 'mqwa.f5r7.b1..4']:
    line.insert_element(index=nn, element=aperture_for_mqwa,
                        name=nn+'_aper_patch')

df_patched = line.check_aperture()


# Initialise collmanager,on the specified buffer
coll_manager = xc.CollimatorManager(
    line=line,
    colldb=xc.load_SixTrack_colldb('colldb/lhc_run3_b1.dat', emit=3.5e-6),
    _buffer=buffer
    )

# Install collimators in line as black absorbers
coll_manager.install_k2_collimators(verbose=True)

# Build the tracker
tracker = coll_manager.build_tracker()

# Align the collimators
coll_manager.align_collimators_to('front')

# Set the collimator openings based on the colldb,
# or manually override with the option gaps={collname: gap}
coll_manager.set_openings()

df_with_coll = line.check_aperture()
