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

"""Parses a single flat file to a list of block objects.

The input of this component is a single file from a ddex report, and a list of
cell and row validators.
The output is a list of protocol buffer block objects.
"""
import csv
import gzip
from os import path

from dsrf import constants
from dsrf import error
from dsrf.proto import block_pb2
from dsrf.proto import cell_pb2
from dsrf.proto import row_pb2


class DSRFFileParser(object):
  """Parses a single file in the DSRF report."""

  def __init__(self, logger, file_path):
    self.logger = logger
    self.file_path = file_path
    self.file_name = path.basename(file_path)

  def get_block_number(self, line, row_number):
    """Returns the line block number if it exists.

    Args:
      line: The line from the file to parse.
      row_number: The line number in the file.

    Returns:
      The block number which appears in the line.
    """
    try:
      return int(line[1])
    except (IndexError, ValueError):
      raise error.RowValidationFailure(
          row_number, self.file_name,
          'The block id "%s" in line number %s was expected to be an integer.'
          % (line[1].upper(), row_number))

  def get_cell_object(self, cell_validator, cell_parsed_data):
    """Parses the cell data to a protocol buffer cell object.

    Args:
      cell_validator: Instance of a subclass of
                      cell_validators.BaseCellValidator.
      cell_parsed_data: The data from the cell, either an integer, float, string
        or boolean.

    Returns:
      A cell_pb2.Cell object.
    """
    cell_proto = cell_pb2.Cell(
        name=cell_validator.cell_name, cell_type=cell_validator.get_cell_type())
    if not isinstance(cell_parsed_data, list):
      cell_parsed_data = [cell_parsed_data]
    if cell_proto.cell_type == cell_pb2.STRING:
      cell_proto.string_value.extend(cell_parsed_data)
    elif cell_proto.cell_type == cell_pb2.INTEGER:
      cell_proto.integer_value.extend(cell_parsed_data)
    elif cell_proto.cell_type == cell_pb2.DECIMAL:
      cell_proto.decimal_value.extend(cell_parsed_data)
    elif cell_proto.cell_type == cell_pb2.BOOLEAN:
      cell_proto.boolean_value.extend(cell_parsed_data)
    return cell_proto

  def get_row_object(self, row_validator, line, row_number, block_number):
    """Parses the row data to a protocol buffer row object.

    Args:
      row_validator: A list of subclass of cell_validators.BaseCellValidator.
      line: The row from the file (eg. ['FFOO', '123']).
      row_number: The row number which is now parsed in the original file.
      block_number: The number of the block, for error reporting purposes.

    Returns:
      A row_pb2.Row object.
    """
    row = row_pb2.Row(type=line[0].upper(), row_number=row_number)
    cells = []
    for cell_validator, cell_content in zip(row_validator, line):
      if not cell_validator:
        continue
      cell_parsed_data = cell_validator.validate_value(
          cell_content, row_number, self.file_name, block_number)
      # If cell_parsed_data is None, it means the cell either contained an
      # invalid value, or was empty.
      if cell_parsed_data not in (None, ''):
        cells.append(self.get_cell_object(cell_validator, cell_parsed_data))
    row.cells.extend(cells)
    return row

  def is_compressed(self):
    return self.file_name.endswith(constants.GZIP_COMPRESSED_FILE_SUFFIX)

  def _get_row_type(self, line, row_validators_list, row_number):
    """Returns the line's row type.

    Args:
      line: The line to parse.
      row_validators_list: A list of subclass of
                           cell_validators.BaseCellValidator.
      row_number: The line number of the parsed line.

    Returns:
      A 4 letters row type code.
    """
    if not line:
      raise error.RowValidationFailure(
          row_number, self.file_name,
          'It is not permissible to include empty Records.')
    row_type = line[0].upper()
    if row_type not in row_validators_list:
      raise error.RowValidationFailure(
          row_number, self.file_name,
          'Row type %s does not exist in the XSD. Valid row types are: %s. ' % (
              row_type, row_validators_list.keys()))
    return row_type

  def parse_file(self, row_validators_list, file_number):
    """Parses the file to a protocol buffer block objects.

    Args:
      row_validators_list: A list of subclass of
                           cell_validators.BaseCellValidator.
        (eg. [[string_validator, decimal_validator],[string_validator]]).
      file_number: The file number in the report (eg. "3of4" -> 3).

    Yields:
      Each yield is a single block object (block_pb2.Block).
    """
    row_number = 0
    if self.is_compressed():
      tsv = gzip.open(self.file_path, 'rU')
    else:
      tsv = open(self.file_path, 'rU')
    current_block = block_pb2.Block(file_number=file_number)
    self.logger.info(
        'Start parsing the HEAD block in file number %s.', file_number)
    for line in csv.reader(tsv, delimiter=constants.FILE_DELIMITER):
      row_number += 1
      # Comment row.
      if line[0].startswith(constants.COMMENT_SIGN):
        continue
      try:
        row_type = self._get_row_type(line, row_validators_list, row_number)
        # End of block check.
        if self.is_end_of_block(line, row_number, current_block):
          yield current_block
          current_block = block_pb2.Block(file_number=file_number)
        # HEAD/FOOT row.
        if row_type in constants.HEAD_ROWS or row_type in constants.FOOT_ROWS:
          current_block.type = block_pb2.HEAD
          if row_type in constants.FOOT_ROWS:
            self.logger.info(
                'Start parsing the FOOT block in file number %s.', file_number)
            current_block.type = block_pb2.FOOT
          if row_type == 'HEAD':
            current_block.version = line[1]
          current_block.rows.extend([self.get_row_object(
              row_validators_list[row_type], line, row_number, row_type)])
          continue
        # Body row.
        block_number = self.get_block_number(line, row_number)
        row = self.get_row_object(
            row_validators_list[row_type], line, row_number, block_number)
        if not current_block.type:
          current_block.type = block_pb2.BODY
          current_block.number = block_number
          self.logger.info('Start parsing block number %s in file number %s.',
                           block_number, file_number)
        current_block.rows.extend([row])
      except error.ValidationError as e:
        self.logger.error(e)

    yield current_block

  def is_end_of_block(self, line, row_number, current_block):
    # If the block is a head, it can be the first block (an actual HEAD) or a
    # new block (new blocks default type is HEAD).
    if current_block.type == block_pb2.HEAD:
      return line[0] not in constants.HEAD_ROWS
    # Foot block is always the last one in a file.
    elif current_block.type == block_pb2.FOOT:
      return line[0] not in constants.FOOT_ROWS
    # Cases of a FOOT block after a BODY block or 2 BODY blocks.
    else:
      return (
          line[0] in constants.FOOT_ROWS or
          current_block.number != self.get_block_number(line, row_number))
