import argparse

import jsontemplate
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

if __name__=="__main__":
    
    parser = argparse.ArgumentParser(description='Generate sitemap.xml for NWC')
    parser.add_argument('--geoserver', help='Geoserver to use to retrieve HUCs and gages', 
                        default='http://cida.usgs.gov/nwc/geoserver/')
    args = parser.parse_args()
    
    template = open('sitemap.template', 'r');
    sitemap_file = open('sitemap.xml', 'w');
    
    print 'Retrieving HUCs and gage IDs from %s' % args.geoserver
    
    waterbudget_hucs = get_feature(args.geoserver, 'NHDPlusHUCs:nationalwbdsnapshot', 'huc_12')    
    streamflow_gage_ids = get_feature(args.geoserver, 'NWC:gagesII', 'STAID')
    streamflow_hucs = get_feature(args.geoserver, 'NWC:huc12_se_basins_v2_local', 'huc12')
    
    context = {
               'waterbudget_hucs' : waterbudget_hucs,
               'streamflow_gage_ids' : streamflow_gage_ids,
               'streamflow_hucs' : streamflow_hucs
               }

    sitemap_file.write(jsontemplate.expand(template.read(), context))
    
    template.close()
    sitemap_file.close()