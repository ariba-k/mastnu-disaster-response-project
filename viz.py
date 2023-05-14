import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np


# List of tuples like (grid_size, num_locations, success_rate)
def process_data(raw_results):
    return []


def scatter_plot_3D(results):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    for r in results:
        grid_size, num_locations, success_rate = r
        ax.scatter(grid_size, num_locations, success_rate, c=plt.cm.viridis(success_rate), s=50 * success_rate)

    ax.set_xlabel('Grid Size')
    ax.set_ylabel('Number of Locations')
    ax.set_zlabel('Success Rate')
    plt.show()


def heat_map(results):
    # Create a 2D array to store the success rate for each combination of grid size and number of locations
    grid_sizes = sorted(set(r[0] for r in results))
    num_locations_list = sorted(set(r[1] for r in results))

    heatmap_data = np.zeros((len(grid_sizes), len(num_locations_list)))

    for r in results:
        grid_size, num_locations, success_rate = r
        i = grid_sizes.index(grid_size)
        j = num_locations_list.index(num_locations)
        heatmap_data[i, j] = success_rate

    # Plot the heatmap using seaborn
    ax = sns.heatmap(heatmap_data, annot=True, fmt='.2f', xticklabels=grid_sizes, yticklabels=num_locations_list,
                     cmap='viridis')
    ax.set_xlabel('Grid Size')
    ax.set_ylabel('Number of Locations')
    plt.show()


def sensitivity_analysis(results, fixed_grid_size=None, fixed_num_locations=None):
    # Create a grid for grid size and number of locations
    grid_sizes = sorted(list(set(r[0] for r in results)))
    num_locations_list = sorted(list(set(r[1] for r in results)))

    # Create a grid for success rate
    success_rate_grid = np.zeros((len(num_locations_list), len(grid_sizes)))
    for r in results:
        i = grid_sizes.index(r[0])
        j = num_locations_list.index(r[1])
        success_rate_grid[j, i] = r[2]

    def line_plot():
        if fixed_grid_size is not None:
            fixed_index = grid_sizes.index(fixed_grid_size)
            plt.plot(num_locations_list, success_rate_grid[:, fixed_index], label='Success Rate', marker='o')
            plt.xlabel('Number of Locations')
            plt.ylabel('Success Rate')
            plt.title(f'Success Rate vs Number of Locations (Grid Size = {fixed_grid_size})')
            plt.legend()
            plt.show()

        if fixed_num_locations is not None:
            fixed_index = num_locations_list.index(fixed_num_locations)
            plt.plot(grid_sizes, success_rate_grid[fixed_index, :], label='Success Rate', marker='o')
            plt.xlabel('Grid Size')
            plt.ylabel('Success Rate')
            plt.title(f'Success Rate vs Grid Size (Number of Locations = {fixed_num_locations})')
            plt.legend()
            plt.show()

    def scatter_plot():
        plt.scatter(results[:, 0], results[:, 1], c=results[:, 2], cmap='viridis')
        plt.xlabel('Grid Size')
        plt.ylabel('Number of Locations')
        plt.title('Success Rate vs (Grid Size, Number of Locations)')
        plt.colorbar(label='Success Rate')
        plt.show()

    def surface_plot():
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.plot_surface(np.array(grid_sizes)[None, :], np.array(num_locations_list)[:, None], success_rate_grid,
                        cmap='viridis')
        ax.set_xlabel('Grid Size')
        ax.set_ylabel('Number of Locations')
        ax.set_zlabel('Success Rate')
        plt.title('Success Rate vs (Grid Size, Number of Locations)')
        plt.show()

    line_plot()
    scatter_plot()
    surface_plot()


data = np.array([(grid_size, num_locations, success_rate) for grid_size, num_locations, success_rate in results])
sensitivity_analysis(data, fixed_grid_size=0, fixed_num_locations=0)
