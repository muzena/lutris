"""Game panel"""
from datetime import datetime
from gi.repository import Gtk, Pango
from lutris.gui.widgets.utils import get_pixbuf_for_panel, get_pixbuf_for_game
from lutris.util.strings import gtk_safe


class GamePanel(Gtk.Fixed):
    """Panel allowing users to interact with a game"""
    def __init__(self, game_actions):
        self.game_actions = game_actions
        self.game = game_actions.game
        self.game.connect("game-start", self.on_game_start)
        self.game.connect("game-stop", self.on_game_stop)

        super().__init__()
        self.get_style_context().add_class("game-panel")
        self.set_size_request(320, -1)
        self.show()

        self.put(self.get_background(), 0, 0)
        self.put(self.get_icon(), 12, 16)
        self.put(self.get_title_label(), 50, 20)
        labels_x = 50
        if self.game.is_installed:
            self.put(self.get_runner_label(), labels_x, 64)
        if self.game.playtime:
            self.put(self.get_playtime_label(), labels_x, 86)
        if self.game.lastplayed:
            self.put(self.get_last_played_label(), labels_x, 108)
        self.buttons = self.get_buttons()
        self.place_buttons(145)

    def get_background(self):
        """Return the background image for the panel"""
        image = Gtk.Image.new_from_pixbuf(get_pixbuf_for_panel(self.game.slug))
        image.show()
        return image

    def get_icon(self):
        """Return the game icon"""
        icon = Gtk.Image.new_from_pixbuf(get_pixbuf_for_game(self.game.slug, "icon"))
        icon.show()
        return icon

    def get_title_label(self):
        """Return the label with the game's title"""
        title_label = Gtk.Label()
        title_label.set_markup("<span font_desc='16'>%s</span>" % gtk_safe(self.game.name))
        title_label.set_ellipsize(Pango.EllipsizeMode.END)
        title_label.set_size_request(256, -1)
        title_label.set_alignment(0, 0.5)
        title_label.set_justify(Gtk.Justification.LEFT)
        title_label.show()
        return title_label

    def get_runner_label(self):
        """Return the label containing the runner info"""
        runner_label = Gtk.Label()
        runner_label.show()
        runner_label.set_markup(
            "For <b>%s</b>, runs with %s" %
            (self.game.platform, self.game.runner.name)
        )
        return runner_label

    def get_playtime_label(self):
        """Return the label containing the playtime info"""
        playtime_label = Gtk.Label()
        playtime_label.show()
        playtime_label.set_markup("Time played: <b>%s</b>" % self.game.formatted_playtime)
        return playtime_label

    def get_last_played_label(self):
        """Return the label containing the last played info"""
        last_played_label = Gtk.Label()
        last_played_label.show()
        lastplayed = datetime.fromtimestamp(self.game.lastplayed)
        last_played_label.set_markup("Last played: <b>%s</b>" % lastplayed.strftime("%Y/%m/%d"))
        return last_played_label

    def get_buttons(self):
        displayed = self.game_actions.get_displayed_entries()
        disabled_entries = self.game_actions.get_disabled_entries()
        icon_map = {
            # "stop": "media-playback-stop-symbolic",
            # "play": "media-playback-start-symbolic",
            "configure": "preferences-system-symbolic",
            "browse": "system-file-manager-symbolic",
            "show_logs": "utilities-system-monitor-symbolic",
            "remove": "user-trash-symbolic",
        }
        buttons = {}
        for action in self.game_actions.get_game_actions():
            action_id, label, callback = action
            if action_id in icon_map:
                button = Gtk.Button.new_from_icon_name(
                    icon_map[action_id], Gtk.IconSize.MENU
                )
                button.set_tooltip_text(label)
                button.set_size_request(32, 32)
            else:
                button = Gtk.Button(label)
                if action_id in ("play", "stop"):
                    button_width = 146
                    button_height = 42
                else:
                    button_width = -1
                    button_height = 24
                    button.props.relief = Gtk.ReliefStyle.NONE
                    button.get_children()[0].set_alignment(0, 0.5)
                    button.get_style_context().add_class("panel-button")
                button.set_size_request(button_width, button_height)
            button.connect("clicked", callback)
            if displayed.get(action_id):
                button.show()
            if disabled_entries.get(action_id):
                button.set_sensitive(False)
            buttons[action_id] = button
        return buttons

    def place_buttons(self, base_height):
        play_x_offset = 87
        icon_offset = 6
        icon_width = 32
        icon_start = 84
        icons_y_offset = 60
        buttons_x_offset = 28
        for action_id, button in self.buttons.items():
            position = None
            if action_id in ("play", "stop"):
                position = (play_x_offset,
                            base_height)
            if action_id == "configure":
                position = (icon_start,
                            base_height + icons_y_offset)
            if action_id == "browse":
                position = (icon_start + icon_offset + icon_width,
                            base_height + icons_y_offset)
            if action_id == "show_logs":
                position = (icon_start + icon_offset * 2 + icon_width * 2,
                            base_height + icons_y_offset)
            if action_id in ("install", "remove"):
                position = (icon_start + icon_offset * 3 + icon_width * 3,
                            base_height + icons_y_offset)
            if action_id == "execute-script":
                position = (50,
                            base_height + 82)

            current_y = base_height + 150
            if action_id in ("add", "install_more"):
                position = (buttons_x_offset, current_y + 40)
            if action_id == "view":
                position = (buttons_x_offset, current_y + 80)
            if action_id in ("desktop-shortcut", "rm-desktop-shortcut"):
                position = (buttons_x_offset, current_y + 120)
            if action_id in ("menu-shortcut", "rm-menu-shortcut"):
                position = (buttons_x_offset, current_y + 160)

            if position:
                self.put(button, position[0], position[1])

    def on_game_start(self, widget):
        self.buttons["play"].hide()
        self.buttons["stop"].show()
        self.buttons["show_logs"].set_sensitive(True)

    def on_game_stop(self, widget):
        self.buttons["play"].show()
        self.buttons["stop"].hide()
