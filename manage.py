from app.simulation import Simulation


def create_simulation_instance(max_time: float, arrivals_interval: float, qty_in_arrival: int) -> Simulation:
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

    transitions_setup_data = [{'str_id': 'ToPreprocessing', 'prob': 0.5, "stats": True, 'priority': 1,
                               'time_distro': {'type_of_distribution': 'const', 'loc': 0}},

                              {'str_id': 'SkipPreprocessing', "stats": True, 'priority': 1,
                               'time_distro': {'type_of_distribution': 'const', 'loc': 0}},

                              {'str_id': 'Preprocessing', "stats": True, 'priority': 2,
                               'time_distro': {'type_of_distribution': 'const', 'loc': 7}},

                              {'str_id': 'Assembling', "stats": True, 'priority': 3,
                               'time_distro': {'type_of_distribution': 'const', 'loc': 6}},

                              {'str_id': 'MarkAsNormal', "stats": True, 'priority': 4,
                               'time_distro': {'type_of_distribution': 'const', 'loc': 0}},

                              {'str_id': 'MarkAsDefect', "stats": True, 'priority': 4,
                               'time_distro': {'type_of_distribution': 'const', 'loc': 0}},

                              {'str_id': 'BackToPreprocessing', "stats": True, 'priority': 5,
                               'time_distro': {'type_of_distribution': 'const', 'loc': 0}},

                              {'str_id': 'Setup', "stats": True, 'priority': 6,
                               'time_distro': {'type_of_distribution': 'exp', 'scale': 8}},
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
    simulation = create_simulation_instance(1000, 10, 3)
    response = simulation.run()
    pass
