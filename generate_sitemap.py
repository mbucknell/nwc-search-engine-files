import argparse
import datetime
import math

from jinja2 import Template
import requests

def get_feature(geoserver_endpoint, layer, attribute):
    response = requests.get(geoserver_endpoint + 'wfs', 
                            {'service' : 'wfs',
                             'version' : '2.0.0',
                             'request' : 'GetFeature',
                             'typeNames' : layer,
                             'propertyName' : attribute,
                             'outputFormat' : 'json'
                             })
    response.raise_for_status()
    return response.json()

def get_sciencebase_data(sciencebase_endpoint, browse_category):
    response = requests.get(sciencebase_endpoint + 'catalog/items',
                            {'facetTermLevelLimit' : 'false',
                             'q' : '',
                             'community' : 'National Water Census',
                             'filter0' : 'browseCategory=' + browse_category,
                             'format' : 'json'
                             })
    response.raise_for_status()
    return response.json()

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
    

if __name__=="__main__":
    
    WB_HUC_TEMPLATE = 'sitemap_waterbudget_huc_template.xml'
    SF_HUC_TEMPLATE = 'sitemap_streamflow_huc_template.xml'
    SF_GAGE_TEMPLATE = 'sitemap_streamflow_gage_template.xml'
    PROJECT_TEMPLATE = 'sitemap_project_template.xml'
    DATA_TEMPLATE = 'sitemap_data_template.xml'
    INDEX_TEMPLATE = 'sitemap_index_template.xml'
    
    parser = argparse.ArgumentParser(description='Generate sitemap.xml for NWC')
    parser.add_argument('--geoserver', 
                        help='Geoserver to use to retrieve HUCs and gages. Defaults to http://cida.usgs.gov/nwc/geoserver/', 
                        default='http://cida.usgs.gov/nwc/geoserver/')
    parser.add_argument('--sciencebase_url', 
                        help='URL where the data discovery tool gets its project information. Defaults to https://www.sciencebase.gov/',
                        default='https://www.sciencebase.gov/')
    parser.add_argument('--root_url', 
                        help='The application\'s root url. Defaults to http://cida.usgs.gov/nwc/',
                        default='http://cida.usgs.gov/nwc/')
    parser.add_argument('--destination_dir', 
                        help='Destination directory for the sitemap.xml file. Defaults to the directory where the script is run.',
                        default='')
    args = parser.parse_args()
    
    sitemap_files = []
    
    context = {'root_url' : args.root_url,
               'last_modified' : datetime.date.today().isoformat()}
    
    print 'Retrieving HUCs and gage IDs from %s' % args.geoserver
    
    waterbudget_hucs = get_feature(args.geoserver, 'NHDPlusHUCs:nationalwbdsnapshot', 'huc_12')['features']    
    streamflow_gage_ids = get_feature(args.geoserver, 'NWC:gagesII', 'STAID')['features']
    streamflow_hucs = get_feature(args.geoserver, 'NWC:huc12_se_basins_v2_local', 'huc12')['features']
    
    print 'Retrieving projects and dataset ids from %s' % args.sciencebase_url 
            
    projects = get_sciencebase_data(args.sciencebase_url, 'Project')['items']
    datasets = get_sciencebase_data(args.sciencebase_url, 'Data')['items']
    
    print 'Creating sitemap files in %s'  % args.destination_dir
    
    sitemap_files.extend(create_sitemaps(waterbudget_hucs, WB_HUC_TEMPLATE, args.destination_dir, 'sitemap_wb_huc', context))
    sitemap_files.extend(create_sitemaps(streamflow_gage_ids, SF_GAGE_TEMPLATE, args.destination_dir, 'sitemap_sf_gage', context))
    sitemap_files.extend(create_sitemaps(streamflow_hucs, SF_HUC_TEMPLATE, args.destination_dir, 'sitemap_sf_huc', context))
    sitemap_files.extend(create_sitemaps(projects, PROJECT_TEMPLATE, args.destination_dir, 'sitemap_project', context))
    sitemap_files.extend(create_sitemaps(datasets, DATA_TEMPLATE, args.destination_dir, 'sitemap_data', context))
    
    template_index_file = open(INDEX_TEMPLATE, 'r')
    template = Template(template_index_file.read())
    template_index_file.close()
    
    context['sitemap_files'] = sitemap_files
    sitemap_file = open('%ssitemap.xml' % args.destination_dir, 'w')
        
    sitemap_file.write(template.render(context))
    sitemap_file.close()