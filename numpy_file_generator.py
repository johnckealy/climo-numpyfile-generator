import os
from matplotlib import cm, pyplot as plt
from netCDF4 import Dataset
import numpy as np
from pathlib import Path
# from PIL import Image
from glob import glob
from copy import copy

SEASONS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
Y_SIZE_PX = 3600


class NumpyFileGenerator:

    def __init__(self):
        self.tdata_path = f'./nc_files'


    def create_numpy_file_chunk(self, season_idx, Tair_seasonal_avg, Tair_season, ncfiles, start_x_index, end_x_index):
        """Create the numpy file."""

        for ncfile_idx, ncfile in enumerate(ncfiles):
            print(ncfile)
            nc = Dataset(ncfile, 'r')
            Tair_season[:, :] = self.get_temp(nc, start_x_index, end_x_index, season_idx=season_idx)
            Tair_seasonal_avg[ncfile_idx, :, :] = Tair_season
        Tair_avg = np.mean(Tair_seasonal_avg, axis=0)    
        return Tair_avg


    def create_numpy_file(self):
        ncfiles = glob(f'{self.tdata_path}/*')
        nc = Dataset(ncfiles[0], 'r')
        temp_shape = np.shape(self.get_temp(nc,  start_x_index=0, end_x_index=int(Y_SIZE_PX/2), season_idx=0))

        Tair_season = np.zeros(( temp_shape[0], temp_shape[1] )) 
        Tair_seasonal_avg = np.zeros(( len(ncfiles), temp_shape[0], temp_shape[1] ))
        for season_idx in range(len(SEASONS)):
            print(f'Season {season_idx}')
            Tair_avg_1 = self.create_numpy_file_chunk(season_idx, Tair_seasonal_avg, 
                                                      Tair_season, ncfiles, start_x_index=0, 
                                                      end_x_index=int(Y_SIZE_PX/2))
            Tair_avg_2 = self.create_numpy_file_chunk(season_idx, Tair_seasonal_avg, 
                                                      Tair_season, ncfiles, start_x_index=int(Y_SIZE_PX/2), 
                                                      end_x_index=Y_SIZE_PX)

            Tair_avg = np.concatenate((Tair_avg_1, Tair_avg_2), axis=0)

            np.save(f'./numpy_files/Tair-avg-{SEASONS[season_idx]}.npy', Tair_avg)


    @staticmethod
    def get_latlon(nc):
        """Get the latitiude and longitude data. Not used in the
           current implementation."""
        lons = nc.variables['lon'][:].filled(fill_value=np.nan)
        lats = nc.variables['lat'][:].filled(fill_value=np.nan)
        return np.meshgrid(lons, lats)

    @staticmethod
    def get_temp(nc, start_x_index, end_x_index, season_idx=0):
        """Return the 2D temperature field for a given season"""
        return nc.variables['Tair'][season_idx][start_x_index:end_x_index].filled(fill_value=230)


    def create_map_image(self, filename, fill_value=230, Tmin=200, Tmax=250):
        with open(filename, 'rb') as f:
            data = np.load(f)
        data[data < Tmin] = Tmin
        data[data > Tmax] = Tmax
        # cmap = copy(cm.get_cmap("jet"))

        plt.imsave("contour_image2.jpg", data, cmap='jet')




generator = NumpyFileGenerator()
generator.create_numpy_file()
generator.create_map_image('./numpy_files/Tair-avg-Jan.npy', Tmin=250, Tmax=1000)