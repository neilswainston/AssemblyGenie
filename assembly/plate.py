'''
AssemblyGenie (c) University of Manchester 2018

All rights reserved.

@author: neilswainston
'''
# pylint: disable=invalid-name
# pylint: disable=too-many-arguments
import itertools
import math
import os

import pandas as pd


class Plate(object):
    '''Class to represent a well plate.'''

    def __init__(self, name, rows=8, cols=12, col_ord=False, properties=None):

        if not properties:
            properties = ['id']

        assert 'id' in properties

        perms = list(itertools.product(properties, list(range(1, cols + 1))))
        columns = pd.MultiIndex.from_tuples(perms)

        self.__plate = pd.DataFrame(index=[chr(r + ord('A'))
                                           for r in range(0, rows)],
                                    columns=columns)
        self.__plate.name = name
        self.__col_ord = col_ord
        self.__next = 0

    def get_name(self):
        '''Get name.'''
        return self.__plate.name

    def shape(self):
        '''Get plate shape.'''
        return self.__plate['id'].shape

    def set(self, obj, row, col):
        '''Set object at a given row, col.'''
        self.__next = max(self.__next, self.get_idx(row, col) + 1)

        for key, val in obj.items():
            self.__plate.loc[:, (key, col + 1)][row] = val

    def get(self, row, col):
        '''Get object at a given row, col.'''
        keys = list(self._Plate__plate.columns.levels[0])

        return {key: self._Plate__plate.loc[:, (key, col + 1)][row]
                for key in keys
                if _is_value(self._Plate__plate.loc[:, (key, col + 1)][row])}

    def get_all(self):
        '''Get all objects.'''
        rows, cols = self.shape()
        return {get_well_name(row, col): self.get(row, col)
                for row in range(rows) for col in range(cols)
                if self.get(row, col)}

    def get_by_well(self, well_name):
        '''Get by well, e.g. by C12.'''
        row, col = get_indices(well_name)
        return self.get(row, col)

    def add(self, obj, well_name=None):
        '''Adds an object to the next well.'''
        if well_name:
            row, col = get_indices(well_name)

            for key, val in obj.items():
                self.__plate.loc[:, (key, col + 1)][row] = val
            return None

        # else:
        return self.__set(obj, self.__next)

    def add_line(self, obj):
        '''Adds a line of objects (row or col) in next empty line.'''
        if self.__col_ord:
            line_len = len(self.__plate.columns)
        else:
            line_len = len(self.__plate.index)

        start = ((self.__next + line_len - 1) // line_len) * line_len

        for idx in range(start, start + line_len):
            row, col = self.get_row_col(idx)
            self.set(obj, row, col)

    def find(self, src_terms):
        '''Finds an object.'''
        return [well
                for well, plate_obj in self.get_all().items()
                if _match(src_terms, plate_obj)]

    def get_row_col(self, idx):
        '''Map idx to well.'''
        rows, cols = self.__plate.shape

        if self.__col_ord:
            return int(idx / cols), int(idx % cols)

        return int(idx % rows), int(idx / rows)

    def get_idx(self, row, col):
        '''Map idx to well, column ordered.'''
        rows, cols = self.__plate.shape

        if self.__col_ord:
            return row * cols + col

        return col * rows + row

    def to_csv(self, out_dir_name='.'):
        '''Export plate to csv.'''
        filepath = os.path.abspath(os.path.join(out_dir_name,
                                                str(self.__plate.name) +
                                                '.csv'))
        self.__plate.to_csv(filepath, encoding='utf-8')

    def __set(self, obj, idx):
        '''Sets an object in the given well.'''
        row, col = self.get_row_col(idx)
        self.set(obj, row, col)
        return get_well_name(row, col)

    def __repr__(self):
        return self.__plate.__repr__()


def get_indices(well_name):
    '''Get indices from well name.'''
    return ord(well_name[0]) - ord('A'), int(well_name[1:]) - 1


def get_well_name(row, col):
    '''Get well name from indices.'''
    return str(chr(row + ord('A'))) + str(col + 1)


def find(plates, obj):
    '''Find object in plates.'''
    found = {}

    for plt in plates.values():
        wells = plt.find(obj)

        if wells:
            found[plt.get_name()] = wells

    return found


def add_component(component, plate_id, is_reagent, plates, well_name):
    '''Add a component to a plate.'''
    for plate in plates.values():
        wells = plate.find(component)

        if wells:
            return wells[0], plate

    if plate_id not in plates:
        plate = Plate(plate_id)
        plates[plate_id] = plate
    else:
        plate = plates[plate_id]

    if is_reagent:
        if well_name:
            return plate.add(component, well_name), plate
        # else:
        plate.add_line(component)
        return add_component(component, plate_id, is_reagent, plates,
                             well_name)

    return plate.add(component, well_name), plate


def from_table(filename):
    '''Generate Plate from tabular data.'''
    _, name = os.path.split(filename)
    df = pd.read_csv(filename)
    df['id'] = df['id'].astype(str)

    # 96 or 384?
    if len(df) > 96:
        rows, cols = 16, 24
    else:
        rows, cols = 8, 12

    props = list(df.columns[df.columns != 'well'])

    plt = Plate(name.split('.')[0], rows=rows, cols=cols, properties=props)

    for _, row in df.iterrows():
        dct = row.to_dict()
        well = dct.pop('well')
        plt.add(dct, well)

    return plt


def _is_value(val):
    '''Return boolean depending on whether value is None or NaN.'''
    return bool(val and not (isinstance(val, float) and math.isnan(val)))


def _match(src_terms, obj):
    '''Match object by search terms.'''
    return all([obj.get(key, None) == src_terms[key]
                for key in src_terms])
