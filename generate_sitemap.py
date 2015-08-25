import sys
import datetime
import generation_commons as gc
from jinja2 import Template
import math

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
generate sitemap.xml and children
  data - a Bunch describing geoserver features and sciencebase items 
  destination_dir - a dir to put the sitemap files into
  rootContext - a dictionary to provide context for the templates
'''
def generate_sitemap(data, destination_dir, context):        
    WB_HUC_TEMPLATE = 'sitemap_waterbudget_huc_template.xml'
    SF_HUC_TEMPLATE = 'sitemap_streamflow_huc_template.xml'
    SF_GAGE_TEMPLATE = 'sitemap_streamflow_gage_template.xml'
    PROJECT_TEMPLATE = 'sitemap_project_template.xml'
    DATA_TEMPLATE = 'sitemap_data_template.xml'
    INDEX_TEMPLATE = 'sitemap_index_template.xml'
    
    print 'Creating sitemap files in %s'  % destination_dir
    sitemap_files = []
    sitemap_files.extend(create_sitemaps(data['waterbudget_hucs'], WB_HUC_TEMPLATE, destination_dir, 'sitemap_wb_huc', context))
    sitemap_files.extend(create_sitemaps(data['streamflow_gages'], SF_GAGE_TEMPLATE, destination_dir, 'sitemap_sf_gage', context))
    sitemap_files.extend(create_sitemaps(data['streamflow_hucs'], SF_HUC_TEMPLATE, destination_dir, 'sitemap_sf_huc', context))
    sitemap_files.extend(create_sitemaps(data['projects'], PROJECT_TEMPLATE, destination_dir, 'sitemap_project', context))
    sitemap_files.extend(create_sitemaps(data['datasets'], DATA_TEMPLATE, destination_dir, 'sitemap_data', context))

    template_index_file = open(INDEX_TEMPLATE, 'r')
    template = Template(template_index_file.read())
    template_index_file.close()
    
    index_context = context.copy()
    index_context['sitemap_files'] = sitemap_files
    sitemap_file = open('%ssitemap.xml' % destination_dir, 'w')
        
    sitemap_file.write(template.render(index_context))
    sitemap_file.close()


def main(argv):

    args = gc.parse_args(sys.argv)
    geoserver = args.geoserver
    sciencebase = args.sciencebase_url
    
    
    context = {
               'root_url' : args.root_url,
               'last_modified' : datetime.datetime.today().isoformat()
               }
    data = gc.get_nwc_data(geoserver, sciencebase)

    generate_sitemap(data, args.destination_dir, context)

if __name__=="__main__":
    main(sys.argv)
    print 'Done'
