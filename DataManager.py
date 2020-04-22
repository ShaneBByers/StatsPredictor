import logging
import Constants
from DataManagerNHL import DataManagerNHL
from DataManagerFD import DataManagerFD
from DataManagerPRED import DataManagerPRED
from DataManagerLP import DataManagerLP
from DataManagerNNInputs import DataManagerNNInputs
from DataManagerNN import DataManagerNN
from database import database


class DataManager:

    def __init__(self, all_active=True):
        self.logger = logging.getLogger(__name__)

        self.logger.debug("Initiating DB connection to " +
                          Constants.DB_NAME +
                          " on " +
                          Constants.DB_HOST +
                          " using user " +
                          Constants.DB_USERNAME +
                          " and password " +
                          Constants.DB_PASSWORD +
                          ".")

        self.db_manager = database.connect(Constants.DB_HOST,
                                           Constants.DB_USERNAME,
                                           Constants.DB_PASSWORD,
                                           Constants.DB_NAME)

        self.logger.info("Successfully connected to " + Constants.DB_NAME)

        if all_active:
            self.manager_nhl = DataManagerNHL(self.db_manager)
            self.manager_fd = DataManagerFD(self.db_manager)
            self.manager_pred = DataManagerPRED(self.db_manager)
            self.manager_lp = DataManagerLP(self.db_manager)
            self.manager_nn_inputs = DataManagerNNInputs(self.db_manager)
            self.manager_nn = DataManagerNN(self.db_manager)

    def update_classes_file(self, file_name):
        self.db_manager.update_classes_file(file_name)

    def current_day_functions(self):
        self.manager_nhl.current_day_functions()
        self.manager_fd.current_day_functions()
        self.manager_pred.current_day_functions()
        self.manager_lp.current_day_functions()
