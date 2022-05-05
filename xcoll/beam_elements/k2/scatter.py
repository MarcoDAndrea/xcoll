import numpy as np

def scatter(*, npart, x_part, xp_part, y_part, yp_part, s_part, p_part, part_hit,
                part_abs, part_impact, part_indiv, part_linteract, nabs_type,linside, run_exenergy, run_anuc, run_zatom,
                run_emr, run_rho,  run_hcut, run_bnref, run_csref0, run_csref1, run_csref4, run_csref5,run_radl, run_dlri, 
                run_dlyi, run_eum, run_ai, run_collnt, run_cprob, run_xintl, run_bn, run_ecmsq, run_xln15s, run_bpp, is_crystal, 
                c_length, c_rotation, c_aperture, c_offset, c_tilt, c_enom, onesided, random_generator_seed, length):
    try:
        import xcoll.beam_elements.pyk2 as pyk2
    except ImportError:
        raise Exception("Error: Failed importing pyK2 (did you compile?). Cannot track.")

    cgen = np.zeros(200, dtype=np.float64)
    pyk2.initialise_random(random_generator_seed=random_generator_seed, cgen=cgen, zatom=run_zatom, emr=run_emr, hcut=run_hcut)

    # Initilaisation
    length  = c_length
    p0 = c_enom


    # Initialise scattering processes
    # call k2coll_scatin(p0,coll_anuc,coll_rho,coll_zatom,coll_emr,&
    #                   coll_csref0,coll_csref1,coll_csref5,coll_bnref,cprob,xintl,bn)

    nhit   = 0
    nabs   = 0
    fracab = 0
    mirror = 1

    # Compute rotation factors for collimator rotation
    cRot   = np.cos(c_rotation)
    sRot   = np.sin(c_rotation)
    cRRot  = np.cos(-c_rotation)
    sRRot  = np.sin(-c_rotation)

    # Set energy and nucleon change variables as with the coupling
    # ien0,ien1: particle energy entering/leaving the collimator
    # energy in MeV
    nnuc0 = 0
    ien0  = 0
    nnuc1 = 0
    ien1  = 0

    for i in range(npart):

        x_in = np.array(x_part[i])
        xp_in = np.array(xp_part[i])
        y_in = np.array(y_part[i])
        yp_in = np.array(yp_part[i])
        s_in = np.array(s_part[i])
        p_in = np.array(p_part[i])
        val_part_hit = np.array(part_hit[i])
        val_part_abs = np.array(part_abs[i])
        val_part_impact = np.array(part_impact[i])
        val_part_indiv = np.array(part_indiv[i])
        val_part_linteract = np.array(part_linteract[i])
        val_nabs_type = np.array(nabs_type[i])
        val_linside = np.array(linside[i])

        if (val_part_abs != 0):
            continue

        
        val_part_impact = -1
        val_part_linteract = -1
        val_part_indiv = -1

        x = x_in
        xp = xp_in
        xp_in0 = xp_in
        z = y_in
        zp = yp_in
        p = p_in
        sp = 0
        dpop = (p - p0)/p0
        x_flk = 0
        y_flk = 0
        xp_flk = 0
        yp_flk = 0

        # Transform particle coordinates to get into collimator coordinate  system
        # First do rotation into collimator frame
        x  =  x_in*cRot + sRot*y_in
        z  =  y_in*cRot - sRot*x_in
        xp = xp_in*cRot + sRot*yp_in
        zp = yp_in*cRot - sRot*xp_in
        
        # For one-sided collimators consider only positive X. For negative X jump to the next particle
        if (onesided & (x < 0)):
            continue

        # Log input energy + nucleons as per the FLUKA coupling
        nnuc0   = nnuc0 + 1
        ien0    = ien0 + p_in * 1.0e3

        # Now mirror at the horizontal axis for negative X offset
        if (x < 0):
            mirror    = -1
            tiltangle = -1*c_tilt[1]
        else:
            mirror    = 1
            tiltangle = c_tilt[0]
    
        x  = mirror*x
        xp = mirror*xp

        # Shift with opening and offset
        x = (x - c_aperture/2) - mirror*c_offset

        # Include collimator tilt
        if(tiltangle > 0):
            xp = xp - tiltangle
        
        if(tiltangle < 0):
            x  = x + np.sin(tiltangle) * c_length
            xp = xp - tiltangle


        # CRY Only: x_in0 has to be assigned after the change of reference frame
        x_in0 = x

        # After finishing the coordinate transformation, or the coordinate manipulations in case of pencil beams,
        # save the initial coordinates of the impacting particles
        xin  = x
        xpin = xp
        yin  = z
        ypin = zp

        # particle passing above the jaw are discarded => take new event
        # entering by the face, shorten the length (zlm) and keep track of
        # entrance longitudinal coordinate (keeps) for histograms

        # The definition is that the collimator jaw is at x>=0.

        # 1) Check whether particle hits the collimator
        isimp = False
        s     = 0
        keeps = 0
        zlm = -1*length


        isimp = np.array(isimp)
        s = np.array(s)
        zlm = np.array(zlm)
        sp = np.array(sp)
        x_flk = np.array(x_flk)
        y_flk = np.array(y_flk)
        xp_flk = np.array(xp_flk)
        yp_flk = np.array(yp_flk)

        x = np.array(x)
        xp = np.array(xp)
        xp_in0 = np.array(xp_in0)
        z = np.array(z)
        zp = np.array(zp)
        p = np.array(p)
        dpop = np.array(dpop)
        x_in0 = np.array(x_in0)
        xin = np.array(xin)
        xpin = np.array(xpin)
        yin = np.array(yin)
        ypin = np.array(ypin)

        pyk2.pyk2_run(
                    x_in=x_in,
                    xp_in=xp_in,
                    y_in=y_in,
                    yp_in=yp_in,
                    s_in=s_in,
                    p_in=p_in,
                    val_part_hit=val_part_hit,
                    val_part_abs=val_part_abs,
                    val_part_impact=val_part_impact,
                    val_part_indiv=val_part_indiv,
                    val_part_linteract=val_part_linteract,
                    val_nabs_type=val_nabs_type,
                    val_linside=val_linside,
                    run_exenergy=run_exenergy,
                    run_anuc=run_anuc,
                    run_zatom=run_zatom,
                    run_emr=run_emr,
                    run_rho=run_rho,
                    run_hcut=run_hcut,
                    run_bnref=run_bnref,
                    run_csref0=run_csref0,
                    run_csref1=run_csref1,
                    run_csref4=run_csref4,
                    run_csref5=run_csref5,
                    run_radl=run_radl,
                    run_dlri=run_dlri,
                    run_dlyi=run_dlyi,
                    run_eum=run_eum,
                    run_ai=run_ai,
                    run_collnt=run_collnt,
                    run_cprob=run_cprob,
                    run_xintl=run_xintl,
                    run_bn=run_bn,
                    run_ecmsq=run_ecmsq,
                    run_xln15s=run_xln15s,
                    run_bpp=run_bpp,
                    run_cgen=cgen,
                    is_crystal=is_crystal,
                    c_length=c_length,
                    c_aperture=c_aperture,
                    c_offset=c_offset,
                    c_tilt=c_tilt,
                    onesided=onesided,
                    length=length,
                    p0=p0,
                    nhit=nhit,
                    nabs=nabs,
                    fracab=fracab,
                    mirror=mirror,
                    crot=cRot,
                    srot=sRot,
                    crrot=cRRot,
                    srrot=sRRot,
                    nnuc0=nnuc0,
                    nnuc1=nnuc1,
                    ien0=ien0,
                    ien1=ien1,
                    isimp=isimp,
                    s=s,
                    keeps=keeps,
                    zlm=zlm,
                    x=x,
                    xp=xp,
                    xp_in0=xp_in0,
                    z=z,
                    zp=zp,
                    p=p,
                    sp=sp,
                    dpop=dpop,
                    x_flk=x_flk,
                    y_flk=y_flk,
                    xp_flk=xp_flk,
                    yp_flk=yp_flk,
                    x_in0=x_in0,
                    xin=xin,
                    xpin=xpin,
                    yin=yin,
                    ypin=ypin,
                    tiltangle=tiltangle
                    )

        x_part[i] = x_in
        xp_part[i] = xp_in
        y_part[i] = y_in
        yp_part[i] = yp_in
        s_part[i] = s_in
        p_part[i] = p_in
        part_hit[i] = val_part_hit
        part_abs[i] = val_part_abs
        part_impact[i] = val_part_impact
        part_indiv[i] = val_part_indiv
        part_linteract[i] = val_part_linteract
        nabs_type[i] = val_nabs_type
        linside[i] = val_linside
