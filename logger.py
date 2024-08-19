import logging
import sys

# Set the basic configuration for the logger
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(funcName)s - %(filename)s:%(lineno)d \n %(message)s',
                    level=logging.INFO,
                    handlers=[
                        logging.FileHandler('app.log'),  # Log to a file named 'app.log'
                        logging.StreamHandler(sys.stdout)  # Log to the console
                    ])
										
logger = logging.getLogger(__name__)
