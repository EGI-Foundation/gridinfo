#!/usr/bin/env python
##############################################################################
# Copyright (c) Members of the EGEE Collaboration. 2004.
# See http://www.eu-egee.org/partners/ for details on the copyright
# holders.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at #
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS
# OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
##############################################################################
# P.J. Harvey
# jhebus@gmail.com

import os
import re
import sys
import time
import getopt
import socket
import signal
import string
import logging
import tempfile

#for the messaging
import stomp


#-------------------------------------------------------------------------------
#location of the broker server, static for the moment (my laptop)
#also the topic
HOST='vtb-generic-26.cern.ch'
PORT=6163
HEADERS={}
ADDITION='/topic/addition/'
DELETION='/topic/deletion/'
MODIFICATION='/topic/modification/'




N=0
#Assuming that there will not be more that 100 fragments per message.....
MAX_PACKETS = 100
PACKET_ARRAY = ["" for col in range(MAX_PACKETS)]
HANDELING_FRAGMENTED_PACKET=1
#-------------------------------------------------------------------------------
#the callback functions 
class MyListener(object):

    def on_connecting(self, host_and_port):
        log.info("connecting...")
        #self.c.connect(wait=True)

    def on_disconnected(self):
        log.info("lost connection")

    """
    Incoming message:
    This contains the glue schema update(add, delete, modify) from a lower level
    process_message will basically compare this to the existing message and
    update the db with the necessary info (additions, deletions, modifications)
    """
    def on_message(self, headers, body):
        #self.__print_async("MESSAGE:consumer", headers, body)
        log.debug("now process the message")


        #process_message(config, log, body)

        
        #just now, providers only get sync messages
        if('destination' in headers):
             if(headers['destination'] == "/topic/sync/"):

		 start = time.time()
                 log.debug ("SYNC REQUEST FOR : %s"%(body))

		 """
                 #collect the ldif
                 
                 pipe=os.popen("/opt/glite/etc/gip/provider/glite-info-provider-site")
                 raw_ldif = pipe.read()
                 pipe.close()

                 pipe=os.popen("/opt/glite/etc/gip/provider/glite-info-provider-service-bdii-site")
                 raw_ldif += pipe.read()
                 pipe.close()

                 pipe=os.popen("/opt/glite/etc/gip/provider/glite-info-provider-site-entry")
                 raw_ldif += pipe.read()
                 pipe.close()


                 #split it and send it back
                 log.debug("There are %i messages"%(len(raw_ldif.split("\n\n"))))
                 num = len(raw_ldif.split("\n\n"))
                 for msg in raw_ldif.split("\n\n"):
                     #print(msg)
                     log.debug("**********" + str(num))
                     conn.send(socket.gethostname() + "\n" + str(num) + "\n\n" + msg,destination=body, ack='auto')
                     num -= 1

		 """
		 
		 #In order to save time, we simply send our name to who requested it
		 #and get them to do an ldap search of us
		 
		 """
		 INPORTANT TODO!!!
		 
		 This should send the current sequence number!!
		 
		 This will allow the consumer to only store/apply messages AFTER this seqnumber,
		 and throw away the rest
		 """
		 conn.send(socket.gethostname() + "\n1\n\n",destination=body, ack='auto')
		 
		 stop = time.time()
		 log.info("The sync request took %f"%(stop-start))
                 sys.stdout.flush()
        

    def on_error(self, headers, body):
        self.__print_async("ERROR", headers, body)

    def on_receipt(self, headers, body):
        self.__print_async("RECEIPT", headers, body)

    def on_connected(self, headers, body):
        self.__print_async("CONNECTED to broker" , headers, body)

    def __print_async(self, frame_type, headers, body):
        log.info("\r  \r")
        log.info(frame_type)

        for header_key in headers.keys():
            log.info("%s: %s" % (header_key, headers[header_key]))

        #the body contains the relevant information, give this back to be parsed
        log.info("body: \n\n " + body + "<end>")
        #log.info(body)
        #sys.stdout.flush()
#-------------------------------------------------------------------------------

################################################################################

def parse_options():

    config = {}

    try:
        opts, args = getopt.getopt(sys.argv[1:], "dc:", ["config"])
    except getopt.GetoptError:
        sys.stderr.write("Error: Invalid option specified.\n")
        print_usage()
        sys.exit(2)
    for o, a in opts:
        if o in ("-c", "--config"):
            config['BDII_CONFIG_FILE'] = a
        if o in ("-d", "--daemon"):
            config['BDII_DAEMON'] = True

    if ( not config.has_key('BDII_CONFIG_FILE')):
        sys.stderr.write("Error: Configuration file not specified.\n")
        print_usage()
        sys.exit(1)         

    if ( not os.path.exists(config['BDII_CONFIG_FILE']) ):
        sys.stderr.write("Error: Configuration file %s does not exist.\n" %  config['BDII_CONFIG_FILE'])
        sys.exit(1)         

    return config

def get_config(config):

    for line in open(config['BDII_CONFIG_FILE']).readlines():
        print(line)
        index=line.find("#")
        if (index > -1):
            line=line[:index]
        index=line.find("=")
        if (index > -1):
            key=line[:index].strip()
            value=line[index+1:].strip()
            config[key] = value

    if ( not config.has_key('BDII_DAEMON') ):
        config['BDII_DAEMON'] = False
        
    for parameter in ['BDII_LOG_FILE', 'BDII_LOG_LEVEL', 'BDII_LDIF_DIR',
                      'BDII_PROVIDER_DIR', 'BDII_PLUGIN_DIR',
                      'BDII_READ_TIMEOUT']:
        if ( not config.has_key(parameter) ):
            sys.stderr.write("Error: Configuration parameter %s is not specified in the configuration file %s.\n" % (parameter, config['BDII_CONFIG_FILE']))
            sys.exit(1)

    for parameter in ['BDII_LDIF_DIR','BDII_PROVIDER_DIR','BDII_PLUGIN_DIR']:
        if ( not os.path.exists(config[parameter])):
            sys.stderr.write("Error: %s %s does not exist.\n" %  (parameter, config[parameter]))
            sys.exit(1)
    if not config.has_key('BDII_LOG_LEVEL'):
        config['BDII_LOG_LEVEL']='ERROR'
    else:
        log_levels=['CRITICAL','ERROR','WARNING','INFO','DEBUG']
        try:
            log_levels.index(config['BDII_LOG_LEVEL'])
        except ValueError, e:
            sys.stderr.write("Error: Log level %s is not an allowed level. %s\n" % (config['BDII_LOG_LEVEL'], log_levels))
            sys.exit(1)

    config['BDII_READ_TIMEOUT'] = int(config['BDII_READ_TIMEOUT'])


    #THIS VALUE SHOULD BE TRUE!
    if ( config['BDII_DAEMON'] == False ):
        for parameter in ['BDII_PORT', 'BDII_BREATHE_TIME',
                          'BDII_ARCHIVE_SIZE', 'BDII_VAR_DIR', 'SLAPD_CONF']:
            if ( not config.has_key(parameter) ):
                sys.stderr.write("Error: Configuration parameter %s is not specified in the configuration file %s.\n" % (parameter, config['BDII_CONFIG_FILE']))
                sys.exit(1)

        if ( os.path.exists(config['SLAPD_CONF']) ):
            config['BDII_PASSWD'] = {}
            rootdn = False
            rootpw = False
            for line in open(config['SLAPD_CONF']):
                if ( line.find("rootdn") > -1 ):
                    rootdn = line.replace("rootdn","").strip()
                    rootdn = rootdn.replace('"','').replace(" ","")
                    if ( rootpw ):
                        config['BDII_PASSWD'][rootdn] = rootpw
                        rootdn = False
                        rootpw = False
                if ( line.find("rootpw") > -1 ):
                    rootpw = line.replace("rootpw","").strip()
                    if ( rootdn ):
                        config['BDII_PASSWD'][rootdn] = rootpw
                        rootdn = False
                        rootpw = False
        config['BDII_BREATHE_TIME'] = float(config['BDII_BREATHE_TIME'])
        config['BDII_ARCHIVE_SIZE'] = int(config['BDII_ARCHIVE_SIZE'])
        config['BDII_HOSTNAME'] = socket.getfqdn()

        

    return config

def print_usage():
    sys.stderr.write('''Usage: %s [ OPTIONS ] 
 
     -c --config      BDII configuration file
     -d --daemon      Run BDII in daemon mode
''' % (str(sys.argv[0])))

def create_daemon(log_file):
    try:
        pid = os.fork()
    except OSError, e:
        return((e.errno, e.strerror))

    if (pid == 0):
        os.setsid()
        signal.signal(signal.SIGHUP, signal.SIG_IGN)
        try:
            pid = os.fork()
        except OSError, e:
            return((e.errno, e.strerror))
        if (pid == 0):
            os.umask(022)
        else:
            os._exit(0)
    else:
        os._exit(0)
    try:
        maxfd=os.sysconf("SC_OPEN_MAX")
    except (AttributeError, ValueError):
        maxfd=256
    for fd in range(3, maxfd):
        try:
            os.close(fd)
        except OSError:
            pass
    os.close(0)
    os.open("/dev/null", os.O_RDONLY)
    os.close(1)
    os.open("/dev/null", os.O_WRONLY)

    # connect stderr to log file
    e = os.open(log_file, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0644)
    os.dup2(e, 2)
    os.close(e)
    sys.stderr = os.fdopen(2, 'a', 0)

    # Write PID
    pid_file = open("%s/bdii-update.pid" % (config['BDII_VAR_DIR']),'w')
    pid_file.write("%s\n" % (str(os.getpid())))
    pid_file.close()

def get_logger(log_file,log_level):

    log = logging.getLogger('bdii-update')
    hdlr = logging.StreamHandler(sys.stderr)
    formatter = logging.Formatter('%(asctime)s: [%(levelname)s] %(message)s')
    hdlr.setFormatter(formatter)
    log.addHandler(hdlr)
    log.setLevel(logging.__dict__.get(log_level))

    return log

def handler(signum, frame):
    if ( signum ==14 ):
        # Commit suicide
        process_group=os.getpgrp()
        os.killpg(process_group, signal.SIGTERM)
        sys.exit(1)

def read_ldif(source):

    # Get pipe file descriptors
    read_fd, write_fd = os.pipe()

    # Fork
    pid = os.fork()

    if pid:
        
        # Close write file descriptor as we don't need it.
        os.close(write_fd)
     
        read_fh = os.fdopen(read_fd)
        raw_ldif = read_fh.read()
        result = os.waitpid(pid, 0)
        if (result[1] > 0):
            log.error("Timed out while reading %s", (source))
            return ""
        raw_ldif = raw_ldif.replace("\n ", "")
        
        return raw_ldif

    else:
        
        # Close read file d
        os.close(read_fd)
        
        # Set process group
        os.setpgrp()
                
        # Setup signal handler
        signal.signal(signal.SIGALRM, handler)
        signal.alarm(config['BDII_READ_TIMEOUT'])

        # Open pipe to LDIF
        if ( source[:7] == 'ldap://'):
            log.debug("first")
            url=source.split('/')
            command = "ldapsearch -LLL -x -h %s -b %s 2>/dev/null" % ( url[2], url[3])
            pipe = os.popen(command)
        elif( source[:7] == 'file://' ):
            log.debug("second")
            pipe=open(source[7:])
        else:
            log.debug("third")
            pipe=os.popen(source)    

        raw_ldif=pipe.read()

        # Close LDIF pipe
        pipe.close()
        try:
            write_fh = os.fdopen(write_fd, 'w')
            write_fh.write(raw_ldif)
            write_fh.close()
        except IOError:
            log.error("Information provider %s terminated unexpectedly." % source)
        signal.alarm(0) # Disable the alarm
        sys.exit(0)

def get_dns(ldif):
    dns = {}
    last_dn_index = len(ldif)
    while ( 1 ):
        dn_index = ldif.rfind("dn:",0,last_dn_index)
        if ( dn_index == -1):
            break
        end_dn_index = ldif.find("\n",dn_index, last_dn_index) 
        dn = ldif[dn_index + 4 :end_dn_index].lower()
        dn = re.sub("\s*,\s*",",",dn)
        dn = re.sub("\s*=\s*","=",dn)
        dn = dn.replace("\\5c","\\\\") # Replace encoded slash
        dn = dn.replace("\\2c","\\,") # Replace encoded comma
        dn = dn.replace("\\3d","\\=") # Replace encoded equals
        dn = dn.replace("\\2b","\\+") # Replace encoded plus
        dn = dn.replace("\\3b","\\;") # Replace encoded semi colon
        dn = dn.replace("\\22","\\\"") # Replace encoded quote
        dn = dn.replace("\\3e","\\>") # Replace encoded greater than
        dn = dn.replace("\\3c","\\<") # Replace encoded less than
        end_entry_index = ldif.find("\n\n",dn_index, last_dn_index) 
        dns[dn] = (dn_index, last_dn_index)
        last_dn_index = dn_index
    return dns

def group_dns(dns):
    grouped = {}
    for dn in dns:
        index = dn.rfind(",")
        root = dn[index +1 :].strip()
        if grouped.has_key(root):
            grouped[root].append(dn)
        else:
            grouped[root] = [ dn ]

    return grouped

def convert_entry(entry_string):

    multivalued={ 'objectclass' : None,
                  'gluehostapplicationsoftwareruntimeenvironment': None,
                  'glueserviceaccesscontrolrule' : None,
                  'glueserviceaccesscontrolbaserule' : None,
                  'glueceaccesscontrolbaserule' : None,
                  'gluesaaccesscontrolbaserule' : None,
                  'gluesecontrolprotocolcapability' : None,
                  'glueseaccessprotocolsupportedsecurity' : None,
                  'gluesacapability' : None,
                  'gluevoinfoaccesscontrolbaserule' : None,
                  'gluesecontrolprotocolcapability' : None,
                  'gluecesebindgroupseuniqueid' : None,
                  'gluecesebindseuniqueid' : None,
                  'gluecesebindmountinfo' : None,
                  'gluecesebindweight' : None,
                  'glueserviceowner' : None,
                  'gluechunkkey' : None,
                  'glueforeignkey' : None,
                  'gluecesebindmountinfo' : None,
                  'glueseaccessprotocolcapability' : None,
                  'gluesiteotherinfo' : None,
                  'gluececapability' : None, 
                  'glueclusterservice' : None }


    entry = {}
    for line in entry_string.split("\n"):
        index = line.find(":")
        if (index > -1):
            attribute = line[:index].lower()
            if ( attribute == "objectclass" ):
                value = line[index + 2:]
            else:
                value = line[index + 2:]
            if (entry.has_key(attribute)):
                
                if( config.has_key('FIX_GLUE')) and ( config['FIX_GLUE'] == 'yes'):
                    if ( multivalued.has_key(attribute)):
                        try:
                            entry[attribute].index(value)
                        except ValueError:
                            entry[attribute].append(value)
                else:
                    try:
                        entry[attribute].index(value)
                    except ValueError:
                        entry[attribute].append(value)
            else:
                entry[attribute]= [value]
    return entry

def convert_back(entry):
    entry_string =  "dn: %s\n" %(entry["dn"][0])
    entry.pop("dn")
    for attribute in entry.keys():
        attribute=attribute.lower()
        for value in entry[attribute]:
            entry_string += "%s: %s\n" %(attribute, value)

    return entry_string

def ldif_diff(dn, old_entry, new_entry):

    add_attribute={}
    delete_attribute={}
    replace_attribute={}

    #convert the strings into entry objects
    old_entry = convert_entry(old_entry)
    new_entry = convert_entry(new_entry)
    for attribute in new_entry.keys():
        attribute=attribute.lower()
        if (attribute.lower() == "dn"):
            continue

        # If the old entry has the attribue we need to compare values 
        if ( old_entry.has_key(attribute) ):

            # If the old entries are different find the modify. 
            if ( not new_entry[attribute] == old_entry[attribute]):
                    replace_attribute[attribute] = new_entry[attribute]

        # The old entry does not have the attribute so add it. 
        else:
            add_attribute[attribute] =  new_entry[attribute]

    # Checking for removed attributes
    for attribute in old_entry.keys():
        if (attribute.lower() == "dn"):
            continue
        if not new_entry.has_key(attribute):
            delete_attribute[attribute]=old_entry[attribute]


    # Create LDIF modify statement
    ldif=['dn: %s' % dn]
    ldif.append('changetype: modify')
    for attribute in add_attribute.keys():
        attribute=attribute.lower()
        ldif.append('add: %s' % (attribute) )
        for value in add_attribute[attribute]:
            ldif.append('%s: %s' % (attribute, value))
        ldif.append('-')
    for attribute in replace_attribute.keys():
        attribute=attribute.lower()
        ldif.append('replace: %s' % (attribute) )
        for value in replace_attribute[attribute]:
            ldif.append('%s: %s' % (attribute, value))
        ldif.append('-')
    for attribute in delete_attribute.keys():
        attribute=attribute.lower()
        ldif.append('delete: %s' % (attribute) )
        ldif.append('-')

    if (len(ldif) > 3):
        ldif = "\n".join(ldif) + "\n\n"
    else:
        ldif = ""
        
    return ldif

def modify_entry(entry, mods):
    mods = convert_entry(mods)
    entry = convert_entry(entry)
    if ( mods.has_key('changetype')):
        # Handle LDIF delete attribute
        if ( mods.has_key('delete')):
            for attribute in mods['delete']:
                attribute=attribute.lower()
                if (entry.has_key(attribute)):
                    if (mods.has_key(attribute)):
                        for value in mods[attribute]:
                            try:
                                entry[attribute].remove(value)
                                if (len(entry[attribute]) == 0):
                                    entry.pop(attribute)
                            except ValueError, e:
                                pass
                    else:
                        entry.pop(attribute)

        # Handle LDIF replace attribute
        if ( mods.has_key('replace')):
            for attribute in mods['replace']:
                attribute=attribute.lower()
                if (entry.has_key(attribute)):
                    if (mods.has_key(attribute)):
                        entry[attribute] = mods[attribute]

        # Handle LDIF add attribute
        if ( mods.has_key('add')):
            for attribute in mods['add']:
                attribute=attribute.lower()
                if ( not entry.has_key(attribute)):
                    log.debug("attribute: %s" %(attribute))
                    entry[attribute] = mods[attribute]
                else:
                    entry[attribute].extend(mods[attribute])
                    
    # Just old style just change
    else:
        for attribute in mods.keys():
            if (entry.has_key(attribute)):
                entry[attribute]=mods[attribute]

    entry_string = convert_back(entry)
    return entry_string
    
def fix(dns,ldif):
    response = []
    append = response.append
    
    for dn in dns.keys():
        if  ( dn[:11].lower() == "mds-vo-name" ):
            value=dn[12:dn.index(",")]
            entry = "dn: %s\nObjectClass: MDS\nMds-Vo-Name: %s\n" %(dn,value)
        else:
           entry = convert_entry(ldif[dns[dn][0]:dns[dn][1]])
           entry = convert_back(entry)         
        append(entry)
    response = "".join(response)
    return response

#-------------------------------------------------------------------------------

def log_errors(error_file, dns):    
    log.debug("Logging Errors")
    request=0
    dn=None
    error_counter=0
    for line in open(error_file).readlines():
        if ( line[:7] == 'request' ):
            request += 1
        else:
            if ( request > 1 ):
                try:
                    if ( not dn == dns[request - 2] ):
                        error_counter += 1
                        dn = dns[request - 2]
                        log.warn( "dn: %s" %(dn) )
                except IndexError, e:
                    log.error("Problem with error reporting ...")
                    log.error("Request Num: %i, Line: %s, dns: %i" %(request,line,len(dns) ))
            if ( len(line) > 5 ):
                log.warn(line.strip())
    return error_counter

#-------------------------------------------------------------------------------

def new_main(config, log):
    log.info("Starting Update Process")

    log.info("Try and create a connection")
    #Connection(host, port, uname, password)
    conn = stomp.Connection([(HOST,PORT)], 'guest', 'password')
    log.info("Try and set the listener")
    conn.set_listener('MyPersonalListener', MyListener())
    log.info("Try and start stomp")
    conn.start()
    log.info("Try and connect")
    conn.connect()
    log.info("Now subscribe to a topic")
    conn.subscribe(destination=TOPIC, ack='auto', headers=HEADERS)


    log.info("Have now started new_main")
    """
    The new logic is that the callback routines of the MyListener class will
    handel the messages. We simply need to keep this process alive, and so we
    sleep.
    """

    while True:
        log.debug("now sleep")
        time.sleep(3600)

################################################################################
def process_message(config, log, data):

    #just now, providers only get sync messages
    if('destination' in headers):
        print "Process Message"
        pass

################################################################################
def main(config, log, conn):

    print("start the main loop")
    log.info("Starting Update Process")

   


    #Per element sync counter
    sync_number = 0

    while 1:
        log.info("Starting Update")
        stats={}
        stats['update_start'] = time.time()

        new_ldif=""

        log.info("Reading static LDIF files ...")
        stats['read_start'] = time.time()
        ldif_files=os.listdir(config['BDII_LDIF_DIR'])
        for file_name in ldif_files:
            if ( file_name[-5:] == '.ldif' ):
                if ( not ((file_name[0] == '#') or (file_name[0] == '.'))):
                    file_url="file://%s/%s" %(config['BDII_LDIF_DIR'],file_name)
                    log.debug("Reading %s" % (file_url[7:]) )  
                    response = read_ldif(file_url)
                    new_ldif = new_ldif + response
                    
        stats['read_stop'] = time.time()

        

        log.info("Running Providers")
        stats['providers_start'] = time.time()
        providers=os.listdir(config['BDII_PROVIDER_DIR'])
        for provider in providers:
            if ( not ( provider[-1:] == '~' ) or (provider[0] == '#') or (provider[0] == '.')):
                log.debug("Running %s/%s" % (config['BDII_PROVIDER_DIR'],provider) )  
                response=read_ldif("%s/%s" % (config['BDII_PROVIDER_DIR'],provider))
                new_ldif = new_ldif + response                
                
        stats['providers_stop'] = time.time()

        new_dns = get_dns(new_ldif)

        log.info("Running Plugins")
        stats['plugins_start'] = time.time()
        plugins=os.listdir(config['BDII_PLUGIN_DIR'])
        for plugin in plugins:
            if ( not ( plugin[-1:] == '~' ) or (plugin[0] == '#') or (plugin[0] == '.')):
                log.debug("Running %s/%s" % (config['BDII_PLUGIN_DIR'],plugin) )  
                response = read_ldif("%s/%s" % (config['BDII_PLUGIN_DIR'],plugin))
                modify_dns = get_dns(response)
                for dn in modify_dns.keys():
                    if ( new_dns.has_key(dn)):
                        mod_entry = modify_entry( new_ldif[new_dns[dn][0]:new_dns[dn][1]],  response[modify_dns[dn][0]:modify_dns[dn][1]])
                        start = len(new_ldif)
                        end = start + len(mod_entry)
                        new_dns[dn]=(start, end)
                        new_ldif = new_ldif + mod_entry
        stats['plugins_stop'] = time.time()

        """
        ***********************************************
        keep the following, this is parsing the info and diffing it
        ***********************************************
        """
        """
        for r in new_ldif.split("\n\n"):
	    	print("----------")
	    	print r
	    	print("----------")
        """

        if( config.has_key('FIX_GLUE')) and ( config['FIX_GLUE'] == 'yes'):
            log.debug("Doing Fix")
            new_ldif = fix(new_dns, new_ldif)

        log.debug("Writing new_ldif to disk")
        if ( config['BDII_LOG_LEVEL'] == 'DEBUG' ):
            dump_fh=open("%s/new.ldif" % (config['BDII_VAR_DIR']),'w')
            dump_fh.write(new_ldif)
            dump_fh.close()

        #if ( not config['BDII_DAEMON'] ):
        #    print new_ldif
        #    print("not the daemon")
        #    sys.exit(0)
            
        log.info("Reading old LDIF file ...")
        stats['read_old_start'] = time.time()
        old_ldif_file = "%s/old.ldif" % (config['BDII_VAR_DIR'])
        if ( os.path.exists(old_ldif_file) ):
            old_ldif = read_ldif("file://%s" % (old_ldif_file))
        else:
            old_ldif = ""
        stats['read_old_stop'] = time.time()



        log.debug("Starting Diff")
        print("start the diff")
        ldif_add=[]
        ldif_modify = ""
        ldif_delete=[]

        new_dns = get_dns(new_ldif)
        old_dns = get_dns(old_ldif)

        for dn in new_dns.keys():
            if old_dns.has_key(dn):
                old = old_ldif[old_dns[dn][0]:old_dns[dn][1]].strip()
                new = new_ldif[new_dns[dn][0]:new_dns[dn][1]].strip()

                # If the entries are different we need to compare them

                #log.debug("old string  :" + str(old))
                #log.debug("new string  :" + str(new))
                if ( not new == old):
                    entry = ldif_diff(dn,old,new)
                    ldif_modify += entry

                #log.debug("the diff    :" + str(ldif_diff(dn,old,new)))
            else:
                ldif_add.append(dn)

        # Checking for removed entries
        for dn in old_dns.keys():
            if not new_dns.has_key(dn):
                ldif_delete.append(dn)
        
        log.debug("Finished Diff")
        
        log.debug("Sorting Add Keys")
        ldif_add.sort(lambda x, y: cmp(len(x), len(y)))

        """
        The plan:

        *  Figure out how exactly scirpt is invoked and from where
        *  modify to include the use of messaging
                jsut send the files inside message at first
        * Consult the papers to begin to consider what data can be split
        * Figure out the push/pull semantics
        
        """
        log.debug("now print the add enrtires")
        
        start = time.time()
        
        #print(ldif_add)
        for r in ldif_add:
                conn.send(socket.gethostname() + "\n" + str(int(sync_number)) + "\n\n" + r,destination=ADDITION, ack='auto')
	    	#log.debug("----- " + str(sync_number) + " -----")
	    	#print r
	    	#log.debug("----------")
                sync_number += 1


        print("now print the modify enrtires")
        #print(ldif_modify)
        for r in ldif_modify.split("\n\n"):
                conn.send(socket.gethostname() +"\n" + str(int(sync_number)) + "\n\n" + r,destination=MODIFICATION, ack='auto')
	    	#log.debug("----- " + str(sync_number) + " -----")
	    	#print r
	    	#log.debug("----------")
                sync_number += 1


        print("now print the delete enrtires")
        #print(ldif_delete)
        for r in ldif_delete:
                conn.send(socket.gethostname() +"\n" + str(int(sync_number)) + "\n\n" + r,destination=DELETION, ack='auto')
	    	#log.debug("----- " + str(sync_number) + " -----")
	    	#print r
	    	#log.debug("----------")
                sync_number += 1

                
        end = time.time()
        #print("It took %i to send all the messages"%(end-start))
        log.debug("It took %f to send all the messages"%(end-start))
        
        log.debug("Writing ldif_add to disk")
        if ( config['BDII_LOG_LEVEL'] == 'DEBUG' ):
            dump_fh=open("%s/add.ldif" % (config['BDII_VAR_DIR']),'w')
            for dn in ldif_add:
                dump_fh.write(new_ldif[new_dns[dn][0]:new_dns[dn][1]])
               
                dump_fh.write("\n")
            dump_fh.close()

        log.debug("Adding New Entries")
        print("Adding New Entries")
        stats['db_update_start'] = time.time()

        if ( config['BDII_LOG_LEVEL'] == 'DEBUG' ):
            error_file="%s/add.err" %(config['BDII_VAR_DIR'])
        else:
            error_file=tempfile.mktemp()

        roots = group_dns(ldif_add)
        
        add_error_counter = 0
        for root in roots.keys():
            try:
                input_fh=os.popen("ldapadd -d 256 -x -c -h %s -p %s -D %s -w %s >/dev/null 2>%s" %(config['BDII_HOSTNAME'], config['BDII_PORT'], root, config['BDII_PASSWD'][root], error_file), 'w')
                for dn in roots[root]:
                    input_fh.write(new_ldif[new_dns[dn][0]:new_dns[dn][1]])
                    #print(new_ldif[new_dns[dn][0]:new_dns[dn][1]])
                    input_fh.write("\n")
                input_fh.close()
            except IOError:
                log.error("Could not add new entries to the database.")
                
  
            add_error_counter += log_errors(error_file,ldif_add)

            if ( not config['BDII_LOG_LEVEL'] == 'DEBUG' ):
                os.remove(error_file)
                        
        log.debug("Writing ldif_modify to disk")
        if ( config['BDII_LOG_LEVEL'] == 'DEBUG' ):
            dump_fh=open("%s/modify.ldif" % (config['BDII_VAR_DIR']),'w')
            dump_fh.write(ldif_modify)
            dump_fh.close()

        log.debug("Modify New Entries")
        print("Modify New Entries")
        if ( config['BDII_LOG_LEVEL'] == 'DEBUG' ):
            error_file="%s/modify.err" % (config['BDII_VAR_DIR'])
        else:
            error_file=tempfile.mktemp()

        ldif_modify_dns = get_dns(ldif_modify)
        roots = group_dns(ldif_modify_dns)
        modify_error_counter = 0
        for root in roots.keys():
            try:
                input_fh=os.popen("ldapmodify -d 256 -x -c -h %s -p %s -D %s -w %s >/dev/null 2>%s" %(config['BDII_HOSTNAME'], config['BDII_PORT'], root, config['BDII_PASSWD'][root], error_file), 'w')
                for dn in roots[root]:
                    input_fh.write(ldif_modify[ldif_modify_dns[dn][0]:ldif_modify_dns[dn][1]])
                    #print(ldif_modify[ldif_modify_dns[dn][0]:ldif_modify_dns[dn][1]])
                    input_fh.write("\n")
                input_fh.close()
            except IOError:
                log.error("Could not modify entries in the database.")

            modify_error_counter += log_errors(error_file, ldif_modify_dns.keys())

            if ( not config['BDII_LOG_LEVEL'] == 'DEBUG' ):
                os.remove(error_file)

        log.debug("Sorting Delete Keys")
        ldif_delete.sort(lambda x, y: cmp(len(y), len(x)))

        log.debug("Writing ldif_delete to disk")
        if ( config['BDII_LOG_LEVEL'] == 'DEBUG' ):
            dump_fh=open("%s/delete.ldif" % (config['BDII_VAR_DIR']),'w')
            for dn in ldif_delete:
                dump_fh.write("%s\n" % (dn))
            dump_fh.close()

        log.debug("Deleting Old Entries")
        print("Deleting Old Entries")
        if ( config['BDII_LOG_LEVEL'] == 'DEBUG' ):
            error_file="%s/delete.err" % (config['BDII_VAR_DIR'])
        else:
            error_file=tempfile.mktemp()

        roots = group_dns(ldif_delete)
        delete_error_counter = 0
        for root in roots.keys():
            try:
                input_fh=os.popen("ldapdelete -d 256 -x -c -h %s -p %s -D %s -w %s >/dev/null 2>%s" %(config['BDII_HOSTNAME'], config['BDII_PORT'], root, config['BDII_PASSWD'][root], error_file), 'w')
                
                for dn in roots[root]:
                    input_fh.write("%s\n" % (dn))
                    #print("%s\n" % (dn))
                input_fh.close()
            except IOError:
                log.error("Could not delete old entries in the database.")

            delete_error_counter += log_errors(error_file, ldif_delete)

            if ( not config['BDII_LOG_LEVEL'] == 'DEBUG' ):
                os.remove(error_file)

        roots = group_dns(new_dns)
        stats['query_start'] = time.time()
        if ( os.path.exists("%s/old.ldif" % config['BDII_VAR_DIR']) ):
            os.remove("%s/old.ldif" % config['BDII_VAR_DIR'])
        if ( os.path.exists("%s/old.err" % config['BDII_VAR_DIR']) ):
            os.remove("%s/old.err" % config['BDII_VAR_DIR'])
        for root in roots.keys():
            command = "ldapsearch -LLL -x -h %s -p %s -b %s >> %s/old.ldif 2>> %s/old.err" % (config['BDII_HOSTNAME'], config['BDII_PORT'], root, config['BDII_VAR_DIR'], config['BDII_VAR_DIR'])
            log.debug("ldapsearch -LLL -x -h %s -p %s -b %s >> %s/old.ldif 2>> %s/old.err" % (config['BDII_HOSTNAME'], config['BDII_PORT'], root, config['BDII_VAR_DIR'], config['BDII_VAR_DIR']))
           # deleteer = ("ldapdelete -d 256 -x -c -h %s -p %s -D %s -w %s >/dev/null 2>%s" %(config['BDII_HOSTNAME'], config['BDII_PORT'], root, config['BDII_PASSWD'][root], error_file))
            #modifyer = ("ldapmodify -d 256 -x -c -h %s -p %s -D %s -w %s >/dev/null 2>%s" %(config['BDII_HOSTNAME'], config['BDII_PORT'], root, config['BDII_PASSWD'][root], error_file))
            #adder = ("ldapadd -d 256 -x -c -h %s -p %s -D %s -w %s >/dev/null 2>%s" %(config['BDII_HOSTNAME'], config['BDII_PORT'], root, config['BDII_PASSWD'][root], error_file))
            #log.debug(deleteer)
            #log.debug(modifyer)
            #log.debug(adder)
            result = os.system(command)
            if ( result > 0):
                log.error("Query to self failed.")
        stats['query_stop'] = time.time()
        out_file="%s/archive/%s-snapshot.gz" % (config['BDII_VAR_DIR'], time.strftime('%y-%m-%d-%H-%M-%S'))
        log.debug("Creating GZIP file")
        os.system("gzip -c %s/old.ldif > %s" %(config['BDII_VAR_DIR'], out_file) )

        infosys_output=""
        if (len(old_ldif) == 0 ):
            log.debug("ldapadd o=infosys compression")
            command="ldapadd"
            
            infosys_output+="dn: o=infosys\n"
            infosys_output+="objectClass: organization\n"
            infosys_output+="o: infosys\n\n"
            infosys_output+="dn: CompressionType=zip,o=infosys\n"
            infosys_output+="objectClass: CompressedContent\n"
            infosys_output+="Hostname: %s\n" %(config['BDII_HOSTNAME'])
            infosys_output+="CompressionType: zip\n"
            infosys_output+="Data: file://%s\n\n" %(out_file)
        else:
            log.debug("ldapmodify o=infosys compression")
            command="ldapmodify"

            infosys_output+="dn: CompressionType=zip,o=infosys\n"
            infosys_output+="changetype: Modify\n"
            infosys_output+="replace: Data\n"
            infosys_output+="Data: file://%s\n\n" %(out_file)
        try:
            output_fh = os.popen("%s -x -c -h %s -p %s -D o=infosys -w %s >/dev/null" %(command, config['BDII_HOSTNAME'], config['BDII_PORT'], config['BDII_PASSWD']['o=infosys']), 'w')
            output_fh.write(infosys_output)
            output_fh.close()
        except IOError:
            log.error("Could not add compressed data to the database.")

        old_files=os.popen("ls -t %s/archive" % (config['BDII_VAR_DIR']) ).readlines()
        log.debug("Deleting old GZIP files")
        for file in old_files[config['BDII_ARCHIVE_SIZE']:]:
            os.remove("%s/archive/%s" % (config['BDII_VAR_DIR'],file.strip()))

        stats['db_update_stop'] = time.time()
        stats['update_stop'] = time.time()

        stats['UpdateTime'] = int(stats['update_stop']
                                  - stats['update_start'])
        stats['ReadTime'] = int(stats['read_old_stop']
                                  - stats['read_old_start'])
        stats['ProvidersTime'] = int(stats['providers_stop']
                                     - stats['providers_start'])
        stats['PluginsTime'] = int(stats['plugins_stop']
                                     - stats['plugins_start'])
        stats['QueryTime'] = int(stats['query_stop']
                                   - stats['query_start'])
        stats['DBUpdateTime'] = int(stats['db_update_stop']
                                   - stats['db_update_start'])
        stats['TotalEntries'] = len(old_dns) 
        stats['NewEntries'] =  len(ldif_add)
        stats['ModifiedEntries'] = len(ldif_modify_dns.keys())
        stats['DeletedEntries'] =  len(ldif_delete)
        stats['FailedAdds'] =  add_error_counter
        stats['FailedModifies'] = modify_error_counter
        stats['FailedDeletes'] = delete_error_counter

        for key in stats.keys():
            if ( key.find("_") == -1 ):
                log.info("%s: %i" % (key, stats[key]) )

        infosys_output=""
        if (len(old_ldif) == 0 ):
            log.debug("ldapadd o=infosys updatestats")
            command="ldapadd"

            infosys_output+="dn: Hostname=%s,o=infosys\n" %(config['BDII_HOSTNAME'])
            infosys_output+="objectClass: UpdateStats\n"
            infosys_output+="Hostname: %s\n" %(config['BDII_HOSTNAME'])
            for key in stats.keys():
                if ( key.find("_") == -1):
                    infosys_output+="%s: %i\n" %(key, stats[key])
            infosys_output+="\n"
        else:
            log.debug("ldapmodify o=infosys updatestats")
            command="ldapmodify"

            infosys_output+="dn: Hostname=%s,o=infosys\n" %(config['BDII_HOSTNAME'])
            infosys_output+="changetype: Modify\n"
            for key in stats.keys():
                if ( key.find("_") == -1):
                    infosys_output+="replace: %s\n" %(key)
                    infosys_output+="%s: %i\n" %(key, stats[key])
                    infosys_output+="-\n"
            infosys_output+="\n"
        try:
            output_fh = os.popen("%s -x -c -h %s -p %s -D o=infosys -w %s >/dev/null" %(command, config['BDII_HOSTNAME'], config['BDII_PORT'], config['BDII_PASSWD']['o=infosys']), 'w')
            output_fh.write(infosys_output)
            output_fh.close()
        except IOError:
            log.error("Could not add stats entries to the database.")

        old_ldif = None
        new_ldif = None
        new_dns = None
        ldif_delete = None
        ldif_add = None
        ldif_modify = None
        
        log.info("Sleeping for %i seconds" %(120))
        print("Sleeping for %i seconds" %(120))

        #while True:
        sys.stdout.flush()
        time.sleep(120)

#-------------------------------------------------------------------------------
def random_generator():
    
    while True:
    	pass


#-------------------------------------------------------------------------------

if __name__ == '__main__':


    config = parse_options()
    config=get_config(config)
    
    if ( config['BDII_DAEMON'] ):
        create_daemon(config['BDII_LOG_FILE'])
        # Giving some time for the init.d script to finish
        time.sleep(3)
    else:
        # connect stderr to log file
        e = os.open(config['BDII_LOG_FILE'], os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0644)
        os.dup2(e, 2)
        os.close(e)
        sys.stderr = os.fdopen(2, 'a', 0)
                        

    log=get_logger(config['BDII_LOG_FILE'],config['BDII_LOG_LEVEL'])

    """
    lastly, create a connection to a/the broker
    This means that we can send messages.
    """

    conn = stomp.Connection([(HOST,PORT)], 'guest', 'password')
    conn.set_listener('MyListener', MyListener())
    conn.start()
    conn.connect()

    print "Subscribe"
    conn.subscribe(destination='/topic/sync/',        ack='auto', headers=HEADERS)
    log.debug("got the config working ok")#
    print("got the config working ok")#

    #conn = None
    
    main(config,log, conn)
    #new_main(config,log)


    
