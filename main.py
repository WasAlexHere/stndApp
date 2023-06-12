import rumps
from datetime import datetime, timedelta

icon = "icon.png"
trophy_icon = "trophy.png"


class StndApp(rumps.App):
    def __init__(self):
        self.count = 0
        self.seconds = 60
        self._stand_interval = 45 * self.seconds
        self._sit_interval = 15 * self.seconds
        self.max_stand_time = str((datetime.now() + timedelta(hours=4)).time())[:-7]

        self.config = {
            "stand": "Alright, alright, alright!",
            "stand_message": f"Let's stand up for {self._stand_interval} mins",
            "sit": "Perfect, let's take a break!",
            "sit_message": f"Sit down for {self._sit_interval} mins",
        }

        super(StndApp, self).__init__("stndApp", icon=icon)
        self.menu = ["Start", "Stop"]

        # rumps.debug_mode(True)

        self.timer_update_time = rumps.Timer(self.ticker, 1)
        self.timer_stand_time = rumps.Timer(self.check_stand_time, 1)
        self.timer_sit_time = rumps.Timer(self.check_sit_time, 1)

        self.delta = None
        self.stop_time = None
        self.current_time = None

    @rumps.clicked("Start")
    def start_button(self, _):
        if not self.timer_update_time.is_alive():
            self.delta = timedelta(seconds=self._stand_interval)
            self.stop_time = str((datetime.now() + self.delta).time())[:-7]
            self.timer_update_time.start()
            self.timer_stand_time.start()
            button = self.menu.get("Start")
            button.hidden = True

    @rumps.clicked("Stop")
    def stop_button(self, _):
        for item in rumps.timers():
            item.stop()
        button = self.menu.get("Start")
        button.hidden = False
        self.count = 0

    def ticker(self, _):
        date = datetime.now().time()
        self.current_time = str(date)[:-7]

    def update_date(self):
        self.stop_time = str((datetime.now() + self.delta).time())[:-7]

    def check_stand_time(self, _):
        # print(f"STAND: {self.current_time}, {self.stop_time}")
        if self.current_time != self.max_stand_time:
            if self.current_time == self.stop_time:
                self.sit_notification()
                self.timer_stand_time.stop()
                self.count += 1

                self.delta = timedelta(seconds=self._sit_interval)
                self.update_date()
                self.timer_sit_time.start()
        else:
            self.stop_button()

    def check_sit_time(self, _):
        # print(f"SIT: {self.current_time}, {self.stop_time}")
        if self.current_time == self.stop_time:
            self.stand_notification()
            self.timer_sit_time.stop()

            self.delta = timedelta(seconds=self._stand_interval)
            self.update_date()
            self.timer_stand_time.start()

    def stand_notification(self):
        rumps.notification(
            self.config["stand"],
            None,
            self.config["stand_message"],
            icon=trophy_icon,
        )

    def sit_notification(self):
        rumps.notification(
            self.config["sit"],
            None,
            self.config["sit_message"],
            icon=icon,
        )


if __name__ == "__main__":
    StndApp().run()
