import pygame
import os
from config import *
import re

class Dropdown:
    def __init__(self, x, y, w, h, font, options, selected_index=0, 
                 bg_color=(30, 30, 30), fg_color=WHITE, border_color=YELLOW, 
                 highlight_color=GREEN, list_bg=(10, 10, 10), max_visible=8):
        self.rect = pygame.Rect(x, y, w, h)
        self.font = font
        self.options = options
        self.selected_index = selected_index
        self.open = False
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.border_color = border_color
        self.highlight_color = highlight_color
        self.list_bg = list_bg
        self.item_height = h
        self.max_visible = max_visible
        self.scroll_offset = 0

    @property
    def value(self):
        return self.options[self.selected_index] if self.options else None

    def set_options(self, options, keep_selection=True):
        old_value = self.value
        self.options = options
        if keep_selection and old_value in options:
            self.selected_index = options.index(old_value)
        else:
            self.selected_index = 0 if options else -1
        self.scroll_into_view()

    def scroll_into_view(self):
        if not self.open:
            return
        if self.selected_index < self.scroll_offset:
            self.scroll_offset = self.selected_index
        visible_count = min(self.max_visible, len(self.options))
        if self.selected_index >= self.scroll_offset + visible_count:
            self.scroll_offset = self.selected_index - visible_count + 1

    def handle_event(self, event):
        changed = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button in (1,):
                if self.rect.collidepoint(event.pos):
                    self.open = not self.open
                elif self.open:
                    # click on list
                    list_rect = pygame.Rect(self.rect.x, self.rect.bottom, self.rect.w, self.item_height * min(self.max_visible, len(self.options)))
                    if list_rect.collidepoint(event.pos):
                        idx = (event.pos[1] - list_rect.y) // self.item_height
                        actual = self.scroll_offset + int(idx)
                        if 0 <= actual < len(self.options):
                            if actual != self.selected_index:
                                self.selected_index = actual
                                changed = True
                        self.open = False
                    else:
                        self.open = False
            # scroll wheel
            if self.open and event.button in (4, 5):
                if event.button == 4:  # up
                    self.scroll_offset = max(0, self.scroll_offset - 1)
                else:  # down
                    max_off = max(0, len(self.options) - self.max_visible)
                    self.scroll_offset = min(max_off, self.scroll_offset + 1)
        elif event.type == pygame.KEYDOWN and self.open:
            if event.key in (pygame.K_UP, pygame.K_w):
                if self.selected_index > 0:
                    self.selected_index -= 1
                    changed = True
                    self.scroll_into_view()
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                if self.selected_index < len(self.options) - 1:
                    self.selected_index += 1
                    changed = True
                    self.scroll_into_view()
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self.open = False
        return changed

    def draw(self, surface):
        # main box
        pygame.draw.rect(surface, self.bg_color, self.rect)
        pygame.draw.rect(surface, self.border_color, self.rect, 2)
        label = self.font.render(self.value if self.value is not None else "-", True, self.fg_color)
        surface.blit(label, (self.rect.x + 8, self.rect.y + (self.rect.h - label.get_height()) // 2))
        # caret (drawn triangle to avoid font issues)
        caret_margin = 14
        caret_width = 12
        caret_height = 8
        cx = self.rect.right - caret_margin
        cy = self.rect.y + self.rect.h // 2
        if not self.open:
            points = [(cx - caret_width // 2, cy - caret_height // 2),
                      (cx + caret_width // 2, cy - caret_height // 2),
                      (cx, cy + caret_height // 2)]
        else:
            points = [(cx - caret_width // 2, cy + caret_height // 2),
                      (cx + caret_width // 2, cy + caret_height // 2),
                      (cx, cy - caret_height // 2)]
        pygame.draw.polygon(surface, self.fg_color, points)

        # list
        if self.open and self.options:
            visible = min(self.max_visible, len(self.options))
            list_rect = pygame.Rect(self.rect.x, self.rect.bottom, self.rect.w, self.item_height * visible)
            pygame.draw.rect(surface, self.list_bg, list_rect)
            pygame.draw.rect(surface, self.border_color, list_rect, 2)
            for i in range(visible):
                idx = self.scroll_offset + i
                if idx >= len(self.options):
                    break
                item_rect = pygame.Rect(self.rect.x, self.rect.bottom + i * self.item_height, self.rect.w, self.item_height)
                color = self.highlight_color if idx == self.selected_index else self.fg_color
                txt = self.font.render(self.options[idx], True, color)
                surface.blit(txt, (item_rect.x + 8, item_rect.y + (item_rect.h - txt.get_height()) // 2))

    # split draw into box and list for better z-order control
    def draw_box(self, surface):
        pygame.draw.rect(surface, self.bg_color, self.rect)
        pygame.draw.rect(surface, self.border_color, self.rect, 2)
        label = self.font.render(self.value if self.value is not None else "-", True, self.fg_color)
        surface.blit(label, (self.rect.x + 8, self.rect.y + (self.rect.h - label.get_height()) // 2))
        caret_margin = 14
        caret_width = 12
        caret_height = 8
        cx = self.rect.right - caret_margin
        cy = self.rect.y + self.rect.h // 2
        if not self.open:
            points = [(cx - caret_width // 2, cy - caret_height // 2),
                      (cx + caret_width // 2, cy - caret_height // 2),
                      (cx, cy + caret_height // 2)]
        else:
            points = [(cx - caret_width // 2, cy + caret_height // 2),
                      (cx + caret_width // 2, cy + caret_height // 2),
                      (cx, cy - caret_height // 2)]
        pygame.draw.polygon(surface, self.fg_color, points)

    def draw_list(self, surface):
        if not (self.open and self.options):
            return
        visible = min(self.max_visible, len(self.options))
        list_rect = pygame.Rect(self.rect.x, self.rect.bottom, self.rect.w, self.item_height * visible)
        pygame.draw.rect(surface, self.list_bg, list_rect)
        pygame.draw.rect(surface, self.border_color, list_rect, 2)
        for i in range(visible):
            idx = self.scroll_offset + i
            if idx >= len(self.options):
                break
            item_rect = pygame.Rect(self.rect.x, self.rect.bottom + i * self.item_height, self.rect.w, self.item_height)
            color = self.highlight_color if idx == self.selected_index else self.fg_color
            txt = self.font.render(self.options[idx], True, color)
            surface.blit(txt, (item_rect.x + 8, item_rect.y + (item_rect.h - txt.get_height()) // 2))

class MuteButton:
    _sound_image = None
    _mute_image = None

    def __init__(self, x, y, size, bg_color=WHITE, border_color=YELLOW):
        self.rect = pygame.Rect(x, y, size, size)
        self.bg_color = bg_color
        self.border_color = border_color
        self.is_muted = pygame.mixer.music.get_volume() == 0
        self.hover = False
        self._icon_size = int(size * 0.7)
        sound_img, mute_img = self._load_images()
        self._sound_icon = pygame.transform.smoothscale(sound_img, (self._icon_size, self._icon_size))
        self._mute_icon = pygame.transform.smoothscale(mute_img, (self._icon_size, self._icon_size))

    @classmethod
    def _load_images(cls):
        if cls._sound_image is None or cls._mute_image is None:
            sound_path = os.path.join("assets", "Sound", "sound.png")
            mute_path = os.path.join("assets", "Sound", "mute.png")
            cls._sound_image = pygame.image.load(sound_path).convert_alpha()
            cls._mute_image = pygame.image.load(mute_path).convert_alpha()
        return cls._sound_image, cls._mute_image

    def toggle(self):
        self.is_muted = not self.is_muted
        pygame.mixer.music.set_volume(0 if self.is_muted else MUSIC_VOLUME)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.toggle()
                return True
        return False

    def draw(self, surface):
        pygame.draw.rect(surface, self.bg_color, self.rect, border_radius=8)
        border_col = RED if self.is_muted else self.border_color
        width = 3 if self.hover else 2
        pygame.draw.rect(surface, border_col, self.rect, width=width, border_radius=8)

        icon = self._mute_icon if self.is_muted else self._sound_icon
        icon_rect = icon.get_rect(center=self.rect.center)
        surface.blit(icon, icon_rect)

def natural_sort_key(s):
    """Sort strings like map1.txt, map2.txt, map10.txt in human order."""
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]


def load_background(image_path, screen_size):
    bg = pygame.image.load(image_path).convert()
    return pygame.transform.scale(bg, screen_size)


def load_fonts(base_size=36):
    try:
        title_font = pygame.font.Font(
            "assets/fonts/PAC-FONT.TTF", base_size + 16)
        menu_font = pygame.font.Font("assets/fonts/PAC-FONT.TTF", base_size)
    except:
        title_font = pygame.font.SysFont("arial", base_size + 16, bold=True)
        menu_font = pygame.font.SysFont("arial", base_size, bold=True)
    return title_font, menu_font


def choose_map(screen, clock, font):
    """Display a map selection menu and return the selected map path."""
    map_folder = "maps"
    maps = [f for f in os.listdir(map_folder) if f.endswith(".txt")]
    if not maps:
        raise FileNotFoundError("No .txt map files found in 'maps' folder.")

    maps.sort(key=natural_sort_key)  # ✅ Fix map1/map10 sorting

    selected = 0
    scroll_offset = 0
    visible_count = 8  # ✅ Number of maps visible at once
    running = True

    background = load_background(
        "assets/menu_bg/PACMAN_MENU.jpg", screen.get_size())
    title_font, menu_font = load_fonts(36)

    while running:
        screen.blit(background, (0, 0))
        title = title_font.render("Choose Map", True, (0, 102, 255))
        screen.blit(title, (COLS * CELL_SIZE //
                    2 - title.get_width() // 2, 50))

        # determine which maps to display
        start_index = scroll_offset
        end_index = scroll_offset + visible_count
        visible_maps = maps[start_index:end_index]

        # draw visible maps
        for i, map_name in enumerate(visible_maps):
            color = GREEN if (start_index + i) == selected else RED
            text = menu_font.render(map_name, True, color)
            screen.blit(text, (COLS * CELL_SIZE // 2 -
                        text.get_width() // 2, 150 + i * 50))

        # scroll indicators
        if scroll_offset > 0:
            up_hint = menu_font.render("↑", True, YELLOW)
            screen.blit(up_hint, (COLS * CELL_SIZE // 2 -
                        up_hint.get_width() // 2, 120))
        if end_index < len(maps):
            down_hint = menu_font.render("↓", True, YELLOW)
            screen.blit(down_hint, (COLS * CELL_SIZE // 2 -
                        down_hint.get_width() // 2, 150 + visible_count * 50))

        pygame.display.flip()
        clock.tick(PLAYER_MODE_FPS)

        # handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w):
                    selected = (selected - 1) % len(maps)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    selected = (selected + 1) % len(maps)
                elif event.key == pygame.K_RETURN:
                    return os.path.join(map_folder, maps[selected])

        # update scroll offset
        if selected < scroll_offset:
            scroll_offset = selected
        elif selected >= scroll_offset + visible_count:
            scroll_offset = selected - visible_count + 1


def main_menu(screen, clock, font):
    """Main menu — choose Player/AI, map, and speed via dropdowns."""
    solver_options = SOLVER_MODES + ["Player"]
    player_speed = PLAYER_SPEED
    running = True

    # background and fonts
    background = load_background("assets/menu_bg/PACMAN_MENU.jpg", screen.get_size())
    title_font, menu_font = load_fonts(40)

    # prepare dropdowns
    # positions
    center_x = COLS * CELL_SIZE // 2
    dd_width = 420
    dd_height = 50
    spacing = 80

    # maps
    map_folder = "maps"
    map_files = [f for f in os.listdir(map_folder) if f.endswith(".txt")]
    if not map_files:
        raise FileNotFoundError("No .txt map files found in 'maps' folder.")
    map_files.sort(key=natural_sort_key)

    solver_dd = Dropdown(center_x - dd_width // 2, 170, dd_width, dd_height, menu_font, solver_options, selected_index=0)
    map_dd = Dropdown(center_x - dd_width // 2, 170 + spacing, dd_width, dd_height, menu_font, map_files, selected_index=0, max_visible=6)
    mute_size = 56
    mute_padding = 30
    mute_btn = MuteButton(screen.get_width() - mute_size - mute_padding, mute_padding, mute_size)

    while running:
        screen.blit(background, (0, 0))

        # title
        title = title_font.render("PAC-MAN", True, (0, 102, 255))
        screen.blit(title, (center_x - title.get_width() // 2, 50))

        # labels
        solver_label = menu_font.render("Mode:", True, WHITE)
        map_label = menu_font.render("Map:", True, WHITE)
        screen.blit(solver_label, (solver_dd.rect.x - solver_label.get_width() - 20, solver_dd.rect.y + (dd_height - solver_label.get_height()) // 2))
        screen.blit(map_label, (map_dd.rect.x - map_label.get_width() - 20, map_dd.rect.y + (dd_height - map_label.get_height()) // 2))

        # speed control
        speed_text = menu_font.render(f"Game Speed: {player_speed} (A/D)", True, WHITE)
        screen.blit(speed_text, (center_x - speed_text.get_width() // 2, map_dd.rect.bottom + 60))

        # hint
        hint = menu_font.render("Press ENTER to Start", True, YELLOW)
        screen.blit(hint, (center_x - hint.get_width() // 2, screen.get_height() - 80))

        mute_caption = menu_font.render("Music", True, WHITE)
        screen.blit(mute_caption, (mute_btn.rect.centerx - mute_caption.get_width() // 2, mute_btn.rect.bottom + 10))

        # draw dropdown boxes first
        solver_dd.draw_box(screen)
        map_dd.draw_box(screen)
        mute_btn.draw(screen)

        # draw lists with correct z-order: draw non-focused first, focused last
        # if both open (rare), prioritize the one that was interacted (handled below)
        if map_dd.open and not solver_dd.open:
            map_dd.draw_list(screen)
        if solver_dd.open:
            solver_dd.draw_list(screen)

        pygame.display.flip()
        clock.tick(PLAYER_MODE_FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            # pass to dropdowns first
            solver_changed = solver_dd.handle_event(event)
            map_changed = map_dd.handle_event(event)
            mute_btn.handle_event(event)

            # auto-close the other dropdown if one is opened via click
            if event.type == pygame.MOUSEBUTTONDOWN and event.button in (1,):
                # clicked inside solver box toggled open state
                if solver_dd.rect.collidepoint(event.pos):
                    map_dd.open = False
                # clicked inside map box toggled open state
                elif map_dd.rect.collidepoint(event.pos):
                    solver_dd.open = False

            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_a, pygame.K_LEFT):
                    player_speed = max(1, player_speed - 1)
                elif event.key in (pygame.K_d, pygame.K_RIGHT):
                    player_speed = min(PLAYER_MODE_FPS, player_speed + 1)
                elif event.key == pygame.K_m:
                    mute_btn.toggle()
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    selected_mode = solver_dd.value
                    selected_map = os.path.join(map_folder, map_dd.value)
                    return selected_mode, player_speed, selected_map, mute_btn.is_muted
