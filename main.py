import argparse
import sys
from models.map_grid import MapGrid


def run_scenario(scenario: int, grid: MapGrid) -> dict | None:
    if scenario == 1:
        from algorithms.ucs import ucs
        return ucs(grid)
    if scenario == 2:
        from algorithms.astar import astar
        return astar(grid)
    if scenario == 3:
        from algorithms.genetic import genetic
        return genetic(grid)
    if scenario == 4:
        from algorithms.idastar import idastar
        return idastar(grid)


def print_result(scenario: int, result: dict | None) -> None:
    if result is None:
        print("No solution found.")
        return

    if scenario == 3:
        print(f"Best makespan (minutes): {result['makespan']:.2f}")
        for agent, info in result['assignments'].items():
            print(
                f"  {agent} at {info['start']} "
                f"assigned targets: {info['targets']} -> coords: {info['coords']}"
            )
    else:
        print(f"Cost: {result['cost']} min")
        print(f"Actions: {result['actions']}")
        print(f"Expanded nodes: {result['expanded']}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description='Intelligent Routing System in Urban Distribution Network'
    )
    parser.add_argument(
        '--scenario', type=int, required=True, choices=[1, 2, 3, 4],
        help='1 = UCS  |  2 = A*  |  3 = Genetic Algorithm  |  4 = IDA*',
    )
    parser.add_argument('--map', type=str, required=True, help='Path to map file')
    parser.add_argument(
        '--visualize', action='store_true',
        help='Print an ASCII map with the solution path overlaid (scenarios 1, 2, 4)',
    )
    args = parser.parse_args()

    try:
        grid = MapGrid.from_file(args.map)
    except FileNotFoundError:
        print(f"Error: map file '{args.map}' not found.", file=sys.stderr)
        sys.exit(1)

    result = run_scenario(args.scenario, grid)
    print_result(args.scenario, result)

    if args.visualize and result and args.scenario != 3:
        from utils.visualize import render_path
        print()
        print(render_path(grid, result['actions']))


if __name__ == '__main__':
    main()
