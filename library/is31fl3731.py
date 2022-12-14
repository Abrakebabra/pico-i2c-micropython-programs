import machine
import utime

# Micropython
# Converted from https://github.com/pimoroni/rgbmatrix5x5-python/
# For rgb 5x5 only


_MODE_REGISTER = 0x00
_FRAME_REGISTER = 0x01
_AUTOPLAY1_REGISTER = 0x02
_AUTOPLAY2_REGISTER = 0x03
_BLINK_REGISTER = 0x05
_AUDIOSYNC_REGISTER = 0x06
_BREATH1_REGISTER = 0x08
_BREATH2_REGISTER = 0x09
_SHUTDOWN_REGISTER = 0x0a
_GAIN_REGISTER = 0x0b
_ADC_REGISTER = 0x0c

_CONFIG_BANK = 0x0b
_BANK_ADDRESS = 0xfd

_PICTURE_MODE = 0x00
_AUTOPLAY_MODE = 0x08
_AUDIOPLAY_MODE = 0x18

_ENABLE_OFFSET = 0x00
_BLINK_OFFSET = 0x12
_COLOR_OFFSET = 0x24

LED_GAMMA = (
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2,
    2, 2, 2, 3, 3, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5,
    6, 6, 6, 7, 7, 7, 8, 8, 8, 9, 9, 9, 10, 10, 11, 11,
    11, 12, 12, 13, 13, 13, 14, 14, 15, 15, 16, 16, 17, 17, 18, 18,
    19, 19, 20, 21, 21, 22, 22, 23, 23, 24, 25, 25, 26, 27, 27, 28,
    29, 29, 30, 31, 31, 32, 33, 34, 34, 35, 36, 37, 37, 38, 39, 40,
    40, 41, 42, 43, 44, 45, 46, 46, 47, 48, 49, 50, 51, 52, 53, 54,
    55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70,
    71, 72, 73, 74, 76, 77, 78, 79, 80, 81, 83, 84, 85, 86, 88, 89,
    90, 91, 93, 94, 95, 96, 98, 99, 100, 102, 103, 104, 106, 107, 109, 110,
    111, 113, 114, 116, 117, 119, 120, 121, 123, 124, 126, 128, 129, 131, 132, 134,
    135, 137, 138, 140, 142, 143, 145, 146, 148, 150, 151, 153, 155, 157, 158, 160,
    162, 163, 165, 167, 169, 170, 172, 174, 176, 178, 179, 181, 183, 185, 187, 189,
    191, 193, 194, 196, 198, 200, 202, 204, 206, 208, 210, 212, 214, 216, 218, 220,
    222, 224, 227, 229, 231, 233, 235, 237, 239, 241, 244, 246, 248, 250, 252, 255)


class IS31FL3731:
    """Represent an IS31LF3731 Matrix Display."""

    _width = 5
    _height = 5

    def __init__(self, i2c):
        """Initialise Matrix."""
        self.i2c = i2c
        self.address = 0x74
        self._is_setup = False
        self._gamma_table = LED_GAMMA
        self._brightness = 1.0

        self.clear()

    def setup(self):
        """Set up device."""
        if self._is_setup:
            return True

        self._is_setup = True
        
        try:
            self._reset()
        except IOError as e:
            if hasattr(e, 'errno') and e.errno == 5:
                e.strerror += '\n\nMake sure your LED SHIM is attached, and double-check your soldering.\n'
            raise e

        self.show()

        # Display initialization

        # Switch to configuration bank
        self._bank(_CONFIG_BANK)

        # Switch to Picture Mode
        self.i2c.writeto_mem(self.address, _MODE_REGISTER, bytearray([_PICTURE_MODE]))

        # Disable audio sync
        self.i2c.writeto_mem(self.address, _AUDIOSYNC_REGISTER, bytearray([0]))

        enable_pattern = [
            0b00000000, 0b10000111,
            0b00111110, 0b00111110,
            0b00111111, 0b10111110,
            0b00000111, 0b10000110,
            0b00110000, 0b00000000,
            0b00111111, 0b10001110,
            0b00111111, 0b10001110,
            0b01111111, 0b11111110,
            0b01111111, 0b00000000,
        ]

        # Switch to bank 1 ( frame 1 )
        self._bank(1)

        # Enable LEDs
        self.i2c.writeto_mem(self.address, 0x00, bytearray(enable_pattern))

        # Switch to bank 0 ( frame 0 )
        self._bank(0)

        # Enable LEDs
        self.i2c.writeto_mem(self.address, 0x00, bytearray(enable_pattern))


    @property
    def width(self):
        """Return width of device."""
        return self._width

    @property
    def height(self):
        """Return height of device."""
        return self._height

    def set_gamma(self, gamma_table):
        """Set the LED gamma table.

        Set the table of values used to give the LEDs a pleasing
        to the eye brightness curve.

        :param gamma_table: List of 256 values in the range 0-255.

        """
        if len(gamma_table) != 256:
            raise ValueError('Gamma table must be a list with 256 values.')

        self._gamma_table = gamma_table

    def clear(self):
        """Clear the buffer.

        You must call `show` after clearing the buffer to update the display.

        """
        self._current_frame = 0

        #try:
        #    del self.buf
        #except AttributeError:
        #    pass

        self.buf = [(0, 0, 0, 1.0) for x in range(self._width * self._height)]

    def set_brightness(self, brightness):
        """Set a global brightness value.

        :param brightness: Brightness value from 0.0 to 1.0

        """
        self._brightness = brightness

    def set_all(self, r, g, b, brightness=1.0):
        """Set all pixels in the buffer.

        :param r, g, b: Intensity of the pixel, from 0 to 255.

        """
        for x in range(self._width):
            for y in range(self._height):
                self.set_pixel(x, y, r, g, b, brightness)

    def set_pixel(self, x, y, r, g, b, brightness=1.0):
        """Set a single pixel in the buffer.

        :param x: Position of pixel from left
        :param y: Position fo pixel from top
        :param r, g, b: Intensity of the pixel, from 0 to 255.

        """
        r, g, b = [int(c) for c in (r, g, b)]

        for c in (r, g, b):
            if c > 255 or c < 0:
                raise ValueError('Value {} out of range. RGB values should be between 0 and 1'.format(c))

        try:
            if x % 2 == 1:
                y = 4 - y
            self.buf[y + (x * 5)] = (r, g, b, brightness)

        except IndexError:
            raise ValueError('x position ({}) is out of range!'.format(x))

    def set_multiple_pixels(self, indexes, from_colour, to_colour=None):
        """Set multiple pixels to a range of colours sweeping from from_colour to to_colour.

        :param from_colour: A tuple with 3 values representing the red, green and blue of the first colour
        :param to_colour: A tuple with 3 values representing the red, green and blue of the second colour

        """
        if to_colour is None:
            to_colour = from_colour

        length = float(len(indexes))
        step = 0
        from_r, from_g, from_b = from_colour
        to_r, to_g, to_b = to_colour
        step_r, step_g, step_b = to_r - from_r, to_g - from_g, to_b - from_b
        step_r /= length
        step_g /= length
        step_b /= length

        for index in indexes:
            if type(index) == int:
                y = index // 5
                x = index % 5
            else:
                x, y = index
            self.set_pixel(x, y, from_r + (step_r * step), from_g + (step_g * step), from_b + (step_b * step))
            step += 1


    def show(self):
        """Show the buffer contents on the display."""
        self.setup()

        next_frame = 0 if self._current_frame == 1 else 1

        output = [0 for x in range(144)]

        for x in range(self._width * self._height):
            r, g, b, br = self.buf[x]
            r, g, b = [self._gamma_table[int(c * self._brightness * br)] for c in (r, g, b)]

            ir, ig, ib = self._pixel_addr(x)
            output[ir] = r
            output[ig] = g
            output[ib] = b

        self._bank(next_frame)

        offset = 0

        for chunk in self._chunk(output, 32):
            self.i2c.writeto_mem(self.address, _COLOR_OFFSET + offset, bytearray(chunk))
            offset += 32

        self._frame(next_frame)

    def _reset(self):
        self._sleep(True)
        utime.sleep(0.00001)
        self._sleep(False)

    def _sleep(self, value):
        return self._register(_CONFIG_BANK, _SHUTDOWN_REGISTER, not value)

    def _frame(self, frame=None, show=True):
        if frame is None:
            return self._current_frame

        if not 0 <= frame <= 8:
            raise ValueError('Frame out of range: 0-8')

        self._current_frame = frame

        if show:
            self._register(_CONFIG_BANK, _FRAME_REGISTER, frame)

    def _bank(self, bank=None):
        """Switch display driver memory bank."""
        if bank is None:
            return self.i2c.readfrom_mem(self.address, _BANK_ADDRESS, 1)[0]

        self.i2c.writeto_mem(self.address, _BANK_ADDRESS, bytearray([bank]))

    def _register(self, bank, register, value=None):
        """Write display driver register."""
        self._bank(bank)

        if value is None:
            return self.i2c.readfrom_mem(self.address, register, 1)[0]

        self.i2c.writeto_mem(self.address, register, bytearray([value]))

    def _chunk(self, data, n):
        for i in range(0, len(data) + 1, n):
            yield data[i:i + n]

    def _pixel_addr(self, x, rgb=None):
        lookup = [
            (118, 69, 85),
            (117, 68, 101),
            (116, 84, 100),
            (115, 83, 99),
            (114, 82, 98),
            (113, 81, 97),
            (112, 80, 96),
            (134, 21, 37),
            (133, 20, 36),
            (132, 19, 35),
            (131, 18, 34),
            (130, 17, 50),
            (129, 33, 49),
            (128, 32, 48),

            (127, 47, 63),
            (121, 41, 57),
            (122, 25, 58),
            (123, 26, 42),
            (124, 27, 43),
            (125, 28, 44),
            (126, 29, 45),
            (15, 95, 111),
            (8, 89, 105),
            (9, 90, 106),
            (10, 91, 107),
            (11, 92, 108),
            (12, 76, 109),
            (13, 77, 93),
        ]
        if rgb is None:
            return lookup[x]
        else:
            return lookup[x][rgb]


