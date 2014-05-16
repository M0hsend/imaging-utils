import cython_blob

def resources():
    return ("CPU", 1) # max option

# What if there are only 9 left.
def batch_size():
    return 10

def ready_to_process(que):
    if que.length() > 10 :
        return True
    return False

def frame_padding():
    return 1

def metadata_required():
    return ("Flats", "Darks", "Angle") # anything from nxTomo.

def process(data, meta):
    #set up input file
    settings = {}
    settings['CPU'] = 1
    # run process
    
    result = cython_blob.run(data, settings)


    return result