'''
Created on 7 Apr 2014

@author: ssg37927
'''


def load_plugin(name):
    mod = __import__(name)
    components = name.split('.')
    for comp in components[1:]:
        mod = getattr(mod, comp)
    class_ = getattr(mod, name.split('.')[-1])
    instance = class_()
    return instance

def load_loader_plugin(name):
    return load_plugin('plugins.loaders.%s' % name)

def load_filter_plugin(name):
    return load_plugin('plugins.filters.%s' % name)

