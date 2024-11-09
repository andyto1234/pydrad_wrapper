import pathlib
import tempfile

import astropy.units as u
from astropy.visualization import ImageNormalize, LogStretch
from datetime import datetime
from pydrad.configure import Configure
from pydrad.configure.data import get_defaults
from pydrad.configure.util import get_clean_hydrad, run_shell_command
from pydrad.parse import Strand

import platform
import os

# config = get_defaults()
config = {
    'general': {
        'loop_length': 80*u.Mm,
        'total_time': 5000*u.s,
        'footpoint_height': 5*u.Mm,
        'loop_inclination': 0*u.deg,
        'force_single_fluid': False,
        'heat_flux_timestep_limit':  1e-10*u.s,
        'logging_frequency': 1000,
        'minimum_collisional_coupling_timescale':  0.01*u.s,
        'output_interval':  10*u.s,
        'heat_flux_limiting_coefficient': 0.167,
        'use_kinetic_model': False,
        'write_file_equation_terms': True,
        'write_file_hydrogen_level_populations': True,
        'write_file_ion_populations': True,
        'write_file_physical': True,
        'write_file_timescales': True,
    },
    'grid': {
        'adapt': True,
        'adapt_every_n_time_steps': 1000,
        'enforce_conservation': True,
        'linear_restriction': True,
        'maximum_cell_width':  0.5*u.Mm,
        'maximum_fractional_difference': 0.1,
        'maximum_refinement_level': 12,
        'initial_refinement_level': 10,
        'maximum_variation': 0.1,
        'minimum_delta_s':  1.*u.cm,
        'minimum_fractional_difference': 0.05,
        'refine_on_density': True,
        'refine_on_electron_energy': True,
        'refine_on_hydrogen_energy': True,
    },
    'heating': {
        'alfven_wave': False,
        'background': {'use_initial_conditions': True},
        'beam': False,
        'electron_heating': 1.0,
        'events': [
            {'time_start': 0.*u.s,
             'rise_duration': 100*u.s,
             'decay_duration': 100*u.s,
             'total_duration': 200*u.s,
             'location': 40*u.Mm,
             'scale_height': 1e300 * u.cm,
             'rate': 0.1 * u.erg/u.s/(u.cm**3)},
        ],
    },
    'initial_conditions': {
        'footpoint_density':  1.e+12*u.cm**(-3),
        'footpoint_temperature':  10000.*u.K,
        'heating_range_fine_tuning': 10000.0,
        'heating_range_lower_bound':  1.e-08*u.erg / (u.cm**3*u.s),
        'heating_range_step_size': 0.01,
        'heating_range_upper_bound':  100.*u.erg / (u.cm**3*u.s),
        'isothermal': False,
        'use_poly_fit_gravity': False,
        'use_poly_fit_magnetic_field': False,
        'heating_location':  45.*u.Mm,
        'heating_scale_height':  1.e+300*u.cm
    },
    'radiation': {
        'abundance_dataset': 'asplund',
        'decouple_ionization_state_solver': False,
        'density_dependent_rates': False,
        'elements_equilibrium': [],
        'elements_nonequilibrium': [],
        'emissivity_dataset': 'chianti_v7',
        'nlte_chromosphere': False,
        'optically_thick_radiation': False,
        'ranges_dataset': 'ranges',
        'rates_dataset': 'chianti_v7',
        'use_power_law_radiative_losses': True
    },
    'solver': {
        'cutoff_ion_fraction': 1e-15,
        'epsilon': 0.01,
        'epsilon_d': 0.1,
        'epsilon_r': 1.8649415311920072,
        'maximum_optically_thin_density': 1.e+12*u.cm**(-3),
        'minimum_radiation_temperature':  20000.*u.K,
        'minimum_temperature':  10000.*u.K,
        'safety_advection': 1.0,
        'safety_atomic': 1.0,
        'safety_conduction': 1.0,
        'safety_radiation': 0.1,
        'safety_viscosity': 1.0,
        'timestep_increase_limit': 0.05,
        'zero_over_temperature_interval':  500.*u.K,
    }
}

config['general']['total_time'] = 1000 * u.s
config['general']['footpoint_height'] = 2.26 * u.Mm # with VALC 2.26 Mm, without 10 Mm
config['general']['output_interval'] = 1 * u.s
config['general']['loop_length'] = 100 * u.Mm
config['heating']['background']['use_initial_conditions'] = True
config['heating'] = {
        'alfven_wave': False,
        'background': {'use_initial_conditions': True},
        'beam': False,
        'electron_heating': 1.0, # whether the heat goes into electron or ions
        'events': [
            # {'time_start': 0.*u.s,
            #  'rise_duration': 100*u.s,
            #  'decay_duration': 100*u.s,
            #  'total_duration': 200*u.s,
            #  'location': 40*u.Mm,
            #  'scale_height': 1e300 * u.cm, # how broad of a gaussian heating it is gaussian width
            #  'rate': 0.1 * u.erg/u.s/(u.cm**3)}, # 0.1 is a strong nanoflare
        ],}
config['radiation']=  {
        'abundance_dataset': 'asplund',
        'decouple_ionization_state_solver': False,
        'density_dependent_rates': False,
        'elements_equilibrium': ['H', 'He', 'O', 'C', 'N', 'Ne', 'Fe', 'Si', 'Mg', 'S', 'Ar', 'Ca', 'Na', 'Ni', 'Al'], # equilibrium ionisation - 15 most abundant elements
        'elements_nonequilibrium': [],
        'emissivity_dataset': 'chianti_v10',
        'nlte_chromosphere': True,
        'optically_thick_radiation': True, # VAL-C
        'ranges_dataset': 'ranges',
        'rates_dataset': 'chianti_v10',
        'use_power_law_radiative_losses': False,
        'minimum_density_limit': 4.2486e9*u.cm**(-3),  # Set the minimum density limit here

    }

config['solver'] = {
        'cutoff_ion_fraction': 1e-15,
        'epsilon': 0.01,
        'epsilon_d': 0.1,
        'epsilon_r': 1.8649415311920072,
        'maximum_optically_thin_density': 1.e+12*u.cm**(-3),
        'minimum_radiation_temperature':  24000*u.K, # changed due to VAL-C
        'minimum_temperature':  4170*u.K, # changed due to VAL-C
        'safety_advection': 1.0,
        'safety_atomic': 1.0,
        'safety_conduction': 0.2, # lower these if crahsed - default is 1
        'safety_radiation': 0.1, # lower these if crahsed - default is 1
        'safety_viscosity': 1.0,
        'timestep_increase_limit': 0.05,
        'zero_over_temperature_interval':  500.*u.K,
    }
config['initial_conditions']= {
    'footpoint_density':  4.2486e9*u.cm**(-3), # needs to be high without VALC
    'footpoint_temperature':  2.4e4*u.K,
    'heating_range_fine_tuning': 10000.0,
    'heating_range_lower_bound':  1.e-08*u.erg / (u.cm**3*u.s),
    'heating_range_step_size': 0.01,
    'heating_range_upper_bound':  100.*u.erg / (u.cm**3*u.s),
    'isothermal': False,
    'use_poly_fit_gravity': False,
    'use_poly_fit_magnetic_field': False,
    'heating_location': 3e9*u.cm,
    'heating_scale_height':  1.e+300*u.cm
}
config['grid']['initial_refinement_level'] = 12 # 12 for active region loop
config['grid']['maximum_refinement_level'] = 12

c = Configure(config)


if platform.system() == 'Linux':
    tmpdir = pathlib.Path('/disk/solar16/st3/python/pydrad_wrapper/hydrads')
else:
    tmpdir = pathlib.Path('/Users/andysh.to/Script/Python_Script/pydrad_wrapper/hydrads')

hydrad_clean = tmpdir / f'HYDRAD_{datetime.now().strftime("%Y%m%d_%H%M%S")}'

get_clean_hydrad(hydrad_clean, base_path='hydrads/HYDRAD_ponderomotive')

test_dir = tmpdir / 'test-run'
print(test_dir)
c.setup_simulation(test_dir, hydrad_clean)

asdf_config = tmpdir / 'test_config.asdf'
c.save_config(asdf_config)
config_from_disk = Configure.load_config(asdf_config)
print(config_from_disk)
