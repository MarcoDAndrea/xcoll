#ifndef XCOLL_EVEREST_H
#define XCOLL_EVEREST_H

#include <math.h>
#include <stdio.h>


// TODO:
//    Do not split 4d and zeta in drifts
//    Use drift function from xtrack Drift element (call its C function)
//    Use rotation function from xtrack XYRotation element (call its C function)

/*gpufun*/
void drift_6d(LocalParticle* part0, double length) {
    //start_per_particle_block (part0->part)
        double const rpp    = LocalParticle_get_rpp(part);
        double const rv0v   = 1./LocalParticle_get_rvv(part);
        double const xp     = LocalParticle_get_px(part) * rpp;
        double const yp     = LocalParticle_get_py(part) * rpp;
        double const dzeta  = 1 - rv0v * ( 1. + ( xp*xp + yp*yp ) / 2. );

        LocalParticle_add_to_x(part, xp * length );
        LocalParticle_add_to_y(part, yp * length );
        LocalParticle_add_to_s(part, length);
        LocalParticle_add_to_zeta(part, length * dzeta );
    //end_per_particle_block
}

// TODO: 
// Write impacts



/*gpufun*/
void track_collimator(EverestCollimatorData el, LocalParticle* part0) {

    double const energy0 = LocalParticle_get_energy0(&part0[0]) / 1e9; // Reference energy in GeV

    // Collimator properties
    double const length  = EverestCollimatorData_get_active_length(el);
    // if collimator.jaw_F_L != collimator.jaw_B_L or collimator.jaw_F_R != collimator.jaw_B_R:
    //     raise NotImplementedError
    double const opening  = EverestCollimatorData_get_jaw_F_L(el) - EverestCollimatorData_get_jaw_F_R(el);
    double const offset   = EverestCollimatorData_get_offset(el) + ( EverestCollimatorData_get_jaw_F_L(el) + EverestCollimatorData_get_jaw_F_R(el) )/2;
    double const tilt0    = EverestCollimatorData_get_tilt(el, 0);
    double const tilt1    = EverestCollimatorData_get_tilt(el, 1);
    double const onesided = EverestCollimatorData_get_onesided(el);
    double const angle    = atan2(EverestCollimatorData_get_sin_z(el), EverestCollimatorData_get_cos_z(el) );

    // Material properties
    MaterialData material = EverestCollimatorData_getp_material(el);
    double const zatom    = MaterialData_get_Z(material);
    double const anuc     = MaterialData_get_A(material);
    double const rho      = MaterialData_get_density(material);
    double const exenergy = MaterialData_get_excitation_energy(material);
    double const emr      = MaterialData_get_nuclear_radius(material);
    double const bnref    = MaterialData_get_nuclear_elastic_slope(material);
    double const csref0   = MaterialData_get_cross_section(material, 0);
    double const csref1   = MaterialData_get_cross_section(material, 1);
    double const csref5   = MaterialData_get_cross_section(material, 5);
    double const hcut     = MaterialData_get_hcut(material);
    double const radl     = MaterialData_get_radiation_length(material);

    // Calculate scattering parameters
    struct ScatteringParameters scat = calculate_scattering(energy0,anuc,rho,zatom,emr,csref0,csref1,csref5,bnref);
    set_rutherford_parameters(zatom, emr, hcut);

    //start_per_particle_block (part0->part)

        scatter(
                part,
                scat,
                EverestCollimatorData_get_dx(el),
                EverestCollimatorData_get_dpx(el),
                EverestCollimatorData_get_dy(el),
                EverestCollimatorData_get_dpy(el),
                exenergy,
                anuc,
                zatom,
                emr,
                rho,
                hcut,
                bnref,
                csref0,
                csref1,
                csref5,
                radl,
                0,   // dlri
                0,   // dlyi
                0,   // eUm
                0,   // ai
                0,   // collnt
                0,   // is_crystal
                length,
                angle,
                opening,
                offset,
                tilt0,
                tilt1,
                onesided,
                0,   // cry_tilt
                0,   // cry_rcurv
                0,   // cry_bend
                0,   // cry_alayer
                0,   // cry_xmax
                0,   // cry_ymax
                0,   // cry_orient
                0,   // cry_miscut
                0,   // cry_cBend
                0,   // cry_sBend
                0,   // cry_cpTilt
                0,   // cry_spTilt
                0,   // cry_cnTilt
                0    // cry_snTilt
        );

    //end_per_particle_block
}

/*gpufun*/
void EverestCollimator_track_local_particle(EverestCollimatorData el, LocalParticle* part0) {
    int8_t const is_active      = EverestCollimatorData_get__active(el);
    double const inactive_front = EverestCollimatorData_get_inactive_front(el);
    double const active_length  = EverestCollimatorData_get_active_length(el);
    double const inactive_back  = EverestCollimatorData_get_inactive_back(el);

    if (!is_active){
        // Drift full length
        drift_6d(part0, inactive_front+active_length+inactive_back);
    } else {
        drift_6d(part0, inactive_front);
        track_collimator(el, part0);
        drift_6d(part0, inactive_back);
    }
}

#endif
