
import tensorflow as tf
import canton as ct
from canton import *
import numpy as np

from midiutil import mido, get_outport, open_midifile
from events import MIDI_to_events, play_events, Event, cr
from datasource import bigstream

categories = cr.get_code_categories()
print(categories,'categories in stream')
print('stream length:',len(bigstream))

# code below partially from gru_text_generation_2.py

# RNN model
def model_builder(style=0):
    c = ct.Can()
    if style==0:
        gru,d1 = (
            c.add(GRU(categories,128)),
            c.add(LastDimDense(128,categories)),
        )
    elif style==1:
        gru,d1 = (
            c.add(GRU(categories,192)),
            c.add(LastDimDense(192,categories)),
        )
    elif style==2:
        gru,d1 = (
            c.add(GRU(categories,128)),
            c.add(LastDimDense(128,categories)),
        )

    def call(i,starting_state=None):
        # i is one-hot encoded
        i = gru(i,starting_state=starting_state)
        # (batch, time_steps, 512)
        shape = tf.shape(i)
        b,t,d = shape[0],shape[1],shape[2]

        ending_state = i[:,t-1,:]

        i = d1(i)
        # i = Act('softmax')(i)

        return i, ending_state

    c.set_function(call)
    return c

# functions to train and eval
def feed_gen(model):
    input_text = tf.placeholder(tf.uint8,
        shape=[None, None]) # [batch, timesteps]

    input_text_onehot= tf.one_hot(input_text,depth=categories,dtype=tf.float32)

    xhead = input_text_onehot[:,:-1] # [batch, 0:timesteps-1, cat]
    gt = input_text_onehot[:,1:] # [batch, 1:timesteps, cat]
    y,_ = model(xhead,starting_state=None) # [batch, 1:timesteps, cat]

    loss = ct.mean_softmax_cross_entropy(y,gt)

    train_step = tf.train.AdamOptimizer(1e-3).minimize(
        loss,var_list=model.get_weights())

    def feed(minibatch):
        nonlocal train_step,loss,input_text
        sess = ct.get_session()
        res = sess.run([loss,train_step],feed_dict={input_text:minibatch})
        return res[0]

    # stateful predict:
    # if we have starting_state for the RNN
    starting_state = tf.placeholder(tf.float32, shape=[None, None])
    stateful_y, ending_state = \
        model(input_text_onehot,starting_state=starting_state)
    stateful_y = Act('softmax')(stateful_y)

    # if we dont have starting state for the RNN
    stateful_y_init, ending_state_init = \
        model(input_text_onehot)
    stateful_y_init = Act('softmax')(stateful_y_init)

    def stateful_predict(i, st=None):
        sess = ct.get_session()
        if st is None: # if we dont have starting_state for the RNN
            res = sess.run([stateful_y_init,ending_state_init],
                feed_dict={input_text:i})
        else:
            res = sess.run([stateful_y,ending_state],
                feed_dict={input_text:i,starting_state:st})
        return res

    return feed, stateful_predict

from plotter import interprocess_plotter as plotter

if __name__ == '__main__':
    models = [model_builder(style=k) for k in [1]]
    feed_predicts = [feed_gen(m) for m in models]
    [m.summary() for m in models]
    iplotter = plotter(num_lines=len(models))

    # model = model_builder()
    # model.summary()
    # feed,stateful_predict = feed_gen(model)
    get_session().run(gvi()) # init global variable

    # training loop

    time_steps = 512
    batch_size = 1

    def r(ep=100):
        length = len(bigstream)
        mbl = time_steps * batch_size
        sr = length - mbl - time_steps - 2
        for i in range(ep):
            print('---------------------iter',i,'/',ep)

            j = np.random.choice(sr)

            minibatch = bigstream[j:j+mbl]
            minibatch.shape = [batch_size, time_steps]

            loss = [fp[0](minibatch) for fp in feed_predicts]
            # print('loss:',loss)
            iplotter.pushys(loss)

            if i%100==0 : pass#show2()

    def eval(length=400,argmax=False,tofile=False,seconds=None):
        for e,fp in enumerate(feed_predicts):
            feed,stateful_predict = fp

            stream = []
            # event = np.array(Event('delay',0.1).to_integer()).reshape(1,1)
            event = np.array([np.random.choice(categories)]).reshape(1,1)
            starting_state = None

            # sequentially generate musical event out of the GRU
            # for i in range(length):
            if seconds is None:
                counter = length # number of events remain to generate
            else:
                counter = 0 # number of seconds of music so far

            while 1:
                # output of RNN, new state of RNN
                stateful_y, ending_state = stateful_predict(
                    event, # input to RNN
                    starting_state, # prev state of RNN
                )
                # use ending_state as new starting_state
                starting_state = ending_state

                dist = stateful_y[0,0] # last dimension is the probability distribution
                if argmax==True:
                    code = np.argmax(dist)
                else:
                    code = np.random.choice(categories, p=dist) # sample a byte from distribution
                stream.append(code)
                # use as input of next timestep
                event[0,0] = code

                if seconds is None:
                    counter-=1
                    if counter==0:
                        break
                else: # if we generate by seconds
                    temp = Event.from_integer(code)
                    if temp.category=='delay':
                        counter+=temp.value
                        if counter>seconds:
                            break
                        else:
                            print(counter,'seconds generated...')

            integerized_stream = [Event.from_integer(i) for i in stream]
            if tofile==False:
                print(length,'events sampled. playing...')
                play_events(integerized_stream)
            else:
                filename = 'sampled_{}.mid'.format(e)
                print(length,'events sampled. saving to',filename)
                midifile = play_events(integerized_stream,tofile=True)
                midifile.save(filename)
                print('total time:',midifile.length)

            # import time
            # time.sleep(2)

    def submit(fn=None):
        import crowdai
        import mido
        from apikey import apikey # as a string

        midi_file_path=filename if fn is not None else 'sampled_0.mid'
        API_KEY=apikey

        midifile = mido.MidiFile(midi_file_path)
        assert midifile.length > 3600 - 10 and midifile.length < 3600 + 10
        midifile.type=0
        assert len(midifile.tracks) == 1
        assert midifile.type == 0

        challenge = crowdai.Challenge("AIGeneratedMusicChallenge", API_KEY)
        challenge.submit(midi_file_path)
