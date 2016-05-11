# Copyright 2015 Google Inc. All Rights Reserved.
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
# ==============================================================================

"""The constants of the dsrf parsing library."""

import re

COLOR_GREEN = '\033[92m'
COLOR_RED = '\033[01;31m'
ENDC = '\033[0m'
BOLD = '\033[1m'


# The XSD tags prefix.
XSD_TAG_PREFIX = '{http://www.w3.org/2001/XMLSchema}'

# Four letter code of the form "SY02" (two numbers and two digits), with HEAD
# and FOOT being special values.
VALID_ROW_TYPE_PATTERN = re.compile('^[A-Z]{2}[0-9]{2}$|HEAD|FOOT')

# Block Id cell's pattern.
BLOCK_PATTERN = re.compile('BL[0-9]+')

# The flat file cells delimiter.
FILE_DELIMITER = '\t'

# The flat file secondary cells delimiter.
REPEATED_VALUE_DELIMITER = '|'

# A comment line sign.
COMMENT_SIGN = '#'

# Row types which are considered as block type HEAD.
HEAD_ROWS = ['HEAD', 'SY01', 'SY02', 'SY03', 'SY04', 'FHEA']

# Row types which are considered as block type FOOT.
FOOT_ROWS = ['FOOT', 'FFOO']

# Fixed string cells type prefix (AVS = Allowed Value Set).
FIXED_STRING_PREFIX = 'avs:'

# Simple cells type prefix.
DSRF_TYPE_PREFIX = 'dsrf:'

# Gzip compressed file extension.
GZIP_COMPRESSED_FILE_SUFFIX = '.tsv.gz'

# The format file name delimiter.
FILE_NAME_DELIMITER = r'_'

# The file name format.
FILE_NAME_FORMAT = (
    'DSR_MessageRecipient_MessageSender_ServiceDescription_MessageNotification'
    'Period_TerritoryOfUseOrSale_xofy_MessageCreatedDateTime.ext')

# File name prefix.
FILE_NAME_PREFIX = 'DSR'

# File name components list.
FILE_NAME_COMPONENTS = [
    FILE_NAME_PREFIX,
    'MessageRecipient',
    'MessageSender',
    'ServiceDescription',
    'MessageNotificationPeriod',
    'TerritoryOfUseOrSale',
    'x',
    'y',
    'MessageCreatedDateTime',
    'ext']

# Supported file types.
SUPPORTED_FILE_EXTENSIONS = ['tsv', 'tsv.gz']

# A pattern for the component MessageNotificationPeriod.
MESSAGE_NOTIFICATION_PERIOD_PATTERN = re.compile(
    r'^\d{4}((-\d{2,3})|(-\d{2}-\d{2}(--\d{4}-\d{2}-\d{2})?)|(-Q\d{1}))?$')

# A pattern for the component TerritoryOfUseOrSale.
TERRITORY_OF_USE_OR_SALE_PATTERN = re.compile(
    r'^(\w{2}|\d{1,4}|Worldwide|multi)$', re.IGNORECASE)

# A pattern for the component MessageCreated-DateTime.
MESSAGE_CREATED_DATETIME_PATTERN = re.compile(r'^\d{8}T\d{6}$')

# These parts of the filename are not allowed to change across files.
FILE_NAME_MATCH_PARTS = [
    'MessageRecipient', 'MessageSender', 'ServiceDescription', 'y']

# These HEAD row cells (keys) should match the file name parts (values).
HEAD_CELLS_MATCH_TO_FILE_NAME_PARTS = {
    'FileNumber': 'x',
    'NumberOfFiles': 'y',
    'ServiceDescription': 'ServiceDescription'}

# One of these HEAD cells should match the MessageRecipient part in the file
# name.
MESSAGE_RECIPIENT_MATCH = ['RecipientPartyId', 'RecipientName']

# One of these HEAD cells should match the MessageSender part in the file name.
MESSAGE_SENDER_MATCH = ['SenderPartyId', 'SenderName']

# In the default implementation, the serialized proto objects are written as a
# byte stream. This delimiter enables the reader of the stream to reconstruct
# the individual protos.
QUEUE_DELIMITER = '==PIPE_PROTO_DELIMITER=='

# The xs:duration cell pattern.
DURATION_PATTERN = re.compile(
    r'(?P<sign>-?)P(?:(?P<years>\d+)Y)?(?:(?P<months>\d+)M)?(?:(?P<days>\d+)D)?'
    r'(?:T(?:(?P<hours>\d+)H)?(?:(?P<minutes>\d+)M)?(?:(?P<seconds>\d+)S)?)?')

# The xs:dateTime cell pattern.
DATETIME_PATTERN = re.compile(r'[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:'
                              r'[0-9]{2}(Z|([-+][0-9]{2}:{0,1}[0-9]{2}))')

# The library default version number.
DEFAULT_VERSION = 3.0

# TODO(b/24666427): Add profile 7.2 when fixed.
# A map between profile numbers and their names.
PROFILE_NUMBER_MAP = {7.3: 'ResourceOnly',
                      7.4: 'Ugc',
                      7.6: 'AudioVisualRelease'}