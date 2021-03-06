#!/usr/bin/env python
#
# VM Encryption extension
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
import subprocess
import sys  
from subprocess import *  
from patch import *
from keymanager import *

class Encryption(object):
    """
    description of class
    """
    def __init__(self, paras):
        self.paras = paras

    def install_extras(self):
        global MyPatching
        MyPatching = GetMyPatching()
        if MyPatching == None:
            sys.exit(1)
        else:
            MyPatching.install_extras()

    def encrypt(self):
        self.install_extras()
        keyManager = KeyManager(self.paras.keyaddess, self.paras.password);
        print(self.paras.command)

        if(self.paras.command == 'disk'):
            #self.paras.path = /dev/sdb
            commandToExecute = '/bin/bash -c "cryptsetup -y luksFormat ' + self.paras.path + ' <<< ' + keyManager.key + ' 2> /dev/null"'
            print(commandToExecute)
            proc = Popen(commandToExecute, shell=True)
            returnCode = proc.wait()
            print('returnCode'+str(returnCode));

            commandToExecute = '/bin/bash -c "cryptsetup luksOpen ' + self.paras.path +' ' + self.paras.mountname + ' <<< ' + keyManager.key + ' 2> /dev/null"'
            print(commandToExecute)
            proc = Popen(commandToExecute, shell=True)
            returnCode = proc.wait()
            print('returnCode'+str(returnCode));

            commandToExecute = '/bin/bash -c "mkfs.ext4 /dev/mapper/' + self.paras.mountname + ' <<< ' + self.paras.mountname + ' 2> /dev/null"'
            print(commandToExecute)
            proc = Popen(commandToExecute, shell=True)
            returnCode = proc.wait()
            print('returnCode'+str(returnCode));

            commandToExecute = '/bin/bash -c "mkdir ' + (self.paras.mountpoint + self.paras.mountname) + ' 2> /dev/null"'
            print(commandToExecute)
            proc = Popen(commandToExecute, shell=True)
            returnCode = proc.wait()
            print('returnCode'+str(returnCode));

            commandToExecute = '/bin/bash -c "mount /dev/mapper/' + self.paras.mountname + ' ' + (self.paras.mountpoint + self.paras.mountname) + ' 2> /dev/null"'
            print(commandToExecute)
            proc = Popen(commandToExecute, shell=True)
            returnCode = proc.wait()
            print('returnCode'+str(returnCode));

        elif(self.paras.command == 'folder'):
            commandToExecute = 'ecryptfs-setup-private'
            proc = Popen(commandToExecute, shell=True)
            returnCode = proc.wait()
            print('returnCode'+str(returnCode));

