import logging

def get_logger(name):
  logger = logging.getLogger(name)
  hdlr = logging.FileHandler('../logs/%s.log' % name)
  formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
  hdlr.setFormatter(formatter)
  logger.addHandler(hdlr)
  logger.setLevel(logging.DEBUG)
  return logger

