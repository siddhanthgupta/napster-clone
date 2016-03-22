'''
Created on 21-Mar-2016

@author: siddhanthgupta
'''
import threading

from communicator import Communicator
import pyinotify


class MyEventHandler(pyinotify.ProcessEvent):

    def process_IN_CREATE(self, event):
        c = Communicator()
        c.add_mapping_for_file(event.pathname.split('/')[-1])
        print('Added mapping via inotify')

    def process_IN_DELETE(self, event):
        print("DELETE event:", event.pathname)

    def process_IN_MODIFY(self, event):
        print("MODIFY event:", event.pathname)


class ThreadFileSync(object):
    """ Threading example class
    The run() method will be started and it will run in the background
    until the application exits.
    """

    def __init__(self):
        """ Constructor
        :type interval: int
        :param interval: Check interval, in seconds
        """
        self.directory = Communicator.doc_folder

        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True                            # Daemonize thread

        # watch manager
        self.wm = pyinotify.WatchManager()
        # Communicator.doc_folder
        self.watch_dict = self.wm.add_watch(
            Communicator.doc_folder, pyinotify.IN_CREATE | pyinotify.IN_DELETE | pyinotify.IN_MODIFY, rec=True)

        # event handler
        eh = MyEventHandler()

        # notifier
        self.notifier = pyinotify.Notifier(self.wm, eh)

        thread.start()                                  # Start the execution

    def run(self):
        self.notifier.loop()

    def remove_watch(self):
        for key, wd in self.watch_dict.items():
            self.wm.rm_watch(wd)
