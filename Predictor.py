from Logger import Logger
from DataManager import DataManager

logger = Logger()
logger.setup_local()

manager = DataManager()
# manager.manager_nn_inputs.pickle_inputs()
# manager.manager_nn.train_network()
manager.manager_pred.calculate_accuracy()