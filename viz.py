import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from collections import defaultdict
from mpl_toolkits.axes_grid1 import make_axes_locatable


# List of tuples like (grid_size, num_locations, success_rate, runtime)
def process_data(test_objects):
    result_dict = defaultdict(lambda: {'total_tests': 0, 'success_tests': 0, 'total_runtime': 0})

    for test_object in test_objects:
        grid_size = test_object.map_size
        num_locations = len(test_object.locations)
        success = test_object.succeeded
        runtime = test_object.test_time

        result_dict[(grid_size, num_locations)]['total_tests'] += 1
        if success:
            result_dict[(grid_size, num_locations)]['success_tests'] += 1
        result_dict[(grid_size, num_locations)]['total_runtime'] += runtime

    results = [(params[0], params[1], result['success_tests'] / result['total_tests'], result['total_runtime']) for
               params, result in result_dict.items()]

    return results


def scatter_plot_3D(results):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # Adding title to the plot
    plt.title("Success Rate for Different Grid Sizes and Number of Locations")

    norm = plt.Normalize(0, 1)
    # low success rates will be represented by
    # dark blue and high success rates by yellow
    colors = plt.cm.viridis(norm([r[2] for r in results]))
    sc = ax.scatter([r[0] for r in results], [r[1] for r in results], [r[2] for r in results], c=colors,
                    s=50 * np.array([r[2] for r in results]))

    ax.set_xlabel('Grid Size')
    ax.set_ylabel('Number of Locations')
    ax.set_zlabel('Success Rate')

    # Adding colorbar as legend
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.1, axes_class=plt.Axes)
    plt.colorbar(sc, cax=cax, label='Success Rate')

    plt.show()


def heat_map(results):
    # Create a 2D array to store the success rate for each combination of grid size and number of locations
    grid_sizes = sorted(set(r[0] for r in results))

    num_locations_list = sorted(set(r[1] for r in results))

    heatmap_data = np.zeros((len(num_locations_list), len(grid_sizes)))

    for r in results:
        grid_size, num_locations, success_rate, _ = r
        i = grid_sizes.index(grid_size)
        j = num_locations_list.index(num_locations)
        heatmap_data[j, i] = success_rate

    ax = sns.heatmap(heatmap_data, annot=True, fmt='.2f', yticklabels=num_locations_list, xticklabels=grid_sizes,
                     cmap='viridis')
    ax.set_xlabel('Grid Size')
    ax.set_ylabel('Number of Locations')
    ax.set_title('Success Rate for Different Grid Sizes and Number of Locations')

    plt.show()


def sensitivity_analysis(results, num_fixed_vals):
    results = np.array(results)

    grid_sizes = sorted(set(results[:, 0]))
    num_locations_list = sorted(set(results[:, 1]))

    # Create a grid for success rate
    success_rate_grid = np.zeros((len(num_locations_list), len(grid_sizes)))
    # Create a grid for run time
    runtime_grid = np.zeros((len(num_locations_list), len(grid_sizes)))

    for r in results:
        grid_size, num_locations, success_rate, runtime = r
        i = grid_sizes.index(grid_size)
        j = num_locations_list.index(num_locations)
        success_rate_grid[j, i] = success_rate
        runtime_grid[j, i] = runtime

    def line_plot_fixed_grid():
        fixed_grid_sizes = np.linspace(min(grid_sizes), max(grid_sizes), num=num_fixed_vals, dtype=int)
        for fixed_grid_size in fixed_grid_sizes:
            fixed_grid_size_index = np.abs(np.array(grid_sizes) - fixed_grid_size).argmin()
            plt.plot(num_locations_list, success_rate_grid[:, fixed_grid_size_index],
                     label=f"Grid Size = {fixed_grid_size}", marker='o')

        plt.xlabel('Number of Locations')
        plt.ylabel('Success Rate')
        plt.title('Success Rate vs Number of Locations (Fixed Grid Size)')
        plt.legend()
        plt.show()

        for fixed_grid_size in fixed_grid_sizes:
            fixed_grid_size_index = np.abs(np.array(grid_sizes) - fixed_grid_size).argmin()
            plt.plot(num_locations_list, runtime_grid[:, fixed_grid_size_index],
                     label=f"Grid Size = {fixed_grid_size}", marker='o')

        plt.xlabel('Number of Locations')
        plt.ylabel('Runtime')
        plt.title('Runtime vs Number of Locations (Fixed Grid Size)')
        plt.legend()
        plt.show()

    def line_plot_fixed_num_locations():
        fixed_num_locations = np.linspace(min(num_locations_list), max(num_locations_list), num=num_fixed_vals,
                                          dtype=int)
        for fixed_num_location in fixed_num_locations:
            fixed_num_location_index = np.abs(np.array(num_locations_list) - fixed_num_location).argmin()
            plt.plot(grid_sizes, success_rate_grid[fixed_num_location_index, :],
                     label=f"Num Locations = {fixed_num_location}", marker='o')

        plt.xlabel('Grid Size')
        plt.ylabel('Success Rate')
        plt.title('Success Rate vs Grid Size (Fixed Number of Locations)')
        plt.legend()
        plt.show()

        for fixed_num_location in fixed_num_locations:
            fixed_num_location_index = np.abs(np.array(num_locations_list) - fixed_num_location).argmin()
            plt.plot(grid_sizes, runtime_grid[fixed_num_location_index, :],
                     label=f"Num Locations = {fixed_num_location}", marker='o')

        plt.xlabel('Grid Size')
        plt.ylabel('Runtime')
        plt.title('Runtime vs Grid Size (Fixed Number of Locations)')
        plt.legend()
        plt.show()

    line_plot_fixed_grid()
    line_plot_fixed_num_locations()
