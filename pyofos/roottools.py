import numpy as np
import uproot


class DataExtractor():
    def __init__(self, input_files):
        '''
        :param input_files: list of input files
        Loads a list of input files and extracts the data from the output trees in a root file in various ways
        '''

        if isinstance(input_files, str):
            input_files = [input_files]

        # Validate all files are valid, do not load invalid files
        valid_files = []
        valid_out_keys = []
        for infile in input_files:
            if self.file_isvalid(infile):
                valid_files.append(infile)
                valid_out_keys.append(self.get_valid_out_key(infile))  # This is a temporary hack

        self.out_keys = valid_out_keys
        self.input_files = valid_files

    # Need to define a better way to get the valid outkey if there are several output trees in file
    def get_valid_out_key(self, infile):
        with uproot.open(infile) as file:
            all_out_keys = [out_key for out_key in file.keys() if out_key.startswith('op_hits')]  # filter metas
            all_out_num = np.array([int(out_key[-1]) for out_key in all_out_keys])
            index = np.argmax(all_out_num)
            return all_out_keys[index]

    def file_isvalid(self, infile):
        try:
            with uproot.open(infile) as file:
                if len(file.keys()) > 1:
                    return True
                else:
                    print("Warning: Opening " + infile + " failed")
                    return False

        except:
            print("Warning: Opening " + infile + " failed")
            return False

    def get_flat_obs_data(self):
        obsdata = uproot.concatenate(
            [self.input_files[i] + ":" + self.out_keys[i] for i in range(len(self.input_files))],
            filter_name=['h_pos_x', "h_pos_y", "h_pos_z", 'h_time'], library='np')

        hit_obs = np.stack([
            np.concatenate(obsdata['h_pos_x']).astype(np.float32),
            np.concatenate(obsdata['h_pos_y']).astype(np.float32),
            np.concatenate(obsdata['h_pos_z']).astype(np.float32),
            np.concatenate(obsdata['h_time']).astype(np.float32)
        ]
            , axis=1)

        del obsdata

        return hit_obs

    def get_hyp_data(self):
        truthdata = uproot.concatenate([infile + ":mc_truth;1" for infile in self.input_files],
                                       filter_name=["i_pos_x", "i_pos_y", "i_pos_z", "i_mom_x", "i_mom_y", "i_mom_z",
                                                    "i_time", "i_E"], library='np')
        momentum = np.stack([
            np.array([mom_x[0] for mom_x in truthdata['i_mom_x']]),
            np.array([mom_y[0] for mom_y in truthdata['i_mom_y']]),
            np.array([mom_z[0] for mom_z in truthdata['i_mom_z']])
        ], axis=1)

        x = np.array([pos_x[0] for pos_x in truthdata['i_pos_x']])
        y = np.array([pos_y[0] for pos_y in truthdata['i_pos_y']])
        z = np.array([pos_z[0] for pos_z in truthdata['i_pos_z']])
        az = np.mod(np.arctan2(momentum[:, 1], momentum[:, 0]), 2 * np.pi).astype(np.float32)
        mom_norm = np.linalg.norm(momentum, axis=1)
        ze = np.arccos(momentum[:, 2] / mom_norm).astype(np.float32)
        t = np.array([time[0] for time in truthdata['i_time']])
        energy = np.array([energy[0] for energy in truthdata['i_E']])

        hyp = np.stack([
            x,
            y,
            z,
            ze,
            az,
            t,
            energy
        ], axis=1)

        return hyp

    def get_all_images(self, side_number=None):
        obsdata = uproot.concatenate(
            [self.input_files[i] + ":" + self.out_keys[i] for i in range(len(self.input_files))],
            filter_name=['h_primary_id', "h_pos_y", "h_pos_z"], library='np')

        if side_number is None:
            print(
                "Warning: Number of fibers on a size not specified for image data, will try calculating based on input data")
            side_number = int(len(np.unique(np.concatenate(obsdata['h_primary_id']))) ** 0.5)
            print("Calculated number of fibers on a side is: " + str(side_number))

        imgs = np.array([self.get_one_image(side_number, obs) for obs in obsdata['h_primary_id']])
        return imgs

    def get_one_image(self, side_number, evtdata):
        img = np.zeros(side_number ** 2)
        index, number = np.unique(evtdata, return_counts=True)
        img[index] = number
#        img = np.flip(img) #for some reason index starts at bottom right corner
        img.shape = (side_number, side_number)
        return img
