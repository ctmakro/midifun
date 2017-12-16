# midifun

neural network piano performance generation.

the training data is extracted from midi formatted piano music.

a char-rnn model is used to predict next event (one of delay, note, velocity), given previously seen events.

## Dependencies

- tensorflow
- <http://github.com/ctmakro/canton> you can `clone` then install with `pip`.
- mido (midi file reading/playing)
- python-rtmidi (as backend for mido to interface with your system's midi devices)
- If you're on OSX you'll probably need a software emulated midi output device(on Windows you already have one provided by Microsoft) in order to play midi notes thru speaker. If that's the case please install SimpleSynth.

## Usage

1. download a bunch of midi files from internet

    ```bash
    $ python download.py
    ```

2. convert all downloaded and extracted midi files into our event stream representation, then save as `converted.npz`. RNN models could take that representation as their input.

    ```bash
    $ python datasource.py
    ```

3. train and eval

    ```bash
    $ ipython -i train.py
    ```

    then enter `r(1000)` to train for 1000 minibatches. enter `eval(1000)` to generate a stream of 1000 events and play via your system's default midi device.
