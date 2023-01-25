import numpy as np
import pandas as pd

from app.simulation import Simulation


def create_simulation_instance(max_time: float, arrivals_interval: float, qty_in_arrival: int,
                               capacity: int) -> Simulation:
    generator_setup_data = {'time_distro': {'type_of_distribution': 'exp',
                                            'scale': arrivals_interval},
                            'n_per_arrival': qty_in_arrival}

    places_setup_data = [{'str_id': 'Arrival', "stats": True},
                         {'str_id': 'PreprocessingQueue', 'stats': True},
                         {'str_id': 'DetailPreprocessed', 'stats': True},
                         {'str_id': 'DetailPassedPreprocessing', 'stats': True},
                         {'str_id': 'Assembled', 'stats': True},
                         {'str_id': 'Exit', 'stats': True},
                         {'str_id': 'Defect', 'stats': True},
                         {'str_id': 'Normal', 'stats': True}]

    transitions_setup_data = [{'str_id': 'ToPreprocessing', 'prob': 0.48, "stats": True, 'priority': 1,
                               'time_distro': {'type_of_distribution': 'const', 'loc': 0}},

                              {'str_id': 'SkipPreprocessing', "stats": True, 'priority': 1,
                               'time_distro': {'type_of_distribution': 'const', 'loc': 0}},

                              {'str_id': 'Preprocessing', "stats": True, 'priority': 2,
                               'time_distro': {'type_of_distribution': 'const', 'loc': 7},
                               'capacity': capacity},

                              {'str_id': 'Assembling', "stats": True, 'priority': 3,
                               'time_distro': {'type_of_distribution': 'const', 'loc': 6},
                               'capacity': 1},

                              {'str_id': 'MarkAsDefect', 'prob': 0.04, "stats": True, 'priority': 4,
                               'time_distro': {'type_of_distribution': 'const', 'loc': 0}},

                              {'str_id': 'MarkAsNormal', "stats": True, 'priority': 4,
                               'time_distro': {'type_of_distribution': 'const', 'loc': 0}},

                              {'str_id': 'BackToPreprocessing', "stats": True, 'priority': 5,
                               'time_distro': {'type_of_distribution': 'const', 'loc': 0}},

                              {'str_id': 'Setup', "stats": True, 'priority': 6,
                               'time_distro': {'type_of_distribution': 'exp', 'scale': 8},
                               'capacity': 1},
                              ]

    arcs_setup_data = [
                       ('Generator', 'Arrival', 1),
                       ('Arrival', 'ToPreprocessing', 1),
                       ('ToPreprocessing', 'PreprocessingQueue', 1),
                       ('PreprocessingQueue', 'Preprocessing', 1),
                       ('Preprocessing', 'DetailPreprocessed', 1),
                       ('Arrival', 'SkipPreprocessing', 1),
                       ('SkipPreprocessing', 'DetailPassedPreprocessing', 1),
                       ('DetailPreprocessed', 'Assembling', 1),
                       ('DetailPassedPreprocessing', 'Assembling', 1),
                       ('Assembling', 'Assembled', 1),
                       ('Assembled', 'MarkAsDefect', 1),
                       ('Assembled', 'MarkAsNormal', 1),
                       ('MarkAsDefect', 'Defect', 1),
                       ('MarkAsNormal', 'Normal', 1),
                       ('Defect', 'BackToPreprocessing', 1),
                       ('BackToPreprocessing', 'PreprocessingQueue', 2),
                       ('Normal', 'Setup', 1),
                       ('Setup', 'Exit', 1)]

    return Simulation(max_time=max_time,
                      generator=generator_setup_data,
                      places=places_setup_data,
                      transitions=transitions_setup_data,
                      arcs=arcs_setup_data)


if __name__ == '__main__':
    time = 3000
    print_stats = False
    left_stats = np.zeros((1000, 1))
    productivity_stats = np.zeros((1000, 1))

    for n in range(1000):
        simulation = create_simulation_instance(40000, 25, 2, 1)
        response = simulation.run()

        arrival_queue = response['Place_Arrival']['load'][:, 1]
        preprocessing_queue = response['Place_PreprocessingQueue']['load'][:, 1]
        preprocessed_details = response['Place_DetailPreprocessed']['load'][:, 1]
        not_preprocessed_details = response['Place_DetailPassedPreprocessing']['load'][:, 1]
        assembled_normal_queue = response['Place_Normal']['load'][:, 1]
        assembled_defect_queue = response['Place_Defect']['load'][:, 1]

        arrived_details = np.sum(response['Place_Arrival']['append'][:, 1])
        left_details = np.sum(response['Place_Exit']['append'][:, 1])

        left_stats[n] = arrived_details - 2 * left_details
        productivity_stats[n] = 2 * left_details / time * 60

    with open('left.npy', 'wb') as f:
        np.save(f, left_stats)
    with open('productivity.npy', 'wb') as f:
        np.save(f, productivity_stats)

    if print_stats:
        print('\nЗагальна статистика')
        print('Відгуки системи:')
        print(f'Усього деталей в системі {arrived_details - 2 * left_details} шт.')
        print(f'Продуктивність системи {2 * left_details / time * 60:.2f} шт./год.')
        print('\nІнше:')
        print(f'Усього надійшло деталей: {arrived_details}')
        print(f'Усього залишило систему зібраних деталей{left_details}')
        print(f'Усього залишило систему зібраних деталей (в початкових одиницях) {2 * left_details}')
        arrival_series = pd.DataFrame(response['Place_Arrival']['append'])
        exit_series = pd.DataFrame(response['Place_Exit']['append'])
        arrival_series.to_pickle('arrival.pickle')
        exit_series.to_pickle('exit.pickle')

        print('\nЗавантаження черг:')
        print('\t\t\t\t\t\t\tМаксимальне\t\t  Середнє')
        print(f'\tЧерга надходження\t\t\t{np.max(arrival_queue)}\t\t\t\t{np.mean(arrival_queue)}')
        print(f'\tЧерга попередньої обробки\t{np.max(preprocessing_queue)}\t\t\t\t{np.mean(preprocessing_queue)}')
        print(f'\tЧерга на повторну обробку\t{np.max(assembled_defect_queue)}\t\t\t\t{np.mean(assembled_defect_queue)}')
        print(f'\tЧерга на регулювання\t\t{np.max(assembled_normal_queue)}\t\t\t\t{np.mean(assembled_normal_queue)}')
        print('--- --- --- --- --- --- --- --- --- --- --- --- --- --- ---')
        print(f'\tПісля попередньої обробки\t{np.max(preprocessed_details)}\t\t\t{np.mean(preprocessed_details)}')
        print(f'\tБез попередньої обробки\t\t{np.max(not_preprocessed_details)}\t\t\t{np.mean(not_preprocessed_details)}')
