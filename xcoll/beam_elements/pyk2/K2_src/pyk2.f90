subroutine pyk2_init(n_alloc, random_generator_seed)
  use floatPrecision
  use numerical_constants
  ! use crcoall    NODIG ??
!  use parpro ,           only : npart
!  use mod_alloc ,        only : alloc      ! to allocate partID etc
 ! use mod_common ,       only : iexact, napx, unit208, aa0
 ! use mod_common_main ,  only : partID, parentID, pairID, naa
  use mod_ranlux ,       only : rluxgo     ! for ranlux init

  use coll_common ,      only : rnd_seed !, rcx, rcxp, rcy, rcyp, rcp, rcs, &
!                                coll_expandArrays
  use coll_materials ! for collmat_init
!  use coll_k2        ! for scattering
  use coll_crystal, only: cry_init

  implicit none

  integer, intent(in)          :: n_alloc
  integer, intent(in)          :: random_generator_seed

  ! Set default values for collimator materials
  call collmat_init
  call cry_init

  rnd_seed = random_generator_seed

  ! Initialize random number generator
  !if(rnd_seed == 0) rnd_seed = time_getSysClock()
  if(rnd_seed <  0) rnd_seed = abs(rnd_seed)
  call rluxgo(3, rnd_seed, 0, 0)

!  call coll_expandArrays(n_alloc)
!  call alloc(naa, n_alloc, aa0, "naa")
!  call alloc(partID, n_alloc, 0, "partID")
!  call alloc(parentID, n_alloc, 0, "parentID")
!  call alloc(pairID, 2, n_alloc, 0, "pairID")

end subroutine
 
subroutine pyk2_run(num_particles, x_particles, xp_particles, &
                y_particles, yp_particles, s_particles, &
                p_particles, part_hit, &
                part_abs, part_impact, &
                part_indiv, part_linteract, nhit_stage, nabs_type, linside, &
                matid, is_crystal, c_length, c_rotation, c_aperture, c_offset, &
                c_tilt, c_enom, onesided, random_generator_seed)

  use floatPrecision
  use numerical_constants

  use parpro ,           only : npart
  use mod_alloc ,        only : alloc      ! to allocate partID etc
  use mod_common ,       only : iexact, napx, unit208, aa0
  use mod_common_main ,  only : partID, parentID, pairID, naa
  use mod_ranlux ,       only : rluxgo     ! for ranlux init

  use coll_common ,      only : rnd_seed, rcx, rcxp, rcy, rcyp, rcp, rcs, coll_expandArrays
  use coll_materials ! for collmat_init
  use coll_k2        ! for scattering

  implicit none


  ! ############################
  ! ## variables declarations ##
  ! ############################

  integer, intent(in)       :: num_particles
  real(kind=8), intent(inout)  :: x_particles(num_particles)
  real(kind=8), intent(inout)  :: xp_particles(num_particles)
  real(kind=8), intent(inout)  :: y_particles(num_particles)
  real(kind=8), intent(inout)  :: yp_particles(num_particles)
  real(kind=8), intent(inout)  :: s_particles(num_particles)
  real(kind=8), intent(inout)  :: p_particles(num_particles)

  integer(kind=4)  , intent(inout) :: part_hit(num_particles)
  integer(kind=4)  , intent(inout) :: part_abs(num_particles)
  real(kind=8) , intent(inout) :: part_impact(num_particles)
  real(kind=8) , intent(inout) :: part_indiv(num_particles)
  real(kind=8) , intent(inout) :: part_linteract(num_particles)
  integer(kind=4)  , intent(inout) :: nhit_stage(num_particles)
  integer(kind=4)  , intent(inout) :: nabs_type(num_particles)
  logical(kind=4)  , intent(inout) :: linside(num_particles)
  integer(kind=4)  , intent(in):: matid
  logical(kind=4)  , intent(in):: is_crystal
  real(kind=8) , intent(in):: c_length
  real(kind=8) , intent(in):: c_rotation
  real(kind=8) , intent(in):: c_aperture
  real(kind=8) , intent(in):: c_offset
  real(kind=8) , intent(inout):: c_tilt(2)
  real(kind=8) , intent(in):: c_enom
  logical(kind=4) , intent(in):: onesided
  integer, intent(in)          :: random_generator_seed

  integer j



  ! ####################
  ! ## initialisation ##
  ! ####################
  !character(len=:),    allocatable   :: numpart
  !numpart="20000"
  !read(numpart,*) napx
  npart=num_particles

  if(random_generator_seed .ge. 0) then
        call rluxgo(3, random_generator_seed, 0, 0)
  end if

  do j=1,npart
    naa(j) = aa0
    partID(j)   = j
    parentID(j) = j
    pairID(1,j) = (j+1)/2    ! The pairID of particle j
    pairID(2,j) = 2-mod(j,2) ! Either particle 1 or 2 of the pair
  end do
  
  napx=npart  ! this decreases after absorptions!
  unit208=109

  do j=1,npart
    rcx(j) = x_particles(j)
    rcxp(j) = xp_particles(j)
    rcy(j) = y_particles(j)
    rcyp(j) = yp_particles(j)
    rcs(j) = s_particles(j)
    rcp(j) = p_particles(j)
  end do

  call k2coll_collimate( &
     matid, is_crystal, c_length, c_rotation, c_aperture, c_offset, c_tilt, &
     rcx, rcxp, rcy, rcyp, rcp, rcs, &
     c_enom*c1m3, part_hit, part_abs, &
     part_impact, part_indiv, part_linteract, &
     onesided, nhit_stage, 1, nabs_type, linside)

  do j=1,npart
     x_particles(j) = rcx(j)
     xp_particles(j) = rcxp(j)
     y_particles(j) = rcy(j)
     yp_particles(j) = rcyp(j)
     s_particles(j) = rcs(j)
     p_particles(j) = rcp(j)
  end do
end subroutine 


subroutine pyk2_startcry(c_length, new_length, c_rotation, cryTilt, cryBend, cryThick, cryXDim, &
                         cryYDim, cryOrient, cryMiscut)
  use coll_crystal, only: cry_startElement

  real(kind=8), intent(in)    :: c_length     ! Collimator length in m
  real(kind=8), intent(inout) :: new_length
  real(kind=8), intent(in)    :: c_rotation   ! Collimator rotation angle vs vertical in radians
  real(kind=8), intent(in)    :: cryTilt
  real(kind=8), intent(in)    :: cryBend
  real(kind=8), intent(in)    :: cryThick
  real(kind=8), intent(in)    :: cryXDim
  real(kind=8), intent(in)    :: cryYDim
  real(kind=8), intent(in)    :: cryOrient
  real(kind=8), intent(in)    :: cryMiscut
  
  call cry_startElement(c_length, new_length, c_rotation, cryTilt, cryBend, cryThick, cryXDim, &
                        cryYDim, cryOrient, cryMiscut)
end subroutine


subroutine pyk2_docrystal(mat,x,xp,z,zp,s,p,x0,xp0,zlm,s_imp,isImp,nhit,nabs, &
  lhit,part_abs,impact,indiv,c_length)
  use coll_crystal, only: cry_doCrystal


  use parpro
  use coll_common, only : cry_proc, cry_proc_prev, cry_proc_tmp
  use mathlib_bouncer

  integer,      intent(in)    :: mat
  real(kind=8), intent(inout) :: x,xp
  real(kind=8), intent(inout) :: z,zp
  real(kind=8), intent(inout) :: s,p
  real(kind=8), intent(inout) :: x0,xp0
  real(kind=8), intent(inout) :: zlm,s_imp
  integer,      intent(inout) :: nhit,nabs
  integer,      intent(inout) :: lhit
  integer,      intent(inout) :: part_abs
  real(kind=8), intent(inout) :: impact
  real(kind=8), intent(inout) :: indiv
  real(kind=8), intent(in)    :: c_length
  logical,      intent(inout) :: isImp


  call cry_doCrystal(mat,x,xp,z,zp,s,p,x0,xp0,zlm,s_imp,isImp,nhit,nabs,lhit,part_abs,impact,indiv,c_length)

end subroutine
