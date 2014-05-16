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
#from pkg_resources import require
#require('mpi4py==1.3.1')
#require('h5py==2.2.0')
#require('numpy') # h5py need to be able to import numpy

# Just to demonstrate that we have zmq in the environment as well
#require('pyzmq==13.1.0')
import zmq

import threading
from Queue import Queue
from mpi4py import MPI

rank_names = {0:'Load', 1:' CPU' , 2:' GPU', 3:'Save'}

rank = MPI.COMM_WORLD.rank  # The process ID (integer 0-3 for 4-process run)
size = MPI.COMM_WORLD.size  # The number of processes in the job.
machines = size/len(rank_names)
machine_rank = rank/machines
machine_number = rank%machines
machine_number_string = "%03i"%(machine_number)

import logging
logging.basicConfig(level=0,format='L %(asctime)s.%(msecs)03d M' + machine_number_string + ' ' + rank_names[machine_rank] + ' %(levelname)-6s %(message)s', datefmt='%H:%M:%S')

import h5py
import numpy as np

import time
import random

#q2lock = threading.Lock()


MPI.COMM_WORLD.barrier()

# get the hostname
import socket
ip = socket.gethostbyname(socket.gethostname())

logging.debug ("ip address is : %s" % (ip))


if machine_rank == 0:
    logging.debug("Loading process")
    # make some data
    for i in range(2):
        data = np.random.rand(1000,1000,1)
        logging.debug("Sending data with mean %f and shape %s" %(data.mean(), str(data.shape)))
        MPI.COMM_WORLD.Send(data, dest=((machines*1) + machine_number), tag=1)
        logging.debug("Sent data with mean %f and shape %s" %(data.mean(), str(data.shape)))
if machine_rank == 1:
    logging.debug("CPU process")
    for i in range(2):
        data = np.empty([1000,1000,1], dtype=np.float64)
        MPI.COMM_WORLD.Recv(data, source=((machines*0) + machine_number), tag=1)
        logging.debug("recieved data with mean %f and shape %s" % (data.mean(), str(data.shape)))
        data = np.sin(data)
        logging.debug("Sending data with mean %f and shape %s" %(data.mean(), str(data.shape)))
        MPI.COMM_WORLD.Send(data, dest=((machines*3) + machine_number), tag=2)
if machine_rank == 2:
    logging.debug("GPU process")
if machine_rank == 3:
    logging.debug("Saving process")
    for i in range(2):
        data = np.empty([1000,1000,1], dtype=np.float64)
        MPI.COMM_WORLD.Recv(data, source=((machines*1) + machine_number), tag=2)
        logging.debug("recieved data with mean %f and shape %s" % (data.mean(), str(data.shape)))



#data = MPI.COMM_WORLD.alltoall(trans)

