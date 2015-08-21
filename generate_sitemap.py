import sys
import argparse
import datetime
import math
from bunch import Bunch
from jinja2 import Template
import requests

def get_features(geoserver_endpoint, layer, attribute):
    response = requests.get(geoserver_endpoint + 'wfs', 
                            {'service' : 'wfs',
                             'version' : '2.0.0',
                             'request' : 'GetFeature',
                             'typeNames' : layer,
                             'propertyName' : attribute,
                             'outputFormat' : 'json'
                             })
    response.raise_for_status()
    my_json = response.json()
    
    return my_json['features']

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
Creates the sitemaps for the ids using template and base_file_name
Return the list of sitemap files created
'''
def create_sitemaps(attributes, template_file_name, dest_dir, base_file_name, base_context):
    SITEMAP_URL_LIMIT = 50000

    template_file = open(template_file_name, 'r')
    template = Template(template_file.read())
    template_file.close()
    
    file_count = math.ceil(len(attributes) / float(SITEMAP_URL_LIMIT))
    index = 1
    file_names = []
    while index <= file_count:
        sitemap_filename = '%s%d.xml' % (base_file_name, index)
        this_file_name = '%s%s' % (dest_dir, sitemap_filename)
        file_names.append(sitemap_filename)
        
        file = open(this_file_name, 'w')
        context = base_context.copy()
        if index == file_count:
            last_index = len(attributes) - 1
        else:
            last_index = index * SITEMAP_URL_LIMIT - 1
        context['attributes'] = attributes[(index - 1) * SITEMAP_URL_LIMIT:last_index]
        file.write(template.render(context))
        file.close()
        
        index = index + 1
    return file_names

'''
parse commandline args and return a dictionary
'''
def parse_args (argv):
    
    DEFAULT_GEOSERVER = 'http://cida.usgs.gov/nwc/geoserver/'
    DEFAULT_SCIENCEBASE = 'https://www.sciencebase.gov/'
    DEFAULT_ROOT_URL = 'http://cida.usgs.gov/nwc/'
    
    parser = argparse.ArgumentParser(description='Generate sitemap.xml for NWC')
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
get waterbudget huc feature information
'''
def get_waterbudget_huc_fetures(geoserver):
    return get_features(geoserver, 'NHDPlusHUCs:nationalwbdsnapshot', 'huc_12')

'''
get streamflow gage ids
'''
def get_streamflow_gage_features(geoserver):
    return get_features(geoserver, 'NWC:gagesII', 'STAID')

'''
get streamflow huc features
'''
def get_streamflow_huc_features(geoserver):
    return get_features(geoserver, 'NWC:huc12_se_basins_v2_local', 'huc12')

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
returns a 'Bunch' of data from the servers
'''
def get_nwc_data(geoserver, sciencebase):
    print 'Retrieving HUCs and gage IDs from %s' % geoserver
    print 'Retrieving projects and dataset ids from %s' % args.sciencebase_url
    return Bunch({
            'waterbudget_hucs' : get_waterbudget_huc_fetures(geoserver),
            'streamflow_gages' : get_streamflow_gage_features(geoserver),
            'streamflow_hucs' : get_streamflow_huc_features(geoserver),
            'projects' : get_project_items(sciencebase),
            'datasets' : get_dataset_items(sciencebase),
    })

'''
generate sitemap.xml and children
  data - a Bunch describing geoserver features and sciencebase items 
  destination_dir - a dir to put the sitemap files into
  rootContext - a dictionary to provide context for the templates
'''
def generate_sitemap(data, destination_dir, root_context):        
    WB_HUC_TEMPLATE = 'sitemap_waterbudget_huc_template.xml'
    SF_HUC_TEMPLATE = 'sitemap_streamflow_huc_template.xml'
    SF_GAGE_TEMPLATE = 'sitemap_streamflow_gage_template.xml'
    PROJECT_TEMPLATE = 'sitemap_project_template.xml'
    DATA_TEMPLATE = 'sitemap_data_template.xml'
    INDEX_TEMPLATE = 'sitemap_index_template.xml'
    
    print 'Creating sitemap files in %s'  % args.destination_dir
    sitemap_files = []
    sitemap_files.extend(create_sitemaps(data.waterbudget_hucs, WB_HUC_TEMPLATE, args.destination_dir, 'sitemap_wb_huc', context))
    sitemap_files.extend(create_sitemaps(data.streamflow_gages, SF_GAGE_TEMPLATE, args.destination_dir, 'sitemap_sf_gage', context))
    sitemap_files.extend(create_sitemaps(data.streamflow_hucs, SF_HUC_TEMPLATE, args.destination_dir, 'sitemap_sf_huc', context))
    sitemap_files.extend(create_sitemaps(data.projects, PROJECT_TEMPLATE, args.destination_dir, 'sitemap_project', context))
    sitemap_files.extend(create_sitemaps(data.datasets, DATA_TEMPLATE, args.destination_dir, 'sitemap_data', context))

    template_index_file = open(INDEX_TEMPLATE, 'r')
    template = Template(template_index_file.read())
    template_index_file.close()
    
    index_context = context.copy()
    index_context['sitemap_files'] = sitemap_files
    sitemap_file = open('%ssitemap.xml' % args.destination_dir, 'w')
        
    sitemap_file.write(template.render(index_context))
    sitemap_file.close()

def generate_root_browse(data, destination_dir, root_context):
    BROWSE_TEMPLATE = 'browse_template.html'
    
    # Create browse.html
    print 'Create browse.html'
    template_browse_file = open(BROWSE_TEMPLATE)
    browse_template = Template(template_browse_file.read())
    template_browse_file.close()
    
    browse_context = root_context.copy()
    browse_context['waterbudget_hucs'] = data.waterbudget_hucs
    browse_context['streamflow_gages'] = data.streamflow_gages
    browse_context['streamflow_hucs'] = data.streamflow_hucs
    browse_context['projects'] = data.projects
    browse_context['datasets'] = data.datasets
    browse_file = open('%sbrowse.html' % destination_dir, 'w')
    browse_file.write(browse_template.render(browse_context))
    browse_file.close()
    return 0
    
if __name__=="__main__":
    

    args = parse_args(sys.argv)
    geoserver = args.geoserver
    sciencebase = args.sciencebase_url
    
    
    context = {
               'root_url' : args.root_url,
               'last_modified' : datetime.datetime.today().strftime("%d/%m/%y")
               }
    data = get_nwc_data(geoserver, sciencebase)

    generate_sitemap(data, args.destination_dir, context)
    generate_root_browse(data, args.destination_dir, context)
    print 'Done'
       
    
