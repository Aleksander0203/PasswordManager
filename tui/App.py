from textual.app import App, ComposeResult
from textual.widgets import Footer, Header
from tui.Screens import LoginScreen, CreatePasswordScreen
from Auth import Auth
import Storage as storage

class PasswordManagerApp(App):
    CSS_PATH = "Styles.css"

    def on_mount(self):
        storage.createDB()
        self.auth = Auth()
        if self.auth.isInitialised():
            self.push_screen(LoginScreen(self.auth))
        else:
            self.push_screen(CreatePasswordScreen(self.auth))
