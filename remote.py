from kivy.app import App
from control import RemoteControl
from kivy.clock import Clock


class RemoteApp(App):
    def build(self):
        remote = RemoteControl()
        remote.start()
        Clock.schedule_interval(remote.update, 1.0 / 60.0)
        return remote


if __name__ == '__main__':
    RemoteApp().run()

