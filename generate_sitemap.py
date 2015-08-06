import argparse

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


if __name__=="__main__":
    
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
    
    template_file = open('sitemap_template.xml', 'r');
    sitemap_file = open('%ssitemap.xml' % args.destination_dir, 'w');
    
    context = {'root_url' : args.root_url}
    
    print 'Retrieving HUCs and gage IDs from %s' % args.geoserver
    
    context['waterbudget_hucs'] = get_feature(args.geoserver, 'NHDPlusHUCs:nationalwbdsnapshot', 'huc_12')    
    context['streamflow_gage_ids'] = get_feature(args.geoserver, 'NWC:gagesII', 'STAID')
    context['streamflow_hucs'] = get_feature(args.geoserver, 'NWC:huc12_se_basins_v2_local', 'huc12')
    
    print 'Retrieving projects and dataset ids from %s' % args.sciencebase_url 
            
    context['projects'] = get_sciencebase_data(args.sciencebase_url, 'Project')['items']
    context['datasets'] = get_sciencebase_data(args.sciencebase_url, 'Data')['items']
    
    print 'Creating sitemap file at %s' % sitemap_file.name
    
    template = Template(template_file.read())
    sitemap_file.write(template.render(context))
    
    template_file.close()
    sitemap_file.close()