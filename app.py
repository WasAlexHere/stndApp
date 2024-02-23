import rumps
from datetime import datetime

main_icon = "main.png"
up_icon = "up.png"
down_icon = "down.png"
trophy_icon = "trophy.png"
edit_icon = "edit.png"
rest_icon = "rest.png"
fail_icon = "fail.png"
success_icon = "success.png"


class MoreThanAnHour(Exception):
    pass


class MoreThanAverage(Exception):
    pass


class StndApp(rumps.App):
    def __init__(self):
        self._seconds = 60
        self._stand_interval = 30
        self._sit_interval = 30
        self._stand_minutes_amount = 0
        self._duration = 4
        self._current_date = 0

        self.config = {
            "stand": "Alright, alright, alright!",
            "sit": "Perfect, let's take a break!",
            "failed_value": "Unfortunately, you can only enter integer numbers!",
            "failed_less": "Unfortunately, you can only enter numbers less than 61!",
            "failed_duration": "Unfortunately, you can only enter numbers less than 4!",
            "rest": "Hold on, tiger!",
            "rest_message": "You've reached the limit for standing work (4 hours a day).\n"
            "Take a rest and continue tomorrow!",
        }

        self.last_timer = {"last": "stand"}

        super(StndApp, self).__init__("stndApp", icon=main_icon, template=True)
        self.menu = [
            "Start",
            "Stop",
            ("Edit", ["Stand/Sit Interval", "Duration"]),
            None,
        ]
        self.menu["Stop"].hidden = True

        # rumps.debug_mode(True)

        self.stand_timer = rumps.Timer(self.countdown_stand, 1)
        self.sit_timer = rumps.Timer(self.countdown_sit, 1)

        # self.check_date = rumps.Timer(self.date_validation, 60)
        # self.check_date.start()

        self.n = self._stand_interval * self._seconds

    @rumps.clicked("Start")
    def start_button(self, sender):
        self._current_date = datetime.now()
        # print(self._current_date)
        if self._stand_minutes_amount / 60 < self._duration or self.date_validation(
            self._current_date
        ):
            self.menu["Stop"].hidden = False
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
        else:
            self.rest_alert()

    @rumps.clicked("Stop")
    def stop_button(self, _):
        self.stand_timer.stop()
        self.sit_timer.stop()

        button = self.menu.get("Start")
        button.title = "Start"

        self.title = None
        self.n = self._stand_interval * self._seconds
        self.last_timer["last"] = "stand"
        self.menu["Edit"].hidden = False
        self.icon = main_icon
        self.menu["Stop"].hidden = True

    @rumps.clicked("Edit", "Stand/Sit Interval")
    def edit_interval_button(self, _):
        if not (self.sit_timer.is_alive() or self.stand_timer.is_alive()):
            response = self.edit_alert(
                title="Edit interval",
                message=f"Type new stand interval (previous {self._stand_interval} minutes).\n"
                f"The sit interval will be update automatically.",
            )

            if response.clicked:
                try:
                    new = int(response.text)
                    if 0 < new < 61:
                        self._stand_interval = new
                        self._sit_interval = 60 - self._stand_interval
                        self.n = self._stand_interval * self._seconds
                        self.send_notification(
                            title="Updated sit/stand interval!",
                            message=f"New intervals are:\n"
                            f"Stand: {self._stand_interval}, "
                            f"Sit: {self._sit_interval} minutes",
                            icon=success_icon,
                        )
                    else:
                        self.send_notification(
                            title="More than 60 !",
                            message=self.config["failed_less"],
                            icon=fail_icon,
                        )
                        raise MoreThanAnHour(
                            "The input value should be more than 0 and less than 61"
                        )
                except ValueError:
                    self.send_notification(
                        title="Incorrect input number!",
                        message=self.config["failed_value"],
                        icon=fail_icon,
                    )
                    raise ValueError("Invalid literal for int() with base 10")

    @rumps.clicked("Edit", "Duration")
    def edit_duration_button(self, _):
        if not (self.sit_timer.is_alive() or self.stand_timer.is_alive()):
            response = self.edit_alert(
                title="Edit duration",
                message=f"Type new duration for standing work (previous {self._duration} hours)",
            )

            if response.clicked:
                try:
                    new = int(response.text)
                    if 0 < new <= 4:
                        self._duration = new
                        self.send_notification(
                            title="Updated duration of standing work!",
                            message=f"New duration is: {self._duration}",
                            icon=success_icon,
                        )
                    else:
                        self.send_notification(
                            title="More than 4 hours a day!",
                            message=self.config["failed_duration"],
                            icon=fail_icon,
                        )
                        raise MoreThanAverage(
                            "The input value should be more than 0 and less or equal 4"
                        )
                except ValueError:
                    self.send_notification(
                        title="Incorrect input number!",
                        message=self.config["failed_value"],
                        icon=fail_icon,
                    )
                    raise ValueError("Invalid literal for int() with base 10")

    def countdown_stand(self, _):
        if self.title != "00:00":
            if self.n > -1:
                m, s = divmod(self.n, 60)
                self.title = "{:02d}:{:02d}".format(m, s)
                self.n -= 1
        else:
            self._stand_minutes_amount += self._stand_interval

            response = self.sit_alert()

            if response.clicked == 1:
                self.change_position(
                    self.stand_timer,
                    self.sit_timer,
                    self._sit_interval * self._seconds,
                    "sit",
                    down_icon,
                )
            elif response.clicked == 2:
                self.stop_button(_)

    def countdown_sit(self, _):
        if self.title != "00:00":
            if self.n > -1:
                m, s = divmod(self.n, 60)
                self.title = "{:02d}:{:02d}".format(m, s)
                self.n -= 1
        else:
            response = self.stand_alert()
            if response.clicked == 1:
                self._current_date = datetime.now()
                if self._stand_minutes_amount / 60 < 4 or self.date_validation(
                    self._current_date
                ):
                    self.change_position(
                        self.sit_timer,
                        self.stand_timer,
                        self._stand_interval * self._seconds,
                        "stand",
                        up_icon,
                    )
                else:
                    self.rest_alert()
                    self.stop_button(_)
            elif response.clicked == 2:
                self.stop_button(_)

    def stand_alert(self):
        window = rumps.Window(
            title=self.config["stand"],
            message=f"Let's stand up for {self._stand_interval} minutes",
            ok="Stand Up",
            dimensions=(0, 0),
        )
        window.icon = trophy_icon
        window.add_button("Stop")

        return window.run()

    def sit_alert(self):
        window = rumps.Window(
            title=self.config["sit"],
            message=f"Sit down for {self._sit_interval} minutes\n"
            f"Total amount of stand time (mins): {self._stand_minutes_amount}",
            ok="Sit Down",
            dimensions=(0, 0),
        )
        window.icon = trophy_icon
        window.add_button("Stop")

        return window.run()

    @staticmethod
    def edit_alert(title, message):
        window = rumps.Window(
            title=title,
            message=message,
            dimensions=(100, 25),
            cancel=True,
        )
        window.icon = edit_icon

        return window.run()

    def rest_alert(self):
        window = rumps.Window(
            title=self.config["rest"],
            message=f"{self.config['rest_message']}\n"
            f"(You're standing hours are {self._stand_minutes_amount // 60}).",
            dimensions=(0, 0),
        )
        window.icon = rest_icon

        return window.run()

    @staticmethod
    def send_notification(title, message, icon=None):
        rumps.notification(title=title, message=message, subtitle=None, icon=icon)

    def change_position(self, func1, func2, num, action, new):
        func1.stop()
        self.n = num
        self.title = None
        func2.start()
        self.last_timer["last"] = action
        self.icon = new

    def date_validation(self, c_date):
        year = datetime.now().year
        month = datetime.now().month
        day = datetime.now().day + 1

        if c_date >= datetime(year, month, day):
            self._stand_minutes_amount = 0
            return False
        return True


if __name__ == "__main__":
    StndApp().run()
