'''
Module containing tests for TupleHolder
'''
# pylint: disable=import-error, wrong-import-order

from dataclasses           import dataclass
from dmu.logging.log_store import LogStore

import pytest
from rx_kernel.tuple_holder   import TupleHolder
from rx_kernel.test_utilities import get_config_holder, make_inputs
from rx_kernel                import MessageSvc

MessageSvc.Initialize(-1)

log=LogStore.add_logger('rx_common:test_tuple_holder')
# -------------------------
class Data:
    '''
    Class used to share data between tests
    '''
    d_input_path : dict[bool, list[str]]
    d_tree_name  : dict[bool, str]

    l_tuple_opt  = [
            'gng',
            'pro',
            'cre',
            'spl',
            'rap',
            'tmp',
            'chainexctrg',
            'pap',
            'ap'
            ]
# -----------------------------------
@pytest.fixture(scope='session', autouse=True)
def _initialize():
    Data.d_input_path        = {}
    Data.d_input_path[False] = make_inputs(is_run3=False)
    Data.d_input_path[True ] = make_inputs(is_run3= True)

    Data.d_tree_name         = {}
    Data.d_tree_name[False]  = 'DT'
    Data.d_tree_name[True ]  = 'DecayTree'

    LogStore.set_level('rx_common:config_holder', 10)
    LogStore.set_level('rx_common:tuple_holder' , 10)
# -------------------------
def test_default():
    '''
    Test for default constructor
    '''
    obj = TupleHolder()
    obj.PrintInline()
# -------------------------
@pytest.mark.parametrize('option' , Data.l_tuple_opt)
@pytest.mark.parametrize('is_run3', [True, False])
def test_options(option : str, is_run3 : bool):
    '''
    Will test options
    '''
    ch  = get_config_holder(is_run3)
    obj = TupleHolder(ch, option)
    obj.PrintInline()
# -------------------------
@pytest.mark.parametrize('is_run3', [True, False])
def test_arg(is_run3 : bool):
    '''
    Test for constructor with file and tuple args
    '''
    file_path = Data.d_input_path[is_run3][0]
    tree_path = Data.d_tree_name[is_run3]

    ch  = get_config_holder(is_run3)
    obj = TupleHolder(ch, file_path, tree_path, 'pap')
    obj.PrintInline()

    rdr = obj.GetTupleReader()
    rdr.PrintInline()
# -------------------------
@pytest.mark.parametrize('is_run3', [True, False])
def test_postap(is_run3 : bool):
    '''
    Test for constructor for post_ap ntuples
    '''

    ch  = get_config_holder(is_run3=is_run3)
    obj = TupleHolder(ch, 'pap')
    obj.Init()

    trd = obj.GetTupleReader()
    trd.Init()
    trd.PrintListOfFiles()
    trd.PrintInline()

    tup = trd.Tuple()
    tup.Print()
