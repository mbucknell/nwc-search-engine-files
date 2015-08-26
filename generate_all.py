import sys
import datetime
import generation_commons as gc
import generate_sitemap
import generate_browse
import generate_skeleton
import os
import errno

def make_sure_path_exists(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

def main(argv):

    args = gc.parse_args(sys.argv)
    geoserver = args.geoserver
    sciencebase = args.sciencebase_url
    destination_dir = args.destination_dir
    make_sure_path_exists(destination_dir)
    
    context = {
               'root_url' : args.root_url,
               'last_modified' : datetime.datetime.today().isoformat()
               }
    data = gc.get_nwc_data(geoserver, sciencebase)

    generate_browse.generate_root_browse(data, destination_dir, context)
    generate_sitemap.generate_sitemap(data, destination_dir, context)
    generate_skeleton.generate_skeleton(data, destination_dir, context)
    
if __name__=="__main__":
    main(sys.argv)
    print 'Done'   
    
