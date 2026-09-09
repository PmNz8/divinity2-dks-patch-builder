"""Real controller/worker with fake Tk, using disposable synthetic archives only."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from contextlib import ExitStack
from pathlib import Path
import tempfile
import threading
import time
import unittest
from unittest import mock

from dks_patch_builder.controller import BuilderController
from tests.test_dks_patch_builder_desktop import (
    _FakeFileDialog, _FakeMessageBox, _FakeRoot, _FakeText,
    _FakeVar, _FakeWidget, _make_app,
)
from tests.test_dks_patch_builder_model import TEMPLATE, write_archive
from tests.test_dks_patch_builder_texture import TexturePackageFixture


class TkControllerIntegrationTests(unittest.TestCase):
    def test_real_worker_transaction_and_main_thread_ui(self) -> None:
        ui_thread = threading.get_ident()
        controller_threads: set[int] = set()
        real_controller = BuilderController()

        class CheckedController:
            def __getattr__(self, name):
                method = getattr(real_controller, name)

                def call(*args, **kwargs):
                    thread = threading.get_ident()
                    if thread == ui_thread:
                        raise AssertionError(f"controller.{name} ran on the Tk thread")
                    controller_threads.add(thread)
                    return method(*args, **kwargs)

                return call

        def ui_checked(method):
            def call(*args, **kwargs):
                self.assertEqual(threading.get_ident(), ui_thread, "Tk/dialog call on worker")
                return method(*args, **kwargs)
            return call

        def settle(app, root):
            deadline = time.monotonic() + 15
            while app.future is not None or root.callbacks:
                self.assertLess(time.monotonic(), deadline, "Tk pipeline did not settle")
                if app.future is not None:
                    app.future.result(timeout=max(0.1, deadline - time.monotonic()))
                if root.callbacks:
                    token = next(iter(root.callbacks))
                    callback, args, kwargs = root.callbacks.pop(token)
                    callback(*args, **kwargs)

        with tempfile.TemporaryDirectory(prefix="dks-tk-integration-") as raw, ExitStack() as stack:
            # Assert the boundary at the fake widget/dialog methods, not just at
            # the controller. No actual tkinter module or window is needed.
            for cls, names in (
                (_FakeVar, ("get", "set", "trace_add")),
                (_FakeWidget, ("pack", "grid", "configure", "state", "bind",
                               "insert", "delete", "get_children", "selection",
                               "selection_set", "item")),
                (_FakeText, ("insert", "delete")),
                (_FakeRoot, ("after", "after_cancel", "destroy")),
                (_FakeFileDialog, ("_take",)),
                (_FakeMessageBox, ("askyesno",)),
            ):
                for name in names:
                    stack.enter_context(mock.patch.object(cls, name, ui_checked(getattr(cls, name))))

            root_path = Path(raw)
            fixture = TexturePackageFixture(root_path / "package")
            packed = root_path / "Packed"
            write_archive(packed / "Patch.dv2", [(TEMPLATE, fixture.template_payload, "zlib")])
            original = root_path / "new" / "DKS_Patch.dv2"
            saved = root_path / "saved" / "DKS_Patch.dv2"
            original.parent.mkdir()
            saved.parent.mkdir()
            executor = ThreadPoolExecutor(max_workers=1)
            stack.callback(executor.shutdown, wait=True)
            app, root, dialogs, messagebox, _ = _make_app(
                CheckedController(), executor=executor, settle=False,
                dialog_values={
                    "askdirectory": [str(packed), str(fixture.root)],
                    "asksaveasfilename": [str(original), str(saved)],
                },
            )
            settle(app, root)
            app.request_new()
            settle(app, root)
            self.assertTrue(app._snapshot["opened"], app.report_text.text)
            empty_bytes = original.read_bytes()
            self.assertFalse(app.entries)

            app.request_import_package()
            settle(app, root)
            self.assertEqual(app._snapshot["pending_count"], 1, app.report_text.text)
            self.assertEqual(app.pending[0]["action"], "ADD_OVERRIDE")
            self.assertEqual(original.read_bytes(), empty_bytes)
            app.request_save_as()
            settle(app, root)
            self.assertEqual(app._snapshot["selected_dks"], str(saved))
            self.assertEqual(len(app.entries), 1)
            self.assertFalse(app.pending)
            self.assertEqual(original.read_bytes(), empty_bytes)

            saved_before = saved.read_bytes()
            app.entry_tree.selection_set("entry-0")
            app.request_remove_override()
            settle(app, root)
            self.assertEqual(app.pending[0]["action"], "REMOVE_OVERRIDE")
            queued = list(app.pending)
            dialogs.values["askdirectory"].append(str(root_path / "missing-package"))
            app.request_import_package()
            settle(app, root)
            self.assertEqual(app.pending, queued)
            self.assertTrue(app._snapshot["dirty"])
            self.assertEqual(saved.read_bytes(), saved_before)

            messagebox.answer = False
            app.request_close_archive()
            settle(app, root)
            self.assertTrue(app._snapshot["opened"])
            self.assertEqual(app.pending, queued)
            app.request_save()
            settle(app, root)
            self.assertFalse(app.entries)
            self.assertFalse(app.pending)
            self.assertEqual(saved.with_name("DKS_Patch.dv2.bak").read_bytes(), saved_before)
            app.request_exit()
            settle(app, root)
            self.assertTrue(root.destroyed)
            self.assertTrue(app.closed)
            self.assertEqual(len(controller_threads), 1)
            self.assertNotIn(ui_thread, controller_threads)


if __name__ == "__main__":
    unittest.main()
