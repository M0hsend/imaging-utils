import cython_zinger

def resources():
    return ("CPU", 4) # max option

# What if there are only 9 left.
def batch_size():
    return 10

def ready_to_process(que):
    if que.length() > 10 :
        return True
    return False

def frame_padding():
    return 1

def process(data):
    #set up input file
    settings = {}
    settings['CPU'] = 4
    # run process
    
    result = cython_zinger.run(data, settings)


    return result