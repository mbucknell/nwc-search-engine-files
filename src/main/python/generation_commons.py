import argparse
import errno
import json
import os
from types import NoneType

import requests


"""
Retrieve a list of features from a geoserver instance. The 'id' attribute on each returned 
list item is set by the 'id_attribute' parameter. Each returned item is a dictionary.
    geoserver_endpoint - String url
    layer - String layer name
    attributes - list of String attribute names
    id_attribute - String attribute name. Must also be listed in the 'attributes' param. 
"""
def get_features(geoserver_endpoint, data_config):
    params = {
        'service' : 'wfs',
        'version' : '2.0.0',
        'request' : 'GetFeature',
        'typeNames' : '{0}:{1}'.format(data_config['namespace'], data_config['layerName']),
        'propertyName' : ','.join([value for (key, value) in data_config['properties'].iteritems()]).encode('utf-8'),
        'outputFormat' : 'json'
    }
    response = requests.get(geoserver_endpoint + 'wfs', params)

    response.raise_for_status()
    response.encoding = 'utf-8'
    
    my_json = response.json()
    features = my_json['features']
    features_with_ids = []
    for feature in features:
        properties = feature['properties']
        id_value = properties.get(data_config['properties']['id'], None)
        if type(id_value) is NoneType :
            raise RuntimeError(
                                "The following feature did not have a value for the id attribute '{0}:'. ".format(data_config['properties']['id']) +
                                str(feature))
        else:
            feature['id'] = id_value
            features_with_ids.append(feature)  
    
    return features_with_ids
"""
Retrieve a list of NWC project or data items from sciencebase. Each returned item is a dictionary.
    sciencebase_endpoint - String url for sciencebase
    browse_category - String category. ex: 'Project', 'Datasets'
"""
def get_sciencebase_items(sciencebase_endpoint, browse_category):
    response = requests.get(sciencebase_endpoint + 'catalog/items',
                            {'facetTermLevelLimit' : 'false',
                             'q' : '',
                             'community' : 'National Water Census',
                             'filter0' : 'browseCategory=' + browse_category,
                             'format' : 'json'
                             })
    response.raise_for_status()
    my_json = response.json() 
    return my_json['items']

'''
parse commandline args and return a dictionary
'''
def parse_args (argv):

    DEFAULT_CONFIG = 'data_config.json'
    DEFAULT_GEOSERVER = 'http://cida.usgs.gov/nwc/geoserver/'
    DEFAULT_SCIENCEBASE = 'https://www.sciencebase.gov/'
    DEFAULT_ROOT_URL = 'http://cida.usgs.gov/nwc/'
    
    parser = argparse.ArgumentParser(description='Generate sitemap.xml for NWC')
    parser.add_argument('--data_config',
                        help='Full path to the JSON file containing constants used to retrieve data and to generate the files',
                        default=DEFAULT_CONFIG)
    parser.add_argument('--geoserver', 
                        help='Geoserver to use to retrieve HUCs and gages. Defaults to %s' % DEFAULT_GEOSERVER, 
                        default=DEFAULT_GEOSERVER)
    parser.add_argument('--sciencebase_url', 
                        help='URL where the data discovery tool gets its project information. Defaults to %s' % DEFAULT_SCIENCEBASE,
                        default=DEFAULT_SCIENCEBASE)
    parser.add_argument('--root_url', 
                        help='The application\'s root url. Defaults to %s' % DEFAULT_ROOT_URL,
                        default=DEFAULT_ROOT_URL)
    parser.add_argument('--destination_dir', 
                        help='Destination directory for the sitemap.xml file. Defaults to the directory where the script is run.',
                        default='')
    args = parser.parse_args(args=argv[1:])
    return args

'''
Read the contents of the structured data config file and return a dictionary
'''
def get_structured_data_config(filename):

    with open(filename, 'r') as fd:
        result = json.loads(fd.read())
    return result

'''
get waterbudget huc feature information
'''
def get_waterbudget_features(geoserver, data_config):
    return {key : get_features(geoserver, value) for (key, value) in data_config['watershed'].iteritems()}

'''
get streamflow gage ids
'''
def get_streamflow_gage_features(geoserver, data_config):
    return get_features(geoserver, data_config['streamflow']['gage'])

'''
get streamflow huc features
'''
def get_streamflow_huc_features(geoserver, data_config):
    return get_features(geoserver, data_config['streamflow']['huc12'])

'''
get sciencebase project items
'''
def get_project_items(sciencebase):
    return get_sciencebase_items(sciencebase, 'Project')

'''
get sciencebase dataset items
'''
def get_dataset_items(sciencebase):
    return get_sciencebase_items(sciencebase, 'Data')

'''
get nwc data from geoserver and sciencebase.
    geoserver - String containing geoserver endpoint
    sciencebase - String containing the sciencebase endpoint
    sd_config - Dictionary used
returns a dictionary of data from the servers
'''
def get_nwc_data(geoserver, sciencebase, data_config):
    print 'Retrieving HUCs and gage IDs from %s' % geoserver
    print 'Retrieving projects and dataset ids from %s' % sciencebase
    return {
        'waterbudget_hucs' : get_waterbudget_features(geoserver, data_config),
            'streamflow_gages' : get_streamflow_gage_features(geoserver, data_config),
            'streamflow_hucs' : get_streamflow_huc_features(geoserver, data_config),
            'projects' : get_project_items(sciencebase),
            'datasets' : get_dataset_items(sciencebase),
    }


def make_sure_path_exists(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise