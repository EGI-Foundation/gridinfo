from django.shortcuts import get_object_or_404, render_to_response
from django.views.decorators.cache import cache_page
from django.http import HttpResponse, Http404
from django.core.urlresolvers import reverse
from django.utils import html
from glue.models import glueservice,gluece, gluevoview
from topology.models import Entity
from core.utils import *
import gsutils
import socket
import re
import time
from datetime import datetime
   
@cache_page(60 * 10)   
def overview(request, site_name):     
    sites = sorted([site.uniqueid for site in Entity.objects.filter(type='Site')])
    # Get the site information from glue database
    gluesite = get_unique_gluesite(site_name)
    if not gluesite:
        gluesite = "N/A"

    # Get all the service and entity at site from topology database
    site_entity = get_unique_entity(site_name, 'Site')
    service_list = get_services([site_entity])
    topbdii_list, sitebdii_list, cluster_list, se_list  = [], [], [], []
    for service in service_list:
        if   service.type == 'bdii_top':  topbdii_list.append(service)
        elif service.type == 'bdii_site': sitebdii_list.append(service)
        elif service.type == 'CE':        cluster_list.append(service)
        elif service.type == 'SE':        se_list.append(service)

    # Get the overall monitoring and validation results
    nagios_status = get_nagios_status_dict()
    status_list_top = []
    hostnames = [topbdii.hostname for topbdii in topbdii_list]
    for hostname in hostnames:
        hosts_from_alias = get_hosts_from_alias(hostname)
        for host in hosts_from_alias:
            dict = {}
            dict['alias']    = hostname
            dict['host']     = host
            dict['instance'] = len(hosts_from_alias)
            if host in nagios_status.keys():
                (status, has_been_checked) = get_overall_check_status(nagios_status[host])
                dict['status']   = get_nagios_status_str(status, has_been_checked)
            else:
                dict['status']   = "N/A"
            status_list_top.append(dict)
            
    status_list_site = []
    hostnames = [sitebdii.hostname for sitebdii in sitebdii_list]
    for hostname in hostnames:
        hosts_from_alias = get_hosts_from_alias(hostname)
        for host in hosts_from_alias:
            dict = {}
            dict['alias']    = hostname
            dict['host']     = host
            dict['instance'] = len(hosts_from_alias)
            if host in nagios_status.keys():
                (status, has_been_checked) = get_overall_check_status(nagios_status[host])
                dict['status']   = get_nagios_status_str(status, has_been_checked)
            else:
                dict['status']   = "N/A"
            status_list_site.append(dict)
                
    # Count the numbers of entities
    count_dict            = {}
    count_dict['ce']      = len(cluster_list)
    count_dict['se']      = len(se_list)
    count_dict['service'] = len(service_list)

    # Calculate how many minutes ago the information is updated
    last_update = 0
    if site_entity:
        last_update = time.mktime(site_entity.updated_at.timetuple())
    
    # Calculate the CPU numbers through all SubCluster
    installed_capacity = {}
    sub_cluster_list = get_gluesubclusters(service_list)
    physical_cpu, logical_cpu, si2000 = "N/A", "N/A", "N/A"
    if sub_cluster_list:
        physical_cpu, logical_cpu = get_installed_capacity_cpu(sub_cluster_list)
        si2000 = get_installed_capacity_si2000(sub_cluster_list)
    installed_capacity['physicalcpus'] = physical_cpu
    installed_capacity['logicalcpus']  = logical_cpu
    installed_capacity['si2000']       = si2000
    
    # Calculate the storage space through all SE
    se_list = get_glueses(service_list)
    totalonlinesize, usedonlinesize, totalnearlinesize, usednearlinesize = "N/A", "N/A", "N/A", "N/A"
    if se_list:
        totalonlinesize, usedonlinesize, totalnearlinesize, usednearlinesize = get_installed_capacity_storage(se_list)
    installed_capacity['totalonlinesize']   = totalonlinesize
    installed_capacity['usedonlinesize']    = usedonlinesize
    installed_capacity['totalnearlinesize'] = totalnearlinesize
    installed_capacity['usednearlinesize']  = usednearlinesize        
    
    # Calculate the jobs numbers through all VOView
    resource_dict = {}
    attributes = ["totaljobs", "runningjobs", "waitingjobs"]
    voview_list = get_gluevoviews(service_list)
    vo_to_voview_mapping = get_vo_to_voview_mapping(voview_list)
    for voview in voview_list:
        try:
            voname = vo_to_voview_mapping[voview.glueceuniqueid][voview.localid]
        except KeyError, e:
            continue
        stats = get_voview_job_stats([voview])   
        if voname not in resource_dict.keys():
            resource_dict[voname] = {}
            resource_dict[voname]['voname'] = voname
            for attr in attributes:
                resource_dict[voname][attr] = 0
        for attr in attributes:
            resource_dict[voname][attr] += stats[attributes.index(attr)]                 
    
    # Calculate the VO-shared storage space through all SA
    attributes = ["totalonlinesize", "usedonlinesize", "totalnearlinesize", "usednearlinesize"]
    sa_list = get_gluesas(service_list)
    vo_to_sa_mapping = get_vo_to_sa_mapping(sa_list)
    for sa in sa_list:
        try:
            voname_list = vo_to_sa_mapping[sa.gluese_fk][sa.localid]
        except KeyError, e:
            continue
        stats = get_sa_storage_stats([sa])
        
        for voname in voname_list:
            if voname not in resource_dict.keys():
                resource_dict[voname] = {}
                resource_dict[voname]['voname'] = voname
                for attr in attributes:
                    resource_dict[voname][attr] = 0
            elif attributes[0] not in resource_dict[voname].keys():
                for attr in attributes:
                    resource_dict[voname][attr] = 0
            for attr in attributes:
                resource_dict[voname][attr] += stats[attributes.index(attr)]     
    
    vo_resources = []
    for voname in resource_dict.keys():
        vo_resources.append(resource_dict[voname])
    
    # sorting list of dictionaries
    sort_on = "voname"
    sorted_list = [(dict_[sort_on], dict_) for dict_ in vo_resources]
    sorted_list.sort()
    vo_resources = [dict_ for (key, dict_) in sorted_list]
    
    return render_to_response('overview.html', 
                              {'sites'              : sites,
                               'site_name'          : site_name,
                               'gluesite'           : gluesite,
                               'status_list_top'    : status_list_top,
                               'status_list_site'   : status_list_site,
                               'count_dict'         : count_dict,
                               'last_update'        : last_update,
                               'installed_capacity' : installed_capacity,
                               'vo_resources'       : vo_resources,
                               'summary_active'     : 1})

@cache_page(60 * 10)
def status(request, site_name, type_name, host_name, check_name):
    site_entity = get_unique_entity(site_name, 'Site')
    
    # Get testing results from TOP BDII    
    nagios_status = get_nagios_status_dict()   
    
    status_list = []
    if host_name == 'all':
        # all checks of all BDIIs
        hostname_list = [ bdii.hostname for bdii in get_services([site_entity], type_name) ]
        hostname_list_all = get_hosts_from_aliases(hostname_list)  
        for hostname in hostname_list_all:
            for check in get_check_list(nagios_status, hostname):
                status_list.append( get_nagios_status(nagios_status, check, hostname) )
    else:
        if check_name == 'all':
            # all checks of single BDII (probably multiple instances)
            hostname_list_all = get_hosts_from_alias(host_name)
            for hostname in hostname_list_all:
                for check in get_check_list(nagios_status, hostname):
                    status_list.append( get_nagios_status(nagios_status, check, hostname) )
        else:
            # single check of single BDII (probably multiple instances)
            hostname_list_all = get_hosts_from_alias(host_name)
            for hostname in hostname_list_all:
                status_list.append( get_nagios_status(nagios_status, check_name, hostname) )
    
    if status_list:
        # Sort status list
        unsorted_list = status_list
        sorted_list = [(dict['hostname'], dict) for dict in unsorted_list]
        sorted_list.sort()
        result_list = [dict for (hostname, dict) in sorted_list]
        status_list = result_list   
    else:
        status_list.append({'hostname': 'N/A',
                            'check': 'N/A',
                            'current_state': 'N/A',
                            'plugin_output': 'N/A',
                            'long_plugin_output': '',
                            'last_check': 'N/A'})

    return render_to_response('status.html', {'status_list' : status_list})

@cache_page(60 * 10)
def treeview(request, site_name, type="", attribute=""):
    sites = sorted([site.uniqueid for site in Entity.objects.filter(type='Site')])
    
    site = get_unique_gluesite(site_name)
    
    # Get service list from topology database
    site_entity = get_unique_entity(site_name, 'Site')
    service_list = get_services([site_entity])
    topbdii_list, sitebdii_list, cluster_list, se_list, others_list  = [], [], [], [], []
    for service in service_list:
        if   service.type == 'bdii_top':  topbdii_list.append(service)
        elif service.type == 'bdii_site': sitebdii_list.append(service)
        elif service.type == 'CE':        cluster_list.append(service)
        elif service.type == 'SE':        se_list.append(service)
        else:                             others_list.append(service)

    # decide expanded tree node
    collapse = {}
    # type: bdii_top, bdii_site, subcluster_cpu, se_online, se_nearline, vo_job, vo_online, vo_nearline
    collapse[type] = "open"

    # Get subtree of TOP BDIIs and associated Nagios check names for testing results
    # ("top bdii hostname", ("check list"))
    nagios_status = get_nagios_status_dict()   
    
    tree_topbdii = []
    if topbdii_list:
        hostnames_topbdii = [topbdii.hostname for topbdii in topbdii_list]
        hostnames_all_topbdii = get_hosts_from_aliases(hostnames_topbdii)        
        for hostname in hostnames_all_topbdii:
            tree_topbdii.append( ( hostname, tuple(get_check_list(nagios_status, hostname)) ) )
        # decide expanded tree node
        if type == "bdii_top":
            hostnames_expand = get_hosts_from_alias(attribute)
            for hostname_expand in hostnames_expand:
                collapse[hostname_expand] = "open"
        
    # Get subtree of Site BDIIs and associated Nagios check names for testing results
    # ("site bdii hostname", ("check list"))
    tree_sitebdii = []
    if sitebdii_list:
        hostnames_sitebdii = [sitebdii.hostname for sitebdii in sitebdii_list]
        hostnames_all_sitebdii = get_hosts_from_aliases(hostnames_sitebdii)   
        for hostname in hostnames_all_sitebdii:
            tree_sitebdii.append( ( hostname, tuple(get_check_list(nagios_status, hostname)) ) )
        # decide expanded tree node
        if type == "bdii_site":
            hostnames_expand = get_hosts_from_alias(attribute)
            for hostname_expand in hostnames_expand:
                collapse[hostname_expand] = "open"

    #print "Starting Mapping...."
    #start_time = time.time()
    
    # Get GlueVOView entity mapping information
    ces = gluece.objects.filter(gluecluster_fk__in = [cluster.uniqueid for cluster in cluster_list])
    voviews = gluevoview.objects.filter(gluece_fk__in = [ce.uniqueid for ce in ces])
    vo_voview_mapping = get_vo_to_voview_mapping(voviews)

    cluster_ce_mapping = {}
    for ce in ces:
        if ce.gluecluster_fk not in cluster_ce_mapping:
            cluster_ce_mapping[ce.gluecluster_fk] = []
        cluster_ce_mapping[ce.gluecluster_fk].append(ce.uniqueid)
    
    ce_voview_mapping = {}
    for voview in voviews:
        if voview.gluece_fk not in ce_voview_mapping:
            ce_voview_mapping[voview.gluece_fk] = []
        if voview.localid not in ce_voview_mapping[voview.gluece_fk]:
            ce_voview_mapping[voview.gluece_fk].append(voview.localid)
    
    cluster_vo_mapping = {}
    for cluster in cluster_list:
        if cluster.uniqueid in cluster_ce_mapping:
            for ce_uniqueid in cluster_ce_mapping[cluster.uniqueid]:
                if ce_uniqueid in ce_voview_mapping:
                    for voview_localid in ce_voview_mapping[ce_uniqueid]:
                        if cluster.uniqueid not in cluster_vo_mapping:
                            cluster_vo_mapping[cluster.uniqueid] = {}
                        try:
                            cluster_vo_mapping[cluster.uniqueid][ vo_voview_mapping[ce_uniqueid][voview_localid] ] = [ce_uniqueid, voview_localid]
                        except KeyError: continue 
    
    # Get GlueSA entity mapping information
    sas = gluesa.objects.filter(gluese_fk__in = [se.uniqueid for se in se_list])
    vo_sa_mapping = get_vo_to_sa_mapping(sas)
    
    se_sa_mapping = {}
    for sa in sas:
        if sa.gluese_fk not in se_sa_mapping:
            se_sa_mapping[sa.gluese_fk] = []
        if sa.localid not in se_sa_mapping[sa.gluese_fk]:
            se_sa_mapping[sa.gluese_fk].append(sa.localid)
        
    se_vo_mapping = {}
    for se in se_list:
        if se.uniqueid in se_sa_mapping:
            for sa_localid in se_sa_mapping[se.uniqueid]:
                if se.uniqueid not in se_vo_mapping:
                    se_vo_mapping[se.uniqueid] = {}
                try:
                    #se_vo_mapping[se.uniqueid][ vo_sa_mapping[se.uniqueid][sa_localid] ] = sa_localid
                    voname_list = vo_sa_mapping[se.uniqueid][sa_localid]
                    for voname in voname_list:
                        if voname not in se_vo_mapping[se.uniqueid]:
                            se_vo_mapping[se.uniqueid][voname] = []
                        se_vo_mapping[se.uniqueid][voname].append(sa_localid)
                except KeyError: continue

    #print "Time taken = %d" %(time.time() - start_time)

    # Get subtree of Clusters and associated SubClusters for static cpu numbers
    # ("cluster hostname", ("subcluster list"))
    tree_cluster_cpu = []
    if cluster_list:
        for cluster in cluster_list:
            tree_cluster_cpu.append( ( cluster.hostname, tuple(sorted(subcluster.uniqueid for subcluster in get_gluesubclusters([cluster]))) ) )
    tree_cluster_cpu.sort()
    
    # Gather information of VOs
    dict_vo = {}
    
    # Get subtree of Clusters and supported VOs for job numbers
    # ("cluster hostname", ("vo list"))
    tree_cluster_job = []
    if cluster_list:
        for cluster in cluster_list:
            if cluster.uniqueid in cluster_vo_mapping:
                vos = cluster_vo_mapping[cluster.uniqueid].keys()
                vos.sort()
                vo_ce_list = []
                for vo in vos:
                    vo_ce_list.append( (vo, cluster_vo_mapping[cluster.uniqueid][vo][0], cluster_vo_mapping[cluster.uniqueid][vo][1]) )
                tree_cluster_job.append( (cluster.hostname, tuple(vo_ce_list) ) )
            
                # Gather information of VOs
                for vo in vos:
                    try:
                        dict_vo[vo][0].append( (cluster.hostname, cluster_vo_mapping[cluster.uniqueid][vo][0], cluster_vo_mapping[cluster.uniqueid][vo][1]) )
                    except:
                        dict_vo[vo] = [[ (cluster.hostname, cluster_vo_mapping[cluster.uniqueid][vo][0], cluster_vo_mapping[cluster.uniqueid][vo][1]) ], []]
        tree_cluster_job.sort()
        
    # Get subtree of SEs and supported VOs for static and shared storage space
    # ("se hostname", ("vo list"))
    tree_se = []
    if se_list:
        for se in se_list:
            if se.uniqueid in se_vo_mapping:
                vos = se_vo_mapping[se.uniqueid].keys()
                vos.sort()
                vo_sa_list = []
                for vo in vos:
                    vo_sa_list.append( (vo, se_vo_mapping[se.uniqueid][vo]) )
                tree_se.append( (se.hostname, tuple(vo_sa_list)) )
                
                # Gather information of VOs
                for vo in vos:
                    try:
                        dict_vo[vo][1].append( (se.hostname, se_vo_mapping[se.uniqueid][vo]) )
                    except:
                        dict_vo[vo] = [[], [ (se.hostname, se_vo_mapping[se.uniqueid][vo]) ]]
        tree_se.sort()
            
    # Get subtree of service type and associated Services
    # ("service type", ("service list"))
    tree_service = []
    dict_service = {}
    if others_list:
        for service in others_list:
            try:
                dict_service[service.type].append(service.uniqueid)
            except:
                dict_service[service.type] = [service.uniqueid]
    keys = dict_service.keys()
    keys.sort()
    for key in keys:
        tree_service.append( (key, tuple(sorted(dict_service[key]))) )
    
    # Get subtree of VO and shared resource
    # ("vo", ("cluster list"), ("se list"))
    tree_vo = []
    keys = dict_vo.keys()
    keys.sort()
    for key in keys:
        #tree_vo.append( [key, [ dict_vo[key][0].sort(), dict_vo[key][1].sort() ]] )
        tree_vo.append( ( key, tuple(sorted(dict_vo[key][0])), tuple(sorted(dict_vo[key][1])) ) )
    
    # decide expanded tree node
    if type.startswith("vo_"):
        collapse[attribute] = "open"
        
    # decide the default viewing content in iframe of treeview page
    url = ""
    if type == "bdii_top":
        # e.g. /gstat/site/CERN-PROD/bdii_top/bdii118.cern.ch/all/
        url = "/".join(["", "gstat", "site", site_name, type, attribute, "all"])
    elif type == "bdii_site":
        # e.g. /gstat/site/CERN-PROD/bdii_site/bdii116.cern.ch/all/
        url = "/".join(["", "gstat", "site", site_name, type, attribute, "all"])
    elif type == "subcluster_cpu":
        # e.g. /gstat/rrd/Site/CERN-PROD/cpu/
        url = "/".join(["", "gstat", "rrd", "Site", site_name, "cpu"])
    elif type == "se_online":
        # e.g. /gstat/rrd/Site/CERN-PROD/online/
        url = "/".join(["", "gstat", "rrd", "Site", site_name, "online"])
    elif type == "se_nearline":
        # e.g. /gstat/rrd/Site/CERN-PROD/nearline/
        url = "/".join(["", "gstat", "rrd", "Site", site_name, "nearline"])
    elif type == "vo_job":
        # e.g. /gstat/rrd/VOSite/CERN-PROD/alice/job/
        url = "/".join(["", "gstat", "rrd", "VOSite", site_name, attribute, "job"])
    elif type == "vo_online":
        # e.g. /gstat/rrd/VOSite/CERN-PROD/alice/online/
        url = "/".join(["", "gstat", "rrd", "VOSite", site_name, attribute, "online"])
    elif type == "vo_nearline":
        # e.g. /gstat/rrd/VOSite/CERN-PROD/alice/nearline/
        url = "/".join(["", "gstat", "rrd", "VOSite", site_name, attribute, "nearline"])

    return render_to_response('treeview_site.html', 
                              {'sites':            sites,
                               'site_name':        site_name,
                               'collapse':         collapse,
                               'tree_topbdii':     tree_topbdii,
                               'tree_sitebdii':    tree_sitebdii,
                               'tree_cluster_cpu': tree_cluster_cpu,
                               'tree_cluster_job': tree_cluster_job,
                               'tree_se':          tree_se,
                               'tree_service':     tree_service,
                               'tree_vo':          tree_vo,
                               'url':              url,
                               'summary_active':   1})