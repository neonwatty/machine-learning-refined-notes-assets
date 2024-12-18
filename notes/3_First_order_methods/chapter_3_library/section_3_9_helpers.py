import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import gridspec
from IPython.display import clear_output
from mpl_toolkits.mplot3d import proj3d
from matplotlib.patches import FancyArrowPatch
from matplotlib.text import Annotation
from mpl_toolkits.mplot3d.proj3d import proj_transform

from autograd import grad as compute_grad
import autograd.numpy as np
import math
import time


class static_visualizer:
    """
    Illustrate a run of your preferred optimization algorithm on a one or two-input function.  Run
    the algorithm first, and input the resulting weight history into this wrapper.
    """

    ##### draw picture of function and run for single-input function ####
    def single_input_plot(self, g, weight_histories, cost_histories, **kwargs):
        # adjust viewing range
        wmin = -3.1
        wmax = 3.1
        if "wmin" in kwargs:
            wmin = kwargs["wmin"]
        if "wmax" in kwargs:
            wmax = kwargs["wmax"]

        onerun_perplot = False
        if "onerun_perplot" in kwargs:
            onerun_perplot = kwargs["onerun_perplot"]

        ### initialize figure
        fig = plt.figure(figsize=(9, 4))
        artist = fig

        # remove whitespace from figure
        # fig.subplots_adjust(left=0, right=1, bottom=0, top=1) # remove whitespace
        # fig.subplots_adjust(wspace=0.01,hspace=0.01)

        # create subplot with 2 panels, plot input function in center plot
        gs = gridspec.GridSpec(1, 2, width_ratios=[1, 1])
        ax1 = plt.subplot(gs[0])
        ax2 = plt.subplot(gs[1])
        ### plot function in both panels
        w_plot = np.linspace(wmin, wmax, 500)
        g_plot = g(w_plot)
        gmin = np.min(g_plot)
        gmax = np.max(g_plot)
        g_range = gmax - gmin
        ggap = g_range * 0.1
        gmin -= ggap
        gmax += ggap

        # plot function, axes lines
        ax1.plot(w_plot, g_plot, color="k", zorder=2)  # plot function
        ax1.axhline(y=0, color="k", zorder=1, linewidth=0.25)
        ax1.axvline(x=0, color="k", zorder=1, linewidth=0.25)
        ax1.set_xlabel(r"$w$", fontsize=13)
        ax1.set_ylabel(r"$g(w)$", fontsize=13, rotation=0, labelpad=25)
        ax1.set_xlim(wmin, wmax)
        ax1.set_ylim(gmin, gmax)

        ax2.plot(w_plot, g_plot, color="k", zorder=2)  # plot function
        ax2.axhline(y=0, color="k", zorder=1, linewidth=0.25)
        ax2.axvline(x=0, color="k", zorder=1, linewidth=0.25)
        ax2.set_xlabel(r"$w$", fontsize=13)
        ax2.set_ylabel(r"$g(w)$", fontsize=13, rotation=0, labelpad=25)
        ax2.set_xlim(wmin, wmax)
        ax2.set_ylim(gmin, gmax)

        #### loop over histories and plot each
        for j in range(len(weight_histories)):
            w_hist = weight_histories[j]
            c_hist = cost_histories[j]

            # colors for points --> green as the algorithm begins, yellow as it converges, red at final point
            s = np.linspace(0, 1, len(w_hist[: round(len(w_hist) / 2)]))
            s.shape = (len(s), 1)
            t = np.ones(len(w_hist[round(len(w_hist) / 2) :]))
            t.shape = (len(t), 1)
            s = np.vstack((s, t))
            self.colorspec = []
            self.colorspec = np.concatenate((s, np.flipud(s)), 1)
            self.colorspec = np.concatenate((self.colorspec, np.zeros((len(s), 1))), 1)

            ### plot all history points
            ax = ax2
            if onerun_perplot == True:
                if j == 0:
                    ax = ax1
                if j == 1:
                    ax = ax2
            for k in range(len(w_hist)):
                # pick out current weight and function value from history, then plot
                w_val = w_hist[k]
                g_val = c_hist[k]
                ax.scatter(
                    w_val, g_val, s=90, color=self.colorspec[k], edgecolor="k", linewidth=0.5 * (1 / (float(k) + 1)) ** (0.4), zorder=3, marker="X"
                )  # evaluation on function
                ax.scatter(w_val, 0, s=90, facecolor=self.colorspec[k], edgecolor="k", linewidth=0.5 * (1 / (float(k) + 1)) ** (0.4), zorder=3)

    ##### draw picture of function and run for two-input function ####
    def two_input_surface_contour_plot(self, g, w_hist, **kwargs):
        ### input arguments ###
        num_contours = 10
        if "num_contours" in kwargs:
            num_contours = kwargs["num_contours"]

        view = [20, 20]
        if "view" in kwargs:
            view = kwargs["view"]

        ##### construct figure with panels #####
        # construct figure
        fig = plt.figure(figsize=(11, 5))
        self.edgecolor = "k"

        # create subplot with 3 panels, plot input function in center plot
        # this seems to be the best option for whitespace management when using
        # both a surface and contour plot in the same figure
        gs = gridspec.GridSpec(1, 3, width_ratios=[1, 5, 10])
        ax1 = plt.subplot(gs[1], projection="3d")
        ax2 = plt.subplot(gs[2], aspect="equal")
        # remove whitespace from figure
        fig.subplots_adjust(left=0, right=1, bottom=0, top=1)  # remove whitespace
        fig.subplots_adjust(wspace=0.01, hspace=0.01)

        # plot 3d surface and path in left panel
        self.draw_surface(g, ax1, **kwargs)
        self.show_inputspace_path(w_hist, ax1)
        ax1.view_init(view[0], view[1])

        ### make contour right plot - as well as horizontal and vertical axes ###
        self.contour_plot_setup(g, ax2, **kwargs)  # draw contour plot
        self.draw_weight_path(ax2, w_hist)  # draw path on contour plot

        # plot
        plt.show()

    ########################################################################################
    #### utility functions - for setting up / making contour plots, 3d surface plots, etc., ####
    # show contour plot of input function
    def contour_plot_setup(self, g, ax, **kwargs):
        xmin = -3.1
        xmax = 3.1
        ymin = -3.1
        ymax = 3.1
        if "xmin" in kwargs:
            xmin = kwargs["xmin"]
        if "xmax" in kwargs:
            xmax = kwargs["xmax"]
        if "ymin" in kwargs:
            ymin = kwargs["ymin"]
        if "ymax" in kwargs:
            ymax = kwargs["ymax"]
        num_contours = 20
        if "num_contours" in kwargs:
            num_contours = kwargs["num_contours"]

        # choose viewing range using weight history?
        if "view_by_weights" in kwargs:
            view_by_weights = True
            weight_history = kwargs["weight_history"]
            if view_by_weights == True:
                xmin = min([v[0] for v in weight_history])[0]
                xmax = max([v[0] for v in weight_history])[0]
                xgap = (xmax - xmin) * 0.25
                xmin -= xgap
                xmax += xgap

                ymin = min([v[1] for v in weight_history])[0]
                ymax = max([v[1] for v in weight_history])[0]
                ygap = (ymax - ymin) * 0.25
                ymin -= ygap
                ymax += ygap

        ### plot function as contours ###
        self.draw_contour_plot(g, ax, num_contours, xmin, xmax, ymin, ymax)

        ### cleanup panel ###
        ax.set_xlabel("$w_0$", fontsize=14)
        ax.set_ylabel("$w_1$", fontsize=14, labelpad=15, rotation=0)
        ax.axhline(y=0, color="k", zorder=0, linewidth=0.5)
        ax.axvline(x=0, color="k", zorder=0, linewidth=0.5)
        # ax.set_xticks(np.arange(round(xmin),round(xmax)+1))
        # ax.set_yticks(np.arange(round(ymin),round(ymax)+1))

        # set viewing limits
        ax.set_xlim(xmin, xmax)
        ax.set_ylim(ymin, ymax)

    ### function for creating contour plot
    def draw_contour_plot(self, g, ax, num_contours, xmin, xmax, ymin, ymax):
        #### define input space for function and evaluate ####
        w1 = np.linspace(xmin, xmax, 400)
        w2 = np.linspace(ymin, ymax, 400)
        w1_vals, w2_vals = np.meshgrid(w1, w2)
        w1_vals.shape = (len(w1) ** 2, 1)
        w2_vals.shape = (len(w2) ** 2, 1)
        h = np.concatenate((w1_vals, w2_vals), axis=1)
        func_vals = np.asarray([g(np.reshape(s, (2, 1))) for s in h])

        w1_vals.shape = (len(w1), len(w1))
        w2_vals.shape = (len(w2), len(w2))
        func_vals.shape = (len(w1), len(w2))

        ### make contour right plot - as well as horizontal and vertical axes ###
        # set level ridges
        levelmin = min(func_vals.flatten())
        levelmax = max(func_vals.flatten())
        cutoff = 1
        cutoff = (levelmax - levelmin) * cutoff
        numper = 4
        levels1 = np.linspace(cutoff, levelmax, numper)
        num_contours -= numper

        # produce generic contours
        levels2 = np.linspace(levelmin, cutoff, min(num_contours, numper))
        levels = np.unique(np.append(levels1, levels2))
        num_contours -= numper
        while num_contours > 0:
            cutoff = levels[1]
            levels2 = np.linspace(levelmin, cutoff, min(num_contours, numper))
            levels = np.unique(np.append(levels2, levels))
            num_contours -= numper

        # plot the contours
        ax.contour(w1_vals, w2_vals, func_vals, levels=levels[1:], colors="k")
        ax.contourf(w1_vals, w2_vals, func_vals, levels=levels, cmap="Blues")

        ###### clean up plot ######
        ax.set_xlabel("$w_0$", fontsize=12)
        ax.set_ylabel("$w_1$", fontsize=12, rotation=0)
        ax.axhline(y=0, color="k", zorder=0, linewidth=0.5)
        ax.axvline(x=0, color="k", zorder=0, linewidth=0.5)

    ### makes color spectrum for plotted run points - from green (start) to red (stop)
    def make_colorspec(self, w_hist):
        # make color range for path
        s = np.linspace(0, 1, len(w_hist[: round(len(w_hist) / 2)]))
        s.shape = (len(s), 1)
        t = np.ones(len(w_hist[round(len(w_hist) / 2) :]))
        t.shape = (len(t), 1)
        s = np.vstack((s, t))
        colorspec = []
        colorspec = np.concatenate((s, np.flipud(s)), 1)
        colorspec = np.concatenate((colorspec, np.zeros((len(s), 1))), 1)
        return colorspec

    ### function for drawing weight history path
    def draw_grads(self, ax, directions, **kwargs):
        # make colors for plot
        colorspec = self.make_colorspec(directions)

        arrows = True
        if "arrows" in kwargs:
            arrows = kwargs["arrows"]

        # plot axes
        ax.axhline(y=0, color="k", zorder=0, linewidth=0.5)
        ax.axvline(x=0, color="k", zorder=0, linewidth=0.5)

        ### plot function decrease plot in right panel
        for j in range(len(directions)):
            # get current direction
            direction = directions[j]

            # draw arrows connecting pairwise points
            head_length = 0.1
            head_width = 0.1
            ax.arrow(
                0,
                0,
                direction[0],
                direction[1],
                head_width=head_width,
                head_length=head_length,
                fc="k",
                ec="k",
                linewidth=1,
                zorder=2,
                length_includes_head=True,
            )
            ax.arrow(
                0,
                0,
                direction[0],
                direction[1],
                head_width=0.1,
                head_length=head_length,
                fc=colorspec[j],
                ec=colorspec[j],
                linewidth=0.25,
                zorder=2,
                length_includes_head=True,
            )

    ### function for drawing weight history path
    def draw_grads_v2(self, ax, directions, **kwargs):
        arrows = True
        if "arrows" in kwargs:
            arrows = kwargs["arrows"]

        # plot axes
        ax.axhline(y=0, color="k", zorder=0, linewidth=0.5)
        ax.axvline(x=0, color="k", zorder=0, linewidth=0.5)

        ### plot function decrease plot in right panel
        head_length = 0.1
        head_width = 0.1
        alpha = 0.1
        for j in range(len(directions) - 1):
            # get current direction
            direction = directions[j]

            # draw arrows connecting pairwise points
            ax.arrow(
                0,
                0,
                direction[0],
                direction[1],
                head_width=head_width,
                head_length=head_length,
                fc="k",
                ec="k",
                linewidth=3.5,
                zorder=2,
                length_includes_head=True,
                alpha=alpha,
            )
            ax.arrow(
                0,
                0,
                direction[0],
                direction[1],
                head_width=0.1,
                head_length=head_length,
                fc=self.colorspec[j],
                ec=self.colorspec[j],
                linewidth=3,
                zorder=2,
                length_includes_head=True,
                alpha=alpha,
            )

        # plot most recent direction
        direction = directions[-1]
        num_dirs = len(directions)

        # draw arrows connecting pairwise points
        ax.arrow(
            0,
            0,
            direction[0],
            direction[1],
            head_width=head_width,
            head_length=head_length,
            fc="k",
            ec="k",
            linewidth=4,
            zorder=2,
            length_includes_head=True,
        )
        ax.arrow(
            0,
            0,
            direction[0],
            direction[1],
            head_width=0.1,
            head_length=head_length,
            fc=self.colorspec[num_dirs],
            ec=self.colorspec[num_dirs],
            linewidth=3,
            zorder=2,
            length_includes_head=True,
        )

    ### function for drawing weight history path
    def draw_weight_path(self, ax, w_hist, **kwargs):
        # make colors for plot
        colorspec = self.make_colorspec(w_hist)

        arrows = True
        if "arrows" in kwargs:
            arrows = kwargs["arrows"]

        ### plot function decrease plot in right panel
        for j in range(len(w_hist)):
            w_val = w_hist[j]

            # plot each weight set as a point
            ax.scatter(
                w_val[0], w_val[1], s=80, color=colorspec[j], edgecolor=self.edgecolor, linewidth=2 * math.sqrt((1 / (float(j) + 1))), zorder=3
            )

            # plot connector between points for visualization purposes
            if j > 0:
                pt1 = w_hist[j - 1]
                pt2 = w_hist[j]

                # produce scalar for arrow head length
                pt_length = np.linalg.norm(pt1 - pt2)
                head_length = 0.1
                alpha = (head_length - 0.35) / pt_length + 1

                # if points are different draw error
                if np.linalg.norm(pt1 - pt2) > head_length and arrows == True:
                    if np.ndim(pt1) > 1:
                        pt1 = pt1.flatten()
                        pt2 = pt2.flatten()

                    # draw color connectors for visualization
                    w_old = pt1
                    w_new = pt2
                    ax.plot([w_old[0], w_new[0]], [w_old[1], w_new[1]], color=colorspec[j], linewidth=2, alpha=1, zorder=2)  # plot approx
                    ax.plot([w_old[0], w_new[0]], [w_old[1], w_new[1]], color="k", linewidth=3, alpha=1, zorder=1)  # plot approx

                    # draw arrows connecting pairwise points
                    # ax.arrow(pt1[0],pt1[1],(pt2[0] - pt1[0])*alpha,(pt2[1] - pt1[1])*alpha, head_width=0.1, head_length=head_length, fc='k', ec='k',linewidth=4,zorder = 2,length_includes_head=True)
                    # ax.arrow(pt1[0],pt1[1],(pt2[0] - pt1[0])*alpha,(pt2[1] - pt1[1])*alpha, head_width=0.1, head_length=head_length, fc='w', ec='w',linewidth=0.25,zorder = 2,length_includes_head=True)

    ### draw surface plot
    def draw_surface(self, g, ax, **kwargs):
        xmin = -3.1
        xmax = 3.1
        ymin = -3.1
        ymax = 3.1
        if "xmin" in kwargs:
            xmin = kwargs["xmin"]
        if "xmax" in kwargs:
            xmax = kwargs["xmax"]
        if "ymin" in kwargs:
            ymin = kwargs["ymin"]
        if "ymax" in kwargs:
            ymax = kwargs["ymax"]

        #### define input space for function and evaluate ####
        w1 = np.linspace(xmin, xmax, 200)
        w2 = np.linspace(ymin, ymax, 200)
        w1_vals, w2_vals = np.meshgrid(w1, w2)
        w1_vals.shape = (len(w1) ** 2, 1)
        w2_vals.shape = (len(w2) ** 2, 1)
        h = np.concatenate((w1_vals, w2_vals), axis=1)
        func_vals = np.asarray([g(np.reshape(s, (2, 1))) for s in h])

        ### plot function as surface ###
        w1_vals.shape = (len(w1), len(w2))
        w2_vals.shape = (len(w1), len(w2))
        func_vals.shape = (len(w1), len(w2))
        ax.plot_surface(w1_vals, w2_vals, func_vals, alpha=0.1, color="w", rstride=25, cstride=25, linewidth=1, edgecolor="k", zorder=2)

        # plot z=0 plane
        ax.plot_surface(w1_vals, w2_vals, func_vals * 0, alpha=0.1, color="w", zorder=1, rstride=25, cstride=25, linewidth=0.3, edgecolor="k")

        # clean up axis
        ax.xaxis.pane.fill = False
        ax.yaxis.pane.fill = False
        ax.zaxis.pane.fill = False

        ax.xaxis.pane.set_edgecolor("white")
        ax.yaxis.pane.set_edgecolor("white")
        ax.zaxis.pane.set_edgecolor("white")

        ax.xaxis._axinfo["grid"]["color"] = (1, 1, 1, 0)
        ax.yaxis._axinfo["grid"]["color"] = (1, 1, 1, 0)
        ax.zaxis._axinfo["grid"]["color"] = (1, 1, 1, 0)

        ax.set_xlabel("$w_0$", fontsize=14)
        ax.set_ylabel("$w_1$", fontsize=14, rotation=0)
        ax.set_title("$g(w_0,w_1)$", fontsize=14)

    ### plot points and connectors in input space in 3d plot
    def show_inputspace_path(self, w_hist, ax):
        # make colors for plot
        colorspec = self.make_colorspec(w_hist)

        for k in range(len(w_hist)):
            pt1 = w_hist[k]
            ax.scatter(pt1[0], pt1[1], 0, s=60, color=colorspec[k], edgecolor="k", linewidth=0.5 * math.sqrt((1 / (float(k) + 1))), zorder=3)
            if k < len(w_hist) - 1:
                pt2 = w_hist[k + 1]
                if np.linalg.norm(pt1 - pt2) > 10 ** (-3):
                    # draw arrow in left plot
                    a = Arrow3D([pt1[0], pt2[0]], [pt1[1], pt2[1]], [0, 0], mutation_scale=10, lw=2, arrowstyle="-|>", color="k")
                    ax.add_artist(a)


class grad_descent_visualizer:
    """
    Illustrate gradient descent, Newton method, and Secant method for minimizing an input function, illustrating
    surrogate functions at each step.  A custom slider mechanism is used to progress each algorithm, and points are
    colored from green at the start of an algorithm, to yellow as it converges, and red as the final point.
    """

    ######## gradient descent ########
    # run gradient descent
    def run_gradient_descent(self):
        w = self.w_init
        self.w_hist = []
        self.w_hist.append(w)
        w_old = np.inf
        j = 0
        for j in range(int(self.max_its)):
            # update old w and index
            w_old = w

            # plug in value into func and derivative
            grad_eval = self.grad(w)

            # normalized or unnormalized?
            if self.version == "normalized":
                grad_norm = np.linalg.norm(grad_eval)
                if grad_norm == 0:
                    grad_norm += 10**-6 * np.sign(2 * np.random.rand(1) - 1)
                grad_eval /= grad_norm

            # check if diminishing steplength rule used
            alpha = 0
            if self.steplength == "diminishing":
                alpha = 1 / (1 + j)
            else:
                alpha = float(self.steplength)

            # take gradient descent step
            w = w - alpha * grad_eval

            # record
            self.w_hist.append(w)

    ##### draw still image of gradient descent on single-input function ####
    def draw_2d(self, **kwargs):
        self.g = kwargs["g"]  # input function
        self.grad = compute_grad(self.g)  # gradient of input function
        self.w_init = float(-2)  # user-defined initial point (adjustable when calling each algorithm)
        self.alpha = 10**-4  # user-defined step length for gradient descent (adjustable when calling gradient descent)
        self.max_its = 20  # max iterations to run for each algorithm
        self.w_hist = []  # container for algorithm path

        wmin = -3.1
        wmax = 3.1
        if "wmin" in kwargs:
            wmin = kwargs["wmin"]
        if "wmax" in kwargs:
            wmax = kwargs["wmax"]

        # get new initial point if desired
        if "w_inits" in kwargs:
            self.w_inits = kwargs["w_inits"]
            self.w_inits = [float(s) for s in self.w_inits]

        # take in user defined step length
        if "steplength" in kwargs:
            self.steplength = kwargs["steplength"]

        # take in user defined maximum number of iterations
        if "max_its" in kwargs:
            self.max_its = float(kwargs["max_its"])

        # version of gradient descent to use (normalized or unnormalized)
        self.version = "unnormalized"
        if "version" in kwargs:
            self.version = kwargs["version"]

        # initialize figure
        fig = plt.figure(figsize=(9, 4))
        artist = fig

        # remove whitespace from figure
        # fig.subplots_adjust(left=0, right=1, bottom=0, top=1) # remove whitespace
        # fig.subplots_adjust(wspace=0.01,hspace=0.01)

        # create subplot with 2 panels, plot input function in center plot
        gs = gridspec.GridSpec(1, 2, width_ratios=[1, 1])

        ax1 = plt.subplot(gs[0])
        ax2 = plt.subplot(gs[1])
        # generate function for plotting on each slide
        w_plot = np.linspace(wmin, wmax, 500)
        g_plot = self.g(w_plot)
        g_range = max(g_plot) - min(g_plot)
        ggap = g_range * 0.1
        width = 30

        #### loop over all initializations, run gradient descent algorithm for each and plot results ###
        for j in range(len(self.w_inits)):
            # get next initialization
            self.w_init = self.w_inits[j]

            # run grad descent for this init
            self.w_hist = []
            self.run_gradient_descent()

            # colors for points --> green as the algorithm begins, yellow as it converges, red at final point
            s = np.linspace(0, 1, len(self.w_hist[: round(len(self.w_hist) / 2)]))
            s.shape = (len(s), 1)
            t = np.ones(len(self.w_hist[round(len(self.w_hist) / 2) :]))
            t.shape = (len(t), 1)
            s = np.vstack((s, t))
            self.colorspec = []
            self.colorspec = np.concatenate((s, np.flipud(s)), 1)
            self.colorspec = np.concatenate((self.colorspec, np.zeros((len(s), 1))), 1)

            # plot function, axes lines
            ax1.plot(w_plot, g_plot, color="k", zorder=2)  # plot function
            ax1.axhline(y=0, color="k", zorder=1, linewidth=0.25)
            ax1.axvline(x=0, color="k", zorder=1, linewidth=0.25)
            ax1.set_xlabel(r"$w$", fontsize=13)
            ax1.set_ylabel(r"$g(w)$", fontsize=13, rotation=0, labelpad=25)

            ax2.plot(w_plot, g_plot, color="k", zorder=2)  # plot function
            ax2.axhline(y=0, color="k", zorder=1, linewidth=0.25)
            ax2.axvline(x=0, color="k", zorder=1, linewidth=0.25)
            ax2.set_xlabel(r"$w$", fontsize=13)
            ax2.set_ylabel(r"$g(w)$", fontsize=13, rotation=0, labelpad=25)

            ### plot all gradient descent points ###
            for k in range(len(self.w_hist)):
                # pick out current weight and function value from history, then plot
                w_val = self.w_hist[k]
                g_val = self.g(w_val)

                ax2.scatter(
                    w_val, g_val, s=90, color=self.colorspec[k], edgecolor="k", linewidth=0.5 * (1 / (float(k) + 1)) ** (0.4), zorder=3, marker="X"
                )  # evaluation on function
                ax2.scatter(w_val, 0, s=90, facecolor=self.colorspec[k], edgecolor="k", linewidth=0.5 * (1 / (float(k) + 1)) ** (0.4), zorder=3)

    ##### draw still image of gradient descent on single-input function ####
    def compare_versions_2d(self, **kwargs):
        self.g = kwargs["g"]  # input function
        self.grad = compute_grad(self.g)  # gradient of input function
        self.w_init = float(-2)  # user-defined initial point (adjustable when calling each algorithm)
        self.alpha = 10**-4  # user-defined step length for gradient descent (adjustable when calling gradient descent)
        self.max_its = 20  # max iterations to run for each algorithm
        self.w_hist = []  # container for algorithm path

        # get new initial point if desired
        if "w_init" in kwargs:
            self.w_init = float(kwargs["w_init"])

        # take in user defined step length
        if "steplength" in kwargs:
            self.steplength = kwargs["steplength"]

        # take in user defined maximum number of iterations
        if "max_its" in kwargs:
            self.max_its = float(kwargs["max_its"])

        # version of gradient descent to use (normalized or unnormalized)
        self.version = "unnormalized"
        if "version" in kwargs:
            self.version = kwargs["version"]

        # define viewing min and max
        wmin = -3.1
        wmax = 3.1
        if "wmin" in kwargs:
            wmin = kwargs["wmin"]
        if "wmax" in kwargs:
            wmax = kwargs["wmax"]

        # initialize figure
        fig = plt.figure(figsize=(9, 4))
        artist = fig

        # remove whitespace from figure
        # fig.subplots_adjust(left=0, right=1, bottom=0, top=1) # remove whitespace
        # fig.subplots_adjust(wspace=0.01,hspace=0.01)

        # create subplot with 2 panels, plot input function in center plot
        gs = gridspec.GridSpec(1, 2, width_ratios=[1, 1])

        ax1 = plt.subplot(gs[0])
        ax2 = plt.subplot(gs[1])
        # generate function for plotting on each slide
        w_plot = np.linspace(wmin, wmax, 500)
        g_plot = self.g(w_plot)
        g_range = max(g_plot) - min(g_plot)
        ggap = g_range * 0.1
        width = 30

        # plot function, axes lines
        for ax in [ax1, ax2]:
            ax.plot(w_plot, g_plot, color="k", zorder=2)  # plot function
            ax.axhline(y=0, color="k", zorder=1, linewidth=0.25)
            ax.axvline(x=0, color="k", zorder=1, linewidth=0.25)
            ax.set_xlabel(r"$w$", fontsize=13)
            ax.set_ylabel(r"$g(w)$", fontsize=13, rotation=0, labelpad=25)

        ax1.set_title("normalized gradient descent", fontsize=13)
        ax2.set_title("unnormalized gradient descent", fontsize=13)

        ### run normalized gradient descent and plot results ###

        # run normalized gradient descent method
        self.version = "normalized"
        self.w_hist = []
        self.run_gradient_descent()

        # colors for points --> green as the algorithm begins, yellow as it converges, red at final point
        s = np.linspace(0, 1, len(self.w_hist[: round(len(self.w_hist) / 2)]))
        s.shape = (len(s), 1)
        t = np.ones(len(self.w_hist[round(len(self.w_hist) / 2) :]))
        t.shape = (len(t), 1)
        s = np.vstack((s, t))
        self.colorspec = []
        self.colorspec = np.concatenate((s, np.flipud(s)), 1)
        self.colorspec = np.concatenate((self.colorspec, np.zeros((len(s), 1))), 1)

        # plot results
        for k in range(len(self.w_hist)):
            # pick out current weight and function value from history, then plot
            w_val = self.w_hist[k]
            g_val = self.g(w_val)

            ax1.scatter(
                w_val, g_val, s=90, color=self.colorspec[k], edgecolor="k", linewidth=0.5 * (1 / (float(k) + 1)) ** (0.4), zorder=3, marker="X"
            )  # evaluation on function
            ax1.scatter(w_val, 0, s=90, facecolor=self.colorspec[k], edgecolor="k", linewidth=0.5 * (1 / (float(k) + 1)) ** (0.4), zorder=3)

        # run unnormalized gradient descent method
        self.version = "unnormalized"
        self.w_hist = []
        self.run_gradient_descent()

        # plot results
        for k in range(len(self.w_hist)):
            # pick out current weight and function value from history, then plot
            w_val = self.w_hist[k]
            g_val = self.g(w_val)

            ax2.scatter(
                w_val, g_val, s=90, color=self.colorspec[k], edgecolor="k", linewidth=0.5 * (1 / (float(k) + 1)) ** (0.4), zorder=3, marker="X"
            )  # evaluation on function
            ax2.scatter(w_val, 0, s=90, facecolor=self.colorspec[k], edgecolor="k", linewidth=0.5 * (1 / (float(k) + 1)) ** (0.4), zorder=3)


#### custom 3d arrow and annotator functions ###
# nice arrow maker from https://stackoverflow.com/questions/11140163/python-matplotlib-plotting-a-3d-cube-a-sphere-and-a-vector
class Arrow3D(FancyArrowPatch):
    def __init__(self, xs, ys, zs, *args, **kwargs):
        super().__init__((0, 0), (0, 0), *args, **kwargs)
        self._verts3d = xs, ys, zs

    def do_3d_projection(self, renderer=None):
        xs3d, ys3d, zs3d = self._verts3d
        xs, ys, zs = proj3d.proj_transform(xs3d, ys3d, zs3d, self.axes.M)
        self.set_positions((xs[0], ys[0]), (xs[1], ys[1]))

        return np.min(zs)


"""
A collection of animations illustrating the steepest descent direction under the L2, L1, and Linfinity norms.
"""


def L2(pt, num_frames, savepath, **kwargs):
    # initialize figure
    fig = plt.figure(figsize=(16, 8))
    artist = fig

    # create subplot with 3 panels, plot input function in center plot
    gs = gridspec.GridSpec(1, 2, width_ratios=[1, 1], wspace=0.3, hspace=0.05)
    ax1 = plt.subplot(gs[0], aspect="equal")
    ax2 = plt.subplot(gs[1], aspect="equal")
    # create dataset for unit circle
    v = np.linspace(0, 2 * np.pi, 1000)
    s = np.sin(v)
    s.shape = (len(s), 1)
    t = np.cos(v)
    t.shape = (len(t), 1)

    # create span of angles to plot over
    v = np.linspace(0, 2 * np.pi, num_frames)
    a = np.arccos(pt[0] / (pt[0] ** 2 + pt[1] ** 2) ** (0.5)) + np.pi
    v = np.append(v, a)
    v = np.sort(v)
    v = np.unique(v)
    y = np.sin(v)
    x = np.cos(v)

    # create inner product plot
    obj = [(x[s] * pt[0] + y[s] * pt[1]) for s in range(len(v))]
    ind_min = np.argmin(obj)

    # rescale directions for plotting with arrows
    x = 0.96 * x
    y = 0.96 * y

    # create linspace for left panel
    w = np.linspace(0, 2 * np.pi, 300)

    # print update
    num_frames = len(v)
    print("starting animation rendering...")

    # animation sub-function
    def animate(k):
        # clear panels for next slide
        ax1.cla()
        ax2.cla()

        # print rendering update
        if np.mod(k + 1, 25) == 0:
            print("rendering animation frame " + str(k + 1) + " of " + str(num_frames))
        if k == num_frames - 1:
            print("animation rendering complete!")
            time.sleep(1.5)
            clear_output()

        ### setup left panel ###
        # plot circle with lines in left panel
        ax1.plot(s, t, color="k", linewidth=3)

        # plot rotation arrow
        ax1.arrow(0, 0, x[k], y[k], head_width=0.1, head_length=0.1, fc="k", ec="k", linewidth=3, zorder=3, length_includes_head=True)

        # plot input point as arrow
        ax1.arrow(0, 0, pt[0], pt[1], head_width=0.1, head_length=0.1, fc="r", ec="r", linewidth=3, zorder=3, length_includes_head=True)
        ax1.arrow(0, 0, pt[0], pt[1], head_width=0.11, head_length=0.1, fc="k", ec="k", linewidth=5, zorder=2, length_includes_head=True)

        # clean up panel
        ax1.grid(True, which="both")
        ax1.axhline(y=0, color="k")
        ax1.axvline(x=0, color="k")
        ax1.set_xlim([-1.5, 1.5])
        ax1.set_ylim([-1.5, 1.5])

        ### setup right panel ###
        current_angle = v[k]
        ind = np.argmin(np.abs(w - current_angle))
        p = w[: ind + 1]

        # plot normalized objective thus far
        ax2.plot(v[: k + 1], obj[: k + 1], color="k", linewidth=4, zorder=2)

        # if we have reached the minimum plot it on all slides going further
        if k >= ind_min:
            # plot direction
            ax1.arrow(
                0, 0, x[ind_min], y[ind_min], head_width=0.1, head_length=0.1, fc="lime", ec="lime", linewidth=3, zorder=3, length_includes_head=True
            )
            ax1.arrow(
                0, 0, x[ind_min], y[ind_min], head_width=0.11, head_length=0.1, fc="k", ec="k", linewidth=5, zorder=2, length_includes_head=True
            )

            # mark objective plot
            ax2.scatter(v[ind_min], obj[ind_min], color="lime", s=200, linewidth=1, edgecolor="k", zorder=3)

        # cleanup plot
        ax2.grid(True, which="both")
        ax2.axhline(y=0, color="k")
        ax2.axvline(x=0, color="k")
        ax2.set_xlim([-0.1, 2 * np.pi + 0.1])
        ax2.set_ylim([min(obj) - 0.2, max(obj) + 0.2])

        # add legend
        ax2.legend([r"$\nabla g(\mathbf{v})^T \mathbf{d}$"], loc="center left", bbox_to_anchor=(0.13, 1.05), fontsize=18, ncol=2)

        return (artist,)

    anim = animation.FuncAnimation(fig, animate, frames=num_frames, interval=num_frames, blit=True)

    # produce animation and save
    fps = 50
    if "fps" in kwargs:
        fps = kwargs["fps"]
    anim.save(savepath, fps=fps, extra_args=["-vcodec", "libx264"])
    clear_output()


def Linf(pt, num_frames, savepath, **kwargs):
    # initialize figure
    fig = plt.figure(figsize=(16, 8))
    artist = fig

    # create subplot with 3 panels, plot input function in center plot
    gs = gridspec.GridSpec(1, 2, width_ratios=[1, 1], wspace=0.3, hspace=0.05)
    ax1 = plt.subplot(gs[0], aspect="equal")
    ax2 = plt.subplot(gs[1], aspect="equal")
    # create dataset for unit square
    v = np.linspace(0, 2 * np.pi, 2000)
    s = np.sin(v)
    s.shape = (len(s), 1)
    t = np.cos(v)
    t.shape = (len(t), 1)
    square = np.concatenate((s, t), axis=1)
    news = []
    for a in square:
        a = a / np.max(abs(a))
        news.append(a)
    news = np.asarray(news)
    s = news[:, 0]
    t = news[:, 1]

    ### create span of angles to plot over
    v = np.linspace(0, 2 * np.pi, num_frames)

    # make sure corners of the square are included
    v = np.append(v, np.pi / float(4))
    v = np.append(v, np.pi * 3 / float(4))
    v = np.append(v, np.pi * 5 / float(4))
    v = np.append(v, np.pi * 7 / float(4))
    v = np.sort(v)
    v = np.unique(v)
    y = np.sin(v)
    x = np.cos(v)

    # make l2 ball
    x.shape = (len(x), 1)
    y.shape = (len(y), 1)
    l2 = np.concatenate((x, y), axis=1)

    # make Linf ball
    linf = []
    for a in l2:
        a = a / np.max(abs(a))
        linf.append(a)
    linf = np.asarray(linf)
    x = linf[:, 0]
    y = linf[:, 1]

    # create inner product plot
    obj = [(x[s] * pt[0] + y[s] * pt[1]) for s in range(len(v))]
    ind_min = np.argmin(obj)

    # rescale directions for plotting with arrows
    x = 0.96 * x
    y = 0.96 * y

    # create linspace for left panel
    w = np.linspace(0, 2 * np.pi, 300)
    pt = [0.975 * a for a in pt]

    # print update
    num_frames = len(v)
    print("starting animation rendering...")

    # animation sub-function
    def animate(k):
        # clear panels for next slide
        ax1.cla()
        ax2.cla()

        # print rendering update
        if np.mod(k + 1, 25) == 0:
            print("rendering animation frame " + str(k + 1) + " of " + str(num_frames))
        if k == num_frames - 1:
            print("animation rendering complete!")
            time.sleep(1.5)
            clear_output()

        ### setup left panel ###
        # plot circle with lines in left panel
        ax1.plot(s, t, color="k", linewidth=3)

        # plot rotation arrow
        ax1.arrow(0, 0, x[k], y[k], head_width=0.1, head_length=0.1, fc="k", ec="k", linewidth=3, zorder=3, length_includes_head=True)

        # plot input point as arrow
        ax1.arrow(0, 0, pt[0], pt[1], head_width=0.1, head_length=0.1, fc="r", ec="r", linewidth=3, zorder=3, length_includes_head=True)
        ax1.arrow(0, 0, pt[0], pt[1], head_width=0.11, head_length=0.1, fc="k", ec="k", linewidth=5, zorder=2, length_includes_head=True)

        # clean up panel
        ax1.grid(True, which="both")
        ax1.axhline(y=0, color="k")
        ax1.axvline(x=0, color="k")
        ax1.set_xlim([-1.5, 1.5])
        ax1.set_ylim([-1.5, 1.5])

        ### setup right panel ###
        current_angle = v[k]
        ind = np.argmin(np.abs(w - current_angle))
        p = w[: ind + 1]

        # plot normalized objective thus far
        ax2.plot(v[: k + 1], obj[: k + 1], color="k", linewidth=4, zorder=2)

        # if we have reached the minimum plot it on all slides going further
        if k >= ind_min:
            # plot direction
            ax1.arrow(
                0, 0, x[ind_min], y[ind_min], head_width=0.1, head_length=0.1, fc="lime", ec="lime", linewidth=3, zorder=3, length_includes_head=True
            )
            ax1.arrow(
                0, 0, x[ind_min], y[ind_min], head_width=0.11, head_length=0.1, fc="k", ec="k", linewidth=5, zorder=2, length_includes_head=True
            )

            # mark objective plot
            ax2.scatter(v[ind_min], obj[ind_min], color="lime", s=200, linewidth=1, edgecolor="k", zorder=3)

        # cleanup plot
        ax2.grid(True, which="both")
        ax2.axhline(y=0, color="k")
        ax2.axvline(x=0, color="k")
        ax2.set_xlim([-0.1, 2 * np.pi + 0.1])
        ax2.set_ylim([min(obj) - 0.2, max(obj) + 0.2])

        # add legend
        ax2.legend([r"$\nabla g(\mathbf{v})^T \mathbf{d}$"], loc="center left", bbox_to_anchor=(0.13, 1.05), fontsize=18, ncol=2)

        return (artist,)

    anim = animation.FuncAnimation(fig, animate, frames=num_frames, interval=num_frames, blit=True)

    # produce animation and save
    fps = 50
    if "fps" in kwargs:
        fps = kwargs["fps"]
    anim.save(savepath, fps=fps, extra_args=["-vcodec", "libx264"])
    clear_output()
