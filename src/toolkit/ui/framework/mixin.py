# src/toolkit/ui/framework/mixin.py
import multiprocessing
import queue
from tkinter import messagebox

from toolkit.i18n import gettext_text as _
from toolkit.ui.framework.progress_dialog import ProgressDialog


class TaskRunnerMixin:
    """
    A core framework Mixin that provides a complete set of functionalities for running
    background processes, polling queues, and displaying progress.
    """

    def __init__(self, status_callback=None, *args, **kwargs):
        self.progress_dialog = None
        self.worker_process = None
        self.cancel_event = None
        self.progress_queue = None
        self.result_queue = None
        self.status_callback = status_callback
        self.saving_ack_event = None  # Event for synchronizing the saving operation

    # --- 1. Contract Methods ---
    def _get_root_window(self):
        """[Contract] Subclasses must implement this to return the top-level tk.Tk() window."""
        raise NotImplementedError

    def _prepare_task(self):
        """
        [Contract] Subclasses must implement this to validate inputs.
        On success: return (target_function, args_tuple, initial_label)
        On failure: return None (and show an error dialog)
        """
        raise NotImplementedError

    # --- 2. Template Method ---
    def run_task_from_ui(self):
        """
        This is the command for all "Start" buttons.
        It defines the template flow: "prepare -> execute".
        """
        try:
            task_data = self._prepare_task()
        except Exception as e:
            messagebox.showerror(_("Internal Error"), _("Failed to prepare task:\n{}").format(e))
            return

        if task_data is None:
            # Task preparation failed (validation failed)
            return

        try:
            target_function, args_tuple, initial_label = task_data
        except (ValueError, TypeError):
            messagebox.showerror(_("Internal Error"), _("Invalid data provided."))
            return

        self._execute_task(target_function, args_tuple, initial_label)

    # --- 3. Private Implementation ---
    def _execute_task(self, target_function, args_tuple, initial_label):
        self.cancel_event = multiprocessing.Event()
        self.progress_queue = multiprocessing.Queue()
        self.result_queue = multiprocessing.Queue()
        self.saving_ack_event = multiprocessing.Event()  # Event for synchronizing the saving operation

        self.progress_dialog = ProgressDialog(
            self._get_root_window(),
            _("Processing..."),  # Progress dialog title
            initial_label,       # Initial text for the progress dialog
            self.request_cancel
        )

        final_args = args_tuple + (self.cancel_event, self.progress_queue, self.result_queue, self.saving_ack_event)

        self.worker_process = multiprocessing.Process(target=target_function, args=final_args)
        self.worker_process.start()

        self._get_root_window().after(100, self.poll_queues)

    def poll_queues(self):
        """GUI poller (heartbeat)."""
        # 1. Prioritize checking the result queue
        try:
            result = self.result_queue.get_nowait()
            result_type, message = result

            # Task finished
            if self.progress_dialog:
                self.progress_dialog.progressbar.stop()
                if result_type == "SUCCESS":
                    self.progress_dialog.progressbar.config(mode='determinate',
                                                            maximum=self.progress_dialog.progressbar['maximum'],
                                                            value=self.progress_dialog.progressbar['maximum'])

            if result_type == "SUCCESS":
                messagebox.showinfo(_("Complete"), message)
                if self.status_callback:
                    self.status_callback(_("Complete: ") + message)
            elif result_type == "CANCEL":
                messagebox.showwarning(_("Cancelled"), message)
                if self.status_callback:
                    self.status_callback(_("Cancelled: ") + message)
            elif result_type == "ERROR":
                messagebox.showerror(_("Error"), message)
                if self.status_callback:
                    self.status_callback(_("Error: ") + message)

            self.cleanup()
            return  # Task is finished, stop polling

        except queue.Empty:
            pass  # Result queue is empty, continue to check the progress queue

        # 2. Check the progress queue
        try:
            msg = self.progress_queue.get_nowait()
            if not self.progress_dialog:
                pass  # Or handle it, e.g., by logging
            elif isinstance(msg, tuple):
                if msg[0] == "INIT":
                    # Switch to a determinate progress bar
                    self.progress_dialog.label.config(text=_("Processing..."))
                    self.progress_dialog.progressbar.stop()
                    self.progress_dialog.progressbar.config(mode='determinate', maximum=msg[1], value=0)
                    if self.status_callback:
                        self.status_callback(_("Processing..."))
                elif msg[0] == "PROGRESS":
                    # Update progress
                    self.progress_dialog.progressbar['value'] = msg[1]
                elif msg[0] == "SAVING":
                    # Switch to an indeterminate progress bar and update the text
                    self.progress_dialog.progressbar.stop()
                    self.progress_dialog.progressbar.config(mode='indeterminate')
                    self.progress_dialog.progressbar.start()
                    self.progress_dialog.label.config(text=msg[1])
                    if self.status_callback:
                        self.status_callback(msg[1])
                    # Force UI update
                    self._get_root_window().update_idletasks()
                    self.saving_ack_event.set()  # Notify the worker process that the UI has processed the SAVING message
        except queue.Empty:
            pass  # No progress message

        # Schedule the next poll
        self._get_root_window().after(100, self.poll_queues)

    def request_cancel(self):
        """Request cancellation."""
        if self.cancel_event:
            self.cancel_event.set()

    def cleanup(self):
        """GUI cleanup."""
        if self.worker_process and self.worker_process.is_alive():
            self.worker_process.join(timeout=0.5)

        if self.progress_dialog:
            self.progress_dialog.destroy()
            self.progress_dialog = None

        self.worker_process = None
        self.cancel_event = None
