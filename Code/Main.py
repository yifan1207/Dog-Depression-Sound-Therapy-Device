# Import libraries
import sounddevice as sd # for playing sound
import soundfile as sf # for reading sound files
import serial # for communication with Arduino
import bluetooth # for communication with phone

# Define constants
SPEAKER_FREQ = 5 # frequency of the modified speaker in Hz
ALPHA_FREQ = 10 # frequency of the alpha brain wave in Hz
SOUND_DIR = "soundtracks/" # directory of the sound files
SD_MODE = 0 # mode for playing sound from sd card
BT_MODE = 1 # mode for playing sound from bluetooth
BUTTON_1 = 2 # pin number for button 1
BUTTON_2 = 3 # pin number for button 2
BUTTON_3 = 4 # pin number for button 3
BUTTON_4 = 5 # pin number for button 4

# Initialize variables
sound_mode = SD_MODE # initial sound mode
sound_index = 0 # initial sound index
sound_list = ["solfeggio1.wav", "solfeggio2.wav", "solfeggio3.wav"] # list of sound files
sound_file = None # current sound file
sound_data = None # current sound data
sound_stream = None # current sound stream
arduino = None # Arduino object
phone = None # Bluetooth object

# Define functions
def play_sound(file):
    """Plays a sound file using the modified speaker"""
    global sound_file, sound_data, sound_stream
    # Stop the previous sound stream if any
    if sound_stream is not None:
        sound_stream.stop()
    # Read the sound file and data
    sound_file = file
    sound_data, fs = sf.read(SOUND_DIR + sound_file)
    # Create a new sound stream
    sound_stream = sd.OutputStream(samplerate=fs, channels=1, callback=callback)
    # Start the sound stream
    sound_stream.start()

def callback(outdata, frames, time, status):
    """Callback function for the sound stream"""
    global sound_data
    # Check if there is any sound data left
    if len(sound_data) < frames:
        # Fill the remaining buffer with zeros
        outdata[:len(sound_data)] = sound_data
        outdata[len(sound_data):] = 0
        # Stop the sound stream
        raise sd.CallbackStop
    else:
        # Fill the buffer with sound data
        outdata[:] = sound_data[:frames]
        # Remove the played sound data
        sound_data = sound_data[frames:]

def switch_sound():
    """Switches to the next sound file in the list"""
    global sound_index, sound_list
    # Increment the sound index
    sound_index = (sound_index + 1) % len(sound_list)
    # Play the next sound file
    play_sound(sound_list[sound_index])

def pause_sound():
    """Pauses or resumes the sound stream"""
    global sound_stream
    # Check if the sound stream is active
    if sound_stream.active:
        # Pause the sound stream
        sound_stream.stop()
    else:
        # Resume the sound stream
        sound_stream.start()

def switch_mode():
    """Switches between sd card and bluetooth mode"""
    global sound_mode, sound_stream, phone
    # Stop the sound stream if any
    if sound_stream is not None:
        sound_stream.stop()
    # Toggle the sound mode
    sound_mode = 1 - sound_mode
    # Check the sound mode
    if sound_mode == SD_MODE:
        # Play the first sound file from the sd card
        play_sound(sound_list[0])
    elif sound_mode == BT_MODE:
        # Connect to the phone via bluetooth
        phone = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        phone.connect(("phone_address", 1)) # replace with actual phone address
        # Receive and play sound data from the phone
        sound_data = phone.recv(1024)
        sound_stream = sd.RawOutputStream(samplerate=44100, channels=1, callback=callback)
        sound_stream.start()

def read_arduino():
    """Reads and processes the input from the Arduino"""
    global arduino
    # Check if there is any data available
    if arduino.in_waiting > 0:
        # Read the data as a byte
        data = arduino.read()
        # Check the data value
        if data == b'1':
            # Button 1 is pressed, switch sound
            switch_sound()
        elif data == b'2':
            # Button 2 is pressed, pause sound
            pause_sound()
        elif data == b'3':
            # Button 3 is pressed, switch mode
            switch_mode()
        elif data == b'4':
            # Button 4 is pressed, do nothing
            pass

# Main program
def main():
    # Initialize the Arduino connection
    global arduino
    arduino = serial.Serial("COM3", 9600) # replace with actual port name
    # Play the first sound file from the sd card
    play_sound(sound_list[0])
    # Loop forever
    while True:
        # Read and process the input from the Arduino
        read_arduino()

# Run the main program
if __name__ == "__main__":
    main()
