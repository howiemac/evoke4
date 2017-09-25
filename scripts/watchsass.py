#!/usr/bin/env python
"""
    Monitor a directory for Sass changes and render to css on change

    Depends on pip install libsass and watchdog

"""
#from sassutils import builder
from sassbuilder import build_directory
import sys
import time
import logging
from watchdog.observers import Observer
from watchdog.events import RegexMatchingEventHandler
from threading import Lock

# Define directories
SASS = 'sass'
CSS = 'css'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')

lock = Lock()


def compile():
    """Compile sass to css"""
    with lock:
        try:
            build_directory(SASS, CSS)
            logging.info('compiled')
        except:
            logging.debug('compilation error', exc_info=True)


class Handler(RegexMatchingEventHandler):
    """Recompile on each file change"""

    def an_event(self, event):
        """"""
        logging.debug(str(event))
        compile()
    on_created = on_modified = on_deleted = on_moved = an_event    


if __name__ == "__main__":
    path = SASS
    event_handler = Handler(regexes=['.*.sass$'], ignore_regexes=['.*.sw.*$'], ignore_directories=True)
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
