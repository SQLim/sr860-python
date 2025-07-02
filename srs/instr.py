import pyvisa


class VisaDevice:

    def __init__(self, devpath):
        self._devpath = devpath
        self._dev = None
        self.open()

    def __del__(self):
        self.close()

    def open(self):
        if self._dev is not None:
            raise RuntimeError('Device has already been opened.')
        self._dev = pyvisa.ResourceManager().open_resource(self._devpath)

    def close(self):
        if self._dev is not None:
            self._dev.close()
            self._dev = None

    def clear(self):
        if self._dev is not None:
            self._dev.clear()

    def write(self, attribute, *args):
        """Writes a value for a given attribute from the SerialDevice.

        Args:
            attribute (str): The name of the attribute to read from self.API dictionary. 
            *args: Arguments to be formatted into the request string.

        Raises:
            ValueError: If the number of arguments does not match the
                expected number based on the attribute's data types, or if
                an invalid return value is received for a boolean type.
        """
        dtype, request, _ = self.API[attribute] # unpacks tuple of three, _ is ignored
        
        # make sure the correct number of arguments are passed
        dtype = dtype if isinstance(dtype, tuple) else (dtype,)
        if len(args) != len(dtype):
            raise ValueError('Number of arguments and data-types are not equal.')

        # If dtype is not bool, convert arg to the specified dtype 
        # (e.g., int(ar), float(ar), str(ar))
        # zip and for loop because dtype and args are tuples
        arg = ((int(ar) if dt is bool else dt(ar)) for dt, ar in zip(dtype, args))
        
        # formats request string with arg, if any, and passes it to the write method
        self._write(request.format(*arg))

    def read(self, attribute, *args):
        """Reads a value for a given attribute from the SerialDevice.

        Args:
            attribute (str): The name of the attribute to read from self.API dictionary. 
            *args: Arguments to be formatted into the request string.

        Returns:
            The read value, converted to the appropriate data type.

        Raises:
            ValueError: If the number of arguments does not match the
                expected number based on the attribute's data types, or if
                an invalid return value is received for a boolean type.
        """
        dtype, _, request = self.API[attribute] 
        dtype = dtype if isinstance(dtype, tuple) else (dtype,)

        # make sure no arguments are passed
        if len(args) != 0:
            raise ValueError('Additional arguments passed but not required.')

        # query
        ret = self._query(request)

        # format query to the correct dtype
        dtype = dtype[-1] 
        if dtype is bool:
            ret = int(ret)
            if ret not in (0, 1):
                raise ValueError('Invalid return value \'{}\' for type bool.'.format(ret))
        
        return dtype(ret)

    def _write(self, data):
        """Write to device.

        Args:
            data (str): write data
        """
        self._dev.write(data)#.encode('utf-8'))

    def _read(self):
        """Read from device.

        Returns:
            str: data
        """
        rdata = self._dev.read(termination='\n', encoding='utf-8') # stripped
        #if not rdata.endswith(b'\n'):
        #    raise TimeoutError('Expected newline terminator.')
        #return rdata.decode('utf-8').strip()
        return rdata

    def _query(self, data):
        """Write to device and read response.

        Args:
            data (str): write data

        Returns:
            str: data
        """
        self._write(data)
        return self._read()

