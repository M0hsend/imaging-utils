import cython_zinger

def resources():
    return ("CPU", 4) # max option

# What if there are only 9 left.
def batch_size():
    return 10

def frame_padding():
    return 1

def frame_padding_method():
    return "Reflect"

def process(data): # data will be [1024,1024,12]
    #set up input file
    
    result = cython_zinger.run(data, cpu=4)

    return result[:,:,1:-1]