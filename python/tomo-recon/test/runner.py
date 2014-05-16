import plugins.utils as pu

test = pu.load_loader_plugin('hdftest')

test.preprocess()
test.process()
test.postprocess()

#test2 = pu.load_filter_plugin('filtertest')
# 
# test2.preprocess()
# test2.process()
# test2.postprocess()

