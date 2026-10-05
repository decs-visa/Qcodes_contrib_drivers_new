"""  DECS driver for TeslatronPT and TeslatronPT Plus systems  """
""" Developed and maintained by Quantum Design Oxford """

from qcodes.instrument import VisaInstrument
from functools import partial
from typing import Any, Union
import numpy as np
import time
import subprocess
from qcodes.parameters import MultiParameter, ManualParameter
from qcodes import validators as vals
import platform

# path required for running in Azure repo
import sys
sys.path.append('../')  
from _decsvisa.src.decs_visa_tools.decs_visa_settings import PORT  # comment out to use simulated instrument in /qcodes/instrument/sims/ directory
from _decsvisa.src.decs_visa_tools.decs_visa_settings import HOST  # comment out to use simulated instrument in /qcodes/instrument/sims/ directory
from _decsvisa.src.decs_visa_tools.decs_visa_settings import SHUTDOWN  # comment out to use simulated instrument in /qcodes/instrument/sims/ directory
from _decsvisa.src.decs_visa_tools.decs_visa_settings import WRITE_DELIM  # comment out to use simulated instrument in /qcodes/instrument/sims/ directory

# path required for official QCoDeS repo
#from qcodes_contrib_drivers.drivers.QuantumDesign._decsvisa.src.decs_visa_tools.decs_visa_settings import PORT
#from qcodes_contrib_drivers.drivers.QuantumDesign._decsvisa.src.decs_visa_tools.decs_visa_settings import HOST
#from qcodes_contrib_drivers.drivers.QuantumDesign._decsvisa.src.decs_visa_tools.decs_visa_settings import SHUTDOWN
#from qcodes_contrib_drivers.drivers.QuantumDesign._decsvisa.src.decs_visa_tools.decs_visa_settings import WRITE_DELIM

'''

    Please see the README.md file in this directory for setup instructions.

'''

#############################################
#    System configuration settings     #
#############################################

# If there is a superconducting magnet
# is it fitted with a switch:
MAGNET_HAS_SWITCH=True

#############################################

class Magnetic_Field_Parameters(MultiParameter):
    """
    Parameter for retrieving X, Y, and Z components of the magnetic field. 

    To Retrieve all three parameters via `instrument.Magnetic_Field_Vector()`
    To retrieve single parameter using index e.g. `instrument.Magnetic_Field_Vector()[2]`

    """

    def __init__(
        self, name, instrument, **kwargs: Any
    ) -> None:
        super().__init__(
            name=name,
            instrument=instrument,
            names=("X_Field", "Y_Field", "Z_Field"),
            labels=(
                f"{instrument} X_Field",
                f"{instrument} Y_Field",
                f"{instrument} Z_Field",
            ),
            units=("T", "T", "T"),
            setpoints=((), (), ()),
            shapes=((), (), ()),
            snapshot_get=True,
            snapshot_value=True,
            **kwargs,
        )

    def get_raw(self) -> tuple[float, ...]:
        """
        Gets the values of magnetic field from the instrument
        """
        assert isinstance(self.instrument, DECS)
        Bx, By, Bz = self.instrument._get_field_data()
        return Bx, By, Bz

    def set_raw(self, value) -> None:
        """
        Disabled setter for this read-only parameter.

        This method overrides the base class setter to prevent users from
        attempting to directly modify magnet currents through this parameter
        """
        print("*** Field cannot be set directly with this function ***")
    
class Magnet_Current_Parameters(MultiParameter):
    """
    Parameter for retrieving X, Y, and Z components of the magnet current. 

    Retrieve all three parameters via `instrument.Magnet_Current_Vector()`
    Retrieve single parameter using index e.g. `instrument.Magnet_Current_Vector()[2]`
    
    """

    def __init__(
        self, name, instrument, **kwargs: Any
    ) -> None:
        super().__init__(
            name=name,
            instrument=instrument,
            names=("X_Current", "Y_Current", "Z_Current"),
            labels=(
                f"{instrument} X_Current",
                f"{instrument} Y_Current",
                f"{instrument} Z_Current",
            ),
            units=("A", "A", "A"),
            setpoints=((), (), ()),
            shapes=((), (), ()),
            snapshot_get=True,
            snapshot_value=True,
            **kwargs,
        )

    def get_raw(self) -> tuple[float, ...]:
        """
        Gets the values of magnet current from the instrument
        """
        assert isinstance(self.instrument, DECS)
        Ix, Iy, Iz = self.instrument._get_field_current_data()
        return Ix, Iy, Iz

    def set_raw(self, value) -> None:
        """
        Disabled setter for this read-only parameter.

        This method overrides the base class setter to prevent users from
        attempting to directly modify magnet currents through this parameter
        """
        print("*** Current cannot be set directly with this function ***")

class Magnet_Field_Target(MultiParameter):
    """
    Parameter for retrieving X, Y and Z components of the magnet field target.

    Retrieve all three parameters via `instrument.Magnet_Field_Target()`
    Retrieve single parameter using index e.g. `instrument.Magnet_Field_Target()[2]`
    
    """
    def __init__(
        self, name, instrument, **kwargs: Any
    ) -> None:
        super().__init__(
            name=name,
            instrument=instrument,
            names=("X_Target", "Y_Target", "Z_Target"),
            labels=(
                f"{instrument} X_Target",
                f"{instrument} Y_Target",
                f"{instrument} Z_Target",
            ),
            units=("T", "T", "T"),
            setpoints=((),(),()),
            shapes=((), (), ()),
            snapshot_get=True,
            snapshot_value=True,
            **kwargs,
        )

    def get_raw(self) -> tuple[float, ...]:
        """
        Gets the values of field target from the instrument
        """
        assert isinstance(self.instrument, DECS)
        Bx, By, Bz = self.instrument._get_field_target_data()
        return Bx, By, Bz

    def set_raw(self, value) -> None:
        """
        Disabled setter for this read-only parameter.

        This method overrides the base class setter to prevent users from
        attempting to directly modify magnet currents through this parameter
        """
        print("*** Field target cannot be set directly with this function ***")
            
class DECS(VisaInstrument):

    def __init__(self, name, decsvisa_path, **kwargs) -> None:
        """
        name (str): instrument name e.g. 'Teslatron'
        decsvisa_path (str): supply the file path from your working directory to the decs_visa.py file
                             or the absolute file path of decsvisa.py
        """
        
        # start decsvisa
        running_on = platform.platform()
        if running_on.startswith("Windows"):
            print(f"Running on {running_on} - start subprocess without PIPEd output")
            subprocess.Popen(["python", decsvisa_path]) # comment out to use simulated instrument in /qcodes/instrument/sims/ directory
        else:
            print(f"Running on {running_on} - start subprocess with PIPEd output")
            subprocess.Popen(["python3", decsvisa_path], stdout=subprocess.PIPE) # comment out to use simulated instrument in /qcodes/instrument/sims/ directory

        time.sleep(1)

        # super().__init__(name, 'TCPIP0::127.0.0.1::33575::SOCKET', terminator="\n", **kwargs) # for using simulated instrument in /qcodes/instrument/sims/ directory
        super().__init__(name, f'TCPIP::{HOST}::{PORT}::SOCKET', terminator=WRITE_DELIM, **kwargs) # for real DECS system with DECSVISA, comment out to use simulated instrument in /qcodes/instrument/sims/ directory
        
        self.add_parameter(
            "PT1_Plate_Temperature",
            unit="K",
            label="PT1 Plate Temperature",
            get_cmd="get_PT1_T",
            get_parser=float
        )

        self.add_parameter(
            "PT2_Plate_Temperature",
            unit="K",
            label="PT2 Plate Temperature",
            get_cmd="get_PT2_T",
            get_parser=float
        )

        self.add_parameter(
            "Magnet_Temperature",
            unit="K",
            label="Magnet Temperature",
            get_cmd="get_MAG_T",
            get_parser=float
        )

        self.add_parameter(
            "Sample_Temperature",
            unit="K",
            label="Sample Temperature",
            get_cmd="get_SAMPLE_T",
            set_cmd=partial(self._param_setter, "set_SAMPLE_T"),
            get_parser=float
        )

        self.add_parameter(
            "Probe_Temperature",
            unit="K",
            label="Probe Temperature",
            get_cmd="get_PROBE_T",
            set_cmd=partial(self._param_setter, "set_PROBE_T"),
            get_parser=float
        )
        
        self.add_parameter(
            "Probe_Target_Temperature",
            unit="K",
            label="Probe Target Temperature",
            get_cmd="get_PROBE_TARGET_T",
            get_parser=float
        )

        self.add_parameter(
            "VTI_Temperature",
            unit="K",
            label="VTI Temperature",
            get_cmd="get_VTI_T",
            set_cmd=partial(self._param_setter, "set_VTI_T"),
            get_parser=float
        )
        
        self.add_parameter(
            "VTI_Target_Temperature",
            unit="K",
            label="VTI Target Temperature",
            get_cmd="get_VTI_TARGET_T",
            get_parser=float
        )

        self.add_parameter(
            "Probe_Heater_Power",
            unit="W",
            label="Probe Heater Power",
            get_cmd="get_PROBE_H",
            set_cmd=partial(self._param_setter, "set_PROBE_H"),
            get_parser=float
        )
        
        self.add_parameter(
            "VTI_Heater_Power",
            unit="W",
            label="VTI Heater Power",
            get_cmd="get_VTI_H",
            set_cmd=partial(self._param_setter, "set_VTI_H"),
            get_parser=float
        )

        self.add_parameter(
            "VTI_Pressure",
            unit="Pa",
            label="VTI Pressure",
            get_cmd="get_PRES",
            set_cmd=partial(self._param_setter, "set_PRES"),
            get_parser=float
        )

        self.add_parameter(
            "Base_Pressure",
            unit="Pa",
            label="Base Pressure",
            parameter_class=ManualParameter,
            initial_value=680
        )
        
        self.add_parameter(
            "Sample_and_VTI_Linked",
            label="Sample and VTI Linked",
            get_cmd="get_CIRC_LINK",
            set_cmd=partial(self._param_setter, "set_CIRC_LINK")
        )


        self.add_parameter(
            "Temperature_Ramp_Rate",
            unit="K/s",
            label="Temperature Ramp Rate",
            get_cmd="get_CIRC_RATE",
            set_cmd=partial(self._param_setter, "set_CIRC_RATE"),
            get_parser=float,
            vals=vals.Numbers(0.000017, 0.166667)
        )
  
        self.add_parameter(
            "Temperature_Ramp_Target",
            unit="K",
            label="Temperature Ramp Target",
            get_cmd="get_CIRC_TARGET",
            get_parser=float,
            set_cmd=partial(self._param_setter, "set_CIRC_TARGET"),
        )

        self.add_parameter(
            "High_Flow_Enabled",
            label="High_Flow_Enabled",
            get_cmd="get_CIRC_HIGH_FLOW",
            set_cmd=partial(self._param_setter, "set_CIRC_HIGH_FLOW")
        )

        self.add_parameter(
            "Temperature_Stable",
            label="Temperature_Stable",
            get_cmd="get_CIRC_TEMP_STAB",
            get_parser=str,
            val_mapping={'True': '1', 'False': '0', 'Undefined': '2'}
        )
            
        self.add_parameter(
            "System_State",
            label="System_State",
            get_cmd="get_STATE",
            get_parser=str,
            val_mapping={'Manual': '0',
                         'Idle': '10',
                         'Cooldown': '1000',
                         'Aborting Cooldown': '2000',
                         'Warming Up': '3000',
                         'Warming Up Skip Recooling': '4000',
                         'Tank Recharging': '5000',
                         'Aborting Tank Recharging': '6000',
                         'Circulating': '7000',
                         'Sample Exchange': '10000',
                         'Disconnect Probe': '10100',
                         'Specify Probe': '10200',
                         'Purge': '10300',
                         'Load Probe': '10400',
                         'Leak Check': '10500',
                         'Flush and Pump': '10600',
                         'Cleaning VTI Sample Space': '11000',
                         'Confirm Sample Space Closed': '11100',
                         'Cleaning': '11200',
                         'Cleaning VTI Circuit': '12000',
                         'Pump Out Contaminants': '12100',
                         'Clean External Trap': '12200',
                         'Circulate VTI': '12300',
                         'Cleaning External Trap While Circulating': '13000',
                         'Prepare Clean Trap': '13100',
                         'Clean Trap': '13200'
                        },
        )

        self.add_parameter(
            "VTI_Target_Pressure", 
            unit="Pa", 
            label=name, 
            get_cmd="get_TARGET_PRES", 
            get_parser=float
        )

        self.add_parameter(
            "Magnet_State",
            label="Magnet State",
            get_cmd="get_MAG_STATE",
            get_parser=str,
            val_mapping={'Holding Not Persistent': '0',
                         'Holding Persistent': '10',
                         'Ramping Magnetic Field': '20',
                         'Ramping Power Supply Output Current': '30',
                         'Opening Superconducting Switches': '40',
                         'Closing Superconducting Switches': '50',
                         'Magnet Safety Non-Persistent': '60',
                         'Magnet Safety Persistent': '70'
                        },
        )

        self.add_parameter(
            name = "Magnetic_Field_Vector",
            parameter_class=Magnetic_Field_Parameters,
        )
        
        self.add_parameter(
            name = "Magnet_Current_Vector",
            parameter_class=Magnet_Current_Parameters,
        )

        self.add_parameter(
            name = "Magnet_Field_Target",
            parameter_class=Magnet_Field_Target,
        )

        if MAGNET_HAS_SWITCH:
            self.add_parameter(
                "Switch_State",
                label="Switch State",
                get_cmd="get_SWZ_STATE",
                get_parser=float,
                val_mapping={'OPEN': 1, 'CLOSED': 0}
            )

        self.connect_message()
    
    def Publish(self, msg, msg_group) -> None:
        """Function to publish an 'event'"""
        self._param_setter("PUBLISH", f"{msg},{msg_group}")
        # message group could be e.g. "Measurement"

    def _get_field_data(self) -> tuple[float, float, float]:
        """
        Low-level instrument query for the magnetic field vector.
        The instrument returns a comma-separated string in the form: "Bx,By,Bz"
            
        Returns:
            (tuple of float) Current values ``(Bx, By, Bz)`` in Tesla.
        """
        B_str = self.ask("get_MAG_VEC")
        B_array = B_str.split(',')
        return float(B_array[0]), float(B_array[1]), float(B_array[2])
    
    def _get_field_current_data(self) -> tuple[float, float, float]:
        """
        Low-level instrument query for the magnet current vector.
        The instrument returns a comma-separated string in the form: "Ix,Iy,Iz"
            
        Returns:
            (tuple of float) Current values ``(Ix, Iy, Iz)`` in amperes.
        """
        I_str = self.ask("get_MAG_CURR_VEC")
        I_array = I_str.split(',')
        return float(I_array[0]), float(I_array[1]), float(I_array[2])

    def _get_field_target_data(self) -> tuple[float, float, float]:
        """
        Low-level instrument query for the magnetic field vector target.
        The instrument returns a comma-separated string in the form: "Bx,By,Bz"
            
        Returns:
            (tuple of float) Current values ``(Bx, By, Bz)`` in Tesla.
        """
        B_str = self.ask("get_MAG_TARGET")
        B_array = B_str.split(',')
        return float(B_array[0]), float(B_array[1]), float(B_array[2])
   
    def probe_heater_off(self) -> None:
        """
        Utility function to turn off the probe heater.
        """
        self._param_setter('set_PROBE_H_OFF', 0)
        
    def vti_heater_off(self) -> None:
        """
        Utility function to turn off the VTI heater.
        """
        self._param_setter('set_VTI_H_OFF', 0)
    
    def set_magnet_target(self, coord: int, x: float, y: float, z: float,
                          sweep_mode: str, sweep_rate: float, persist_on_completion: bool) -> None:
        """
        Function to set field vector target
        
            Args: 
                coord: integer to choose coordinate system, 0 for cartesian 
                    10 for cylindrical and 20 for spherical 
                x, y, z: target field values (Tesla) 
                sweep_mode: specify how the field should be ramped, 'ASAP', 
                    'TIME' or 'RATE'
                sweep_rate: parameter asosicated with selected sweep mode, if 
                    sweep_mode is 'TIME' this should be desired time for sweep
                    in seconds. 
                    If sweep_mode is 'RATE', this should be rate of 
                    sweep in T/s. 
                    If sweep_mode is 'ASAP' sweep_rate is ignored.
                persist_on_completion: boolean, True to persist magnet once 
                    field has been ramped to target

        """

        allowed_states = ["Holding Not Persistent", "Holding Persistent"] # states from which it is acceptable to ramp field
        
        if self.Magnet_State() not in allowed_states: 
            
            print("Magnet is currently ramping.\nWait until magnet has finished ramping to set new target.")
            print("Set magnet state to \"Holding Not Persistent\" (0) to stop the ongoing ramp.")
            
        else: 
            match sweep_mode:
                case 'RATE':
                    param = [coord, x, y, z, 20, sweep_rate, persist_on_completion]
                    self._param_setter('set_MAG_TARGET', param)
                case 'TIME':
                    param = [coord, x, y, z, 10, sweep_rate, persist_on_completion]
                    self._param_setter('set_MAG_TARGET', param)
                case 'ASAP':
                    param = [coord, x, y, z, 0, sweep_rate, persist_on_completion]
                    self._param_setter('set_MAG_TARGET', param)
                case _:
                    print('Incorrect inputs.')
                    print('[x,y,z,mode,rate,persist_on_completion]')


    def set_output_current_target(self, x, y, z, sweep_mode, sweep_rate, persist_on_completion) -> None:
        """
        This function is not compatible with the IPS3 magnet power supply. 
        For use with the iPS magnet power supply only.
        
        Function to set current vector target
        
        Args: 
            x, y, z: target current values (Amps) 
            sweep_mode: specify how the current should be ramped, 'ASAP', 
                'TIME' or 'RATE'
            sweep_rate: parameter associated with selected sweep omde, if 
                sweep_mode is 'TIME' this should be desired time for sweep
                in seconds.  
                If sweep_mode is 'RATE', this should be the rate of 
                sweep in A/s.  
                If sweep_mode is 'ASAP' sweep_rate is ignored.
            persist_on_completion: boolean, True to persist magnet once current
                has been ramped to target
        
        """
        try: 
            match sweep_mode:
                case 'RATE':
                    param = [x, y, z, 20, sweep_rate, persist_on_completion]
                    self._param_setter('set_CURR_TARGET', param)
                case 'TIME':
                    param = [x, y, z, 10, sweep_rate, persist_on_completion]
                    self._param_setter('set_CURR_TARGET', param)
                case 'ASAP':
                    param = [x, y, z, 0, sweep_rate, persist_on_completion]
                    self._param_setter('set_CURR_TARGET', param)
                case _:
                    print('Incorrect inputs.')
                    print('[x,y,z,mode,rate,persist_on_completion]')
        except Exception as err:
            print("This function is not compatible with the IPS3 magnet power supply. For use with the iPS magnet power supply only.")

    def set_magnet_state(self, state: int) -> None:
        """
        Function to set VRM state target using MagnetVectorRotateDemandedState
        enumeration.

        Demandable states are determined by the magnet power supply (iPS or IPS3).
        
        Args: 
            state: integer determines which state is set on the 
                magnet.

        """

        try:
            match state:
                case 0:
                    self._param_setter('set_MAG_STATE', state)
                    print('Holding Field')
                case 10:
                    self._param_setter('set_MAG_STATE', state)
                    print('Entering Persistent Mode')
                case 20:
                    self._param_setter('set_MAG_STATE', state)
                    print('Leaving Persistent Mode')
                case 30:
                    target = self.ask("get_MAG_TARGET")
                    self._param_setter('set_MAG_STATE', state)
                    print(f'Sweeping Field to {target} T')
                case 40:
                    self._param_setter('set_MAG_STATE', state)
                    print('Sweeping PSU Output')
                case _:
                    print("**NB** Demandable states for iPS magnet power supply are:")
                    print("0 - Hold, 10 - Enter Persistent Mode")
                    print("20 - Leave Persistent Mode, 30 - Sweep Field, 40 - Sweep PSU Output")
                    print("\nDemandable states for IPS3 magnet power supply are:")
                    print("0 - Hold, 30 - Sweep Field")
        except Exception as err:
            print("This magnet state is not demandable from the IPS3 magnet power supply. It is demandable from the iPS magnet power supply only.")
            
    def sweep_field(self):
        """
        Utility function to start a field sweep.
        """
        self.set_magnet_state(30)
        
    def sweep_PSU_output(self):
        """
        Utility function to start a PSU output sweep.

        This function is not compatible with the IPS3 magnet power supply. 
        For use with the iPS magnet power supply only.
        """
        try:
            self.set_magnet_state(40)
        except Exception as err:
            print("This function is not compatible with the IPS3 magnet power supply. For use with the iPS magnet power supply only.")
        
    def enter_persistent_mode(self):
        """
        Utility function to enter persistent mode.

        This function is not compatible with the IPS3 magnet power supply. 
        For use with the iPS magnet power supply only.
        """
        try:
            self.set_magnet_state(10)
        except Exception as err:
            print("This function is not compatible with the IPS3 magnet power supply. For use with the iPS magnet power supply only.")
        
    def leave_persistent_mode(self):
        """
        Utility function to leave persistant mode.
        
        This function is not compatible with the IPS3 magnet power supply. 
        For use with the iPS magnet power supply only.
        """
        try:
            self.set_magnet_state(20)
        except Exception as err:
            print("This function is not compatible with the IPS3 magnet power supply. For use with the iPS magnet power supply only.")
        
    def hold_field(self):
        """
        Utility function to hold field.
        """
        self.set_magnet_state(0)
        
    def open_switch(self):
        """
        Utility function to open superconducting switch.
        
        This function is not compatible with the IPS3 magnet power supply. 
        For use with the iPS magnet power supply only.
        """
        try:
            self.set_magnet_state(20)
        except Exception as err:
            print("This function is not compatible with the IPS3 magnet power supply. For use with the iPS magnet power supply only.")
        
    def close_switch(self):
        """
        Utility function to close superconducting switch.
        
        This function is not compatible with the IPS3 magnet power supply. 
        For use with the iPS magnet power supply only.
        """
        try:
            self.set_magnet_state(10)
        except Exception as err:
            print("This function is not compatible with the IPS3 magnet power supply. For use with the iPS magnet power supply only.")
        
    def sweep_small_field_step(self, coord): 
        '''
        This function is not required with the IPS3 magnet power supply. 
        It is intended to be used with the iPS magnet power supply only.
        
        This routine is intended for fine field changes (< 100 mA) using the iPS 
        magnet power supply. 
        It begins by sweeping the VRM group and waits until the magnet reaches the
        'Holding Not Persistent' state. Once stable, it triggers a small sweep on
        the specified VRM axis ('X', 'Y', or 'Z') by issuing the appropriate
        parameter‑setter command.

        This function is ONLY to be used for sweeping the field <100 mA.
        The conversion between mA and T will depend on your magnet.

        For the IPS3 magnet power supply, small field sweeps can be performed 
        with the `sweep_field` function.
        
        Args:
        coord (str): The VRM axis to sweep. Must be one of:
            - 'X' for the X‑axis
            - 'Y' for the Y‑axis
            - 'Z' for the Z‑axis
        '''
        try:
            # sweep VRM group
            self.sweep_field()
            # wait until sweep failed
            time.sleep(2)
            status = self.Magnet_State()
            while status != 'Holding Not Persistent':
                status = self.Magnet_State()
                time.sleep(1)
            # sweep X, Y or Z group of VRM
            if coord=='X':
                self._param_setter('set_MAG_X_STATE', 10)
            elif coord=='Y':
                self._param_setter('set_MAG_Y_STATE', 10)
            elif coord=='Z':
                self._param_setter('set_MAG_Z_STATE', 10)
        except Exception as err:
            print("This function is not required with the IPS3 magnet power supply. For use with the iPS magnet power supply only.")
            print("For the IPS3 magnet power supply, small field sweeps can be performed with the `sweep_field` function.")
        
    def wait_until_field_stable(self):
        """
        The function continuously polls the magnet state once per second until the 
        reported state is 'Holding Not Persistent'.
        """
        time.sleep(2)
        status = self.Magnet_State()
        while status != 'Holding Not Persistent':
            status = self.Magnet_State()
            time.sleep(1)
        print(f'Magnet Status: {self.Magnet_State()}.')

    def wait_until_temperature_stable(self):
        """
        The function continuously polls the temperature stable endpoint once per second until the 
        reported value is True.
        """
        time.sleep(30)
        status = self.Temperature_Stable()
        while status != 'True':
            status = self.Temperature_Stable()
            time.sleep(1)
        print(f'Temperature Stable: {self.Temperature_Stable()}')
        
    def wait_until_field_persistent(self):
        """
        The function continuously polls the magnet state once per second until the 
        reported state is 'Holding Persistent'.
        """
        status = self.Magnet_State()
        while status != 'Holding Persistent':
            status = self.Magnet_State()
            time.sleep(1)
        print(f'Magnet Status: {self.Magnet_State()}.')
        
    def wait_until_field_depersisted(self):
        """
        The function repeatedly polls the magnet state and waits until it reports
        'Holding Not Persistent'. If the magnet has entered the 'Holding Not Persistent'
        state within 600 seconds, a field‑hold command is issued to encourage the transition.
        """
        status = self.Magnet_State()
        start_time = time.time()
        while status != 'Holding Not Persistent':
            if time.time() > (start_time+600):
                self.hold_field()
            status = self.Magnet_State()
            time.sleep(1)
        print(f'Magnet Status: {self.Magnet_State()}.')

    def get_x_field(self, ):
        """
        return only the x-component of the magnetic field vector.
        """
        return self.Magnetic_Field_Vector()[0]
        
    def get_y_field(self, ):
        """
        return only the y-component of the magnetic field vector.
        """
        return self.Magnetic_Field_Vector()[1]
        
    def get_z_field(self, ):
        """
        return only the z-component of the magnetic field vector.
        """
        return self.Magnetic_Field_Vector()[2]  

    def go_to_base_pressure(self, base_pressure: float = 680) -> None:
        """
        Function to take system down to base pressure and wait until base pressure is reached.

        Args:
            base_pressure: (float, optional) default 680 Pa. The target base pressure.
        """
        # set manual parameter to base pressure value
        if base_pressure != self.Base_Pressure():
            self.Base_Pressure(base_pressure)
            time.sleep(1)
        # set VTI to base pressure
        self.VTI_Pressure(self.Base_Pressure())
        time.sleep(1)

        print(f'Waiting for base pressure of {self.Base_Pressure()} Pa.')
        while self.VTI_Pressure() >= self.Base_Pressure()+30: # wait until within 30 Pa of base pressure
            time.sleep(1)

 
    # function here until stablity control work in DECS
    def wait_until_temperature_stable_std_control(self, setpoint, stable_mean, stable_std, time_between_readings):
        """
        sample temperature control utility function

        Takes a moving average of 30 temperature readings and finds the mean and the std of the last 30 readings,
        until the difference between the mean and target value is below 'stable_mean' and the standard deviation is below 'stable_std'.

        Args:
            stable_mean: (float) difference between the mean and target value to be achieved by the last 30 temperature readings
            stable_std: (float) standard deviation to be achieved by the last 30 temperature readings
            time_between_readings: (float) time between taking temperature readings
            setpoint: (float) the setpoint which the function will the function will wait to stabilise at
        
        """
        time.sleep(2)
        target_temp = setpoint

        print(f'Waiting for temperature to stablilise at {target_temp} K.')
        
        #take 30 temperature readings 
        t1 = time.time()
        t_array = np.zeros(30)
        for n in range(0,30):
            time.sleep(time_between_readings)
            temp = self.Probe_Temperature()
            t_array[n] = float(temp)
            
        stab = False
        while stab is False:
            time.sleep(time_between_readings)
            temp = self.Probe_Temperature()
            t_array = np.append(t_array, float(temp))

            t_array = t_array[1:]
            s = np.std(t_array)
            m = np.abs(np.mean(t_array) - target_temp)
            
            if (s < stable_std) and (m < stable_mean):
                stab = True
                
        t2 = time.time()
        tt = t2-t1
        print(f'Temperature = {t_array[-1]} K')
        print(f'Temperature stable after {int(tt)} seconds. (Mean-Target = {m} K, StdDev = {s} K)')

    def ramp_temperature(self, target_temperature: float, rate: float, link: bool = True, high_flow: bool = False) -> None:
        """
        Function to begin a temperature ramp. 
        
        Args: 
            target_temperature: (float) the temperature value to reach at the end of the ramp.
                This sets the "Temperature_Ramp_Target" parameter.
            rate: (float) the rate to sweep the temperature in K/s.
                This sets the "Temperature_Ramp_Rate" parameter.
            link: (bool, optional) default True. whether the VTI temperature is linked with
            the sample temperature.
                This is the "Sample_and_VTI_Linked" parameter.
            high_flow: (bool, optional) default False. whether to use high flow during the ramp.
                This is the "High_Flow_Enabled" parameter.
        """
        # only try ramp temperature if system is in circulating state
        if self.System_State() == 'Circulating':
            # link or unlink the sample and VTI temperatures
            self.Sample_and_VTI_Linked(link)
            # set high flow 
            self.High_Flow_Enabled(high_flow)
            # set ramp rate
            self.Temperature_Ramp_Rate(rate)
            # start temperature ramp to target_temperature
            self._param_setter("set_CIRC_TARGET", target_temperature)
            print(f'Ramping to {self.Temperature_Ramp_Target()} K.')
        else:
            print('System state must in Circulating to start a temperature ramp.')
    
    def ask(self, cmd: str) -> str:
        """
        Args:
            cmd: the command to send to the instrument
        """
        resp = self.visa_handle.query(cmd)

        return resp
    
    def _param_setter(self, set_cmd: str, value: Union[float, str]) -> None:
        """
        General setter function for parameters

        Args:
            set_cmd: raw string for the command, e.g. 'set_target_temperature'
        """
        dressed_cmd = f"{set_cmd}:{value}"
        # the instrument always provides a response
        # even when issuing a 'set' command.
        # Hence ask rather than write
        self.ask(dressed_cmd)

    def get_DECS_version(self) -> str:
        """
        Function to query the DECS version from its IDN string.
        """
        idn = self.ask("*IDN?")
        firmware_version = idn.split(",")[3]
        firmware_version = firmware_version.replace(" ", "")
        return firmware_version
    
    def close(self) -> None:
        # Kill off the WAMP and socket connections
        self.write(SHUTDOWN) # comment out to use simulated instrument in /qcodes/instrument/sims/ directory
        return super().close()