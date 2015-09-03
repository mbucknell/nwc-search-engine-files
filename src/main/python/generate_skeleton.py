import sys
import datetime
import generation_commons as gc
from jinja2 import Template
import math
import hashlib
import os
from jinja2 import FileSystemLoader
from jinja2.environment import Environment
import codecs

"""
    generate all of the skeleton html files of a particular kind
    theme-data - a list of dictionaries. Each dictionary in the list is written to a different file. Each dictionary in the list should have an 'id' attribute. 
    template_file_name - the String file name of the template
    context - a dict of things to pass to the template
    theme_path - a String appended to context.root_url. Contains trailing slash.
    env - jinja.environment
    destination_dir - String path with trailing slash
"""
def generate_themed_skeletons(theme_data, template_file_name, context, theme_path, env, destination_dir):
    
    template = env.get_template(template_file_name)
    data_length = len(theme_data)
    for index, datum in enumerate(theme_data):
        try:
            datum_url = theme_path + datum['id']
            datum_file_name = os.path.join(destination_dir, hashlib.sha1(datum_url).hexdigest() + ".html")
            print 'saving skeletal representation of {0} to {1} ({2}/{3})'.format(datum_url, datum_file_name, index+1, data_length)
            datum_file = codecs.open(datum_file_name, 'w', 'utf-8')
            merged_context = context.copy()
            merged_context.update(datum)
            datum_file.write(template.render(merged_context))
            datum_file.close()
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise
'''
generate skeletal versions of all pages in the app
  data - a dictionary describing geoserver features and sciencebase items 
  destination_dir - a dir to put the sitemap files into
  rootContext - a dictionary to provide context for the templates
'''
def generate_skeleton(data, destination_dir, context):
    TEMPLATE_BASE_DIR =       os.path.join('templates', 'skeleton')
    WB_HUC_TEMPLATE = 'waterbudget_huc.html'
    SF_HUC_TEMPLATE = 'streamflow_huc.html'
    SF_GAGE_TEMPLATE = 'streamflow_gage.html'
    PROJECT_TEMPLATE = 'project.html'
    DATA_TEMPLATE = 'data.html'
    SKELETON_DIR = 'skeleton'
    skeleton_destination_dir = os.path.join(destination_dir, SKELETON_DIR)
    gc.make_sure_path_exists(skeleton_destination_dir)
    env = Environment(autoescape=True)
    env.loader = FileSystemLoader(TEMPLATE_BASE_DIR)
    
    print 'Creating files in %s'  % skeleton_destination_dir

    generate_themed_skeletons(data['datasets'], DATA_TEMPLATE, context, '#!data-discovery/dataDetail/', env, skeleton_destination_dir)
    generate_themed_skeletons(data['projects'], PROJECT_TEMPLATE, context, '#!data-discovery/projectDetail/', env, skeleton_destination_dir)
    generate_themed_skeletons(data['streamflow_gages'], SF_GAGE_TEMPLATE, context, '#!streamflow-stats/gage/', env, skeleton_destination_dir)
    generate_themed_skeletons(data['streamflow_hucs'], SF_HUC_TEMPLATE, context, '#!streamflow-stats/huc/', env, skeleton_destination_dir)
    generate_themed_skeletons(data['waterbudget_hucs'], WB_HUC_TEMPLATE, context, '#!waterbudget/huc/', env, skeleton_destination_dir)

def main(argv):

    args = gc.parse_args(sys.argv)
    geoserver = args.geoserver
    sciencebase = args.sciencebase_url
    
    
    context = {
               u'root_url' : u'' + args.root_url,
               u'last_modified' : u'' + datetime.datetime.today().isoformat()
               }
    data = {}
    data = gc.get_nwc_data(geoserver, sciencebase)
    generate_skeleton(data, args.destination_dir, context)

if __name__=="__main__":
    main(sys.argv)
    print 'Done'
