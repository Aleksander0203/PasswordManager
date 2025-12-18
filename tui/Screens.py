from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Input, ListItem, Button, Label, Header, Footer, ListView
from textual.containers import Vertical, Horizontal
import Storage as storage
import Crypto as crypto

class CreatePasswordScreen(Screen):
    def __init__(self, auth):
        super().__init__()
        self.auth = auth

    def compose(self) -> ComposeResult:
        yield Vertical(
            Label("Create a master password"),
            Input(password=True, placeholder="Password", id="pw1"),
            Input(password=True, placeholder="Confirm password", id="pw2"),
            Button("Create", id="create"),
        )

    def on_button_pressed(self, event: Button.Pressed):
        pw1 = self.query_one("#pw1", Input).value
        pw2 = self.query_one("#pw2", Input).value

        if pw1 != pw2:
            self.notify("Passwords do not match", severity="error")
            return

        self.auth.createMasterPassword(pw1)
        self.app.pop_screen()
        self.app.push_screen(LoginScreen(self.auth))

class LoginScreen(Screen):
    def __init__(self, auth):
        super().__init__()
        self.auth = auth
    def compose(self) -> ComposeResult:
        yield Vertical(
            Label("Enter master password"),
            Input(password=True, placeholder="Password", id="pw"),
            Button("Unlock", id="unlock"),
        )
    def on_button_pressed(self, event: Button.Pressed):
        password = self.query_one("#pw", Input).value
        if not self.auth.unlock(password):
            self.notify("Incorrect password", severity="error")
            return
        self.notify("Vault unlocked!", severity="information")
        self.app.pop_screen()
        self.app.push_screen(VaultScreen(self.auth))


class VaultScreen(Screen):
    def __init__(self,auth):
        super().__init__()
        self.auth = auth

    def compose(self) -> ComposeResult:
        yield Header()
        yield Vertical(
            Label("Vault"),
            ListView(id="pwdEntries"),
            Button("Add Entry", id="add"),
            Button("Logout", id="logout")
        )
        yield Footer()

    def on_mount(self):
        self.populateEntries()

    def on_button_pressed(self, event):
        if event.button.id == "add":
            self.app.push_screen(AddEntryScreen(self.auth))
        if event.button.id == "logout":
            self.auth.lock()
            self.app.push_screen(LoginScreen(self.auth))

    def on_list_view_selected(self, event: ListView.Selected):
        item = event.item
        entry = item.entry
        self.app.push_screen(ViewEntryScreen(self.auth, entry))

    def populateEntries(self):
        entries=storage.getAllPasswords()
        listView = self.query_one("#pwdEntries", ListView)
        listView.clear()
        for i in entries:
            item = ListItem(
                Horizontal(
                    Label(i.serviceName),
                    Label(i.username),
                    Label("********")
                )
            )
            item.entry = i 
            listView.append(item)




class AddEntryScreen(Screen):

    def __init__(self,auth):
        super().__init__()
        self.auth = auth

    def compose(self) -> ComposeResult:
        yield Header()
        yield Vertical(
            Label("Enter Service Name:"),
            Input(placeholder="Service Name", id="serviceName"),
            Label("Enter Username"),
            Input(placeholder="Username", id="username"),
            Label("Enter Password"),
            Horizontal(
                Input(password=True,placeholder="Password", id="password"),
                Button("Show", id="toggleView")
            ),
            Button("Add Entry", id="addEntry")
        ) 
        yield Footer()

    def on_button_pressed(self, event):
        if event.button.id == "toggleView":
            passwordInput = self.query_one("#password", Input)
            passwordInput.password = not passwordInput.password
            event.button.label = "Hide" if passwordInput.password == True else "Show"
        elif event.button.id == "addEntry":
            serviceNameEntry = self.query_one("#serviceName", Input)
            username = self.query_one("#username", Input)
            passwordInput = self.query_one("#password", Input)
            encryptedPassword = crypto.encrypt(passwordInput.value, self.auth.getKey())
            storage.addUserPasswordCombo(serviceNameEntry.value, username.value, encryptedPassword)
            self.app.pop_screen()
            vaultScreen = self.app.screen_stack[-1]
            vaultScreen.populateEntries()

class ViewEntryScreen(Screen):

    def __init__(self,auth,passwordEntry):
        super().__init__()
        self.auth = auth
        self.passwordEntry = passwordEntry

    def compose(self) -> ComposeResult:
        yield Header()
        yield Vertical(
            Horizontal(
                Label("Service Name: "),
                Label(self.passwordEntry.getServiceName())
            ),
            Horizontal(
                Label("Username: "),
                Label(self.passwordEntry.getUsername())
            ),
            Horizontal(
                Label("Password: "),
                Label("********", id="passwordLabel"),
                Button("Show", id="toggleView")
            ),
            Button("Back", id="back")
        )

    def on_button_pressed(self, event):
        if event.button.id == "toggleView":
            if event.button.label == "Show":
                passwordLabel = self.query_one("#passwordLabel", Label)
                passwordLabel.update(crypto.decrypt(ciphertext= self.passwordEntry.password, key = self.auth.getKey()))
                event.button.label = "Hide"
            else:
                passwordLabel = self.query_one("#passwordLabel",Label)
                passwordLabel.update("********")
                event.button.label = "Show"
        elif event.button.id == "back":
            self.app.pop_screen()
            vaultScreen = self.app.screen_stack[-1]
            vaultScreen.populateEntries()

