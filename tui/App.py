from textual.app import App, ComposeResult
from textual.widgets import Footer, Header
from tui.Screens import LoginScreen, CreatePasswordScreen
from Auth import Auth
import Storage as storage

class PasswordManagerApp(App):
    CSS_PATH = "Styles.css"

    def on_mount(self):
        INACTIVITY_TIMER = 60 * 2 
        storage.createDB()
        self.auth = Auth()
        self.inactivityTimer = self.set_timer(INACTIVITY_TIMER, self.autolock,pause=True)
        self.pushStartScreen()

    def autolock(self):
        if self.auth.isUnlocked():
            self.auth.lock()
            self.notify("Vault locked due to inactivity", severity="warning")
            self.screen_stack.clear()
            self.pushStartScreen()

    def pushStartScreen(self):
        if self.auth.isInitialised():
            self.push_screen(LoginScreen(self.auth))
        else:
            self.push_screen(CreatePasswordScreen(self.auth))

    def resetTimer(self):
        if hasattr(self, "inactivityTimer"):
            self.inactivityTimer.reset()
