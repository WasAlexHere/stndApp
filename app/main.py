import rumps
from constants import w_icon, b_icon, about_message


class AwesomeStatusBarApp(rumps.App):
    def __init__(self):
        super(AwesomeStatusBarApp, self).__init__("Awesome App", icon=w_icon)
        self.menu = ["About", "Set timer"]

    @rumps.clicked("About")
    def prefs(self, _):
        rumps.alert(title='About', message=about_message, icon_path=w_icon)

    @rumps.clicked("Say hi")
    def sayhi(self, _):
        rumps.notification("Please_Stand UP!", "amazing subtitle", "hi!!1", icon=w_icon)
        self.change_icon()

    def change_icon(self):
        if self.icon == w_icon:
            self.icon = b_icon
        else:
            self.icon = w_icon


if __name__ == "__main__":
    AwesomeStatusBarApp().run()
