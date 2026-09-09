# SPDX-FileCopyrightText: 2026 PmNz8
# SPDX-License-Identifier: AGPL-3.0-only

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest

from dks_patch_builder.desktop import (
    DKS_FILE_TYPES,
    DKS_PATCH_FILE_NAME,
    BuilderTkApp,
    PROFILE_URL,
    TkDialogAdapter,
)


class _FakeVar:
    def __init__(self, value: str = "") -> None:
        self.value = value
        self.callbacks = []

    def get(self) -> str:
        return self.value

    def set(self, value: str) -> None:
        self.value = value
        for callback in tuple(self.callbacks):
            callback("", "", "write")

    def trace_add(self, _mode: str, callback):
        self.callbacks.append(callback)
        return str(len(self.callbacks))


class _FakeWidget:
    _next_iid = 0

    def __init__(self, *_args, **kwargs) -> None:
        self.kwargs = kwargs
        self.config = {}
        self.bindings = {}
        self.items: dict[str, tuple[object, ...]] = {}
        self.selected: tuple[str, ...] = ()
        self._state: set[str] = set()
        self.command = kwargs.get("command")

    def pack(self, **_kwargs):
        return None

    def grid(self, **_kwargs):
        return None

    def columnconfigure(self, *_args, **_kwargs):
        return None

    def rowconfigure(self, *_args, **_kwargs):
        return None

    def configure(self, **kwargs):
        self.config.update(kwargs)

    config_widget = configure

    def state(self, flags=None):
        if flags is not None:
            for flag in flags:
                if flag == "disabled":
                    self._state.add("disabled")
                elif flag == "!disabled":
                    self._state.discard("disabled")
        return tuple(sorted(self._state))

    def bind(self, event, callback):
        self.bindings[event] = callback

    def heading(self, *_args, **_kwargs):
        return None

    def column(self, *_args, **_kwargs):
        return None

    def insert(self, _parent, _index, iid=None, values=()):
        if iid is None:
            iid = f"item-{self._next_iid}"
            type(self)._next_iid += 1
        self.items[str(iid)] = tuple(values)
        return str(iid)

    def delete(self, *items):
        if not items:
            self.items.clear()
            self.selected = ()
            return
        for item in items:
            self.items.pop(str(item), None)
        self.selected = tuple(item for item in self.selected if item in self.items)

    def get_children(self):
        return tuple(self.items)

    def selection(self):
        return self.selected

    def selection_set(self, item):
        self.selected = (str(item),)

    def selection_clear(self, *_args):
        self.selected = ()

    def item(self, item, option=None, **kwargs):
        if "values" in kwargs:
            self.items[str(item)] = tuple(kwargs["values"])
        values = self.items.get(str(item), ())
        return values if option == "values" else {"values": values}

    def yview(self, *_args):
        return None

    def xview(self, *_args):
        return None

    def set(self, *_args):
        return None

    def invoke(self):
        if self.command is not None:
            return self.command()
        return None


class _FakeText(_FakeWidget):
    def __init__(self, *_args, **kwargs):
        super().__init__(*_args, **kwargs)
        self.text = ""

    def delete(self, *_args):
        self.text = ""

    def insert(self, _index, value):
        self.text += str(value)


class _FakeRoot:
    def __init__(self) -> None:
        self.callbacks: dict[str, tuple[object, tuple, dict]] = {}
        self.protocols = {}
        self.destroyed = False
        self._token = 0

    def title(self, *_args):
        return None

    def geometry(self, *_args):
        return None

    def minsize(self, *_args):
        return None

    def columnconfigure(self, *_args, **_kwargs):
        return None

    def rowconfigure(self, *_args, **_kwargs):
        return None

    def protocol(self, name, callback):
        self.protocols[name] = callback

    def after(self, _delay, callback, *args):
        self._token += 1
        token = str(self._token)
        self.callbacks[token] = (callback, args, {})
        return token

    def after_cancel(self, token):
        self.callbacks.pop(str(token), None)

    def run_all(self):
        guard = 0
        while self.callbacks:
            guard += 1
            if guard > 200:
                raise AssertionError("fake Tk callback queue did not settle")
            token = next(iter(self.callbacks))
            callback, args, _kwargs = self.callbacks.pop(token)
            callback(*args)

    def run_one(self):
        token = next(iter(self.callbacks))
        callback, args, _kwargs = self.callbacks.pop(token)
        callback(*args)

    def mainloop(self):
        self.run_all()

    def destroy(self):
        self.destroyed = True


class _FakeTk:
    END = "end"
    StringVar = _FakeVar
    Text = _FakeText
    Label = _FakeWidget


class _FakeTtk:
    Frame = _FakeWidget
    Label = _FakeWidget
    Entry = _FakeWidget
    Button = _FakeWidget
    Treeview = _FakeWidget
    Scrollbar = _FakeWidget


class _FakeFileDialog:
    def __init__(self, values=None) -> None:
        self.values = {name: list(items) for name, items in (values or {}).items()}
        self.calls: list[tuple[str, dict[str, object]]] = []

    def _take(self, name: str, **kwargs):
        self.calls.append((name, kwargs))
        values = self.values.get(name, [])
        return values.pop(0) if values else ""

    def askdirectory(self, **kwargs):
        return self._take("askdirectory", **kwargs)

    def askopenfilename(self, **kwargs):
        return self._take("askopenfilename", **kwargs)

    def asksaveasfilename(self, **kwargs):
        return self._take("asksaveasfilename", **kwargs)


class _FakeMessageBox:
    def __init__(self, answer: bool = True) -> None:
        self.answer = answer
        self.questions: list[str] = []
        self.errors: list[str] = []

    def askyesno(self, _title, message, **_kwargs):
        self.questions.append(message)
        return self.answer

    def showerror(self, _title, message, **_kwargs):
        self.errors.append(str(message))


class _ImmediateFuture:
    def __init__(self, value=None, error: Exception | None = None) -> None:
        self.value = value
        self.error = error

    def done(self):
        return True

    def result(self):
        if self.error is not None:
            raise self.error
        return self.value


class _ImmediateExecutor:
    def __init__(self) -> None:
        self.calls = 0
        self.shutdown_called = False

    def submit(self, operation):
        self.calls += 1
        try:
            return _ImmediateFuture(operation())
        except Exception as error:
            return _ImmediateFuture(error=error)

    def shutdown(self, wait=True):
        self.shutdown_called = wait


class _ManualFuture:
    def __init__(self):
        self.value = None
        self.error = None
        self.finished = False

    def done(self):
        return self.finished

    def result(self):
        if self.error is not None:
            raise self.error
        return self.value


class _ManualExecutor:
    def __init__(self):
        self.pending: list[tuple[_ManualFuture, object]] = []
        self.shutdown_called = False

    def submit(self, operation):
        future = _ManualFuture()
        self.pending.append((future, operation))
        return future

    def complete_next(self):
        future, operation = self.pending.pop(0)
        try:
            future.value = operation()
        except Exception as error:
            future.error = error
        future.finished = True

    def shutdown(self, wait=True):
        self.shutdown_called = wait


class _FakeController:
    def __init__(self, *, opened=False, dirty=False, error_import=False):
        self.calls: list[tuple[str, tuple, dict]] = []
        self.error_import = error_import
        self.entries = [{
            "path": "Textures\\old.nif",
            "storage_mode": "zlib",
            "logical_size": 12,
            "pending_action": None,
        }]
        self.pending = [{
            "order": 1,
            "action": "REPLACE",
            "target_logical_path": "Textures\\old.nif",
            "warnings": ["example warning"],
        }] if dirty else []
        self.state_doc = {
            "opened": opened,
            "packed_root": "Packed" if opened else None,
            "selected_dks": "DKS_Patch.dv2" if opened else None,
            "selected_sha256": "a" * 64 if opened else None,
            "selected_size": 10 if opened else None,
            "entry_count": 1 if opened else 0,
            "pending_count": len(self.pending),
            "dirty": dirty,
        }

    def _response(self, result=None, *, ok=True, error=None):
        response = {"ok": ok, "state": dict(self.state_doc)}
        if ok:
            response["result"] = result
        else:
            response.update({"error": error or "operation failed", "error_type": "BuilderModelError"})
        return response

    def state(self):
        self.calls.append(("state", (), {}))
        return self._response(dict(self.state_doc))

    def list_entries(self, substring=None):
        self.calls.append(("list_entries", (substring,), {}))
        query = (substring or "").casefold()
        result = [item for item in self.entries if not query or query in str(item["path"]).casefold()]
        return self._response(result)

    def pending_changes(self):
        self.calls.append(("pending_changes", (), {}))
        return self._response(list(self.pending))

    def open_archive(self, packed, selected, *, discard_pending=False, **kwargs):
        self.calls.append(("open_archive", (packed, selected), {"discard_pending": discard_pending, **kwargs}))
        self.state_doc.update({"opened": True, "packed_root": packed, "selected_dks": selected, "dirty": False, "pending_count": 0})
        self.pending.clear()
        return self._response(dict(self.state_doc))

    def create_archive(self, packed, output, *, discard_pending=False, **kwargs):
        self.calls.append(("create_archive", (packed, output), {"discard_pending": discard_pending, **kwargs}))
        self.state_doc.update({"opened": True, "packed_root": packed, "selected_dks": output, "dirty": False, "pending_count": 0})
        self.pending.clear()
        return self._response(dict(self.state_doc))

    def close(self, *, discard_pending=False):
        self.calls.append(("close", (), {"discard_pending": discard_pending}))
        if self.state_doc["dirty"] and not discard_pending:
            return self._response(ok=False, error="pending changes")
        self.state_doc.update({"opened": False, "packed_root": None, "selected_dks": None, "dirty": False, "pending_count": 0})
        self.pending.clear()
        return self._response(dict(self.state_doc))

    def import_package(self, package):
        self.calls.append(("import_package", (package,), {}))
        if self.error_import:
            return self._response(ok=False, error="bad package")
        self.pending.append({"order": len(self.pending) + 1, "action": "ADD", "target_logical_path": "Textures\\new.nif", "warnings": []})
        self.state_doc.update({"dirty": True, "pending_count": len(self.pending)})
        return self._response(self.pending[-1])

    def save(self):
        self.calls.append(("save", (), {}))
        self.state_doc.update({"dirty": False, "pending_count": 0})
        self.pending.clear()
        return self._response({"warnings": []})

    def save_as(self, output):
        self.calls.append(("save_as", (output,), {}))
        self.state_doc.update({"dirty": False, "pending_count": 0})
        self.pending.clear()
        return self._response({"warnings": []})

    def remove_override(self, path):
        self.calls.append(("remove_override", (path,), {}))
        return self.import_package("remove:" + path)

    def cancel(self, path):
        self.calls.append(("cancel", (path,), {}))
        if self.pending:
            self.pending.pop(0)
        self.state_doc.update({"dirty": bool(self.pending), "pending_count": len(self.pending)})
        return self._response({"target_logical_path": path})

    def clear_pending(self):
        self.calls.append(("clear_pending", (), {}))
        count = len(self.pending)
        self.pending.clear()
        self.state_doc.update({"dirty": False, "pending_count": 0})
        return self._response(count)

    def preview(self):
        self.calls.append(("preview", (), {}))
        return self._response(list(self.pending))


def _make_app(controller=None, *, executor=None, dialog_values=None, answer=True, browser=None, settle=True):
    root = _FakeRoot()
    filedialog = _FakeFileDialog(dialog_values)
    messagebox = _FakeMessageBox(answer)
    controller = controller or _FakeController()
    app = BuilderTkApp(
        root=root,
        tk_module=_FakeTk,
        ttk_module=_FakeTtk,
        filedialog_module=filedialog,
        messagebox_module=messagebox,
        controller=controller,
        browser_opener=browser,
        executor=executor or _ImmediateExecutor(),
    )
    if settle:
        root.run_all()
    return app, root, filedialog, messagebox, controller


class DKSBuilderDesktopTests(unittest.TestCase):
    def test_module_import_is_headless_and_old_frontend_is_absent(self):
        completed = subprocess.run(
            [sys.executable, "-c", "import sys; import dks_patch_builder.desktop; assert 'tkinter' not in sys.modules"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        source = Path("dks_patch_builder/desktop.py").read_text(encoding="utf-8").casefold()
        for marker in ("terrain_viewer", "webview", "html", "javascript"):
            self.assertNotIn(marker, source)

    def test_dialogs_cancel_and_new_save_use_exact_basename_suggestion(self):
        root = _FakeRoot()
        filedialog = _FakeFileDialog({
            "askdirectory": [""],
            "askopenfilename": ["selected.dv2"],
            "asksaveasfilename": ["DKS_Patch.dv2", "copy.dv2"],
        })
        adapter = TkDialogAdapter(root, filedialog)
        self.assertIsNone(adapter.choose_packed_folder())
        self.assertEqual(adapter.choose_existing_dks(), "selected.dv2")
        self.assertEqual(adapter.choose_new_dks(), "DKS_Patch.dv2")
        self.assertEqual(adapter.choose_save_as(), "copy.dv2")
        save_calls = [kwargs for name, kwargs in filedialog.calls if name == "asksaveasfilename"]
        self.assertEqual(save_calls[0]["initialfile"], DKS_PATCH_FILE_NAME)
        self.assertEqual(save_calls[0]["filetypes"], DKS_FILE_TYPES)

    def test_initial_state_and_live_filter_are_serialized(self):
        controller = _FakeController(opened=True)
        app, root, _dialogs, _messagebox, controller = _make_app(controller)
        app.filter_var.set("old")
        root.run_all()
        self.assertIn(("list_entries", ("old",), {}), controller.calls)
        self.assertTrue(app.entries)

    def test_busy_request_does_not_open_dialog_or_dispatch(self):
        executor = _ManualExecutor()
        app, root, dialogs, _messagebox, controller = _make_app(
            _FakeController(opened=False), executor=executor, settle=False
        )
        self.assertTrue(app.busy)
        app.request_open()
        self.assertEqual(dialogs.calls, [])
        self.assertFalse(any(name == "open_archive" for name, _args, _kwargs in controller.calls))
        executor.complete_next()
        root.run_all()

    def test_declined_discard_does_not_dispatch_and_restores_controls(self):
        controller = _FakeController(opened=True, dirty=True)
        app, root, dialogs, messagebox, controller = _make_app(
            controller,
            dialog_values={"askdirectory": ["Packed"], "askopenfilename": ["DKS_Patch.dv2"]},
            answer=False,
        )
        app.request_open()
        self.assertEqual(messagebox.questions, ["Discard pending changes before opening another archive?"])
        self.assertFalse(any(name == "open_archive" for name, _args, _kwargs in controller.calls))
        app.request_exit()
        self.assertFalse(app.closing_requested)
        self.assertFalse(app.busy)
        self.assertNotIn("disabled", app.open_button.state())

    def test_accepted_discard_dispatches_true_after_paths(self):
        controller = _FakeController(opened=True, dirty=True)
        app, root, _dialogs, _messagebox, controller = _make_app(
            controller,
            dialog_values={"askdirectory": ["Packed"], "askopenfilename": ["DKS_Patch.dv2"]},
            answer=True,
        )
        app.request_open()
        root.run_all()
        calls = [call for call in controller.calls if call[0] == "open_archive"]
        self.assertEqual(calls[0][2]["discard_pending"], True)

    def test_callback_routing_import_save_saveas_remove_cancel_clear(self):
        controller = _FakeController(opened=True, dirty=True)
        app, root, dialogs, _messagebox, controller = _make_app(
            controller,
            dialog_values={"askdirectory": ["asset-package"], "asksaveasfilename": ["copy.dv2"]},
        )
        app.request_import_package()
        root.run_all()
        app.request_save()
        root.run_all()
        controller.state_doc["dirty"] = True
        app._snapshot = dict(controller.state_doc)
        app.request_save_as()
        root.run_all()
        app.entry_tree.selection_set("entry-0")
        app.request_remove_override()
        root.run_all()
        app.pending_tree.selection_set("pending-0")
        app.request_cancel_pending()
        root.run_all()
        app.request_clear_pending()
        root.run_all()
        names = [name for name, _args, _kwargs in controller.calls]
        for expected in ("import_package", "save", "save_as", "remove_override", "cancel", "clear_pending"):
            self.assertIn(expected, names)
        self.assertEqual(dialogs.calls[0][0], "askdirectory")

    def test_error_preserves_cached_rows_and_report(self):
        controller = _FakeController(opened=True, dirty=True, error_import=True)
        app, root, _dialogs, _messagebox, _controller = _make_app(
            controller,
            dialog_values={"askdirectory": ["bad-package"]},
        )
        old_entries = list(app.entries)
        old_pending = list(app.pending)
        app.request_import_package()
        root.run_all()
        self.assertEqual(app.entries, old_entries)
        self.assertEqual(app.pending, old_pending)
        self.assertIn("bad package", app.report_text.text)

    def test_deferred_exit_waits_for_operation_then_closes_safely(self):
        executor = _ManualExecutor()
        controller = _FakeController(opened=False, dirty=True)
        app, root, _dialogs, _messagebox, _controller = _make_app(
            controller,
            executor=executor,
            answer=True,
            settle=False,
        )
        executor.complete_next()
        root.run_all()
        app.request_preview()
        app.request_exit()
        self.assertFalse(root.destroyed)
        executor.complete_next()
        root.run_one()
        self.assertTrue(executor.pending)
        executor.complete_next()
        root.run_all()
        self.assertTrue(root.destroyed)
        self.assertTrue(executor.shutdown_called)

    def test_profile_opener_runs_only_after_click(self):
        opened: list[str] = []
        app, _root, _dialogs, _messagebox, _controller = _make_app(browser=opened.append)
        self.assertEqual(opened, [])
        app.open_profile()
        self.assertEqual(opened, [PROFILE_URL])


if __name__ == "__main__":
    unittest.main(verbosity=2)
