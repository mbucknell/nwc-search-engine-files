import datetime
import os
import sys

import generation_commons as gc
import generate_sitemap
import generate_skeleton

def main(argv):

    args = gc.parse_args(sys.argv)
    data_config_filename = args.data_config
    geoserver = args.geoserver
    sciencebase = args.sciencebase_url
    destination_dir = args.destination_dir
    gc.make_sure_path_exists(destination_dir)

    data_config = gc.get_structured_data_config(data_config_filename)
    
    context = {
               'root_url' : args.root_url,
               'last_modified' : datetime.datetime.now().strftime('%Y-%m-%d')
               }
    data = gc.get_nwc_data(geoserver, sciencebase, data_config)

    generate_sitemap.generate_sitemap(data, os.path.join(destination_dir, 'sitemap'), data_config, context)
    generate_skeleton.generate_skeleton(data, os.path.join(destination_dir, 'skeleton'), data_config, context)
    
if __name__ == "__main__":
    main(sys.argv)
    print 'Done'
