#ifndef XCOLL_EVEREST_SCAT_H
#define XCOLL_EVEREST_SCAT_H
#include <math.h>
#include <stdlib.h>
#include <stdio.h>

/*gpufun*/
double drift_zeta_single(double rvv, double xp, double yp, double length){
    double const rv0v = 1./rvv;
    double const dzeta = 1 - rv0v * (1. + (pow(xp,2.) + pow(yp,2.))/2.);
    return length * dzeta;
}

/*gpufun*/
void scatter(EverestCollimatorData el, LocalParticle* part, struct ScatteringParameters scat) {

    // Collimator properties
    double const length     = EverestCollimatorData_get_active_length(el);
    // if collimator.jaw_F_L != collimator.jaw_B_L or collimator.jaw_F_R != collimator.jaw_B_R:
    //     raise NotImplementedError
    double const c_aperture = EverestCollimatorData_get_jaw_F_L(el) - EverestCollimatorData_get_jaw_F_R(el);
    double const c_offset   = EverestCollimatorData_get_offset(el) + ( EverestCollimatorData_get_jaw_F_L(el) + EverestCollimatorData_get_jaw_F_R(el) )/2;
    double const c_tilt0    = EverestCollimatorData_get_tilt(el, 0);
    double const c_tilt1    = EverestCollimatorData_get_tilt(el, 1);
    double const onesided   = EverestCollimatorData_get_onesided(el);
    double const c_rotation = atan2(EverestCollimatorData_get_sin_z(el), EverestCollimatorData_get_cos_z(el) );
    double const co_x       = EverestCollimatorData_get_dx(el);
    double const co_y       = EverestCollimatorData_get_dy(el);

    // Material properties
    MaterialData material = EverestCollimatorData_getp_material(el);
    double const zatom    = MaterialData_get_Z(material);
    double const anuc     = MaterialData_get_A(material);
    double const rho      = MaterialData_get_density(material);
    double const exenergy = MaterialData_get_excitation_energy(material);
//     double const emr      = MaterialData_get_nuclear_radius(material);
//     double const bnref    = MaterialData_get_nuclear_elastic_slope(material);
//     double const csref0   = MaterialData_get_cross_section(material, 0);
//     double const csref1   = MaterialData_get_cross_section(material, 1);
//     double const csref5   = MaterialData_get_cross_section(material, 5);
//     double const hcut     = MaterialData_get_hcut(material);
    double const radl     = MaterialData_get_radiation_length(material);
    EverestRandomData evran = EverestCollimatorData_getp_random_generator(el);

    // Store initial coordinates for updating later
    double const rpp_in  = LocalParticle_get_rpp(part);
    double const rvv_in  = LocalParticle_get_rvv(part);
    double const e0      = LocalParticle_get_energy0(part) / 1e9; // Reference energy in GeV
    double const beta0   = LocalParticle_get_beta0(part);
    double const ptau_in = LocalParticle_get_ptau(part);
    double const x_in2    = LocalParticle_get_x(part);
    double const px_in2   = LocalParticle_get_px(part);
    double const y_in2    = LocalParticle_get_y(part);
    double const py_in2   = LocalParticle_get_py(part);
    double p0 = LocalParticle_get_p0c(part) / 1e9;

    // Move to closed orbit
    LocalParticle_add_to_x(part, -co_x);
    LocalParticle_add_to_y(part, -co_y);

    double x_in  = LocalParticle_get_x(part);
    double xp_in = LocalParticle_get_px(part)*rpp_in;
    double y_in  = LocalParticle_get_y(part);
    double yp_in = LocalParticle_get_py(part)*rpp_in;

    // TODO: missing correction due to m/m0 (but also wrong in xpart...)
    double p_in = p0*ptau_in + e0; // energy, not momentum, in GeV

    // Status flags
    int val_part_hit = 0;
    int val_part_abs = 0;
    int val_part_impact = -1;
    double val_part_indiv = -1.;
    double val_part_linteract = -1.;
    double val_nabs_type = 0;
    double val_linside = 0;

    p0 = e0;
    double nhit   = 0;
    double nabs   = 0;
    double fracab = 0;
    double nnuc0  = 0;
    double ien0   = 0;
    double nnuc1  = 0;
    double ien1   = 0;

    double x = x_in;
    double xp = xp_in;
    double z = y_in;
    double zp = yp_in;
    double p = p_in;
    double sp = 0;
    double dpop = (p - p0)/p0;
    double tiltangle = 0.;

    double mirror = 1.;

    // TODO: use xtrack C-code for rotation element

    // Compute rotation factors for collimator rotation
    double cRot   = cos(c_rotation);
    double sRot   = sin(c_rotation);
    double cRRot  = cos(-c_rotation);
    double sRRot  = sin(-c_rotation);

    // Transform particle coordinates to get into collimator coordinate  system
    // First do rotation into collimator frame
    x  =  x_in*cRot + sRot*y_in;
    z  =  y_in*cRot - sRot*x_in;
    xp = xp_in*cRot + sRot*yp_in;
    zp = yp_in*cRot - sRot*xp_in;

    // Output variables
    double x_out = x_in;
    double y_out = y_in;
    double xp_out = xp_in;
    double yp_out = yp_in;
    double p_out = p_in;
    double s_out = 0;


    // For one-sided collimators consider only positive X. For negative X jump to the next particle
    if (!onesided || (x >= 0.)) {
        // Log input energy + nucleons as per the FLUKA coupling
        nnuc0 = nnuc0 + 1.;
        ien0 = ien0 + p_in * 1.0e3;

        // Now mirror at the horizontal axis for negative X offset
        if (x < 0) {
            mirror    = -1;
            tiltangle = -1*c_tilt1;
        } else {
            mirror    = 1;
            tiltangle = c_tilt0;
        }
        x  = mirror*x;
        xp = mirror*xp;

        // Shift with opening and offset
        x = (x - c_aperture/2.) - mirror*c_offset;

        // Include collimator tilt
        if (tiltangle > 0.) {
            xp = xp - tiltangle;
        }
        if (tiltangle < 0.) {
            x  = x + sin(tiltangle) * length;
            xp = xp - tiltangle;
        }

        // particle passing above the jaw are discarded => take new event
        // entering by the face, shorten the length (zlm) and keep track of
        // entrance longitudinal coordinate (keeps) for histograms

        // The definition is that the collimator jaw is at x>=0.

        // 1) Check whether particle hits the collimator
        int isimp = 0;
        double s = 0.;
        double zlm = -1*length; 


        if (x >= 0.) {
        // Particle hits collimator and we assume interaction length ZLM equal
        // to collimator length (what if it would leave collimator after
        // small length due to angle???)
            zlm  = length;
            val_part_impact = x;
            val_part_indiv  = xp;
        }
        else if (xp <= 0.) {
        // Particle does not hit collimator. Interaction length ZLM is zero.
            zlm = 0.;
        }
        else {
        // Calculate s-coordinate of interaction point
            s = -x/xp;

            if (s < length) {
                zlm = length - s;
                val_part_impact = 0.;
                val_part_indiv  = xp;
            }
            else {
                zlm = 0.;
            }

        }
        // First do the drift part
        // DRIFT PART
        double drift_length = length - zlm;
        if (drift_length > 0) {
            x  = x  + xp * drift_length;
            z  = z  + zp * drift_length;
            sp = sp + drift_length;
        }
        // Now do the scattering part
        if (zlm > 0.) {
            if (!val_linside) {
            // first time particle hits collimator: entering jaw
                val_linside = 1;
            }
            nhit = nhit + 1;


            double* jaw_result = jaw(evran, part, exenergy,
                            anuc,
                            zatom,
                            rho,
                            radl,
                            scat.cprob0,
                            scat.cprob1,
                            scat.cprob2,
                            scat.cprob3,
                            scat.cprob4,
                            scat.cprob5,
                            scat.xintl,
                            scat.bn,
                            scat.ecmsq,
                            scat.xln15s,
                            scat.bpp,
                            p0,
                            nabs,
                            s,
                            zlm,
                            x,
                            xp,
                            z,
                            zp,
                            dpop);

            p0 = jaw_result[0];
            nabs = jaw_result[1];
            s = jaw_result[2];
            zlm = jaw_result[3];
            x = jaw_result[4];
            xp = jaw_result[5];
            z = jaw_result[6];
            zp = jaw_result[7];
            dpop = jaw_result[8];

            val_nabs_type = nabs;
            val_part_hit  = 1;

            isimp = 1;
            // simp  = s_impact

            // Writeout should be done for both inelastic and single diffractive. doing all transformations
            // in x_flk and making the set to 99.99 mm conditional for nabs=1
            if (nabs == 1 || nabs == 4) {
            // Transform back to lab system for writeout.
            // keep x,y,xp,yp unchanged for continued tracking, store lab system variables in x_flk etc

            // Finally, the actual coordinate change to 99 mm
                if (nabs == 1) {
                    fracab = fracab + 1;
                    x = 99.99e-3;
                    z = 99.99e-3;
                    val_part_linteract = zlm;
                    val_part_abs = 1;
                // Collimator jaw interaction
                }
            }

            if (nabs != 1. && zlm > 0.) {
            // Do the rest drift, if particle left collimator early
                drift_length = (length-(s+sp));

                if (drift_length > 1.0e-15) {
                    val_linside = 0;
                    x  = x  + xp * drift_length;
                    z  = z  + zp * drift_length;
                    sp = sp + drift_length;
                }
                val_part_linteract = zlm - drift_length;
            }

        }

        // Transform back to particle coordinates with opening and offset
        if (x < 99.0e-3) {
            // Include collimator tilt
            if (tiltangle > 0) {
                x  = x  + tiltangle*length;
                xp = xp + tiltangle;
            } else if (tiltangle < 0) {
                x  = x  + tiltangle*length;
                xp = xp + tiltangle;
                x  = x  - sin(tiltangle) * length;
            }

            // Transform back to particle coordinates with opening and offset
            x   = (x + c_aperture/2) + mirror*c_offset;

            // Now mirror at the horizontal axis for negative X offset
            x  = mirror * x;
            xp = mirror * xp;

            // Last do rotation into collimator frame
            x_out  =  x*cRRot +  z*sRRot;
            y_out  =  z*cRRot -  x*sRRot;
            xp_out = xp*cRRot + zp*sRRot;
            yp_out = zp*cRRot - xp*sRRot;

            // Log output energy + nucleons as per the FLUKA coupling
            // Do not log dead particles
            nnuc1       = nnuc1 + 1;                           // outcoming nucleons
            ien1        = ien1  + p_out * 1e3;                 // outcoming energy

            p_out = (1 + dpop) * p0;
            s_out = sp;
        } else {
            x_out = x;
            y_out = z;
        }
    }

    LocalParticle_set_x(part, x_out);
    LocalParticle_set_px(part, xp_out/rpp_in);
    LocalParticle_set_y(part, y_out);
    LocalParticle_set_py(part, yp_out/rpp_in);

    double energy_out = p_out;       //  Cannot assign energy directly to LocalParticle as it would update dependent variables, but needs to be corrected first!

    // Update energy    ---------------------------------------------------
    // Only particles that hit the jaw and survived need to be updated
    if (val_part_hit>0 && val_part_abs==0){
        double ptau_out = (energy_out - e0) / (e0 * beta0);
        LocalParticle_update_ptau(part, ptau_out);
    }

    // Return from closed orbit
    LocalParticle_add_to_x(part, co_x);
    LocalParticle_add_to_y(part, co_y);

    // Update 4D coordinates    -------------------------------------------
    // Absorbed particles get their coordinates set to the entrance of collimator
    if (val_part_abs>0){
        LocalParticle_set_x(part, x_in2);
        LocalParticle_set_px(part, px_in2);
        LocalParticle_set_y(part, y_in2);
        LocalParticle_set_py(part, py_in2);
    }

    // Update longitudinal coordinate zeta    -----------------------------
    // Absorbed particles keep coordinates at the entrance of collimator, others need correcting:
    // Non-hit particles are just drifting (zeta not yet drifted in K2, so do here)
    if (val_part_hit==0){
        LocalParticle_add_to_zeta(part, drift_zeta_single(rvv_in, px_in2*rpp_in, py_in2*rpp_in, length) );
    }
    // Hit and survived particles need correcting:
    if (val_part_hit>0 && val_part_abs==0){
        double px  = LocalParticle_get_px(part);
        double py  = LocalParticle_get_py(part);
        double rvv = LocalParticle_get_rvv(part);
        double rpp = LocalParticle_get_rpp(part);
        // First we drift half the length with the old angles:
        LocalParticle_add_to_zeta(part, drift_zeta_single(rvv_in, px_in2*rpp_in, py_in2*rpp_in, length/2) );
        // then half the length with the new angles:
        LocalParticle_add_to_zeta(part, drift_zeta_single(rvv, px*rpp, py*rpp, length/2) );
    }

    // Update s    --------------------------------------------------------
    // TODO: move absorbed particles to last impact location
    if (val_part_abs==0){
        LocalParticle_add_to_s(part, length);
    }

    // Update state    ----------------------------------------------------
    if (val_part_abs > 0){
        LocalParticle_set_state(part, -333);
    }

    return;

}

#endif
