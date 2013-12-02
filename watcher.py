#coding=utf-8
import pyinotify
from pyinotify import WatchManager, Notifier, ProcessEvent, ExcludeFilter
from optparse import OptionParser


class processHandler(ProcessEvent):
    def process_IN_CLOSE_WRITE(self, event):
        if event.name == '4913' or event.name.endswith('.swp') or event.name.endswith('.swx'):
            return
        print event
        return

    def process_IN_CLOSE_NOWRITE(self, event):
        print event
        return

    def process_IN_DELETE(self, event):
        if event.name.endswith('.swp') or event.name.endswith('.swx'):
            return
        print event
        return

    def process_IN_MODIFY(self, event):
        if event.name.endswith('.swp') or event.name.endswith('.swx'):
            return
        print event
        return

    def process_IN_MOVED_TO(self, event):
        print event
        return


def optParser():
    optp = OptionParser()
    #settings
    optp.add_option('-d', '--dir', help='directory',
                    dest='dir', default=None)

    opts, args = optp.parse_args()
    return opts.dir


def main():
    target_dir = optParser()

    wm = WatchManager()
    mask = pyinotify.IN_CLOSE_WRITE | pyinotify.IN_DELETE \
        | pyinotify.IN_MODIFY | pyinotify.IN_MOVED_TO | pyinotify.IN_CLOSE_NOWRITE
    excl_list = ['^.*/m3u8$', ]
    excl = ExcludeFilter(excl_list)
    wadd = wm.add_watch('/home/dtynn/work/test/inotify', mask, rec=True, exclude_filter=excl)
    notifier = Notifier(wm, processHandler())
    while True:
        try:
            notifier.process_events()
            if notifier.check_events():
                notifier.read_events()
        except KeyboardInterrupt:
            notifier.stop()
            break
    return


if __name__ == '__main__':
    main()