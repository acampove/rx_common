'''
Module that will transform lists of LFNs from Ganga post_ap jobs
into a yaml file ready to be plugged into the RX c++ framework
'''
# pylint: disable=line-too-long, import-error
# pylint: disable=invalid-name

import os
import glob
import json
import argparse

from importlib.resources    import files
from dataclasses            import dataclass
from functools              import cache

import yaml
from dmu.logging.log_store  import LogStore
from rx_data.path_splitter  import PathSplitter

log = LogStore.add_logger('rx_common:make_tree_structure')
# ---------------------------------
@dataclass
class Data:
    '''
    Class used to hold shared data
    '''
    out_dir   = 'yaml_files'
    max_files : int
    lfn_vers  : str
    d_project : dict[str,list[str]]
    d_sample  : dict[str, dict[str, list[str]]]
# ---------------------------------
def _get_paths() -> list[str]:
    '''
    Returns list of LFNs, taken from data stored in project itself, rx_data_lfns
    '''
    files_wc = files('rx_data_lfns').joinpath(f'{Data.lfn_vers}/*.json')
    files_wc = str(files_wc)
    l_file   = glob.glob(files_wc)
    nfile    = len(l_file)

    if nfile == 0:
        raise ValueError(f'Cannot find any file in: {files_wc}')

    l_path   = []

    for file in l_file:
        with open(file, encoding='utf-8') as ifile:
            l_path_file = json.load(ifile)
            nlfn        = len(l_path_file)
            log.debug(f'Adding {nlfn} LFNs')
            l_path     += l_path_file

    return l_path
# ---------------------------------
@cache
def _load_config(name : str) -> dict:
    '''
    Loads config file in rx_config, using its name as argument
    '''
    cfg_path = files('rx_config').joinpath(name)
    cfg_path = str(cfg_path)

    with open(cfg_path, encoding='utf-8') as ifile:
        d_conf = yaml.safe_load(ifile)

    return d_conf
# ---------------------------------
def _get_args() -> argparse.Namespace:
    '''
    Parse arguments
    '''
    parser = argparse.ArgumentParser(description='Will make YAML files with specific formatting from lists of LFNs in project')
    parser.add_argument('-m', '--max', type=int, help='Maximum number of paths, for test runs'   , default =-1)
    parser.add_argument('-v', '--ver', type=str, help='Version of LFNs'                          , required=True)
    parser.add_argument('-l', '--lvl', type=int, help='log level', choices=[10, 20, 30]          , default =20)
    args = parser.parse_args()

    return args
# ---------------------------------
def _initialize(args : argparse.Namespace) -> None:
    Data.max_files = args.max
    Data.lfn_vers  = args.ver
    Data.d_project = _load_config('sample_run3.yaml')
    Data.d_sample  = _get_formatted_lfns()

    LogStore.set_level('rx_data:lfn_to_yaml', args.lvl)
# ---------------------------------
def _get_formatted_lfns() -> dict[str, dict[str, list[str]]]:
    '''
    Returns dictionary between sample name and 
    dictionary between HLT trigger and list of LFNs
    '''
    l_path   = _get_paths()
    splt     = PathSplitter(paths=l_path, max_files=Data.max_files)
    d_path   = splt.split()
    d_sample = _reformat_paths(d_path)

    return d_sample
# ---------------------------------
def _reformat_paths(d_path : dict[tuple[str,str],list[str]]) -> dict[str,dict[str,list[str]]]:
    d_sample = {}
    for (sample, trigger), l_path in d_path.items():
        if sample not in d_sample:
            d_sample[sample] = {}

        d_sample[sample][trigger] = l_path

    return d_sample
# ---------------------------------
def _get_metadata(project : str) -> dict[str,str]:
    d_meta = {
            'DTName'   : 'DecayTree',
            'MCDTName' : 'MCDecayTree',
            }

    if not project.startswith('Data'):
        return d_meta

    d_meta['LumiTreeName'] = 'LumiTree'

    return d_meta
# ---------------------------------
def _path_from_list(l_lfn : list[str], sample : str, hlt : str) -> str:
    '''
    Takes list of LFNs and names of sample and HLT2 trigger
    Makes list of LFNs and returns path to it.
    '''

    json_path = f'{Data.out_dir}/{sample}_{hlt}.json'
    json_dir  = os.path.dirname(json_path)

    os.makedirs(json_dir, exist_ok=True)
    with open(json_path, 'w', encoding='utf-8') as ofile:
        json.dump(l_lfn, ofile)

    return json_path
# ---------------------------------
def _lfns_path_from_sample(sample : str) -> dict[str,str]:
    '''
    For a sample name, return a dictionary between trigger and path to list of LFNs 
    '''
    sample = sample.lower()
    if sample not in Data.d_sample:
        log.warning(f'Sample {sample} not found')
        return {}

    d_hlt_lfn = Data.d_sample[sample]
    d_hlt_path= {hlt : _path_from_list(l_lfn, sample, hlt) for hlt, l_lfn in d_hlt_lfn.items()}

    return d_hlt_path
# ---------------------------------
def _get_samples(project : str) -> dict[str,dict[str,str]]:
    '''
    Returns dictionary between sample and
    dictionary between HLT2 trigger and path to list of LFNs
    '''
    l_sample = Data.d_project[project]

    d_sample_lfn = {sample : _lfns_path_from_sample(sample) for sample in l_sample}

    return d_sample_lfn
# ---------------------------------
def _get_data_dict() -> dict[str,dict[str,str]]:
    d_data    = {}
    for proj in Data.d_project:
        d_sam={}
        d_sam.update(_get_samples (proj))
        d_sam.update(_get_metadata(proj))

        d_data[proj] = d_sam

    return d_data
# ---------------------------------
def main():
    '''
    Script starts here
    '''
    args = _get_args()
    _initialize(args)

    d_data = _get_data_dict()

    with open('samples.yaml', 'w', encoding='utf-8') as ofile:
        yaml.safe_dump(d_data, ofile)
# ---------------------------------
if __name__ == '__main__':
    main()
