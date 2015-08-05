import argparse

if __name__=="__main__":
    
    parser = argparse.ArgumentParser(description='Generate sitemap.xml for NWC')
    parser.add_argument('--geoserver', help='Geoserver to use to retrieve HUCs and gages', 
                        default='http://cida.usgs.gov/nwc/geoserver/')
    args = parser.parse_args()
    
    print 'Retrieving HUCs and gage IDs from %s' % args.geoserver