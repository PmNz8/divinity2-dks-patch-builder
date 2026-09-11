"""Tkinter desktop shell for the DKS Patch Builder.

The frontend is deliberately thin: all archive, package, planning and
transaction work remains in :class:`BuilderController`.  Tk and dialogs stay
on the main thread while every controller call is serialized through one
worker executor.
"""

# SPDX-FileCopyrightText: 2026 PmNz8
# SPDX-License-Identifier: AGPL-3.0-only

from __future__ import annotations

from concurrent.futures import Future, ThreadPoolExecutor
import json
from pathlib import Path
from queue import Queue, Empty, Full
from threading import Event
import webbrowser
from typing import Any, Callable

from .archive_factory import DKS_PATCH_FILE_NAME
from .controller import BuilderController
from .version import APP_NAME, COPYRIGHT, LICENSE_NAME, PROFILE_URL, VERSION


WINDOW_TITLE = f"Divinity II {APP_NAME} {VERSION}"
FOOTER_TEXT = f"{COPYRIGHT} · AGPLv3 ({LICENSE_NAME}) · No warranty"
ABOUT_TEXT = (
    f"Divinity II {APP_NAME} {VERSION}\n\n"
    f"{COPYRIGHT}\n"
    "Licensed under GNU AGPL-3.0-only. Redistribution is permitted only under "
    "the license terms. LICENSE and third-party notices are beside the executable. "
    "The matching source ZIP accompanies this release.\n\n"
    "No warranty is provided; use the tool and modified archives at your own risk."
)
DKS_FILE_TYPES = ("DV2 archives", "*.dv2"), ("All files", "*.*")
POLL_MS = 30
FILTER_DELAY_MS = 200


class TkDialogAdapter:
    """Main-thread file-dialog adapter with cancellation represented by ``None``."""

    def __init__(self, root: Any, filedialog_module: Any):
        self.root = root
        self.filedialog = filedialog_module

    @staticmethod
    def _path(value: Any) -> str | None:
        if value is None or value == "":
            return None
        if isinstance(value, (tuple, list)):
            return None if not value else TkDialogAdapter._path(value[0])
        return str(value)

    def choose_packed_folder(self) -> str | None:
        return self._path(
            self.filedialog.askdirectory(
                parent=self.root,
                title="Choose complete Packed root",
            )
        )

    def choose_existing_dks(self) -> str | None:
        return self._path(
            self.filedialog.askopenfilename(
                parent=self.root,
                title="Open selected DKS_Patch.dv2",
                filetypes=DKS_FILE_TYPES,
            )
        )

    def choose_new_dks(self) -> str | None:
        return self._path(
            self.filedialog.asksaveasfilename(
                parent=self.root,
                title="Create DKS_Patch.dv2",
                initialfile=DKS_PATCH_FILE_NAME,
                defaultextension=".dv2",
                filetypes=DKS_FILE_TYPES,
            )
        )

    def choose_asset_package(self) -> str | None:
        return self._path(
            self.filedialog.askdirectory(
                parent=self.root,
                title="Choose exported asset package",
            )
        )

    def choose_save_as(self) -> str | None:
        return self._path(
            self.filedialog.asksaveasfilename(
                parent=self.root,
                title="Save DKS_Patch.dv2 As",
                initialfile=DKS_PATCH_FILE_NAME,
                defaultextension=".dv2",
                filetypes=DKS_FILE_TYPES,
            )
        )


# Retain the old public name for callers that imported the dialog adapter; it
# now means the native Tk adapter and has no dependency on the old frontend.
NativeDialogAdapter = TkDialogAdapter


class DesktopBuilderController(BuilderController):
    """Named controller type used by the Tk frontend and tests."""


class BuilderTkApp:
    """Tk view/controller shell over one serialized BuilderController worker."""

    def __init__(
        self,
        *,
        root: Any,
        tk_module: Any,
        ttk_module: Any,
        filedialog_module: Any,
        messagebox_module: Any,
        controller: BuilderController | None = None,
        browser_opener: Callable[[str], Any] | None = None,
        executor: Any | None = None,
    ) -> None:
        self.root = root
        self.tk = tk_module
        self.ttk = ttk_module
        self.filedialog = filedialog_module
        self.messagebox = messagebox_module
        self.controller = controller or DesktopBuilderController()
        self.dialogs = TkDialogAdapter(root, filedialog_module)
        self.browser_opener = browser_opener or webbrowser.open_new_tab
        self.executor = executor or ThreadPoolExecutor(
            max_workers=1,
            thread_name_prefix="dks-patch-builder-backend",
        )
        self.future: Future[Any] | None = None
        self._future_callback: Callable[[dict[str, object]], None] | None = None
        self._future_description = ""
        self._filter_after_id: Any | None = None
        self._snapshot: dict[str, object] = {
            "opened": False,
            "packed_root": None,
            "selected_dks": None,
            "selected_sha256": None,
            "selected_size": None,
            "entry_count": 0,
            "pending_count": 0,
            "dirty": False,
        }
        self.entries: list[dict[str, object]] = []
        self.pending: list[dict[str, object]] = []
        self.closing_requested = False
        self.closed = False
        self.busy = False
        self._batch_cancel = Event()
        self._batch_progress = Queue(maxsize=1)
        self._mutable_widgets: list[Any] = []

        self.filter_var = self.tk.StringVar(value="")
        self.status_var = self.tk.StringVar(value="Ready")
        self.packed_var = self.tk.StringVar(value="Packed root: —")
        self.selected_var = self.tk.StringVar(value="Selected DKS: —")
        self.pending_var = self.tk.StringVar(value="Pending: 0")
        self.busy_var = self.tk.StringVar(value="Idle")
        self._build_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.request_exit)
        self._submit(self.controller.state, self._on_state_response, "state")

    def _button(
        self,
        parent: Any,
        text: str,
        command: Callable[[], None],
        name: str,
        *,
        pack: bool = True,
    ) -> Any:
        button = self.ttk.Button(parent, text=text, command=command)
        if pack:
            button.pack(side="left", padx=2)
        self._mutable_widgets.append(button)
        setattr(self, f"{name}_button", button)
        return button

    def _build_ui(self) -> None:
        self.root.title(WINDOW_TITLE)
        self.root.geometry("1320x900")
        self.root.minsize(1000, 650)

        toolbar = self.ttk.Frame(self.root, padding=6)
        toolbar.grid(row=0, column=0, sticky="ew")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(2, weight=1)
        for text, callback, name in (
            ("New", self.request_new, "new"),
            ("Open", self.request_open, "open"),
            ("Close", self.request_close_archive, "close"),
            ("Import Package", self.request_import_package, "import_package"),
            ("Import Batch", self.request_import_batch, "import_batch"),
            ("Save", self.request_save, "save"),
            ("Save As", self.request_save_as, "save_as"),
            ("About", self.show_about, "about"),
        ):
            self._button(toolbar, text, callback, name)
        self.busy_label = self.ttk.Label(toolbar, textvariable=self.busy_var)
        self.batch_cancel_button = self.ttk.Button(toolbar,
            text="Stop batch", command=self._batch_cancel.set)
        self.batch_cancel_button.pack(side="left", padx=2)
        self.busy_label.pack(side="right", padx=8)
        self.status_label = self.ttk.Label(toolbar, textvariable=self.status_var)
        self.status_label.pack(side="right", padx=8)

        info = self.ttk.Frame(self.root, padding=(8, 0, 8, 6))
        info.grid(row=1, column=0, sticky="ew")
        info.columnconfigure(0, weight=1)
        info.columnconfigure(1, weight=1)
        self.ttk.Label(info, textvariable=self.packed_var).grid(row=0, column=0, sticky="w")
        self.ttk.Label(info, textvariable=self.selected_var).grid(row=0, column=1, sticky="w")
        self.ttk.Label(info, textvariable=self.pending_var).grid(row=0, column=2, sticky="e")

        body = self.ttk.Frame(self.root, padding=(8, 0, 8, 6))
        body.grid(row=2, column=0, sticky="nsew")
        body.columnconfigure(0, weight=1)
        body.columnconfigure(1, weight=2)
        body.rowconfigure(0, weight=1)

        left = self.ttk.Frame(body)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        left.columnconfigure(0, weight=1)
        left.rowconfigure(2, weight=1)
        self.ttk.Label(left, text="Filter entries").pack(anchor="w")
        self.filter_entry = self.ttk.Entry(left, textvariable=self.filter_var, width=34)
        self.filter_entry.pack(fill="x", pady=(2, 4))
        self._mutable_widgets.append(self.filter_entry)
        self._trace_filter()
        filter_buttons = self.ttk.Frame(left)
        filter_buttons.pack(fill="x")
        self._button(filter_buttons, "Reset", self.reset_filter, "reset_filter")

        self.ttk.Label(left, text="Entries").pack(anchor="w", pady=(8, 2))
        entry_frame = self.ttk.Frame(left)
        entry_frame.pack(fill="both", expand=True)
        entry_frame.columnconfigure(0, weight=1)
        entry_frame.rowconfigure(0, weight=1)
        self.entry_tree = self.ttk.Treeview(
            entry_frame,
            columns=("path", "storage", "size", "pending"),
            show="headings",
            selectmode="browse",
            height=22,
        )
        for column, heading, width in (
            ("path", "Path", 300),
            ("storage", "Storage", 86),
            ("size", "Size", 82),
            ("pending", "Pending", 100),
        ):
            self.entry_tree.heading(column, text=heading)
            self.entry_tree.column(column, width=width, anchor="w")
        self.entry_tree.grid(row=0, column=0, sticky="nsew")
        entry_y = self.ttk.Scrollbar(entry_frame, orient="vertical", command=self.entry_tree.yview)
        entry_y.grid(row=0, column=1, sticky="ns")
        entry_x = self.ttk.Scrollbar(entry_frame, orient="horizontal", command=self.entry_tree.xview)
        entry_x.grid(row=1, column=0, sticky="ew")
        self.entry_tree.configure(yscrollcommand=entry_y.set, xscrollcommand=entry_x.set)
        self.entry_tree.bind("<<TreeviewSelect>>", self._on_entry_selected)
        self._mutable_widgets.append(self.entry_tree)
        remove_frame = self.ttk.Frame(left)
        remove_frame.pack(fill="x", pady=(4, 0))
        self.remove_button = self._button(
            remove_frame, "Remove Override", self.request_remove_override, "remove"
        )

        center = self.ttk.Frame(body)
        center.grid(row=0, column=1, sticky="nsew")
        center.columnconfigure(0, weight=1)
        center.rowconfigure(1, weight=1)
        center.rowconfigure(4, weight=1)

        self.ttk.Label(center, text="Pending operations").grid(row=0, column=0, sticky="w")
        pending_frame = self.ttk.Frame(center)
        pending_frame.grid(row=1, column=0, sticky="nsew")
        pending_frame.columnconfigure(0, weight=1)
        pending_frame.rowconfigure(0, weight=1)
        self.pending_tree = self.ttk.Treeview(
            pending_frame,
            columns=("order", "action", "target", "warnings"),
            show="headings",
            selectmode="browse",
            height=10,
        )
        for column, heading, width in (
            ("order", "#", 42),
            ("action", "Action", 120),
            ("target", "Target", 360),
            ("warnings", "Warnings", 300),
        ):
            self.pending_tree.heading(column, text=heading)
            self.pending_tree.column(column, width=width, anchor="w")
        self.pending_tree.grid(row=0, column=0, sticky="nsew")
        pending_y = self.ttk.Scrollbar(pending_frame, orient="vertical", command=self.pending_tree.yview)
        pending_y.grid(row=0, column=1, sticky="ns")
        pending_x = self.ttk.Scrollbar(pending_frame, orient="horizontal", command=self.pending_tree.xview)
        pending_x.grid(row=1, column=0, sticky="ew")
        self.pending_tree.configure(yscrollcommand=pending_y.set, xscrollcommand=pending_x.set)
        self.pending_tree.bind("<<TreeviewSelect>>", self._on_pending_selected)
        self._mutable_widgets.append(self.pending_tree)

        pending_buttons = self.ttk.Frame(center)
        pending_buttons.grid(row=2, column=0, sticky="w", pady=(4, 8))
        self._button(pending_buttons, "Preview", self.request_preview, "preview")
        self._button(pending_buttons, "Cancel Selected", self.request_cancel_pending, "cancel_pending")
        self._button(pending_buttons, "Clear Pending", self.request_clear_pending, "clear_pending")

        self.ttk.Label(center, text="Plan / operation report").grid(row=3, column=0, sticky="nw")
        report_frame = self.ttk.Frame(center)
        report_frame.grid(row=4, column=0, sticky="nsew")
        center.rowconfigure(4, weight=1)
        self.report_text = self.tk.Text(report_frame, height=12, wrap="word", state="disabled")
        self.report_text.pack(side="left", fill="both", expand=True)
        report_scroll = self.ttk.Scrollbar(report_frame, orient="vertical", command=self.report_text.yview)
        report_scroll.pack(side="right", fill="y")
        self.report_text.configure(yscrollcommand=report_scroll.set)

        footer = self.ttk.Frame(self.root, padding=(8, 0, 8, 6))
        footer.grid(row=3, column=0, sticky="ew")
        footer.columnconfigure(0, weight=1)
        self.ttk.Label(footer, text="New creates an archive; queued changes are written only by Save / Save As.").grid(
            row=0, column=0, sticky="w"
        )
        profile = self.tk.Label(footer, text="PmNz8 profile", cursor="hand2")
        profile.grid(row=0, column=1, sticky="e")
        profile.bind("<Button-1>", self.open_profile)
        self.ttk.Label(footer, text=FOOTER_TEXT).grid(row=1, column=0, columnspan=2, sticky="w")

    def _trace_filter(self) -> None:
        callback = lambda *_args: self._schedule_filter_refresh()
        if hasattr(self.filter_var, "trace_add"):
            self.filter_var.trace_add("write", callback)
        elif hasattr(self.filter_var, "trace"):
            self.filter_var.trace("w", callback)

    def _set_status(self, message: str, *, error: bool = False) -> None:
        self.status_var.set(message)
        try:
            self.status_label.configure(foreground="#b00020" if error else "")
        except Exception:
            pass

    def _set_report(self, value: object) -> None:
        try:
            text = json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True, default=str)
        except Exception:
            text = str(value)
        self.report_text.configure(state="normal")
        self.report_text.delete("1.0", "end")
        self.report_text.insert("end", text)
        self.report_text.configure(state="disabled")

    def _apply_snapshot(self, state: object) -> None:
        if not isinstance(state, dict):
            return
        self._snapshot = dict(state)
        packed = state.get("packed_root") or "—"
        selected = state.get("selected_dks") or "—"
        pending_count = state.get("pending_count", 0)
        self.packed_var.set(f"Packed root: {packed}")
        self.selected_var.set(f"Selected DKS: {selected}")
        self.pending_var.set(f"Pending: {pending_count}")

    def _handle_response(self, response: object, *, show_report: bool = True) -> bool:
        if not isinstance(response, dict):
            response = {
                "ok": False,
                "error": f"unexpected controller response: {response!r}",
                "error_type": "TypeError",
            }
        state = response.get("state")
        if isinstance(state, dict):
            self._apply_snapshot(state)
        if show_report:
            self._set_report(response)
        if response.get("ok") is True:
            self._set_status("Ready")
            return True
        message = response.get("error") or response.get("reason") or "operation failed"
        self._set_status(str(message), error=True)
        return False

    def _update_action_states(self) -> None:
        if self.busy or self.closed or self.closing_requested:
            return
        opened = bool(self._snapshot.get("opened"))
        dirty = bool(self._snapshot.get("dirty"))
        for widget in self._mutable_widgets:
            self._set_widget_enabled(widget, True)
        for name, enabled in (
            ("close_button", opened),
            ("import_package_button", opened),
            ("import_batch_button", opened),
            ("save_button", opened and dirty),
            ("save_as_button", opened and dirty),
            ("remove_button", opened and bool(self.entry_tree.selection())),
            ("preview_button", bool(self.pending_tree.selection())),
            ("cancel_pending_button", bool(self.pending_tree.selection())),
            ("clear_pending_button", dirty),
        ):
            button = getattr(self, name, None)
            if button is not None:
                self._set_widget_enabled(button, enabled)

    @staticmethod
    def _set_widget_enabled(widget: Any, enabled: bool) -> None:
        try:
            state = getattr(widget, "state", None)
            if callable(state):
                state(["!disabled"] if enabled else ["disabled"])
            else:
                widget.configure(state="normal" if enabled else "disabled")
        except Exception:
            pass

    def _set_busy(self, value: bool) -> None:
        self.busy = value
        self.busy_var.set("Busy" if value else "Idle")
        if value:
            for widget in self._mutable_widgets:
                self._set_widget_enabled(widget, False)
        else:
            self._update_action_states()

    def _submit(
        self,
        operation: Callable[[], Any],
        callback: Callable[[dict[str, object]], None],
        description: str,
    ) -> bool:
        if self.future is not None or self.closed:
            return False
        self._set_busy(True)
        self._future_callback = callback
        self._future_description = description
        try:
            self.future = self.executor.submit(operation)
        except Exception as error:
            self.future = None
            self._set_busy(False)
            self._handle_response({"ok": False, "error": str(error), "error_type": type(error).__name__})
            return False
        self.root.after(POLL_MS, self._poll_future)
        return True

    def _poll_future(self) -> None:
        self._show_batch_progress()
        future = self.future
        if future is None:
            return
        if not future.done():
            self.root.after(POLL_MS, self._poll_future)
            return
        self.future = None
        callback = self._future_callback
        self._future_callback = None
        try:
            result = future.result()
        except Exception as error:
            result = {"ok": False, "error": str(error), "error_type": type(error).__name__}
        self._set_busy(False)
        if callback is not None:
            callback(result if isinstance(result, dict) else {"ok": False, "error": str(result)})
        if self.future is None and not self.closed:
            self._update_action_states()
        if self.closing_requested and self.future is None and not self.closed:
            self._begin_exit()

    def _confirm_discard(self, operation: str) -> bool | None:
        if not bool(self._snapshot.get("dirty")) and not int(self._snapshot.get("pending_count", 0) or 0):
            return False
        try:
            accepted = self.messagebox.askyesno(
                "Discard pending changes?",
                f"Discard pending changes before {operation}?",
                parent=self.root,
            )
        except Exception as error:
            self._set_status(str(error), error=True)
            return None
        return True if accepted else None

    def _request_allowed(self) -> bool:
        return not self.busy and not self.closed and not self.closing_requested

    def _choose_paths(self, *, new: bool) -> tuple[str, str] | None:
        try:
            packed = self.dialogs.choose_packed_folder()
            if packed is None:
                return None
            selected = self.dialogs.choose_new_dks() if new else self.dialogs.choose_existing_dks()
            if selected is None:
                return None
            return packed, selected
        except Exception as error:
            self._set_status(str(error), error=True)
            return None

    def request_new(self) -> None:
        if not self._request_allowed():
            return
        paths = self._choose_paths(new=True)
        if paths is None:
            return
        discard = self._confirm_discard("creating a new archive")
        if discard is None:
            return
        self._submit(
            lambda: self.controller.create_archive(paths[0], paths[1], discard_pending=bool(discard)),
            self._on_opened,
            "create archive",
        )

    def request_open(self) -> None:
        if not self._request_allowed():
            return
        paths = self._choose_paths(new=False)
        if paths is None:
            return
        discard = self._confirm_discard("opening another archive")
        if discard is None:
            return
        self._submit(
            lambda: self.controller.open_archive(paths[0], paths[1], discard_pending=bool(discard)),
            self._on_opened,
            "open archive",
        )

    def request_close_archive(self) -> None:
        if not self._request_allowed():
            return
        discard = self._confirm_discard("closing the archive")
        if discard is None:
            return
        self._submit(
            lambda: self.controller.close(discard_pending=bool(discard)),
            self._on_closed,
            "close archive",
        )

    def request_import_package(self) -> None:
        if not self._request_allowed():
            return
        try:
            package = self.dialogs.choose_asset_package()
        except Exception as error:
            self._set_status(str(error), error=True)
            return
        if package is None:
            return
        self._submit(
            lambda: self.controller.import_package(package),
            self._on_mutation,
            "import package",
        )

    def request_import_batch(self) -> None:
        if not self._request_allowed():
            return
        try:
            parent = self.filedialog.askdirectory(parent=self.root,
                title="Choose batch parent (direct child texture packages)")
        except Exception as error:
            self._set_status(str(error), error=True)
            return
        if not parent:
            return
        self._batch_cancel.clear()
        self._submit(lambda: self.controller.import_packages(str(parent),
            progress=self._queue_batch_progress, cancelled=self._batch_cancel.is_set),
            self._on_batch_import, "batch import")

    def _queue_batch_progress(self, progress):
        try:
            self._batch_progress.put_nowait(progress)
        except Full:
            try:
                self._batch_progress.get_nowait()
            except Empty:
                pass
            self._batch_progress.put_nowait(progress)

    def _show_batch_progress(self):
        mailbox = getattr(self, "_batch_progress", None)
        if mailbox is None:
            return
        try:
            progress = mailbox.get_nowait()
        except Empty:
            return
        self._set_status(f"Importing {progress['processed']}/{progress['total']} · {progress['path']}")

    def _on_batch_import(self, response):
        if self._handle_response(response):
            report = response["result"]
            counts = {status: sum(item["status"] == status for item in report["items"])
                      for status in ("imported", "skipped", "error")}
            self.messagebox.showinfo("Batch import",
                f"{'Stopped' if report['cancelled'] else 'Finished'}: "
                f"{counts['imported']} queued, {counts['skipped']} skipped, {counts['error']} errors.\n"
                "Nothing saved yet. Review Pending before Save / Save As.", parent=self.root)
            self._batch_report_after_refresh = report
            self._refresh_all()

    def request_save(self) -> None:
        if not self._request_allowed():
            return
        self._submit(self.controller.save, self._on_mutation, "save")

    def request_save_as(self) -> None:
        if not self._request_allowed():
            return
        try:
            output = self.dialogs.choose_save_as()
        except Exception as error:
            self._set_status(str(error), error=True)
            return
        if output is None:
            return
        self._submit(lambda: self.controller.save_as(output), self._on_mutation, "save as")

    def request_remove_override(self) -> None:
        if not self._request_allowed():
            return
        path = self._selected_entry_path()
        if path is None:
            self._set_status("select an entry first", error=True)
            return
        self._submit(lambda: self.controller.remove_override(path), self._on_mutation, "remove override")

    def request_cancel_pending(self) -> None:
        if not self._request_allowed():
            return
        path = self._selected_pending_target()
        if path is None:
            self._set_status("select a pending operation first", error=True)
            return
        self._submit(lambda: self.controller.cancel(path), self._on_mutation, "cancel pending")

    def request_clear_pending(self) -> None:
        if not self._request_allowed():
            return
        self._submit(self.controller.clear_pending, self._on_mutation, "clear pending")

    def request_preview(self) -> None:
        if not self._request_allowed():
            return
        self._submit(self.controller.preview, self._on_pending_response, "preview")

    def reset_filter(self) -> None:
        if not self._request_allowed():
            return
        self.filter_var.set("")
        self._refresh_entries()

    def _selected_entry_path(self) -> str | None:
        selection = self.entry_tree.selection()
        if not selection:
            return None
        values = self.entry_tree.item(selection[0], "values")
        return str(values[0]) if values else None

    def _selected_pending_target(self) -> str | None:
        selection = self.pending_tree.selection()
        if not selection:
            return None
        values = self.pending_tree.item(selection[0], "values")
        return str(values[2]) if len(values) > 2 else None

    def _schedule_filter_refresh(self) -> None:
        if self.closed or self.closing_requested:
            return
        if self._filter_after_id is not None:
            try:
                self.root.after_cancel(self._filter_after_id)
            except Exception:
                pass
        self._filter_after_id = self.root.after(FILTER_DELAY_MS, self._run_filter_refresh)

    def _run_filter_refresh(self) -> None:
        self._filter_after_id = None
        if not self.busy and not self.closed and not self.closing_requested:
            self._refresh_entries()

    def _refresh_entries(self) -> None:
        if not self._snapshot.get("opened"):
            self.entries = []
            self._render_entries()
            return
        substring = self.filter_var.get()
        self._submit(
            lambda: self.controller.list_entries(substring),
            self._on_entries_response,
            "list entries",
        )

    def _refresh_pending(self) -> None:
        if not self._snapshot.get("opened"):
            self.pending = []
            self._render_pending()
            return
        self._submit(
            self.controller.pending_changes,
            lambda response: self._on_pending_response(response, show_report=False),
            "list pending",
        )

    def _refresh_all(self) -> None:
        self._refresh_entries()

    def _render_entries(self) -> None:
        self.entry_tree.delete(*self.entry_tree.get_children())
        for index, entry in enumerate(self.entries):
            self.entry_tree.insert(
                "",
                "end",
                iid=f"entry-{index}",
                values=(
                    entry.get("path", ""),
                    entry.get("storage_mode", ""),
                    entry.get("logical_size", ""),
                    entry.get("pending_action") or "",
                ),
            )

    def _render_pending(self) -> None:
        self.pending_tree.delete(*self.pending_tree.get_children())
        for index, item in enumerate(self.pending):
            warnings = item.get("warnings") or ()
            warning_text = "; ".join(str(value) for value in warnings)
            self.pending_tree.insert(
                "",
                "end",
                iid=f"pending-{index}",
                values=(
                    item.get("order", index + 1),
                    item.get("action", ""),
                    item.get("target_logical_path", ""),
                    warning_text,
                ),
            )

    def _on_entry_selected(self, _event: Any = None) -> None:
        self._update_action_states()

    def _on_pending_selected(self, _event: Any = None) -> None:
        self._update_action_states()

    def _on_state_response(self, response: dict[str, object]) -> None:
        if self._handle_response(response):
            self._refresh_all()

    def _on_opened(self, response: dict[str, object]) -> None:
        if self._handle_response(response):
            self._refresh_all()

    def _on_closed(self, response: dict[str, object]) -> None:
        if self._handle_response(response):
            self.entries = []
            self.pending = []
            self._render_entries()
            self._render_pending()

    def _on_mutation(self, response: dict[str, object]) -> None:
        if self._handle_response(response):
            self._refresh_all()

    def _on_entries_response(self, response: dict[str, object]) -> None:
        if not self._handle_response(response, show_report=False):
            return
        result = response.get("result")
        self.entries = [dict(item) for item in result if isinstance(item, dict)] if isinstance(result, list) else []
        self._render_entries()
        self._refresh_pending()

    def _on_pending_response(self, response: dict[str, object], *, show_report: bool = True) -> None:
        if not self._handle_response(response, show_report=show_report):
            return
        result = response.get("result")
        self.pending = [dict(item) for item in result if isinstance(item, dict)] if isinstance(result, list) else []
        self._render_pending()

        report = getattr(self, "_batch_report_after_refresh", None)
        if report is not None:
            self._batch_report_after_refresh = None
            self._set_report(report)

    def show_about(self) -> None:
        try:
            self.messagebox.showinfo("About DKS Patch Builder", ABOUT_TEXT, parent=self.root)
        except Exception as error:
            self._set_status(str(error), error=True)

    def open_profile(self, _event: Any = None) -> None:
        try:
            accepted = self.browser_opener(PROFILE_URL)
            if accepted is False:
                raise RuntimeError("browser did not accept the profile URL")
        except Exception as error:
            self._set_status(str(error), error=True)

    def _begin_exit(self) -> None:
        if self.closed or self.future is not None:
            return
        discard = self._confirm_discard("closing the window")
        if discard is None:
            self.closing_requested = False
            self._update_action_states()
            return
        self._submit(
            lambda: self.controller.close(discard_pending=bool(discard)),
            self._on_exit_response,
            "exit",
        )

    def request_exit(self) -> None:
        if self.closed:
            return
        self.closing_requested = True
        if hasattr(self, "_batch_cancel"):
            self._batch_cancel.set()
        if self._filter_after_id is not None:
            try:
                self.root.after_cancel(self._filter_after_id)
            except Exception:
                pass
            self._filter_after_id = None
        if self.future is not None:
            self._set_status("Waiting for the current operation to finish…")
            return
        self._begin_exit()

    def _on_exit_response(self, response: dict[str, object]) -> None:
        if not self._handle_response(response):
            self.closing_requested = False
            return
        self.closed = True
        try:
            self.executor.shutdown(wait=True)
        finally:
            self.root.destroy()

    def run(self) -> None:
        self.root.mainloop()


def run_gui(
    *,
    controller: BuilderController | None = None,
    root: Any | None = None,
    tk_module: Any | None = None,
    ttk_module: Any | None = None,
    filedialog_module: Any | None = None,
    messagebox_module: Any | None = None,
    browser_opener: Callable[[str], Any] | None = None,
    executor: Any | None = None,
) -> int:
    """Launch the Tk frontend; Tk is imported only when this function runs."""

    if tk_module is None or ttk_module is None or filedialog_module is None or messagebox_module is None:
        import tkinter as tk
        from tkinter import filedialog, messagebox, ttk

        tk_module = tk_module or tk
        ttk_module = ttk_module or ttk
        filedialog_module = filedialog_module or filedialog
        messagebox_module = messagebox_module or messagebox
    if root is None:
        root = tk_module.Tk()
    app = BuilderTkApp(
        root=root,
        tk_module=tk_module,
        ttk_module=ttk_module,
        filedialog_module=filedialog_module,
        messagebox_module=messagebox_module,
        controller=controller,
        browser_opener=browser_opener,
        executor=executor,
    )
    app.run()
    return 0


__all__ = [
    "APP_NAME",
    "DKS_FILE_TYPES",
    "DKS_PATCH_FILE_NAME",
    "BuilderTkApp",
    "DesktopBuilderController",
    "NativeDialogAdapter",
    "PROFILE_URL",
    "TkDialogAdapter",
    "run_gui",
]
