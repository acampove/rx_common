'''
Module making AllowedConf c++ class available to namespace
'''
# pylint: disable=import-error, invalid-name
import os

from ROOT import SettingDef as SettingDef_cpp
from ROOT import std

def Initialize(conf_dir : str) -> None:
    '''
    Interface to AllowedConf's initializer
    '''
    if not os.path.isdir(conf_dir):
        raise FileNotFoundError(f'Directory with config YAML files: {conf_dir} not found')

    conf_dir_str = std.string(conf_dir)

    SettingDef_cpp.AllowedConf.Initialize(conf_dir_str)
