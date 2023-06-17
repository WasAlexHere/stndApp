import rumps

icon = "icon.png"
trophy_icon = "trophy.png"


class StndApp(rumps.App):
    def __init__(self):
        self._seconds = 60
        self._stand_interval = 45
        self._sit_interval = 15

        self.config = {
            "stand": "Alright, alright, alright!",
            "stand_message": f"Let's stand up for {self._stand_interval} minutes",
            "sit": "Perfect, let's take a break!",
            "sit_message": f"Sit down for {self._sit_interval} minutes"
        }
        self.last_timer = {'last': "stand"}

        super(StndApp, self).__init__("stndApp", icon=icon)
        self.menu = ["Start", "Stop"]

        rumps.debug_mode(True)

        self.stand_timer = rumps.Timer(self.countdown_stand, 1)
        self.sit_timer = rumps.Timer(self.countdown_sit, 1)

        self.n = 10

    @rumps.clicked("Start")
    def start_button(self, sender):
        if sender.title == "Start":
            if self.last_timer.get("last") == "stand":
                self.stand_timer.start()
                self.last_timer["last"] = "stand"
            else:
                self.sit_timer.start()
                self.last_timer["last"] = "sit"
            sender.title = "Pause"
        else:
            sender.title = "Start"
            if self.stand_timer.is_alive():
                self.stand_timer.stop()
            if self.sit_timer.is_alive():
                self.sit_timer.stop()

    @rumps.clicked("Stop")
    def stop_button(self, _):
        for item in rumps.timers():
            item.stop()

        button = self.menu.get("Start")
        button.title = "Start"

        self.title = None
        self.n = 10
        self.last_timer['last'] = "stand"

    def countdown_stand(self, _):
        if self.title != "00:00":
            if self.n > -1:
                m, s = divmod(self.n, 60)
                self.title = "{:02d}:{:02d}".format(m, s)
                self.n -= 1
                print(self.title, self.last_timer)
        else:
            response = self.sit_alert()
            if response.clicked == 1:
                self.change_interval(self.stand_timer,
                                     self.sit_timer,
                                     5,
                                     "sit")
            if response.clicked == 2:
                self.stop_button(_)

    def countdown_sit(self, _):
        if self.title != "00:00":
            if self.n > -1:
                m, s = divmod(self.n, 60)
                self.title = "{:02d}:{:02d}".format(m, s)
                self.n -= 1
                print(self.title, self.last_timer)
        else:
            response = self.stand_alert()
            if response.clicked == 1:
                self.change_interval(self.sit_timer,
                                     self.stand_timer,
                                     10,
                                     "stand")
            if response.clicked == 2:
                self.stop_button(_)

    def stand_alert(self):
        window = rumps.Window(
            title=self.config["stand"],
            message=self.config["stand_message"],
            ok="Stand Up",
            dimensions=(0, 0),
        )
        window.icon = "trophy.png"
        window.add_button("Stop")

        return window.run()

    def sit_alert(self):
        window = rumps.Window(
            title=self.config["sit"],
            message=self.config["sit_message"],
            ok="Sit Down",
            dimensions=(0, 0),
        )
        window.icon = "trophy.png"
        window.add_button("Stop")

        return window.run()

    def change_interval(self, func1, func2, num, action):
        func1.stop()
        self.n = num
        self.title = None
        func2.start()
        self.last_timer["last"] = action


if __name__ == "__main__":
    StndApp().run()
