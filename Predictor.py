from Logger import Logger
from DataManager import DataManager

# Using average of each stat up to that point in the year:
# TOTAL : 687049
# TOLERANCE +/- 2 POINTS  : 114396 = 16.650%
# TOLERANCE +/- 5 POINTS  : 327886 = 47.724%
# TOLERANCE +/- 10 POINTS : 581320 = 84.611%

logger = Logger()
logger.setup_local()

manager = DataManager()
# manager.manager_nn_inputs.insert_new_inputs()
manager.manager_nn_inputs.pickle_inputs()
# manager.manager_nn_inputs.fix_server_pickle()
# manager.manager_nn.train_network()
# manager.manager_pred.calculate_accuracy()
