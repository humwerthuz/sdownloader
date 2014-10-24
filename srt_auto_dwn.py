import os
import time
import subprocess
from pyinotify import WatchManager, Notifier, ThreadedNotifier
from pyinotify import ProcessEvent, EventsCodes


mask = EventsCodes.ALL_FLAGS['IN_CREATE'] | EventsCodes.ALL_FLAGS['IN_MOVED_TO']
allowed_extensions = ['mkv', 'avi', 'mp4']
target_dir = '/home/humberto/Media/New'


class MyWatcher(ProcessEvent):
  def process_IN_CREATE(self, event):
    self._dispatch_event(event)

  def process_IN_MOVED_TO(self, event):
    self._dispatch_event(event)

  def _dispatch_event(self, event):
    print "New event"
    if event.dir:
      self._process_directory(os.path.join(event.path, event.name))
    else:
      self._process_file(event.path, event.name)

  def _dispatch_download(self, file_path, file_name):
    print "Dispatching download for %s" % file_name
    command = ['/usr/local/bin/periscope', file_name, '-l', 'es', '-l', 'en']

    #Do not wait, and hope for the best!
    #Let the child process output go to stdout/err
    os.chdir(file_path)
    child=subprocess.Popen(command)

  def _process_file(self, file_path, file_name):
    if file_name.split('.')[-1].lower() in allowed_extensions:
      self._dispatch_download(file_path, file_name)
    else:
      print "Skipping %s" % file_name

  def _process_directory(self, dir_path):
    candidates = os.listdir(dir_path)
    print candidates
    for candidate in candidates:
      if candidate.split('.')[-1].lower() in allowed_extensions:
        self._dispatch_download(dir_path, candidate)
      else:
        print "Skipping %s" % candidate

print "SDownloader is now starting..."

wm = WatchManager()

wm.add_watch(target_dir, mask, rec=True, auto_add=True)
print "Sdownloader is now watching %s" % target_dir

notifier = ThreadedNotifier(wm, MyWatcher())
notifier.start()


while True:
  try:
    time.sleep(0.5)
  except (Exception, KeyboardInterrupt):
    notifier.stop()
    break
