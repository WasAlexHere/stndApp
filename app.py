import rumps

main_icon = "main.png"
up_icon = "up.png"
down_icon = "down.png"
trophy_icon = "trophy.png"
edit_icon = "edit.png"
fail_icon = "fail.png"
success_icon = "success.png"


class LessThanAnHour(Exception):
    pass


class StndApp(rumps.App):
    def __init__(self):
        self._seconds = 60
        self._stand_interval = 45
        self._sit_interval = 15

        self.config = {
            "stand": "Alright, alright, alright!",
            "stand_message": f"Let's stand up for {self._stand_interval} minutes",
            "sit": "Perfect, let's take a break!",
            "sit_message": f"Sit down for {self._sit_interval} minutes",
            "failed_value": "Unfortunately, you can only enter integer numbers!",
            "failed_less": "Unfortunately, you can only enter numbers less than 61!",
        }
        self.last_timer = {"last": "stand"}

        super(StndApp, self).__init__("stndApp", icon=main_icon)
        self.menu = ["Start", "Stop", "Edit", None]

        # rumps.debug_mode(True)

        self.stand_timer = rumps.Timer(self.countdown_stand, 1)
        self.sit_timer = rumps.Timer(self.countdown_sit, 1)

        self.n = self._stand_interval * self._seconds

    @rumps.clicked("Start")
    def start_button(self, sender):
        if sender.title == "Start":
            if self.last_timer.get("last") == "stand":
                self.stand_timer.start()
                self.icon = up_icon
                self.last_timer["last"] = "stand"
            else:
                self.sit_timer.start()
                self.icon = down_icon
                self.last_timer["last"] = "sit"
            sender.title = "Pause"
            self.menu["Edit"].hidden = True
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
        self.n = self._stand_interval * self._seconds
        self.last_timer["last"] = "stand"
        self.menu["Edit"].hidden = False
        self.icon = "main.png"

    @rumps.clicked("Edit")
    def edit_button(self, _):
        if not (self.sit_timer.is_alive() or self.stand_timer.is_alive()):
            response = self.edit_alert()

            if response.clicked:
                try:
                    new = int(response.text)
                    if 0 < new < 61:
                        self._stand_interval = new
                        self._sit_interval = 60 - self._stand_interval
                        self.successful_notification()
                    else:
                        self.failed_notification(
                            title="Less than 60", message=self.config["failed_less"]
                        )
                        raise LessThanAnHour(
                            "The input value should be more than 0 and less than 61"
                        )
                except ValueError:
                    self.failed_notification(
                        title="Incorrect input number",
                        message=self.config["failed_value"],
                    )
                    raise ValueError("invalid literal for int() with base 10")

    def countdown_stand(self, _):
        if self.title != "00:00":
            if self.n > -1:
                m, s = divmod(self.n, 60)
                self.title = "{:02d}:{:02d}".format(m, s)
                self.n -= 1
                # print(self.title, self.last_timer)
        else:
            response = self.sit_alert()
            if response.clicked == 1:
                self.change_interval(
                    self.stand_timer,
                    self.sit_timer,
                    self._stand_interval * self._seconds,
                    "sit",
                    down_icon,
                )
            if response.clicked == 2:
                self.stop_button(_)

    def countdown_sit(self, _):
        if self.title != "00:00":
            if self.n > -1:
                m, s = divmod(self.n, 60)
                self.title = "{:02d}:{:02d}".format(m, s)
                self.n -= 1
                # print(self.title, self.last_timer)
        else:
            response = self.stand_alert()
            if response.clicked == 1:
                self.change_interval(
                    self.sit_timer,
                    self.stand_timer,
                    self._sit_interval * self._seconds,
                    "stand",
                    up_icon,
                )
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

    def edit_alert(self):
        window = rumps.Window(
            title="Edit interval",
            message=f"Type new stand interval (previous {self._stand_interval} minutes). "
            f"\n The sit interval will be update automatically.",
            dimensions=(100, 25),
            cancel=True,
        )
        window.icon = edit_icon

        return window.run()

    def successful_notification(self):
        rumps.notification(
            title="Update sit/stand interval",
            message=f"New intervals are: "
            f"Stand {self._stand_interval}, "
            f"Sit {self._sit_interval} minutes",
            subtitle=None,
            icon=success_icon,
        )

    def failed_notification(self, title, message):
        rumps.notification(title=title, message=message, subtitle=None, icon=fail_icon)

    def change_interval(self, func1, func2, num, action, new):
        func1.stop()
        self.n = num
        self.title = None
        func2.start()
        self.last_timer["last"] = action
        self.icon = new


if __name__ == "__main__":
    StndApp().run()
