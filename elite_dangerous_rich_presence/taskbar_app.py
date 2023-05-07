import os
import sys
from pathlib import Path
from typing import Callable

import pywintypes
import win32api
import win32con
import win32gui
import winerror
from loguru import logger


class TaskbarApp:
    # https://github.com/mhammond/pywin32/blob/master/win32/Demos/win32gui_taskbar.py

    def __init__(
        self,
        title: str = "PythonTaskbarDemo",
        icon_path: str | Path | None = None,
        callback: Callable[[], None] = lambda: None,
    ) -> None:
        logger.debug(
            "Creating TaskbarApp(title={title}, icon_path={icon_path})",
            title=title,
            icon_path=icon_path,
        )
        self.title = title
        self.icon_path = str(icon_path)
        self.callback = callback

        msg_taskbar_restart = win32gui.RegisterWindowMessage("TaskbarCreated")
        message_map = {
            msg_taskbar_restart: self.on_restart,
            win32con.WM_DESTROY: self.on_destroy,
            win32con.WM_COMMAND: self.on_command,
            win32con.WM_USER + 20: self.on_taskbar_notify,
        }
        # Register the Window class.
        window_class = win32gui.WNDCLASS()
        handle_instance = window_class.hInstance = win32api.GetModuleHandle(None)
        window_class.lpszClassName = title
        window_class.style = win32con.CS_VREDRAW | win32con.CS_HREDRAW
        window_class.hCursor = win32api.LoadCursor(0, win32con.IDC_ARROW)
        window_class.hbrBackground = win32con.COLOR_WINDOW
        window_class.lpfnWndProc = message_map  # could also specify a wndproc.

        # Don't blow up if class already registered to make testing easier
        try:
            win32gui.RegisterClass(window_class)
        except win32gui.error as err_info:
            if err_info.winerror != winerror.ERROR_CLASS_ALREADY_EXISTS:
                raise

        # Create the Window.
        style = win32con.WS_OVERLAPPED | win32con.WS_SYSMENU
        self.hwnd = win32gui.CreateWindow(
            window_class.lpszClassName,
            title,
            style,
            0,
            0,
            win32con.CW_USEDEFAULT,
            win32con.CW_USEDEFAULT,
            0,
            0,
            handle_instance,
            None,
        )
        win32gui.UpdateWindow(self.hwnd)
        self._create_icons()

    def _create_icons(self):
        # Try and find a custom icon
        handle_instance = win32api.GetModuleHandle(None)
        exe_path = Path(sys.executable).parent
        icon_path = self.icon_path

        if not icon_path:
            icon_path = exe_path / "pyc.ico"
        else:
            icon_path = Path(icon_path)

        if not icon_path.is_file():
            # Look in DLLs dir, a-la py 2.5
            icon_path = exe_path / "DLLs" / "pyc.ico"

        if not icon_path.is_file():
            # Look in the source tree.
            icon_path = exe_path.parent / "PC" / "pyc.ico"

        if os.path.isfile(icon_path):
            icon_flags = win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE
            self.hicon = win32gui.LoadImage(
                handle_instance, str(icon_path), win32con.IMAGE_ICON, 0, 0, icon_flags
            )
        else:
            logger.warning("Unable to find icon file! Using default!")
            self.hicon = win32gui.LoadIcon(0, win32con.IDI_APPLICATION)

        flags = win32gui.NIF_ICON | win32gui.NIF_MESSAGE | win32gui.NIF_TIP
        nid = (self.hwnd, 0, flags, win32con.WM_USER + 20, self.hicon, self.title)
        try:
            win32gui.Shell_NotifyIcon(win32gui.NIM_ADD, nid)
        except win32gui.error:
            # This is common when windows is starting, and this code is hit
            # before the taskbar has been created.
            logger.warning("Failed to add the taskbar icon - is explorer running?")
            # but keep running anyway - when explorer starts, we get the
            # TaskbarCreated message.

    def on_restart(self, hwnd, msg, wparam, lparam):
        self._create_icons()
        return 0

    def on_destroy(self, hwnd, msg, wparam, lparam):
        nid = (self.hwnd, 0)
        win32gui.Shell_NotifyIcon(win32gui.NIM_DELETE, nid)
        win32gui.PostQuitMessage(0)
        logger.debug("Destroying TaskbarApp")
        return 1

    def on_command(self, hwnd, msg, wparam, lparam):
        command = win32api.LOWORD(wparam)
        if command == 1023:
            self.callback()
        elif command == 1024:
            win32gui.DestroyWindow(self.hwnd)
        else:
            logger.debug("Unknown command: {command}", command=command)
        return 0

    def on_taskbar_notify(self, hwnd, msg, wparam, lparam):
        if lparam == win32con.WM_LBUTTONUP:
            self.on_left_mouse_button()
        elif lparam == win32con.WM_LBUTTONDBLCLK:
            self.on_double_click()
        elif lparam == win32con.WM_RBUTTONUP:
            self.on_right_mouse_button()
        elif lparam == 1029:  # Ballon Tooltip clicked
            self.toast_callback()
        return 1

    def on_left_mouse_button(self, *args):
        ...

    def on_right_mouse_button(self, *args):
        menu = win32gui.CreatePopupMenu()
        win32gui.AppendMenu(menu, win32con.MF_STRING, 1023, "Settings")
        win32gui.AppendMenu(menu, win32con.MF_STRING, 1024, "Exit")

        position = win32gui.GetCursorPos()

        try:
            win32api.keybd_event(13, 0, 0, 0)
            win32gui.SetForegroundWindow(self.hwnd)
        except pywintypes.error as exc:
            logger.error("Unable to focus window: {exc}", exc=exc)

        win32gui.TrackPopupMenu(
            menu,
            win32con.TPM_LEFTALIGN,
            position[0],
            position[1],
            0,
            self.hwnd,
            None,
        )
        win32gui.PostMessage(self.hwnd, win32con.WM_NULL, 0, 0)

    def on_double_click(self, *args):
        ...

    def show_toast(self, msg: str, toast_callback: Callable[[], None]):
        self.toast_callback = toast_callback
        win32gui.Shell_NotifyIcon(
            win32gui.NIM_MODIFY,
            (
                self.hwnd,
                0,
                win32gui.NIF_INFO,
                win32con.WM_USER + 20,
                self.hicon,
                "Ballon Tooltip",
                msg,
                200,
                self.title,
            ),
        )
