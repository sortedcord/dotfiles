"""From ~/.config/niri: python3 -m unittest discover -s scripts/tests -v"""

import asyncio
import importlib.machinery
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import AsyncMock, patch

loader = importlib.machinery.SourceFileLoader(
    "power_wallpaper", str(Path(__file__).resolve().parents[1] / "niri-power-wallpaper")
)
spec = importlib.util.spec_from_loader(loader.name, loader)
wallpaper = importlib.util.module_from_spec(spec)
loader.exec_module(wallpaper)


class PositionTests(unittest.TestCase):
    def test_position_validation(self):
        for value in (0, 1, 1.5):
            self.assertTrue(wallpaper.valid_position(value))
        for value in (-1, float("nan"), float("inf"), True, None, "1"):
            self.assertFalse(wallpaper.valid_position(value))


class IPCTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.path = Path(self.directory.name) / "mpv.sock"
        self.socket_patch = patch.object(wallpaper, "SOCKET", self.path)
        self.socket_patch.start()
        self.server = None

    async def asyncTearDown(self):
        if self.server:
            self.server.close()
            await self.server.wait_closed()
        self.socket_patch.stop()
        self.directory.cleanup()

    async def serve(self, handler):
        self.server = await asyncio.start_unix_server(handler, str(self.path))

    async def test_events_and_multiple_lines_are_buffered(self):
        async def handler(reader, writer):
            try:
                for value in (True, 4.5):
                    request = json.loads(await reader.readline())
                    messages = [
                        {"event": "property-change"},
                        {"request_id": 999, "error": "success", "data": "wrong reply"},
                        {"request_id": request["request_id"], "error": "success", "data": value},
                        {"event": "pause"},
                    ]
                    writer.write("".join(json.dumps(m) + "\n" for m in messages).encode())
                    await writer.drain()
            finally:
                writer.close()
                await writer.wait_closed()
        await self.serve(handler)
        async with wallpaper.IPC() as ipc:
            self.assertTrue(await ipc.command("set_property", "pause", True))
            self.assertEqual(await ipc.command("get_property", "time-pos"), 4.5)

    async def test_eof_is_an_error_not_a_busy_loop(self):
        async def handler(reader, writer):
            await reader.readline()
            writer.close()
            await writer.wait_closed()
        await self.serve(handler)
        with self.assertRaises(ConnectionError):
            async with wallpaper.IPC() as ipc:
                await asyncio.wait_for(ipc.command("get_property", "time-pos"), 0.5)

    async def test_missing_reply_has_a_deadline(self):
        async def handler(reader, writer):
            await reader.read()
            writer.close()
            await writer.wait_closed()
        await self.serve(handler)
        with self.assertRaises(TimeoutError):
            async with wallpaper.IPC() as ipc:
                await ipc.command("get_property", "time-pos", timeout=0.03)


class ControllerTests(unittest.IsolatedAsyncioTestCase):
    async def test_power_notification_is_deduplicated(self):
        controller = wallpaper.Wallpaper()
        controller.power_changed(False)
        self.assertTrue(controller.changed.is_set())
        controller.changed.clear()
        controller.power_changed(False)
        self.assertFalse(controller.changed.is_set())
        controller.power_changed(True)
        self.assertTrue(controller.changed.is_set())

    async def test_owned_static_is_not_duplicated(self):
        controller = wallpaper.Wallpaper()
        controller.static = AsyncMock(returncode=None)
        with tempfile.TemporaryDirectory() as directory:
            image = Path(directory) / "frame.png"
            image.write_bytes(b"image")
            controller.static_image = image
            with patch.object(wallpaper, "FRAME", image), patch.object(
                wallpaper.asyncio, "create_subprocess_exec", new_callable=AsyncMock
            ) as spawn:
                await controller.show_static()
                spawn.assert_not_called()

    async def test_player_start_failure_keeps_static(self):
        controller = wallpaper.Wallpaper()
        controller.online = True
        controller.start_player = AsyncMock(side_effect=RuntimeError("failed"))
        controller.stop_player = AsyncMock()
        controller.show_static = AsyncMock()
        with self.assertRaises(RuntimeError):
            await controller.reconcile()
        controller.stop_player.assert_awaited_once()
        controller.show_static.assert_awaited_once()

    async def test_battery_stops_video_even_if_static_fails(self):
        controller = wallpaper.Wallpaper()
        controller.online = False
        controller.capture_frame = AsyncMock()
        controller.show_static = AsyncMock(side_effect=RuntimeError("failed"))
        controller.stop_player = AsyncMock()
        with self.assertRaises(RuntimeError):
            await controller.reconcile()
        controller.stop_player.assert_awaited_once()

    async def test_canceled_capture_invalidates_paused_player(self):
        controller = wallpaper.Wallpaper()
        controller.player = AsyncMock(returncode=None)
        controller.video_ready = True
        entered = asyncio.Event()

        class BlockingIPC:
            async def __aenter__(self):
                return self

            async def __aexit__(self, *_):
                pass

            async def command(self, *command):
                entered.set()
                await asyncio.Event().wait()

        with tempfile.TemporaryDirectory() as directory, patch.object(
            wallpaper, "FRAME", Path(directory) / "frame.png"
        ), patch.object(wallpaper, "IPC", BlockingIPC):
            task = asyncio.create_task(controller.capture_frame())
            await entered.wait()
            task.cancel()
            with self.assertRaises(asyncio.CancelledError):
                await task
        self.assertFalse(controller.video_ready)

    async def test_power_change_interrupts_transition_and_shutdown_cleans_up(self):
        controller = wallpaper.Wallpaper()
        started = asyncio.Event()
        interrupted = asyncio.Event()
        offline = asyncio.Event()

        async def reconcile():
            if controller.online:
                started.set()
                try:
                    await asyncio.Event().wait()
                finally:
                    interrupted.set()
            else:
                offline.set()

        controller.reconcile = reconcile
        controller.stop_player = AsyncMock()
        controller.stop_static = AsyncMock()
        controller.power_changed(True)
        task = asyncio.create_task(controller.run())
        await asyncio.wait_for(started.wait(), 1)
        controller.power_changed(False)
        await asyncio.wait_for(offline.wait(), 1)
        self.assertTrue(interrupted.is_set())
        controller.stop()
        await asyncio.wait_for(task, 1)
        controller.stop_player.assert_awaited_once()
        controller.stop_static.assert_awaited_once()

    async def test_failed_transition_waits_before_retry(self):
        controller = wallpaper.Wallpaper()
        failed = asyncio.Event()

        async def reconcile():
            failed.set()
            raise RuntimeError("startup failed")

        controller.reconcile = AsyncMock(side_effect=reconcile)
        controller.stop_player = AsyncMock()
        controller.stop_static = AsyncMock()
        controller.power_changed(True)
        task = asyncio.create_task(controller.run())
        try:
            await asyncio.wait_for(failed.wait(), 1)
            await asyncio.sleep(0.05)
            self.assertEqual(controller.reconcile.await_count, 1)
        finally:
            controller.stop()
            await asyncio.wait_for(task, 1)

    async def test_startup_crash_does_not_bypass_backoff(self):
        controller = wallpaper.Wallpaper()
        process = AsyncMock()
        process.wait.return_value = 1
        controller.player = process
        controller.watch(process, "player")
        await asyncio.gather(*controller.watchers)
        self.assertFalse(controller.changed.is_set())
        controller.video_ready = True
        controller.watch(process, "player")
        await asyncio.gather(*controller.watchers)
        self.assertTrue(controller.changed.is_set())


if __name__ == "__main__":
    unittest.main()
