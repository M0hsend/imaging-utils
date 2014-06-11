import threading
import logging
import optparse
import socket

import numpy as np

from Queue import Queue
from mpi4py import MPI

from plugins import utils as pu

##########################################################
##  Sort out logging and initial MPI setup
##########################################################
rank_names = {0:'Load', 1:'Proc'}

rank = MPI.COMM_WORLD.rank
size = MPI.COMM_WORLD.size
machines = size/len(rank_names)
machine_rank = rank/machines
machine_number = rank%machines
machine_number_string = "%03i"%(machine_number)

logging.basicConfig(level=0,format='L %(asctime)s.%(msecs)03d M' + machine_number_string + ' ' + rank_names[machine_rank] + ' %(levelname)-6s %(message)s', datefmt='%H:%M:%S')

MPI.COMM_WORLD.barrier()

usage = "%prog [options] input_nexus_file output_nexus_file"
version = "%prog 0.1"
parser = optparse.OptionParser(usage=usage, version=version)
parser.add_option("-s", "--slices", dest="slices", help="Number of points between sinograms", default=128, type='int')
    
(options, args) = parser.parse_args()

inputfile = args[0]

logging.info("File to work with is %s" % (inputfile))

MPI.COMM_WORLD.barrier()


# get the hostname
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
        #MPI.COMM_WORLD.Send(data, dest=((machines*3) + machine_number), tag=2)
if machine_rank == 2:
    logging.debug("GPU process")
if machine_rank == 3:
    logging.debug("Saving process")
    for i in range(2):
        data = np.empty([1000,1000,1], dtype=np.float64)
        #MPI.COMM_WORLD.Recv(data, source=((machines*1) + machine_number), tag=2)
        logging.debug("recieved data with mean %f and shape %s" % (data.mean(), str(data.shape)))



#data = MPI.COMM_WORLD.alltoall(trans)

