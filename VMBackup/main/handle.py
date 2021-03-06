#!/usr/bin/env python
#
# VM Backup extension
#
# Copyright 2014 Microsoft Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Requires Python 2.7+
#

import array
import base64
import os
import os.path
import re
import string
import subprocess
import sys
import imp
import shlex
import traceback
import httplib
import xml.parsers.expat
from mounts import Mounts
from mounts import Mount
from fsfreezer import FsFreezer
from common import CommonVariables
from parameterparser import ParameterParser
from Utils import HandlerUtil
from urlparse import urlparse
from snapshotter import Snapshotter
from backuplogger import Backuplogger

#Main function is the only entrence to this extension handler
def main():
    global backup_logger
    global hutil
    HandlerUtil.LoggerInit('/var/log/waagent.log','/dev/stdout')
    HandlerUtil.waagent.Log("%s started to handle." % (CommonVariables.extension_name)) 
    hutil = HandlerUtil.HandlerUtility(HandlerUtil.waagent.Log, HandlerUtil.waagent.Error, CommonVariables.extension_name)
    backup_logger = Backuplogger(hutil)
    for a in sys.argv[1:]:
        if re.match("^([-/]*)(disable)", a):
            disable()
        elif re.match("^([-/]*)(uninstall)", a):
            uninstall()
        elif re.match("^([-/]*)(install)", a):
            install()
        elif re.match("^([-/]*)(enable)", a):
            enable()
        elif re.match("^([-/]*)(update)", a):
            update()


def install():
    hutil.do_parse_context('Install')
    hutil.do_exit(0, 'Install','Installed','0', 'Install Succeeded')

def enable():
    freezer = FsFreezer(backup_logger)
    unfreeze_result     = None
    snapshot_result     = None
    freeze_result       = None
    global_error_result = None
    para_parser         = None
    run_result          = 1
    error_msg           = None
    run_status          = None
    # precheck 
    try:
        hutil.do_parse_context('Enable')
        hutil.exit_if_enabled()
        # we need to freeze the file system first
        backup_logger.log('starting to enable', True)
        """
        protectedSettings is the privateConfig passed from Powershell.
        """
        protected_settings = hutil._context._config['runtimeSettings'][0]['handlerSettings'].get('protectedSettings')
        public_settings = hutil._context._config['runtimeSettings'][0]['handlerSettings'].get('publicSettings')
        para_parser = ParameterParser(protected_settings, public_settings)

        commandToExecute = para_parser.commandToExecute
        #validate all the required parameter here
        if(commandToExecute.lower() == CommonVariables.iaas_install_command):
            backup_logger.log("install succeed.",True)
            run_status = 'success'
            error_msg  = 'Install Succeeded'
            run_result = 0
            backup_logger.log(error_msg)
        elif(commandToExecute.lower() == CommonVariables.iaas_vmbackup_command):
            if(para_parser.backup_metadata is None or para_parser.public_config_obj is None or para_parser.private_config_obj is None):
                run_result = 11
                run_status = 'error'
                error_msg  = 'required field empty or not correct'
            else:
                backup_logger.log('commandToExecute is ' + commandToExecute, True)
                if(commandToExecute.lower() == CommonVariables.iaas_vmbackup_command):
                    """
                    make sure the log is not doing when the file system is freezed.
                    """
                    backup_logger.log("doing freeze now...", True)
                    freeze_result   = freezer.freezeall()
                    backup_logger.log("freeze result " + str(freeze_result))
                
                    backup_logger.log("doing snapshot now...")
                    snap_shotter    = Snapshotter(backup_logger)
                    snapshot_result = snap_shotter.snapshotall(para_parser)
                    backup_logger.log("snapshotall ends...")
                    if(snapshot_result != None and len(snapshot_result.errors) > 0):
                        error_msg  = "snapshot result: " + str(snapshot_result.errors)
                        run_result = 2
                        run_status = 'error'
                        backup_logger.log(error_msg, False, 'Error')
                    else:
                        if(freeze_result != None and len(freeze_result.errors) > 0 ):
                            run_result = 1
                            run_status = 'warning'
                            error_msg  = 'Enable Succeeded with error' + str(freeze_result.errors)
                            backup_logger.log(error_msg, False, 'Warning')
                        else:
                            run_result = 1
                            run_status = 'success'
                            error_msg  = 'Enable Succeeded'
                            backup_logger.log(error_msg)

    except Exception as e:
        errMsg = "Failed to enable the extension with error: %s, stack trace: %s" % (str(e), traceback.format_exc())
        backup_logger.log(errMsg, False, 'Error')
        global_error_result = e
    finally:
        backup_logger.log("doing unfreeze now...")
        unfreeze_result = freezer.unfreezeall()
        backup_logger.log("unfreeze result " + str(unfreeze_result))
        error_msg += ('Enable Succeeded with error: ' + str(unfreeze_result.errors))
        if(unfreeze_result is not None and len(unfreeze_result.errors) > 0):
            backup_logger.log(error_msg, False, 'Warning')
        backup_logger.log("unfreeze ends...")

    if(para_parser!= None):
        backup_logger.commit(para_parser.logsBlobUri)
    """
    we do the final report here to get rid of the complex logic to handle the logging when file system be freezed issue.
    """
    if(global_error_result != None):
        if(global_error_result.errno==2):
            run_result = 12
        else:
            run_result = 2
        run_status = 'error'
        error_msg  += ('Enable failed.' + str(global_error_result))

    hutil.do_exit(run_result, 'Enable', run_status, str(run_result), error_msg)

def uninstall():
    hutil.do_parse_context('Uninstall')
    hutil.do_exit(0,'Uninstall','success','0', 'Uninstall succeeded')

def disable():
    hutil.do_parse_context('Disable')
    hutil.do_exit(0,'Disable','success','0', 'Disable Succeeded')

def update():
    hutil.do_parse_context('Upadate')
    hutil.do_exit(0,'Update','success','0', 'Update Succeeded')

if __name__ == '__main__' :
    main()
