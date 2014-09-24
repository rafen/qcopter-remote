import serial
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty

PORT = '/dev/ttyACM0'

def check_serial(f):
    """
    Function decorator to verify if the serial PORT is open,
     if so: execute the function,
     if not do not execute the function at all.
    :param f:
    :return:
    """
    def wrapper(*args):
        self = args[0]
        if self.serial and self.serial.isOpen():
            return f(*args)
        else:
            return None
    return wrapper


class RemoteControl(Widget):
    acc = ObjectProperty(None)
    acc_progress = ObjectProperty(None)
    term = ObjectProperty(None)
    start_btn = ObjectProperty(None)
    connect_btn = ObjectProperty(None)
    reset_btn = ObjectProperty(None)
    stop_btn = ObjectProperty(None)
    clear_btn = ObjectProperty(None)

    serial = None
    last_acc_command = ''

    def start(self):
        """
        Initialization function
        :return:
        """
        # Bind events to buttons
        self.connect_btn.bind(on_release=lambda o: self.connect_serial())
        self.start_btn.bind(on_release=lambda o: self.start_command(o))
        self.stop_btn.bind(on_release=lambda o: self.stop_command(o))
        self.reset_btn.bind(on_release=lambda o: self.reset())
        self.clear_btn.bind(on_release=lambda o: self.clear())

    def connect_serial(self):
        """
        Connect to Serial PORT. If it was already connected, close and connect
        again.
        :return:
        """
        if self.serial:
            self.term.text += 'Close serial %s \n' % PORT
            self.serial.close()
        try:
            self.term.text += 'Connecting to serial %s \n' % PORT
            self.serial = serial.Serial(PORT, 115200, timeout=0)
        except serial.serialutil.SerialException as e:
            self.term.text += 'Connection Error %s \n' % e
            self.serial = None


    @check_serial
    def update(self, dt):
        """
        Update function to be called frequently to read the serial port
        and Update controls
        :param dt:
        :return:
        """
        self.read_serial()
        self.update_controls()

    def update_controls(self):
        """
        Update control widget with new user interaction and update controls
        using term widget data
        :return:
        """
        self.acc_command()
        self.acc_progress_command()

    def read_serial(self):
        """
        Read data from serial port and write it on the term widget
        :return:
        """
        try:
            data = self.serial.readline()
        except serial.serialutil.SerialException as e:
            self.term.text += 'Serial Error %s \n' % e
            data = None
        if data:
            try:
                self.term.text += data
            except UnicodeDecodeError as e:
                self.term.text += 'Read Error %s \n' % e

    def acc_command(self):
        """
        Send acc command to serial PORT
        :return:
        """
        acc = str(self.acc.value).split('.')[0]
        command = 'acc: %s;' % acc
        if self.last_acc_command != command:
            self.serial.write(command)
            # Update progress bar
            self.acc_progress.value = self.acc.value
            # Save last command sent
            self.last_acc_command = command

    def acc_progress_command(self):
        """
        Update acc progress bar with data on the term widget
        :return:
        """
        index = self.term.text.rfind('acc:')
        if index >= 0:
            value = self.term.text[index + 4:index + 7]
            try:
                self.acc_progress.value = int(value)
            except ValueError:
                pass

    @check_serial
    def start_command(self, obj):
        """
        Send a simple character to the serial PORT to start the process
        :param obj:
        :return:
        """
        self.term.text += 'Sending "y" to start \n'
        self.serial.write('y')

    @check_serial
    def stop_command(self, obj):
        """
        Send a "stop" command to serial PORT and set acc to 0 for emergency
        stop!
        :param obj:
        :return:
        """
        self.term.text += 'Sending STOP \n'
        # Send stop signal several times for security
        self.serial.write('stop;')
        self.acc_progress.value = 0
        self.acc.value = 0

    def reset(self):
        """
        reset terminal, flush serial PORT and close serial connection
        :return:
        """
        self.term.text = ''
        if self.serial:
            self.serial.flushInput()
            self.serial.flushOutput()
            self.serial.close()
        self.serial = None

    def clear(self):
        """
        Clear terminal widget
        :return:
        """
        self.term.text = ''
