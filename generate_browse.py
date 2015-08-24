import sys
import datetime
import generation_commons as gc
from jinja2 import Template

def generate_root_browse(data, destination_dir, root_context):
    BROWSE_TEMPLATE = 'browse_template.html'
    
    # Create browse.html
    print 'Create browse.html'
    template_browse_file = open(BROWSE_TEMPLATE)
    browse_template = Template(template_browse_file.read())
    template_browse_file.close()
    
    browse_context = root_context.copy()
    browse_context['waterbudget_hucs'] = data['waterbudget_hucs']
    browse_context['streamflow_gages'] = data['streamflow_gages']
    browse_context['streamflow_hucs'] = data['streamflow_hucs']
    browse_context['projects'] = data['projects']
    browse_context['datasets'] = data['datasets']
    browse_file = open('%sbrowse.html' % destination_dir, 'w')
    browse_file.write(browse_template.render(browse_context))
    browse_file.close()
    return 0

def main(argv):

    args = gc.parse_args(sys.argv)
    geoserver = args.geoserver
    sciencebase = args.sciencebase_url
    
    
    context = {
               'root_url' : args.root_url,
               'last_modified' : datetime.datetime.today().isoformat()
               }
    data = gc.get_nwc_data(geoserver, sciencebase)

    generate_root_browse(data, args.destination_dir, context)

if __name__=="__main__":
    main(sys.argv)
    print 'Done'   
    