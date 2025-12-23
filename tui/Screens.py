from textual.app import ComposeResult
from textual.screen import Screen, ModalScreen
from textual.widgets import Input, ListItem, Button, Label, Header, Footer, ListView
from textual.containers import Vertical, Horizontal
import Storage as storage
import Crypto as crypto
import random

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
        self.app.resetTimer()
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
        self.app.resetTimer()
        password = self.query_one("#pw", Input).value
        if not self.auth.unlock(password):
            self.notify("Incorrect password", severity="error")
            return
        self.notify("Vault unlocked!", severity="information")
        self.app.pop_screen()
        self.app.inactivityTimer.resume()
        self.app.push_screen(VaultScreen(self.auth))


class VaultScreen(Screen):
    def __init__(self,auth):
        super().__init__()
        self.auth = auth
        self.searchQuery = ""

    def compose(self) -> ComposeResult:
        yield Header()
        yield Vertical(
            Label("Vault"),
            Input(placeholder="Search",id="search"),
            ListView(id="pwdEntries"),
            Horizontal(Button("Add Entry", id="add"),Button("Logout", id="logout"), Button("Generate Password", id="genPassword"))
        )
        yield Footer()

    def on_mount(self):
        self.populateEntries()

    def on_button_pressed(self, event):
        self.app.resetTimer()
        if event.button.id == "add":
            self.app.push_screen(AddEntryScreen(self.auth))
        if event.button.id == "logout":
            self.auth.lock()
            self.app.push_screen(LoginScreen(self.auth))
        if event.button.id == "genPassword":
            self.app.push_screen(GeneratePasswordScreen())

    def on_list_view_selected(self, event: ListView.Selected):
        self.app.resetTimer()
        item = event.item
        entry = item.entry
        self.app.push_screen(ViewEntryScreen(self.auth, entry))

    def on_input_changed(self, event: Input.Changed):
        if event.input.id == "search":
            self.searchQuery = event.value.lower()
            self.populateEntries()

    def populateEntries(self):
        entries=storage.getAllPasswords()
        listView = self.query_one("#pwdEntries", ListView)
        listView.clear()
        for i in entries:
            if self.searchQuery:
                if (self.searchQuery not in i.getUsername().lower() and self.searchQuery not in i.getServiceName().lower()):
                    continue
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
        self.STRING_OF_CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"

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
            Button("Generate", id="generate"),
            Button("Back", id="back"),
            Button("Add Entry", id="addEntry")
        ) 
        yield Footer()

    def on_button_pressed(self, event):
        self.app.resetTimer()
        if event.button.id == "toggleView":
            passwordInput = self.query_one("#password", Input)
            passwordInput.password = not passwordInput.password
            event.button.label = "Show" if passwordInput.password == True else "Hide"
        elif event.button.id == "addEntry":
            serviceNameEntry = self.query_one("#serviceName", Input)
            username = self.query_one("#username", Input)
            passwordInput = self.query_one("#password", Input)
            encryptedPassword = crypto.encrypt(passwordInput.value, self.auth.getKey())
            storage.addUserPasswordCombo(serviceNameEntry.value, username.value, encryptedPassword)
            self.app.pop_screen()
            vaultScreen = self.app.screen_stack[-1]
            vaultScreen.populateEntries()
        elif event.button.id == "generate":
            generatedPassword = ""
            for _ in range(16):
                generatedPassword+= random.choice(self.STRING_OF_CHARS)
            self.query_one("#password", Input).value = generatedPassword
        elif event.button.id == "back":
            self.query_one("#serviceName", Input).value = ""
            self.query_one("#username", Input).value = ""
            self.query_one("#password", Input).value = ""
            self.app.pop_screen()

    def on_unmount(self):
        try:
            self.query_one("#password", Input).value = ""
            self.query_one("#username", Input).value = ""
            self.query_one("serviceName", Input).value = ""
        except:
            pass

class EditEntryScreen(AddEntryScreen):

    def __init__(self, auth, passwordEntry):
        super().__init__(auth)
        self.passwordEntry = passwordEntry

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
            Button("Edit Entry", id="editEntry")
        ) 
        yield Footer()

    def on_mount(self):
        self.query_one("#password", Input).value = crypto.decrypt(ciphertext=self.passwordEntry.getPassword(),key=self.auth.getKey())
        self.query_one("#username", Input).value = self.passwordEntry.getUsername()
        self.query_one("#serviceName", Input).value = self.passwordEntry.getServiceName()

    def on_button_pressed(self, event):
        self.app.resetTimer()
        if event.button.id == "toggleView":
            passwordInput = self.query_one("#password", Input)
            passwordInput.password = not passwordInput.password
            event.button.label = "Hide" if passwordInput.password == True else "Show"
        elif event.button.id == "editEntry":
            serviceNameEntry = self.query_one("#serviceName", Input)
            username = self.query_one("#username", Input)
            passwordInput = self.query_one("#password", Input)
            encryptedPassword = crypto.encrypt(passwordInput.value, self.auth.getKey())
            storage.editPasswordByID(serviceNameEntry.value, username.value, encryptedPassword, self.passwordEntry.getID())
            
            self.app.pop_screen()
            self.app.pop_screen()
            self.app.push_screen(ViewEntryScreen(self.auth, storage.getEntryByID(self.passwordEntry.getID())))




class ViewEntryScreen(Screen):
    BINDINGS = [
        ("c", "copyPassword", "Copy Password"), 
        ("u", "copyUsername", "Copy Username"), 
        ("d", "deleteEntry", "Delete Entry")
    ]

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
            Button("Edit", id="editEntry"),
            Button("Back", id="back")
        )
        yield Footer()

    def on_unmount(self):
        try:
            passwordLabel = self.query_one("#passwordLabel", Label)
            passwordLabel.update("********")
        except:
            pass

    def on_button_pressed(self, event):
        self.app.resetTimer()
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
            self.clearClipboard()
            self.app.pop_screen()
            vaultScreen = self.app.screen_stack[-1]
            vaultScreen.populateEntries()
        elif event.button.id == "editEntry":
            self.app.push_screen(EditEntryScreen(self.auth, self.passwordEntry))

    def action_copyUsername(self):
        self.app.copy_to_clipboard(self.passwordEntry.getUsername())
        self.notify("Username has been added to clipboard.", severity="information")
        self.set_timer(delay=60 * 10, callback=self.clearClipboard)

    def action_copyPassword(self):
        plaintext = crypto.decrypt(ciphertext = self.passwordEntry.getPassword(), key = self.auth.getKey())
        self.app.copy_to_clipboard(plaintext)
        self.notify("Password has been added to clipboard.", severity="information")
        self.set_timer(delay=60 * 10, callback=self.clearClipboard)

    def action_deleteEntry(self):
        self.app.push_screen(ConfirmDeleteScreen("Are you sure you want to delete this entry?"), self._handle_deleteConfirmation)

    def clearClipboard(self):
        if self.app.clipboard:
            self.app.copy_to_clipboard("")
            self.notify("Clipboard has been cleared.", severity="information")

    def _handle_deleteConfirmation(self, confirmed):
        if not confirmed:
            return
        entryid = self.passwordEntry.getID()
        storage.deleteEntryByID(entryid)
        self.app.pop_screen()
        vaultScreen = self.app.screen_stack[-1]
        vaultScreen.populateEntries()

        

class ConfirmDeleteScreen(ModalScreen[bool]):

    def __init__(self, message: str):
        super().__init__()
        self.message = message
    
    def compose(self):
        yield Vertical(
            Label(self.message),
            Horizontal(
                Button("Cancel", id="cancel"),
                Button("Delete", id="confirm", variant="error"),
            )
        )

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "confirm":
            self.dismiss(True)
        else:
            self.dismiss(False)

class GeneratePasswordScreen(Screen):

    def __init__(self):
        super().__init__()
        self.STRING_OF_CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
    
    def compose(self):
        yield Header()
        yield Vertical(
            Label("Generate a password:"),
            Horizontal(
                Input(password=True, placeholder="Password", id="password"),
            ),
            Button("Show", id="toggleView"),
            Button("Generate", id="generate")

        )
        yield Button("Back", id="back")
        yield Footer()
    
    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "generate":
            password = self.query_one("#password", Input)
            generatedPassword = ""
            for _ in range(16):
                generatedPassword += random.choice(self.STRING_OF_CHARS)
            password.value = generatedPassword
            self.app.copy_to_clipboard(password.value)
            self.notify("Generated password added to clipboard",severity="information")
            self.set_timer(delay=60*10, callback = self.clearClipboard)
        elif event.button.id == "toggleView":
            passwordInput = self.query_one("#password", Input)
            passwordInput.password = not passwordInput.password
            event.button.label = "Show" if passwordInput.password == True else "Hide"
        else:
            self.app.pop_screen()

    def clearClipboard(self):
        if self.app.clipboard:
            self.app.copy_to_clipboard("")
            self.notify("Clipboard has been cleared.", severity="information")

