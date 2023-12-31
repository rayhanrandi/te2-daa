import os
import time

import networkx as nx
import matplotlib.pyplot as plt
import psutil

from utils.dataset import Generator
from utils.visualizer import Visualizer 

from vertex_cover.vc_bnb import BranchAndBound
from vertex_cover.vc_dp import DynamicProgramming


def process_memory() -> int:
    '''
    evaluates memory usage in MB
    '''

    process = psutil.Process(os.getpid())
    mem_info = process.memory_info()
    return mem_info.rss / (1024 ** 2)   # bytes to MB


def vertex_cover_dp(adj_list: dict, N: int) -> set:
    '''
    Run dynamic programming solution for vertex cover
    '''

    # convert adj_list to valid format
    temp = [[] for i in range(N + 1)]
    for i in range(1, N + 1):
        temp[i] = adj_list[i]
    adj_list = temp
    
    dp = DynamicProgramming()
    
    time_start = time.perf_counter()

    vc, mem_usage = dp.solve(adj_list, N)

    time_end = time.perf_counter()

    elapsed = (time_end - time_start) * 1000  # to ms

    return vc, elapsed, mem_usage


def vertex_cover_bnb(adj_list: dict, N: int, cutoff_time: int) -> set:
    '''
    Run branch and bound solution for vertex cover,
    only calculating either 100, 300, or 900 tree nodes.
    '''

    G = nx.from_dict_of_lists(adj_list)

    subgraph = {
        10 ** 4: 100,
        10 ** 5: 300,
        10 ** 6: 900
    }

    nodes = [i for i in range(1, subgraph[N] + 1)]
    subtree = G.subgraph(nodes)

    '''Uncomment to visualize calculated subgraph'''
    # viz = Visualizer()
    # pos = viz.hierarchy_pos(G, 1)
    # nx.draw(subtree, pos, with_labels=True)
    # plt.show()

    bnb = BranchAndBound()

    time_start = time.perf_counter()

    vc, times, cutoff, mem_usage = bnb.solve(subtree, cutoff_time)

    time_end = time.perf_counter()

    for element in vc:
        if element[1]==0:
            vc.remove(element)

    elapsed = (time_end - time_start) * 1000  # to ms
    print(f'[BnB] Times for solutions: {times}')

    return len(vc), elapsed, mem_usage, cutoff, times
    

def main():

    # initialize size of tree
    N = {
        'small': 10 ** 4,
        'medium': 10 ** 5,
        'large': 10 ** 6
    }

    BNB_CUTOFF_TIME = 600

    # leave parameter empty for default generator values (10^4, 10^5, 10^5)
    generator = Generator(N['small'], N['medium'], N['large'])


    print('''
        Rayhan Putra Randi
        2106705644 - DAA A - 1
          ''')
    

    print('Generating dataset...')
    
    dataset = generator.generate()

    print('Dataset generated.\n')

    print(f'''
          Solving for sizes:
          Small : {N['small']}
          Medium: {N['medium']}
          Large : {N['large']}
          ''')

    for size in dataset:

        filename = f'{size}_output.txt'

        with open(os.path.join(os.getcwd(), 'output', filename), "w") as f:
        
            tree_root, adj_list = dataset[size]

            header_dp = f'[DP] Solving for size {size} ({N[size]})...\n'

            print(header_dp, end='')
            f.write(header_dp)

            dp_result, dp_time, dp_mem = vertex_cover_dp(adj_list, len(adj_list))

            print('[DP] Done.')
            f.write('[DP] Done.\n')

            dp_write_result = f'[DP] Total minimum vertex cover: {dp_result}\n'
            dp_write_time = f'[DP] Elapsed time: {dp_time:.2f} ms.\n'
            dp_write_mem = f'[DP] Memory usage: {dp_mem} MB.\n\n'

            print(dp_write_result, end='')
            f.write(dp_write_result)

            print(dp_write_time, end='')
            f.write(dp_write_time)

            print(dp_write_mem, end='')
            f.write(dp_write_mem)

            header_bnb = f'[BnB] Solving for size {size} ({N[size]}) (subgraph only, cutoff time {BNB_CUTOFF_TIME}s)...\n'
            
            print(header_bnb, end='')
            f.write(header_bnb)

            bnb_result, bnb_time, bnb_mem, cutoff, times = vertex_cover_bnb(adj_list, len(adj_list), BNB_CUTOFF_TIME)

            print('[BnB] Done.')
            f.write('[BnB] Done.\n')

            if cutoff:
                bnb_write_cutoff = '[BnB] CUTOFF TIME REACHED'
                print(bnb_write_cutoff, end='\n')
                f.write(bnb_write_cutoff + '\n')

                bnb_write_result = f'[BnB] Found vertex cover: {bnb_result}\n'
                
            else:
                bnb_write_result = f'[BnB] Total minimum vertex cover: {bnb_result}\n'

            bnb_write_time = f'[BnB] Elapsed time for found vertex cover: {(times[-1][-1] * 1000):.2f} ms.\n'  # to ms
            bnb_write_total_time = f'[BnB] Total elapsed time: {bnb_time:.2f} ms.\n'
            bnb_write_mem = f'[BnB] Memory usage: {bnb_mem} MB.\n'


            print(bnb_write_result, end='')
            f.write(bnb_write_result)

            print(bnb_write_time, end='')
            f.write(bnb_write_time)

            print(bnb_write_total_time, end='')
            f.write(bnb_write_total_time)

            print(bnb_write_mem, end='')
            f.write(bnb_write_mem)

            print('\n')
            f.write('\n\n')

            '''
            Uncomment to visualize full tree
            '''
            # G = nx.from_dict_of_lists(adj_list)

            # print("Adjacency List:")
            # print(adj_list)

            # viz = Visualizer()
            # pos = viz.hierarchy_pos(G, 1)
            # nx.draw(G, pos, with_labels=True)
            # plt.show()
    
    print('''
          Done.
          Results exported to ./output/
          ''')
        


if __name__ == '__main__':

    main()
