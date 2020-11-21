import os
from matplotlib import cm, pyplot as plt
from netCDF4 import Dataset
import numpy as np
from pathlib import Path
from PIL import Image
from glob import glob
from copy import copy

NUM_OF_SEASONS = 12


class NumpyFileGenerator:

    def __init__(self):
        self.tdata_path = f'./nc_files'


    def create_numpy_file(self):
        """Create the numpy file."""
        ncfiles = glob(f'{self.tdata_path}/*')
        nc = Dataset(ncfiles[0], 'r')
        temp_shape = np.shape(self.get_temp(nc, season_idx=0))
        
        Tair_season = np.zeros(( temp_shape[0], temp_shape[1], len(ncfiles) ))
        Tair_avg = np.zeros(( temp_shape[0], temp_shape[1], NUM_OF_SEASONS ))
        for season_idx in range(NUM_OF_SEASONS):
            for ncfile_idx, ncfile in enumerate(ncfiles):
                nc = Dataset(ncfile, 'r')
                Tair_season[:, :, ncfile_idx] = self.get_temp(nc, season_idx=season_idx)
            Tair_avg[:, :, season_idx] = Tair_season.mean(axis=2)
            print(np.shape(Tair_avg))
            np.save(f'./numpy_files/Tair-avg-{season_idx}.npy', Tair_avg)


    @staticmethod
    def get_latlon(nc):
        """Get the latitiude and longitude data. Not used in the
           current implementation."""
        lons = nc.variables['lon'][:].filled(fill_value=np.nan)
        lats = nc.variables['lat'][:].filled(fill_value=np.nan)
        return np.meshgrid(lons, lats)

    @staticmethod
    def get_temp(nc, season_idx=0):
        """Return the 2D temperature field for a given season"""
        return nc.variables['Tair'][season_idx].filled(fill_value=-9999)


    def create_map_image(self, filename, fill_value=-9999, Tmin=200, Tmax=250):
        with open(filename, 'rb') as f:
            data = np.load(f)
        data[data < Tmin] = Tmin
        data[data > Tmax] = Tmax
        cmap = copy(cm.get_cmap("jet"))

        plt.imsave("contour_image2.jpg", data, cmap=cmap)




generator = NumpyFileGenerator()
generator.create_numpy_file()
generator.create_map_image('./numpy_files/Tair2016.npy', Tmin=250, Tmax=1000)