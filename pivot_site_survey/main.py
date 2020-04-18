import sys
from os import path

import numpy as np
import pandas as pd


def main(filename):
    basefilename = path.splitext(path.basename(filename))[0]

    original_df = pd.read_csv(filename)
    final_df = pd.DataFrame()

    for sector in range(1, 4):
        for antena in range(1, 4):
            cols = {
                'Customer Site ID*': 'Customer Site ID',
                f'Sector {sector} Antenna {antena} Model': 'Model',
                f'Sector {sector} Antenna {antena} Azimut': 'Azimut',
                f'Sector {sector} Antenna {antena} Height': 'Height',
                f'Sector {sector} Antenna {antena} Mec. Tilt': 'Mec. Tilt',
                f'Sector {sector} Antenna {antena} Elect. Tilt': 'Elect. Tilt'
            }
            partial_df = original_df.loc[:, list(cols.keys())]
            partial_df.insert(1, 'Antena', antena)
            partial_df.insert(1, 'Sector', sector)
            partial_df = partial_df.rename(columns=cols)
            partial_df['Antena'] = f'{antena}{sector}'
            final_df = final_df.append(partial_df)

    final_df.sort_values(['Customer Site ID', 'Sector', 'Antena'], inplace=True)
    final_df.reset_index(drop=True, inplace=True)
    final_df.fillna('NO DATA', inplace=True)
    # print(final_df)
    final_df.to_csv(path.join(path.dirname(filename), f'{basefilename}_pivot.csv'))

if __name__ == '__main__':
    filename = sys.argv.pop() if len(sys.argv) == 2 else None
    if filename is None:
        print('Missing argument: filename\nUsage: main.py [filename.csv]')
    elif path.exists(filename):
        print(f'Processing file: {filename}')
        main(filename)
    else:
        print(f'Can\'t find filename: {filename}')
