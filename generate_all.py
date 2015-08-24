import sys
import datetime
import generation_commons as gc
import generate_sitemap
import generate_browse
from jinja2 import Template

def main(argv):

    args = gc.parse_args(sys.argv)
    geoserver = args.geoserver
    sciencebase = args.sciencebase_url
    
    
    context = {
               'root_url' : args.root_url,
               'last_modified' : datetime.datetime.today().isoformat()
               }
    data = gc.get_nwc_data(geoserver, sciencebase)

    generate_browse.generate_root_browse(data, args.destination_dir, context)
    generate_sitemap.generate_sitemap(data, args.destination_dir, context)
    
if __name__=="__main__":
    main(sys.argv)
    print 'Done'   
    
