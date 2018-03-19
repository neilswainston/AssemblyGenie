'''
AssemblyGenie (c) University of Manchester 2018

All rights reserved.

@author: neilswainston
'''
import os
import sys

from assembly import pipeline, plate
from assembly.app import lcr, part_pcr, part_qc, part_dig, utils


def main(args):
    '''main method.'''
    ice_helper = utils.ICEHelper(args[0], args[1], args[2])
    plasmid_parts = ice_helper.get_plasmid_parts(args[6:])
    parts_ice = {ice_id: part_ice
                 for _, parts_map in plasmid_parts.iteritems()
                 for ice_id, part_ice in parts_map.iteritems()
                 if part_ice.get_parameter('Type') != 'DOMINO'}
    part_ids = parts_ice.keys()

    writers = [part_pcr.PartPcrWriter(parts_ice, ice_helper),
               part_dig.PartDigestWriter(part_ids),
               [part_qc.PartQcWriter(part_ids),
                lcr.LcrWriter(plasmid_parts)]]

    input_plates = {}

    for(dirpath, _, filenames) in os.walk(args[3]):
        for filename in filenames:
            if filename[-4:] == '.csv':
                plt = plate.from_table(os.path.join(dirpath, filename))
                input_plates[plt.get_name()] = plt

    pipeline.run(writers, input_plates, {'reagents': args[4]}, args[5])


if __name__ == '__main__':
    main(sys.argv[1:])
