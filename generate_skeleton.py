import sys
import datetime
import generation_commons as gc
from jinja2 import Template
import math
import hashlib
import os
from jinja2 import FileSystemLoader
from jinja2.environment import Environment


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
    
    for datum in theme_data:
        datum_url = context['root_url'] + theme_path + datum['id']
        datum_file_name = os.path.join(destination_dir, hashlib.sha1(datum_url).hexdigest() + ".html")
        print 'saving skeletal representation of {0} to {1}'.format(datum_url, datum_file_name)
        datum_file = open(datum_file_name, 'w')
        merged_context = context.copy()
        merged_context.update(datum)
        datum_file.write(template.render(merged_context))
        datum_file.close()
'''
generate skeletal versions of all pages in the app
  data - a Bunch describing geoserver features and sciencebase items 
  destination_dir - a dir to put the sitemap files into
  rootContext - a dictionary to provide context for the templates
'''
def generate_skeleton(data, destination_dir, context):
    BASE_DIR =       'templates/skeleton/'
    WB_HUC_TEMPLATE = 'waterbudget_huc.html'
    SF_HUC_TEMPLATE = 'streamflow_huc.html'
    SF_GAGE_TEMPLATE = 'streamflow_gage.html'
    PROJECT_TEMPLATE = 'project.html'
    DATA_TEMPLATE = 'data.html'
    INDEX_TEMPLATE = 'index.html'
    
    env = Environment()
    env.loader = FileSystemLoader(BASE_DIR)
    
    print 'Creating files in %s'  % destination_dir
    
    #generate_themed_skeletons(data['datasets'], DATA_TEMPLATE, context, '#!data-discovery/dataDetail/', env, destination_dir)
    generate_themed_skeletons(data['projects'], PROJECT_TEMPLATE, context, '#!data-discovery/projectDetail/', env, destination_dir)
#     sitemap_files = []
#     sitemap_files.extend(create_sitemaps(data['waterbudget_hucs'], WB_HUC_TEMPLATE, destination_dir, 'sitemap_wb_huc', context))
#     sitemap_files.extend(create_sitemaps(data['streamflow_gages'], SF_GAGE_TEMPLATE, destination_dir, 'sitemap_sf_gage', context))
#     sitemap_files.extend(create_sitemaps(data['streamflow_hucs'], SF_HUC_TEMPLATE, destination_dir, 'sitemap_sf_huc', context))
#     sitemap_files.extend(create_sitemaps(data['projects'], PROJECT_TEMPLATE, destination_dir, 'sitemap_project', context))
#     sitemap_files.extend(create_sitemaps(data['datasets'], DATA_TEMPLATE, destination_dir, 'sitemap_data', context))

def main(argv):

    args = gc.parse_args(sys.argv)
    geoserver = args.geoserver
    sciencebase = args.sciencebase_url
    
    
    context = {
               'root_url' : args.root_url,
               'last_modified' : datetime.datetime.today().isoformat()
               }
    data = {}
#     data = gc.get_nwc_data(geoserver, sciencebase)

    data['projects'] = gc.get_project_items(sciencebase)
    generate_skeleton(data, args.destination_dir, context)

if __name__=="__main__":
    main(sys.argv)
    print 'Done'
