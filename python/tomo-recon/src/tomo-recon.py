#!/bin/env dls-python

# Run this script with a suitable mpirun command. 
# The DLS controls installation of h5py is built against openmpi version 1.6.5.
# Note that the current default mpirun in the controls environment (module load controls-tools)
# is an older version of mpirun - so use the full path to mpirun as demonstrated in the
# example below.
#
# For documentation, see: http://www.h5py.org/docs/topics/mpi.html
# 
# Example:
# /dls_sw/prod/tools/RHEL6-x86_64/openmpi/1-6-5/prefix/bin/mpirun -np 5 dls-python parallel-hdf5-demo.py
#

# First to pick up the DLS controls environment and versioned libraries
from pkg_resources import require
require('mpi4py==1.3.1')
require('h5py==2.2.0')
require('numpy') # h5py need to be able to import numpy

# Just to demonstrate that we have zmq in the environment as well
require('pyzmq==13.1.0')
import zmq
import logging

# Use multiprocessing
#from multiprocessing import Process, Queue
#logging.basicConfig(level=0,format=' %(asctime)s.%(msecs)03d %(processName)-16s %(levelname)-6s %(message)s', datefmt='%H:%M:%S')

# use threadinng
from threading import Thread as Process
from Queue import Queue
logging.basicConfig(level=0,format=' %(asctime)s.%(msecs)03d %(threadName)-16s %(levelname)-6s %(message)s', datefmt='%H:%M:%S')



from mpi4py import MPI
import h5py
import numpy as np
import socket

import time

#q2lock = threading.Lock()


def proc(inq, outq):
    i = 0
    while True:
        data = inq.get()
        if data == "END" :
            inq.put("END")
            logging.debug("Found end statement, finishing after processing %04i Frames" %(i))
            return
        logging.debug("Processing Frame %04i" % (data[0]))
        result = np.cos((data[1]))
        #q2lock.acquire()
        outq.put((data[0], result), block=True)
        logging.debug("Finished")
        #logging.debug("outq size is now %04i" % (outq.qsize()))
        #q2lock.release()
        i+=1

def loadproc(frames, input_file, outq):
    logging.debug ("reading from file: %s" % ( input_file))

    f = h5py.File(input_file, 'r')#, driver='mpio', comm=MPI.COMM_WORLD)
    
    for i in range(frames):
        logging.debug ("Reading frame: %i" % (i))
        data = f[input_data_loc][((rank*frames)+i):((rank*frames)+i+1),:,:]
        logging.debug ("Finished")
        outq.put((i,data))
        time.sleep(0.1)
    
    f.close()
    
    outq.put("END")
    
    #logging.debug("Finished reading from file")


rank = MPI.COMM_WORLD.rank  # The process ID (integer 0-3 for 4-process run)
size = MPI.COMM_WORLD.size  # The number of processes in the job.

# logging.debug a little report of what we have loaded
# if (rank == 0):
#     logging.debug ("mpi5py loaded: \n\t", MPI)
#     logging.debug ("h5py loaded:   \n\t", h5py)
#     logging.debug ("zmq loaded:    \n\t", zmq)

MPI.COMM_WORLD.barrier()

frames = 20

# get the hostname
ip = socket.gethostbyname(socket.gethostname())

logging.debug ("ip address is : %s" % (ip))

input_file = "/dls/sci-scratch/ExampleData/HDF/balls_m3_real_00014.h5"
input_data_loc = "/entry/instrument/detector/data"

logging.debug ("preparing Processing thread")
q1 = Queue()
q2 = Queue()
pp = []
for i in range(4):
    pp1 = Process(name='ProcThread-%02i'%(i), target=proc, args = (q1,q2))
    pp1.daemon = True
    pp1.start()
    pp.append(pp1)


logging.debug ("Preparing Loading thread")

lt = Process(name='LoadingThread', target=loadproc, args = (frames, input_file, q1))
lt.daemon = True
lt.start()

#logging.debug ("Starting Collecting Frames")
#pp.start()

# for p in pp:
#     p.join()


dd = []
for i in range(frames):
    d = q2.get(block=True)
    logging.debug ("Collected Frame %03i q has %03i left" % (d[0],q2.qsize()))
    dd.append(d)

dd.sort()

dd2 = []
for d in dd:
    dd2.append(d[1])

data = np.vstack(dd2)

logging.debug ("Transfering data shape is %s" % (str(data.shape)))

chunk_height = int(data.shape[1]/(size-1))

logging.debug ("chunk height is :%i" % (chunk_height))

trans = []
trans_mean = []
for i in range(size):
    section = data[:,(i*chunk_height):((i+1)*chunk_height),:]
    trans.append(section)
    trans_mean.append(section.shape)


logging.debug ("Sending data : %s" % (trans_mean))


data = MPI.COMM_WORLD.alltoall(trans)


trans_mean = []
for d in data:
    trans_mean.append(d.shape)

logging.debug("recieving data : %s" % (trans_mean))

# filename = 'parallel_h5py_demo.h5'
# 
# 
# logging.debug "Process %d writing to file: %s" % (rank, filename)
# 
# f = h5py.File(filename, 'w', driver='mpio', comm=MPI.COMM_WORLD)
# 
# dset = f.create_dataset('test', (size*10,size*10,size*10), dtype=np.float32)
# dset[:,rank*10:(rank+1)*10,:] = newdata
# 
# f.close()
# 
# if (rank == 0): 
#     logging.debug "\nNow examine file content with this command:"
#     logging.debug "\th5dump %s" % filename
#     
