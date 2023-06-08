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
        valid_mc_keys = []
        valid_init_mc_keys = []
        for infile in input_files:
            if self.file_isvalid(infile):
                valid_files.append(infile)
                valid_out_keys.append(self.get_valid_out_key(infile))  # This is a temporary hack
                valid_mc_keys.append(self.get_valid_mc_key(infile))
                valid_init_mc_keys.append(self.get_valid_init_mc_key(infile))

        self.out_keys = valid_out_keys
        self.mc_keys = valid_mc_keys
        self.init_mc_keys = valid_init_mc_keys
        self.input_files = valid_files

    # Need to define a better way to get the valid outkey if there are several output trees in file
    def get_valid_out_key(self, infile):
        with uproot.open(infile) as file:
            all_out_keys = [out_key for out_key in file.keys() if out_key.startswith('op_hits')]  # filter metas
            all_out_num = np.array([int(out_key[-1]) for out_key in all_out_keys])
            index = np.argmax(all_out_num)
            return all_out_keys[index]

    def get_valid_mc_key(self, infile):
        with uproot.open(infile) as file:
            all_out_keys = [out_key for out_key in file.keys() if out_key.startswith('mc_truth')]  # filter metas
            all_out_num = np.array([int(out_key[-1]) for out_key in all_out_keys])
            index = np.argmax(all_out_num)
            return all_out_keys[index]

    def get_valid_init_mc_key(self, infile):
        with uproot.open(infile) as file:
            try:
                all_out_keys = [out_key for out_key in file.keys() if out_key.startswith('init_mc')]  # filter metas
                all_out_num = np.array([int(out_key[-1]) for out_key in all_out_keys])
                index = np.argmax(all_out_num)
                return all_out_keys[index]
            except:
                print('no init_mc tree found')
                return None

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

    def get_truth_data(self):
        truthdata = uproot.concatenate(
            [self.input_files[i] + ":" + self.mc_keys[i] for i in range(len(self.input_files))],
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

    def get_init_truth_data(self, stop_num=None, start_num=0):
        if stop_num < start_num:
            raise ValueError('stop_num should be equal to or larger than start_num')

        hypdata = uproot.concatenate(
            [self.input_files[i] + ":" + self.init_mc_keys[i] for i in range(len(self.input_files))],
            filter_name=["mcx", "mcy", "mcz", "mct", "mcu", "mcv", "mcw", "mcke", "mcpid"], library='np')

        if stop_num > len(hypdata['mcx']):
            raise ValueError('stop_num should be equal to or smaller than the total number of events: ',
                             len(hypdata['mcx']))

        mcaz = np.mod(np.arctan2(hypdata['mcv'], hypdata['mcu']), 2 * np.pi).astype(np.float32)[start_num:stop_num]
        mcze = np.arccos(hypdata['mcw']).astype(np.float32)[start_num:stop_num]
        hyp = np.stack([hypdata['mcx'].astype(np.float32)[start_num:stop_num],
                        hypdata['mcy'].astype(np.float32)[start_num:stop_num],
                        hypdata['mcz'].astype(np.float32)[start_num:stop_num],
                        mcze,
                        mcaz,
                        hypdata['mct'].astype(np.float32)[start_num:stop_num],
                        hypdata['mcke'].astype(np.float32)[start_num:stop_num],
                        hypdata['mcpid'].astype(np.float32)[start_num:stop_num]
                        ], axis=1)
        return hyp

    def get_all_images(self, side_number=None, stop_num=None, start_num=0):
        if stop_num < start_num:
            raise ValueError('stop_num should be equal to or larger than start_num')

        obsdata = uproot.concatenate(
            [self.input_files[i] + ":" + self.out_keys[i] for i in range(len(self.input_files))],
            filter_name=['h_primary_id'], library='np')
        if stop_num > len(obsdata['h_primary_id']):
            raise ValueError('stop_num should be equal to or smaller than the total number of events: ',
                             len(obsdata['h_primary_id']))

        if side_number is None:
            print(
                "Warning: Number of fibers on a size not specified for image data, will try calculating based on input data")
            side_number = int(len(np.unique(np.concatenate(obsdata['h_primary_id']))) ** 0.5)
            print("Calculated number of fibers on a side is: " + str(side_number))

        imgs = []
        if stop_num is None:
            stop_num = len(obsdata['h_primary_id'])
        for i in range(start_num, stop_num):
            imgs.append(self.get_one_image(side_number, obsdata['h_primary_id'][i]))

        imgs = np.array(imgs).astype(np.uint16)
        return imgs

    def get_one_image(self, side_number, evtdata):
        img = np.zeros(side_number ** 2)
        index, number = np.unique(evtdata, return_counts=True)
        img[index] = number
        #        img = np.flip(img) #for some reason index starts at bottom right corner
        img.shape = (side_number, side_number)
        return img.astype(np.uint16)

    def get_hitman_train_data(self):
        obsdata = uproot.concatenate(
            [self.input_files[i] + ":" + self.out_keys[i] for i in range(len(self.input_files))],
            filter_name=['h_primary_id', 'h_time'], library='np')

        nhit = np.array([len(hits) for hits in obsdata['h_primary_id']], dtype=np.int32)
        charge_obs = np.stack([
            nhit.astype(np.float32)
        ], axis=1)

        hit_obs = np.stack([
            np.concatenate(obsdata['h_primary_id']).astype(np.float32),
            np.concatenate(obsdata['h_time']).astype(np.float32)
        ]
            , axis=1)

        hit_obs[:, 1] = hit_obs[:, 1] + np.random.exponential(10, len(hit_obs[:, 1]))  # Add random time decay

        del obsdata

        charge_hyp = self.get_init_truth_data()
        hit_hyp = np.repeat(charge_hyp, nhit, axis=0)

        return charge_obs, hit_obs, charge_hyp, hit_hyp

    def get_hitman_reco_data(self):
        obsdata = uproot.concatenate(
            [self.input_files[i] + ":" + self.out_keys[i] for i in range(len(self.input_files))],
            filter_name=['h_primary_id', 'h_time'], library='np')

        charge_hyp = self.get_init_truth_data()

        nhit = np.array([len(hits) for hits in obsdata['h_primary_id']], dtype=np.int32)
        charge_obs = np.stack([
            nhit.astype(np.float32)
        ], axis=1)

        events = []

        for i in range(len(nhit)):
            hit_idx = obsdata['h_primary_id'][i].astype(np.float32)
            hit_t = obsdata['h_time'][i].astype(np.float32)
            hit_t = hit_t + np.random.exponential(10, len(hit_t))  # Add random time decay

            hits = np.stack([
                hit_idx,
                hit_t.astype(np.float32)
            ]
                , axis=1)

            event = {
                "hits": hits,
                "total_charge": charge_obs[i],
                "truth": charge_hyp[i]
            }

        del obsdata

        return events
