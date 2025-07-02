from .instr import VisaDevice


class SR860(VisaDevice):
    """
    API hash tables
    """
    API = {
        # name              type     write          read
        # Lock-in reference signal settings
        'frequency':        (float, 'FREQ {:.3f}', 'FREQ?'),    # Frequency in Hz 
        'amplitude':        (float, 'SLVL {:.9f}', 'SLVL?'),    # Amplitude in V 
        'phase':            (float, 'PHAS {:.7f}', 'PHAS?'),    # Phase 
        'dc_offset':        (float, 'SOFF {:.4f}', 'SOFF?'),    # Sine out dc offset in V
        'harmonic':         (int,   'HARM {}',     'HARM?'),    # Harmonic number
        'ref_source':       (int,   'RSRC {}',     'RSRC?'),    # Source of the reference signal
        'ext_ref_trigger':  (int,   'RTRG {}',     'RTRG?'),    # External reference trigger mode
        'ext_ref_input_Z':  (int,   'REFZ {}',     'REFZ?'),    # External reference input impedance/gain
        'blaze_x':          (int,   'BLAZEX {}',   'BLAZEX?'),  # Configure BlazeX/sync output

        # Amplifier settings
        'sensitivity':      (int,   'SCAL {}',     'SCAL?'),    # Sensitivity range

        # Filter settings
        'filter_slope':     (int,   'OFSL {}',     'OFSL?'),    # Filter slope
        'syncfilt':         (bool,  'SYNC {}',     'SYNC?'),    # Sync filter enabled
        'advfilt':          (bool,  'ADVFILT {}',  'ADVFILT?'), # Advance filtering
        'time_constant':    (int,   'OFLT {}',     'OFLT?'),    # Filter time constant

        # Input signal settings
        'input_coupling':   (int,   'ICPL {}',     'ICPL?'),    # Input coupling AC/DC
        'input_mode':       (int,   'IVMD {}',     'IVMD?'),    # Voltage/current input
        'V_input_range':    (int,   'IRNG {}',     'IRNG?'),    # Voltage input range
        'V_input_config':   (int,   'ISRC {}',     'ISRC?'),    # Voltage input configuration
        'V_input_grnd':     (int,   'IGND {}',     'IGND?'),    # Voltage input shield ground type
        'I_input_Z':        (int,   'ICUR {}',     'ICUR?'),    # Current input impedance/gain
   
        # get some useful input signal properties
        'noise_bw':         (float, None,          'ENBW?'),     # Equivalent noise bandwidth
        'signal_strength':  (int,   None,          'ILVL?'),     # Query input signal low/overload

        # Output signal settings
        # Offset and expand
        'X_offset':         (float, 'COFP 0, {:.2f}', 'COFP? 0'),
        'Y_offset':         (float, 'COFP 1, {:.2f}', 'COFP? 1'),
        'R_offset':         (float, 'COFP 2, {:.2f}', 'COFP? 2'),
        'X_expand':         (int,   'CEXP 0, {}',     'CEXP? 0'),
        'Y_expand':         (int,   'CEXP 1, {}',     'CEXP? 1'),
        'R_expand':         (int,   'CEXP 2, {}',     'CEXP? 2'),
        'X_offset_enable':  (bool,  'COFA 0, {}',     'COFA? 0'),
        'Y_offset_enable':  (bool,  'COFA 1, {}',     'COFA? 1'),
        'R_offset_enable':  (bool,  'COFA 2, {}',     'COFA? 2'),
        # AUTO functions
        'auto_range':       ((),    'ARNG',        None),
        'auto_scale':       ((),    'ASCL',        None),
        'auto_phase':       ((),    'APHS',        None),
        'auto_offset_X':    ((),    'OAUT 0',      None),
        'auto_offset_Y':    ((),    'OAUT 1',      None),
        'auto_offset_R':    ((),    'OAUT 2',      None),

        # Data channels
        'X':                (float,  None,         'OUTP? 0'),  # Get X channel amplitude
        'Y':                (float,  None,         'OUTP? 1'),  # Get Y channel amplitude
        'R':                (float,  None,         'OUTP? 2'),  # Get R channel amplitude
        'P':                (float,  None,         'OUTP? 3'),  # Get P channel amplitude
        'XYRP':             (str,    None,         'SNAPD?'),   # Get XYRP outputs simultaneously

        # Instrument functions
        'model_type':       (str,   None,          '*IDN?'),
        'reset':            ((),    '*RST',        None)
    }

    def __init__(self, devpath):
        super().__init__(devpath)
        self._model = None
        self._model = self.model
        self._serial_num = self.serial_number
        self._fw_ver = self.firmware_version
        if self.model == 'SR860':
            self._f_range = {'start Hz': 1.e-3, 'stop Hz': 500.e3, 'step Hz': 1.e-3}
        elif self.model == 'SR865':
            self._f_range = {'start Hz': 1.e-3, 'stop Hz': 2.e6, 'step Hz': 1.e-3}
        elif self.model == 'SR865A':
            self._f_range = {'start Hz': 1.e-3, 'stop Hz': 4.e6, 'step Hz': 1.e-3}
        else: 
            self._f_range = None

    def init(self):
        """Initialize device: put into a known, safe state."""
        self.clear()
        f_range = self.frequency_range
        if f_range is not None:
            self.frequency = 1.0e3
            self.amplitude = 1.0
            self.phase = 0.0
            self.dc_offset = 0.0
            self.harmonic = 1
            self.reference_source = 'internal'
            self.external_reference_trigger = 'positive TTL'
            self.blaze_x_config = 'positive sync'
            self.input_mode = 'voltage'
            self.input_Vconfig = 'A'
            self.input_coupling_mode = 'AC'
            self.filter_slope = 24
            self.sync_filter_enable = True
            self.adv_filter_enable = False
            self.X_offset = 0.0
            self.Y_offset = 0.0
            self.R_offset = 0.0
            self.X_expand = 1
            self.Y_expand = 1
            self.R_expand = 1

    def _isNumber(self, value):
        if not isinstance(value, (float, int)):
            raise ValueError('Expected float or int.')

    def _isBoolean(self, value):
        if not isinstance(value, bool):
            raise ValueError('Expected bool.')

    @property
    def model(self):
        """Model. This is the binned version that dictates API support.

        Returns:
            str: model version or None if unsupported
        """
        if self._model is not None:
            return self._model
        
        modeltype = self.read('model_type')
        if 'SR86' in modeltype:
            return modeltype.split(',')[1]
            
        else:
            # Unsupported model. Return None.
            return None

    @property
    def serial_number(self):
        """Get instrument serial number.

        Returns:
            str: serial number.
        """
        return self.read('model_type').split(',')[2]

    @property
    def firmware_version(self):
        """Get instrument firmware version.

        Returns:
            str: firmware version.
        """
        return self.read('model_type').split(',')[3]

    def reset(self):
        """Resets instrument to default settings. NOT the same as initialize."""
        self.write('reset')

    @property
    def frequency_range(self):
        """Get frequency range in Hz.

        Returns: 
            dict: frequency range and resolution.
        """
        return None if self.model is None else self._f_range.copy()

    @property
    def frequency(self): 
        """Get frequency in Hz.

        Returns:
            float: frequency in Hz
        """
        return self.read('frequency')

    @frequency.setter
    def frequency(self, value):
        """Set frequency in Hz.

        Args:
            value (float / int): frequency in Hz
        """
        self._isNumber(value)

        f_range = self.frequency_range
        if f_range is not None and not f_range['start Hz'] <= value <= f_range['stop Hz']:
            raise ValueError('Expected float in range [{:.3f}, {d}] Hz.'.format(f_range['start Hz'], f_range['stop Hz']))
        self.write('frequency', value)

    @property
    def amplitude_range(self):
        """Get amplitude range in V.

        Returns: 
            str: amplitude range and resolution.
        """
        return None if self.model is None else 'min: 1.e-9 V, max: 2.0 V, resolution: 1.e-9 V.'

    @property
    def amplitude(self):
        """Get amplitude in V.

        Returns:
            float: amplitude in V
        """
        return self.read('amplitude')

    @amplitude.setter
    def amplitude(self, value):
        """Set amplitude in V.

        Args:
            value (float / int): amplitude in V
        """
        self._isNumber(value)
        if self.model is not None and not 1.e-9 <= value <= 2.0:
            raise ValueError('Expected float in range [{:.9f}, {:.2f}] Hz.'.format(1.e-9, 2.0))
        self.write('amplitude', value)

    @property
    def phase_range(self):
        """Get phase range in deg.

        Returns: 
            str: phase range and resolution.
        """
        return None if self.model is None else 'min: -360000, max: 360000, resolution: 1.e-7 [deg].'

    @property
    def phase(self):
        """Get phase in deg.

        Returns:
            float: phase in deg
        """
        return self.read('phase')

    @phase.setter
    def phase(self, value):
        """Set phase in deg.

        Args:
            value (float / int): phase in deg
        """
        self._isNumber(value)
        if self.model is not None and not -360000. <= value <= 360000.:
            raise ValueError('Expected float in range [{d}, {d}] Hz.'.format(-360000., 360000.))
        self.write('phase', value)

    @property
    def dc_offset_range(self):
        """Get DC offset range in V.

        Returns:
            str: DC offset range and resolution in V
        """
        return None if self.model is None else 'min: -5.0 V, max: 5.0 V, resolution: 0.1e-3 V.'

    @property
    def dc_offset(self):
        """Get DC offset in V.

        Returns:
            float: DC offset in V
        """
        return self.read('dc_offset')

    @dc_offset.setter
    def dc_offset(self, value):
        """Set DC offset in V.

        Args:
            value (float / int): DC offset in V
        """
        self._isNumber(value)
        if self.model is not None and not -5. <= value <= 5.:
            raise ValueError('Expected float in range [{:.2f}, {:.2f}] Hz.'.format(-5., 5.))
        self.write('dc_offset', value)

    @property
    def harmonic_range(self):
        """Get harmonic range.

        Returns:
            str: harmonic range 
        """
        return None if self.model is None else 'min: 1, max: 99.'

    @property
    def harmonic(self):
        """Get harmonic number.

        Returns:
            int: harmonic number
        """
        return self.read('harmonic')

    @harmonic.setter
    def harmonic(self, value):
        """Set harmonic number.

        Args:
            value (int): harmonic number
        """
        if not isinstance(value, int):
            raise ValueError('Expected int between 1 and 99.')
        
        if self.model is not None and not 1 <= value <= 99:
            raise ValueError('Expected int between 1 and 99.')
        self.write('harmonic', value)

    @property
    def reference_sources(self):
        """List reference sources.

        Returns:
            tuple: Tuple of str of reference sources.
        """
        return (
            'internal', 
            'external',
            'dual',
            'chop'
            )

    @property
    def reference_source(self):
        """Get reference source.

        Returns:
            str: reference source
        """
        return self.reference_sources[self.read('ref_source')]

    @reference_source.setter
    def reference_source(self, value):
        """Set reference source.

        Args:
            value (str): reference source
        """
        sources = self.reference_sources
        if value not in sources:
            raise ValueError('Expected str in set: {}.'.format(sources))
        self.write('ref_source', sources.index(value))

    @property
    def external_reference_triggers(self):
        """List external reference trigger modes.

        Returns:
            tuple: Tuple of str of external reference trigger modes.
        """
        return (
            'sine', 
            'positive TTL',
            'negative TTL'
            )

    @property
    def external_reference_trigger(self):
        """Get external reference trigger mode.

        Returns:
            str: external reference trigger mode
        """
        return self.external_reference_triggers[self.read('ext_ref_trigger')]

    @external_reference_trigger.setter
    def external_reference_trigger(self, value):
        """Set external reference trigger mode.

        Args:
            value (str): external reference trigger mode
        """
        modes = self.external_reference_triggers
        if value not in modes:
            raise ValueError('Expected str in set: {}.'.format(modes))
        self.write('ext_ref_trigger', modes.index(value))

    @property
    def blaze_x_configs(self):
        """List blaze x connector configurations.

        Returns:
            tuple: Tuple of str of blaze x connector configurations.
        """
        return (
            'blaze x', 
            'bipolar sync',
            'positive sync'
            )

    @property
    def blaze_x_config(self):
        """Get blaze x connector configuration.

        Returns:
            str: blaze x connector configuration
        """
        return self.blaze_x_configs[self.read('blaze_x')]

    @blaze_x_config.setter
    def blaze_x_config(self, value):
        """Set blaze x connector configuration.

        Args:
            value (str): blaze x connector configuration
        """
        configs = self.blaze_x_configs
        if value not in configs:
            raise ValueError('Expected str in set: {}.'.format(configs))
        self.write('blaze_x', configs.index(value))

    @property
    def external_reference_input_Zs(self):
        """List external reference input impedances.

        Returns:
            tuple: Tuple of str of external reference input impedances.
        """
        return (
            '50 Ohm', 
            '1 MOhm'
            )

    @property
    def external_reference_input_Z(self):
        """Get external reference input impedance.

        Returns:
            str: external reference input impedance
        """
        return self.external_reference_input_Zs[self.read('ext_ref_input_Z')]

    @external_reference_input_Z.setter
    def external_reference_input_Z(self, value):
        """Set external reference input impedance.

        Args:
            value (str): external reference input impedance
        """
        Zs = self.external_reference_input_Zs
        if value not in Zs:
            raise ValueError('Expected str in set: {}.'.format(Zs))
        self.write('ext_ref_input_Z', Zs.index(value))

    @property
    def sensitivity_range(self):
        """List range of sensitivities.
        voltage mode: V 
        current mode: uA

        Returns:
            tuple: Tuple of str of sensitivities in V or uA
        """
        return (1.0, 0.5, 0.2, 0.1, 0.05, 0.02, 0.01, 0.005, 0.002, 0.001, 0.0005, 0.0002, 0.0001, 5e-05, 2e-05, 1e-05, 5e-06, 2e-06, 1e-06, 5e-07, 2e-07, 1e-07, 5e-08, 2e-08, 1e-08, 5e-09, 2e-09, 1e-09)

    @property
    def sensitivity(self):
        """Get sensitivity in V or uA.

        Returns:
            float: sensitivity in V or uA
        """
        return self.sensitivity_range[self.read('sensitivity')]

    @sensitivity.setter
    def sensitivity(self, value):
        """Set sensitivity in V or uA.

        Args:
            value (float): sensitivity in V or uA
        """
        sens_range = self.sensitivity_range
        if value not in sens_range:
            raise ValueError('Expected float in set: {}.'.format(sens_range))
        self.write('sensitivity', sens_range.index(value))

    @property
    def filter_slopes(self):
        """List filter slopes in dB/oct.

        Returns:
            tuple: Tuple of int of filter slopes in dB/oct.
        """
        return (6, 12, 18, 24)

    @property
    def filter_slope(self):
        """Get filter slope in dB/oct.

        Returns:
            int: filter slope in dB/oct
        """
        return self.filter_slopes[self.read('filter_slope')]

    @filter_slope.setter
    def filter_slope(self, value):
        """Set filter slope in dB/oct.

        Args:
            value (int): filter slope in dB/oct.
        """
        slopes = self.filter_slopes
        if value not in slopes:
            raise ValueError('Expected int in set: {}.'.format(slopes))
        self.write('filter_slope', slopes.index(value))

    @property
    def sync_filter_enable(self):
        """Sync filter enable.

        Returns:
            bool: enable
        """
        return self.read('syncfilt')

    @sync_filter_enable.setter
    def sync_filter_enable(self, value):
        """Sync filter enable.

        Args:
            value (bool): enable
        """
        self._isBoolean(value)
        self.write('syncfilt', value)

    @property
    def adv_filter_enable(self):
        """Advanced filter enable.

        Returns:
            bool: enable
        """
        return self.read('advfilt')

    @adv_filter_enable.setter
    def adv_filter_enable(self, value):
        """Advanced filter enable.

        Args:
            value (bool): enable
        """
        self._isBoolean(value)
        self.write('advfilt', value)

    @property
    def time_constants(self):
        """List time constants in seconds.

        Returns:
            tuple: Tuple of float of time constants in seconds.
        """
        return (1e-06, 3e-06, 1e-05, 3e-05, 0.0001, 0.0003, 0.001, 0.003, 0.01, 0.03, 0.1, 0.3, 1, 3, 10, 30, 100, 300, 1000.0, 3000.0, 10000.0, 30000.0)

    @property
    def time_constant(self):
        """Get time constant in second.

        Returns:
            float: time constant in second
        """
        return self.time_constants[self.read('time_constant')]

    @time_constant.setter
    def time_constant(self, value):
        """Set time constant in second.

        Args:
            value (float): time constant in second
        """
        times = self.time_constants
        if value not in times:
            raise ValueError('Expected float in set: {}.'.format(times))
        self.write('time_constant', times.index(value))

    @property
    def input_coupling_modes(self):
        """List input coupling modes.

        Returns:
            tuple: Tuple of str of input coupling modes.
        """
        return ('AC', 'DC')

    @property
    def input_coupling_mode(self):
        """Get input coupling mode.

        Returns:
            str: input coupling mode
        """
        return self.input_coupling_modes[self.read('input_coupling')]

    @input_coupling_mode.setter
    def input_coupling_mode(self, value):
        """Set input coupling mode.

        Args:
            value (str): input coupling mode
        """
        modes = self.input_coupling_modes
        if value not in modes:
            raise ValueError('Expected str in set: {}.'.format(modes))
        self.write('input_coupling', modes.index(value))

    @property
    def input_modes(self):
        """List input modes.

        Returns:
            tuple: Tuple of str of input modes.
        """
        return ('voltage', 'current')

    @property
    def input_mode(self):
        """Get input mode.

        Returns:
            str: input mode
        """
        return self.input_modes[self.read('input_mode')]

    @input_mode.setter
    def input_mode(self, value):
        """Set input mode.

        Args:
            value (str): input mode
        """
        modes = self.input_modes
        if value not in modes:
            raise ValueError('Expected str in set: {}.'.format(modes))
        self.write('input_mode', modes.index(value))

    @property
    def input_Vranges(self):
        """List input ranges in V.

        Returns:
            tuple: Tuple of float of input ranges in V.
        """
        return (1.0, 0.3, 0.1, 0.03, 0.01)

    @property
    def input_Vrange(self):
        """Get input range in V.

        Returns:
            str: input range in V
        """
        return self.input_Vranges[self.read('V_input_range')]

    @input_Vrange.setter
    def input_Vrange(self, value):
        """Set input range in V.

        Args:
            value (float): input range in V
        """
        input_range = self.input_Vranges
        if value not in input_range:
            raise ValueError('Expected float in set: {}.'.format(input_range))
        self.write('V_input_range', input_range.index(value))

    @property
    def input_Vconfigs(self):
        """List input configurations.

        Returns:
            tuple: Tuple of str of input configurations.
        """
        return ('A', 'A-B')

    @property
    def input_Vconfig(self):
        """Get input configuration.

        Returns:
            str: input configuration
        """
        return self.input_Vconfigs[self.read('V_input_config')]

    @input_Vconfig.setter
    def input_Vconfig(self, value):
        """Set input configuration.

        Args:
            value (str): input configuration
        """
        configs = self.input_Vconfigs
        if value not in configs:
            raise ValueError('Expected str in set: {}.'.format(configs))
        self.write('V_input_config', configs.index(value))

    @property
    def input_grounds(self):
        """List input ground configurations.

        Returns:
            tuple: Tuple of str of input ground configurations.
        """
        return ('float', 'ground')

    @property
    def input_ground(self):
        """Get input ground configuration.

        Returns:
            str: input ground configuration
        """
        return self.input_grounds[self.read('V_input_grnd')]

    @input_ground.setter
    def input_ground(self, value):
        """Set input ground configuration.

        Args:
            value (str): input ground configuration
        """
        configs = self.input_grounds
        if value not in configs:
            raise ValueError('Expected str in set: {}.'.format(configs))
        self.write('V_input_grnd', configs.index(value))

    @property
    def I_input_Zs(self):
        """List current input impedances.

        Returns:
            tuple: Tuple of str of current input impedances.
        """
        return ('1 MOhm', '100 MOhm')

    @property
    def I_input_Z(self):
        """Get input impedance.

        Returns:
            str: input impedance
        """
        return self.I_input_Zs[self.read('I_input_Z')]

    @I_input_Z.setter
    def I_input_Z(self, value):
        """Set input impedance.

        Args:
            value (str): input impedance
        """
        Zs = self.I_input_Zs
        if value not in Zs:
            raise ValueError('Expected str in set: {}.'.format(Zs))
        self.write('I_input_Z', Zs.index(value))

    @property
    def ENBW(self):
        """Get equivalent noise bandwidth in Hz. 
        Neglects effect of SYNC filter.

        Returns:
            float: equivalent noise bandwidth in Hz
        """
        return self.read('noise_bw')

    @property
    def input_signal_strengths(self):
        """List input signal strengths. 

        Returns:
            tuple: Tuple of str of input signal strength
        """
        return ('very low', 'low', 'medium', 'high', 'overload')

    @property
    def input_signal_strength(self):
        """Get input signal strength
        to check if low/overloaded.

        Returns:
            str: input signal strength
        """
        return self.input_signal_strengths[self.read('signal_strength')]

    @property
    def output_offset_range(self):
        """List XYR offset range in percent.

        Returns:
            str: XYR offset range and resolution in percent.
        """
        return None if self.model is None else 'min: -999.99%, max: 999.99%, resolution: 0.01%.'

    @property
    def X_offset(self):
        """Get X offset in percent.

        Returns:
            float: X offset in percent
        """
        return self.read('X_offset')

    @X_offset.setter
    def X_offset(self, value):
        """Set X offset in percent.

        Args:
            value (float / int): X offset in percent
        """
        self._isNumber(value)
        if self.model is not None and not -999.99 <= value <= 999.99:
            raise ValueError('Expected float/int in range [{:.2f}, {:.2f}] Hz.'.format(-999.99, 999.99))
        self.write('X_offset', value)

    @property
    def Y_offset(self):
        """Get Y offset in percent.

        Returns:
            float: Y offset in percent
        """
        return self.read('Y_offset')

    @Y_offset.setter
    def Y_offset(self, value):
        """Set Y offset in percent.

        Args:
            value (float / int): Y offset in percent
        """
        self._isNumber(value)
        if self.model is not None and not -999.99 <= value <= 999.99:
            raise ValueError('Expected float/int in range [{:.2f}, {:.2f}] Hz.'.format(-999.99, 999.99))
        self.write('Y_offset', value)

    @property
    def R_offset(self):
        """Get R offset in percent.

        Returns:
            float: R offset in percent
        """
        return self.read('R_offset')

    @R_offset.setter
    def R_offset(self, value):
        """Set R offset in percent.

        Args:
            value (float / int): R offset in percent
        """
        self._isNumber(value)
        if self.model is not None and not -999.99 <= value <= 999.99:
            raise ValueError('Expected float/int in range [{:.2f}, {:.2f}] Hz.'.format(-999.99, 999.99))
        self.write('R_offset', value)

    @property
    def X_offset_enable(self):
        """X offset enable.

        Returns:
            bool: enable
        """
        return self.read('X_offset_enable')

    @X_offset_enable.setter
    def X_offset_enable(self, value):
        """X offset enable.

        Args:
            value (bool): enable
        """
        self._isBoolean(value)
        self.write('X_offset_enable', value)

    @property
    def Y_offset_enable(self):
        """Y offset enable.

        Returns:
            bool: enable
        """
        return self.read('Y_offset_enable')

    @Y_offset_enable.setter
    def Y_offset_enable(self, value):
        """Y offset enable.

        Args:
            value (bool): enable
        """
        self._isBoolean(value)
        self.write('Y_offset_enable', value)

    @property
    def R_offset_enable(self):
        """R offset enable.

        Returns:
            bool: enable
        """
        return self.read('R_offset_enable')

    @R_offset_enable.setter
    def R_offset_enable(self, value):
        """R offset enable.

        Args:
            value (bool): enable
        """
        self._isBoolean(value)
        self.write('R_offset_enable', value)

    @property
    def output_expands(self):
        """List XYR expands.

        Returns:
            Tuple: tuple of int of XYR expands.
        """
        return (1, 10, 100)

    @property
    def X_expand(self):
        """Get X expand.

        Returns:
            int: X expand
        """
        expand = 10 ** self.read('X_expand')
        return expand

    @X_expand.setter
    def X_expand(self, value):
        """Set X expand.

        Args:
            value (int): X expand
        """
        expands = self.output_expands
        if value not in expands:
            raise ValueError('Expected int in set: {}.'.format(expands))
        self.write('X_expand', expands.index(value))

    @property
    def Y_expand(self):
        """Get Y expand.

        Returns:
            int: Y expand
        """
        expand = 10 ** self.read('Y_expand')
        return expand

    @Y_expand.setter
    def Y_expand(self, value):
        """Set Y expand.

        Args:
            value (int): Y expand
        """
        expands = self.output_expands
        if value not in expands:
            raise ValueError('Expected int in set: {}.'.format(expands))
        self.write('Y_expand', expands.index(value))

    @property
    def R_expand(self):
        """Get R expand.

        Returns:
            int: R expand
        """
        expand = 10 ** self.read('R_expand')
        return expand

    @R_expand.setter
    def R_expand(self, value):
        """Set R expand.

        Args:
            value (int): R expand
        """
        expands = self.output_expands
        if value not in expands:
            raise ValueError('Expected int in set: {}.'.format(expands))
        self.write('R_expand', expands.index(value))

    def auto_range(self):
        """Auto-range function"""
        self.write('auto_range')

    def auto_scale(self):
        """Auto-scale function"""
        self.write('auto_scale')

    def auto_phase(self):
        """Auto-phase function"""
        self.write('auto_phase')

    def auto_offset_X(self):
        """Auto-offset function"""
        self.write('auto_offset_X')

    def auto_offset_Y(self):
        """Auto-offset function"""
        self.write('auto_offset_Y')

    def auto_offset_R(self):
        """Auto-offset function"""
        self.write('auto_offset_R')

    def X_output(self):
        """Get X output amplitude in V.

        Returns:
            float: X output amplitude in V
        """
        return self.read('X')

    def Y_output(self):
        """Get Y output amplitude in V.

        Returns:
            float: Y output amplitude in V
        """
        return self.read('Y')

    def R_output(self):
        """Get R output amplitude in V.

        Returns:
            float: R output amplitude in V
        """
        return self.read('R')

    def P_output(self):
        """Get P output amplitude in deg.

        Returns:
            float: P output amplitude in deg
        """
        return self.read('P')

    def XYRP_outputs(self):
        """Get XYRP output amplitudes simultaneously.
    
        Returns:
            float: XYRP output amplitudes
        """
        outputs = self.read('XYRP').split(',')  # type str
        return (float(output) for output in outputs)