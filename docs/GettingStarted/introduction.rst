#######################
Introduction
#######################

Workflow for uni-directional soft-linking

.. image:: /images/UnidirectionalSoftlinking.png

Workflow for bi-directional soft-linking

.. image:: /images/BidirectionalSoftlinking.png

Functions
#########

Code:

.. code-block:: python

    def define_units(names):
        """
        Define Units and name them according to source model names (1-1 mapping)
        :param names:   list of unit names
        :return:        power plant database in Dispa-SET readable format
        """
        power_plants = pd.DataFrame(columns=column_names, index=names)
        logging.info('All unit names (' + ' '.join(map(str,names)) + ') assigned to the power plant DataFrame.')
        return power_plants
