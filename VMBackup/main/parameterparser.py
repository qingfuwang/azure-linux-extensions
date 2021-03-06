#!/usr/bin/env python
#
#CustomScript extension
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
from Utils import HandlerUtil
from common import CommonVariables
import base64
import json

class ParameterParser(object):
    def __init__(self, protected_settings, public_settings):
        """
        TODO: we should validate the parameter first
        """
        self.blobs = []
        self.backup_metadata = None
        self.public_config_obj = None
        self.private_config_obj = None
        self.blobs = None
        """
        get the public configuration
        """
        self.commandToExecute = public_settings.get(CommonVariables.command_to_execute)
        self.taskId = public_settings.get(CommonVariables.task_id)
        self.locale = public_settings.get(CommonVariables.locale)
        self.publicObjectStr = public_settings.get(CommonVariables.object_str)
        if(self.publicObjectStr != None and self.publicObjectStr != ""):
            decoded_public_obj_string = base64.standard_b64decode(self.publicObjectStr)
            decoded_public_obj_string = decoded_public_obj_string.strip()
            decoded_public_obj_string = decoded_public_obj_string.strip('\'')
            self.public_config_obj = json.loads(decoded_public_obj_string)
            self.backup_metadata = self.public_config_obj['backupMetadata']
        """
        first get the protected configuration
        """
        self.logsBlobUri = protected_settings.get(CommonVariables.logs_blob_uri)
        self.privateObjectStr = protected_settings.get(CommonVariables.object_str)
        if(self.privateObjectStr!=None and self.privateObjectStr != ""):
            decoded_private_obj_string = base64.standard_b64decode(self.privateObjectStr)
            decoded_private_obj_string = decoded_private_obj_string.strip()
            decoded_private_obj_string = decoded_private_obj_string.strip('\'')
            self.private_config_obj = json.loads(decoded_private_obj_string)
            self.blobs = self.private_config_obj['blobSASUri']
