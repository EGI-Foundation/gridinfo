from django.shortcuts import get_object_or_404, render_to_response
from django.views.decorators.cache import cache_page
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.utils import html
import gsutils
# for python 2.6
#import json 
from django.utils import simplejson as json
from django.utils.datastructures import SortedDict
from topology.models import Entity
from topology.models import Entityrelationship
from core.utils import *
import time

@cache_page(60 * 10)
def main(request, type='GRID', value='ALL'):
    sites = sorted([site.uniqueid for site in Entity.objects.filter(type='Site')])
    return render_to_response('single_table.html', 
                              {'summary_active'  : 1,
                               'type'            : type,
                               'value'           : value,
                               'sites'           : sites,
                               'filters_enabled' : True})

@cache_page(60 * 10)
def get_json(request, type='GRID', value='ALL'):
    data = []
    if (value == "ALL"):
        groups = get_groups(type=type)
        topology = {}
        site_list = []
        for group in groups:
            topology[group.uniqueid]=[]
            sites = get_sites(type=type, value=group.uniqueid, groups=[group])
            site_list.extend(sites)       
            for site in sites:
                topology[group.uniqueid].append(site.uniqueid)
    else:
        site_list = get_sites(type, value)
    if (value == "ALL"):
        site_data  = get_installed_capacities(site_list)
        for group in topology.keys():
            group_summary = [group, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            for site_id in topology[group]:
                group_summary[1] += 1
                for i in range(10):
                    group_summary[i + 2] += site_data[site_id][i]
            data.append(group_summary)  
    else:
        site_data = None
        if ( type == 'VO'):
            site_data = get_installed_capacities(site_list, vo_name=value)
        else:
            site_data = get_installed_capacities(site_list)
        status_data = get_status_for_sites(site_list)
        for site_id in site_data.keys():
            row = [site_id, status_data[site_id]]
            row.extend(site_data[site_id])
            data.append(row)

    content = '{"aaData": %s}' % (json.dumps(data))
    return HttpResponse(content, mimetype='application/json')  

@cache_page(60 * 10)
def get_public_json(request):
    # Publicly supported interface
    data = []
    site_list = Entity.objects.filter(type='Site')
    site_data  = get_installed_capacities(site_list, hepspec06=True)
    keys = ["Sitename", "PhyCPU", "LogCPU", "HEPSPEC06", "TotalOnlineStorage", "TotalNearlineStorage"]
    site_ids = sorted(site_data.keys())
    for site_id in site_ids:
        row = []
        row.append(site_id)
        row.append(site_data[site_id][0])
        row.append(site_data[site_id][1])
        row.append(site_data[site_id][2])
        row.append(site_data[site_id][3])
        row.append(site_data[site_id][5])
        data.append( [(key, row[keys.index(key)]) for key in keys] )
    content = json.dumps([SortedDict(item) for item in data])
    return HttpResponse(content, mimetype='application/json')  
