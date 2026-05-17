import threading

from AppKit import (
    NSWindow,
    NSTextField,
    NSButton,
    NSColor,
    NSFont,
    NSScreen,
    NSTimer,
    NSBackingStoreBuffered,
    NSFloatingWindowLevel,
)
from Foundation import NSObject, NSMakeRect
import objc

_W = 320
_H = 80
_MARGIN = 20
_TIMEOUT = 8.0


class _PopupController(NSObject):
    def initWithMessage_subtitle_(self, message, subtitle):
        self = objc.super(_PopupController, self).init()
        if self is None:
            return None
        self._message = message
        self._subtitle = subtitle
        self._event = threading.Event()
        self._cancelled = False
        self._window = None
        self._timer = None
        return self

    def show_(self, _):
        screen = NSScreen.mainScreen()
        sf = screen.visibleFrame()
        x = sf.origin.x + sf.size.width - _W - _MARGIN
        y = sf.origin.y + _MARGIN

        self._window = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
            NSMakeRect(x, y, _W, _H), 0, NSBackingStoreBuffered, False
        )
        self._window.setLevel_(NSFloatingWindowLevel)
        self._window.setOpaque_(True)
        self._window.setHasShadow_(True)
        self._window.setBackgroundColor_(NSColor.windowBackgroundColor())

        cv = self._window.contentView()

        title_lbl = NSTextField.alloc().initWithFrame_(NSMakeRect(12, _H - 32, _W - 24, 20))
        title_lbl.setStringValue_("Sortable")
        title_lbl.setBezeled_(False)
        title_lbl.setDrawsBackground_(False)
        title_lbl.setEditable_(False)
        title_lbl.setSelectable_(False)
        title_lbl.setFont_(NSFont.boldSystemFontOfSize_(12))
        title_lbl.setTextColor_(NSColor.labelColor())
        cv.addSubview_(title_lbl)

        msg_lbl = NSTextField.alloc().initWithFrame_(NSMakeRect(12, _H - 50, _W - 100, 18))
        msg_lbl.setStringValue_(self._message)
        msg_lbl.setBezeled_(False)
        msg_lbl.setDrawsBackground_(False)
        msg_lbl.setEditable_(False)
        msg_lbl.setSelectable_(False)
        msg_lbl.setFont_(NSFont.systemFontOfSize_(12))
        msg_lbl.setTextColor_(NSColor.secondaryLabelColor())
        cv.addSubview_(msg_lbl)

        if self._subtitle:
            sub_lbl = NSTextField.alloc().initWithFrame_(NSMakeRect(12, _H - 66, _W - 24, 16))
            sub_lbl.setStringValue_(self._subtitle)
            sub_lbl.setBezeled_(False)
            sub_lbl.setDrawsBackground_(False)
            sub_lbl.setEditable_(False)
            sub_lbl.setSelectable_(False)
            sub_lbl.setFont_(NSFont.systemFontOfSize_(10))
            sub_lbl.setTextColor_(NSColor.tertiaryLabelColor())
            cv.addSubview_(sub_lbl)

        btn = NSButton.alloc().initWithFrame_(NSMakeRect(_W - 86, _H - 50, 74, 22))
        btn.setTitle_("Cancel")
        btn.setBezelStyle_(1)
        btn.setTarget_(self)
        btn.setAction_(objc.selector(self.cancelPressed_, signature=b"v@:@"))
        cv.addSubview_(btn)

        self._window.makeKeyAndOrderFront_(None)

        self._timer = NSTimer.scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_(
            _TIMEOUT,
            self,
            objc.selector(self.timerFired_, signature=b"v@:@"),
            None,
            False,
        )

    def cancelPressed_(self, sender):
        self._cancelled = True
        self._dismiss()

    def timerFired_(self, timer):
        self._dismiss()

    def _dismiss(self):
        if self._timer:
            self._timer.invalidate()
            self._timer = None
        if self._window:
            self._window.orderOut_(None)
            self._window = None
        self._event.set()

    def wait(self) -> bool:
        self._event.wait()
        return self._cancelled


def show(folder_name: str, is_new_folder: bool) -> bool:
    """Show a bottom-right popup. Returns True if the user pressed Cancel."""
    display = "root folder" if folder_name == "root" else folder_name
    message = f"Saving to: {display}"
    subtitle = "New folder will be created" if is_new_folder else ""

    controller = _PopupController.alloc().initWithMessage_subtitle_(message, subtitle)
    controller.performSelectorOnMainThread_withObject_waitUntilDone_("show:", None, False)
    return controller.wait()
