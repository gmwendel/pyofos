from pyofos.roottools import DataExtractor
import matplotlib.pyplot as plt
import numpy as np
import argparse


def plot_truth(input_files):
    data = DataExtractor(input_files)
    hyp = data.get_truth_data()

    xlabels = ['x (mm)', 'y (mm)', 'z (mm)', 'cos(zenith)', 'azimuth (rad)', 't (ns)', 'E (MeV)']
    fig, axs = plt.subplots(2, 4)
    for i in range(7):
        col = i % 4
        row = int(i / 4)
        if i == 3:  # take cos(zenith) for easier visualization
            axs[row, col].hist(np.cos(hyp[:, i]), bins=20)
        else:
            axs[row, col].hist(hyp[:, i], bins=20)
        axs.flat[i].set(xlabel=xlabels[i], ylabel='Number of Events')
    fig.suptitle("Truth Data")
    plt.show()
    return 0


def plot_obs(input_files):
    data = DataExtractor(input_files)
    obs = data.get_flat_obs_data()
    xlabels = ['x hit pos (mm)', 'y hit pos (mm)', 'z hit pos (mm)', 't hit (ns)']
    fig, axs = plt.subplots(1, 4)
    for i in range(4):
        col = i % 4
        row = int(i / 4)
        axs[col].hist(obs[:, i], bins=20)
        axs.flat[i].set(xlabel=xlabels[i], ylabel='Number of hits')
    fig.suptitle("Observational Data")
    plt.show()
    return 0


def plot_img(input_files, event_number=0):
    data = DataExtractor(input_files)
    imgs = data.get_all_images()
    plt.imshow(imgs[event_number])
    clb = plt.colorbar()
    clb.ax.set_title('Number of hits')
    plt.suptitle("Image of event {}".format(event_number))
    plt.show()


def get_args():
    parser = argparse.ArgumentParser(description='Get files to plot truth and observation data')
    parser.add_argument('input_files', nargs='+', help='Input files to plot')
    return parser.parse_args()


if __name__ == '__main__':
    args = get_args()
    plot_truth(args.input_files)
    plot_obs(args.input_files)
    plot_img(args.input_files)
