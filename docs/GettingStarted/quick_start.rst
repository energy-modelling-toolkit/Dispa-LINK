###########################
Quick Start
###########################

For installation instructions see :doc:`installation`.

In principle, the following Dispa-LINK function ``assign_parameters`` with 1-1 mapping type:

.. code:: python

    def assign_parameters(power_plants, values, parameter):
        """
        Populate power plant database with known parameters such as capacity, technology, fuel (1-1 mapping)
        :param power_plants:    power plant database in Dispa-SET readable format
        :param values:          list of parameter values
        :param parameter:       parameter "PowerCapacity, Efficiency etc."
        :return:                power plant database in Dispa-SET readable format
        """
        power_plants[parameter] = values
        logging.info('Mapping of source model ' + parameter + ' to Dispa-SET ' + parameter + ' complete!')
        return power_plants

for a system with 3 power plants can be called as follows:

.. code:: python

    import dispa_link as dl
    import numpy as np
    import pandas as pd

    power_plants = pd.DataFrame(columns=['PowerCapacity','Nunits','Efficiency'])
    values = {'PowerCapacity': [100, 50, 250],
              'Technology': ['COMC', 'GTUR', 'STUR'],
              'Fuel': ['GAS', 'OIL', 'NUC'],
              'Nunits': [1, 1, 2]}
    for parameter in ['PowerCapacity', 'Technology', 'Fuel', 'Nunits']
        power_plants = dl.assign_parameters(power_plants, values, parameter)

and would result in dataframe as follows:

.. csv-table:: List of power plants
    :header: Name, PowerCapacity, Technology, Fuel, Nunits
    :widths: 20, 25, 25, 15, 15

    A, 100MW, COMC, GAS, 1
    B, 50MW, GTUR, OIL, 1
    C, 250MW, STUR, NUC, 2
