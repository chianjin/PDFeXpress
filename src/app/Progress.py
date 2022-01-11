from constants import APP_ICON, TRANSLATER as _
from ui.UiProgress import UiProgress
from utils import get_geometry

PROGRESS_BAR_DELAY = 20


class Progress(UiProgress):
    def __init__(self, master=None, process_list=[], queue=None, maximum=100, auto_destroy=False, **kw):
        super(Progress, self).__init__(master, **kw)

        self.grab_set()
        self.iconbitmap(APP_ICON)
        self.geometry(get_geometry(self, None))
        self.app_info.set(_('Processing...'))

        self._process_list = process_list
        self._queue = queue
        self._maximum = maximum
        self._count = 0
        self._auto_destroy = auto_destroy
        self.status = False

        self.Progressbar.configure(maximum=maximum)
        self.Progressbar.after(PROGRESS_BAR_DELAY, self._get_progress)

    def _get_progress(self):
        while not self._queue.empty():
            self._queue.get()
            self._count += 1

        if self._count:
            self.progress.set(self._count)
            self.process_info.set(f'{self._count} / {self._maximum}')

        if self._process_list:
            alive_list = [process.is_alive() for process in self._process_list]
            if True in alive_list:
                self.Progressbar.after(PROGRESS_BAR_DELAY, self._get_progress)
            else:
                self.status = True
                if self._auto_destroy:
                    self.destroy()
                else:
                    self.app_info.set(_('Completed.'))
                    self.ButtonStop.configure(text=_('OK'), command=self.destroy)

    def stop_process(self):
        for process in self._process_list:
            if process.is_alive():
                process.terminate()
        self.destroy()
