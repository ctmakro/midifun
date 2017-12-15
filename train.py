import tensorflow as tf
import canton as ct
from canton import *
import numpy as np

from midiutil import mido, outport, open_midifile
from events import MIDI_to_events, play_events, Event, cr
from datasource import bigstream

categories = cr.get_code_categories()
print(categories,'categories in stream')

# code below partially from gru_text_generation_2.py

# RNN model
def model_builder():
    c = ct.Can()
    gru,d1 = (
        c.add(GRU(categories,256)),
        # c.add(LastDimDense(256,256)),
        c.add(LastDimDense(256,categories)),
    )

    def call(i,starting_state=None):
        # i is one-hot encoded
        i = gru(i,starting_state=starting_state)
        # (batch, time_steps, 512)
        shape = tf.shape(i)
        b,t,d = shape[0],shape[1],shape[2]

        ending_state = i[:,t-1,:]

        i = Act('lrelu',alpha=0.05)(i)
        i = d1(i)
        # i = Act('softmax')(i)

        return i, ending_state

    c.set_function(call)
    return c

model = model_builder()

# functions to train and eval
def feed_gen():
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

feed,stateful_predict = feed_gen()

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

        loss = feed(minibatch)
        print('loss:',loss)

        if i%100==0 : pass#show2()

def eval(length=400,argmax=False):
    stream = []
    event = np.array(Event('delay',0.1).to_integer()).reshape(1,1)
    starting_state = None

    # sequentially generate musical event out of the GRU
    for i in range(length):
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

    print(length,'events sampled. playing...')
    play_events([Event.from_integer(i) for i in stream])
