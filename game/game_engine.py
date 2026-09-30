import random
import pygame
from game.text_box import TextBox


class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        # Word list
        self.words = [
            "PYTHON",
            "PYGAME",
            "PLANET",
            "ROCKET",
            "GALAXY",
            "STREAM",
            "PUZZLE",
            "ALGORITHM"
        ]

        self.secret_word = ""
        self.scrambled_word = ""

        # Score
        self.score = 0

        # =========================================================
        # TASK 2 - HINT SYSTEM
        # =========================================================
        self.revealed_positions = set()

        # =========================================================
        # TASK 3 - TIMER
        # =========================================================
        self.round_time = 20
        self.time_left = 20
        self.round_start_time = pygame.time.get_ticks()
        self.time_up = False
        self.timeout_start = 0

        # =========================================================
        # TASK 4 - LETTER TILES
        # =========================================================
        self.tiles = []
        self.selected_tile = None

        self.tile_size = 55
        self.tile_gap = 8
        self.tile_y = 145

        # Feedback
        self.feedback_msg = "Unscramble the letters above!"
        self.feedback_color = (210, 215, 225)

        # =========================================================
        # INPUT BOX
        # =========================================================
        self.input_box = TextBox(
            width // 2 - 130,
            245,
            160,
            46
        )

        # =========================================================
        # SUBMIT BUTTON
        # =========================================================
        self.submit_btn = pygame.Rect(
            width // 2 + 45,
            245,
            95,
            46
        )

        # =========================================================
        # HINT BUTTON
        # =========================================================
        self.hint_btn = pygame.Rect(
            width // 2 + 150,
            245,
            95,
            46
        )

        # Fonts
        self.font_title = pygame.font.SysFont(None, 40)
        self.font_word = pygame.font.SysFont(None, 52)
        self.font_msg = pygame.font.SysFont(None, 26)
        self.font_btn = pygame.font.SysFont(None, 24)
        self.font_tile = pygame.font.SysFont(None, 32)

        self.next_round()

    # =============================================================
    # SCRAMBLE
    # =============================================================

    def scramble_string(self, word):
        letters = list(word)

        while True:
            random.shuffle(letters)
            shuffled = "".join(letters)

            if shuffled != word or len(word) <= 1:
                return shuffled

    # =============================================================
    # CREATE TILES
    # =============================================================

    def create_tiles(self):
        self.tiles = []

        total_width = (
            len(self.scrambled_word) * self.tile_size
            + (len(self.scrambled_word) - 1) * self.tile_gap
        )

        start_x = self.width // 2 - total_width // 2

        for i, letter in enumerate(self.scrambled_word):

            x = start_x + i * (
                self.tile_size + self.tile_gap
            )

            rect = pygame.Rect(
                x,
                self.tile_y,
                self.tile_size,
                self.tile_size
            )

            self.tiles.append({
                "letter": letter,
                "rect": rect
            })

    # =============================================================
    # NEXT ROUND
    # =============================================================

    def next_round(self):

        self.secret_word = random.choice(self.words)

        self.scrambled_word = self.scramble_string(
            self.secret_word
        )

        # Reset hint positions
        self.revealed_positions.clear()

        # Reset selected tile
        self.selected_tile = None

        # Reset timer
        self.time_left = self.round_time
        self.round_start_time = pygame.time.get_ticks()

        # Reset timeout
        self.time_up = False
        self.timeout_start = 0

        # Clear text input
        self.input_box.clear()

        # Reset feedback
        self.feedback_msg = "Unscramble the letters above!"
        self.feedback_color = (210, 215, 225)

        # Create new tiles
        self.create_tiles()

    # =============================================================
    # TASK 1 - SUBMIT GUESS
    # =============================================================

    def submit_guess(self):

        if self.time_up:
            return

        # Build guess from tile arrangement
        tile_guess = "".join(
            tile["letter"]
            for tile in self.tiles
        )

        # Check typed input
        typed_guess = self.input_box.text.strip().upper()

        # If user typed a word, use that.
        # Otherwise use tile arrangement.
        if typed_guess:
            guess = typed_guess
        else:
            guess = tile_guess

        if not guess:
            self.feedback_msg = "Arrange or type a word first!"
            self.feedback_color = (240, 170, 50)
            return

        # =========================================================
        # TASK 1 FIX
        # =========================================================
        is_correct = (guess == self.secret_word)

        if is_correct:

            self.score += 1

            self.feedback_msg = (
                f"CORRECT! '{self.secret_word}' is right."
            )

            self.feedback_color = (80, 230, 110)

            self.next_round()

        else:

            self.feedback_msg = "WRONG GUESS! Try again."
            self.feedback_color = (240, 80, 80)

            self.input_box.clear()

    # =============================================================
    # TASK 2 - HINT
    # =============================================================

    def use_hint(self):

        if self.time_up:
            return

        # Find first unrevealed position
        for i in range(len(self.secret_word)):

            if i not in self.revealed_positions:

                self.revealed_positions.add(i)

                # Deduct one point
                self.score = max(
                    0,
                    self.score - 1
                )

                self.feedback_msg = (
                    f"Hint revealed: {self.secret_word[i]}  (-1 point)"
                )

                self.feedback_color = (
                    255,
                    200,
                    80
                )

                return

        self.feedback_msg = (
            "All letters are already revealed!"
        )

        self.feedback_color = (
            210,
            215,
            225
        )

    # =============================================================
    # TASK 4 - TILE CLICK / SWAP
    # =============================================================

    def handle_tile_click(self, position):

        if self.time_up:
            return

        for index, tile in enumerate(self.tiles):

            if tile["rect"].collidepoint(position):

                # First tile
                if self.selected_tile is None:

                    self.selected_tile = index

                    self.feedback_msg = (
                        "Tile selected - choose another tile."
                    )

                    self.feedback_color = (
                        100,
                        200,
                        255
                    )

                # Same tile
                elif self.selected_tile == index:

                    self.selected_tile = None

                    self.feedback_msg = (
                        "Tile selection cancelled."
                    )

                    self.feedback_color = (
                        210,
                        215,
                        225
                    )

                # Second tile -> swap
                else:

                    first = self.selected_tile
                    second = index

                    self.tiles[first]["letter"], \
                    self.tiles[second]["letter"] = (
                        self.tiles[second]["letter"],
                        self.tiles[first]["letter"]
                    )

                    self.selected_tile = None

                    self.feedback_msg = (
                        "Letters swapped!"
                    )

                    self.feedback_color = (
                        100,
                        200,
                        255
                    )

                return

    # =============================================================
    # EVENT HANDLING
    # =============================================================

    def handle_event(self, event):

        # Text box
        self.input_box.handle_event(event)

        if self.time_up:
            return

        # Keyboard
        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_RETURN:
                self.submit_guess()

        # Mouse
        elif event.type == pygame.MOUSEBUTTONDOWN:

            if event.button == 1:

                # HINT first
                if self.hint_btn.collidepoint(event.pos):

                    self.use_hint()
                    return

                # SUBMIT
                if self.submit_btn.collidepoint(event.pos):

                    self.submit_guess()
                    return

                # TILE
                for tile in self.tiles:

                    if tile["rect"].collidepoint(event.pos):

                        self.handle_tile_click(event.pos)
                        return

    # =============================================================
    # TASK 3 - TIMER
    # =============================================================

    def update(self):

        if self.time_up:
            return

        current_time = pygame.time.get_ticks()

        elapsed_seconds = (
            current_time - self.round_start_time
        ) / 1000

        self.time_left = max(
            0,
            self.round_time - elapsed_seconds
        )

        # Timer expired
        if self.time_left <= 0:

            self.time_up = True

            # Reveal complete word
            self.revealed_positions = set(
                range(len(self.secret_word))
            )

            self.feedback_msg = (
                f"TIME'S UP! The word was {self.secret_word}"
            )

            self.feedback_color = (
                240,
                80,
                80
            )

            self.timeout_start = pygame.time.get_ticks()

    # =============================================================
    # TIMEOUT TRANSITION
    # =============================================================

    def handle_timeout(self):

        if not self.time_up:
            return

        current_time = pygame.time.get_ticks()

        if current_time - self.timeout_start >= 1000:

            self.next_round()

    # =============================================================
    # RENDER
    # =============================================================

    def render(self, screen):

        screen.fill((26, 30, 38))

        # =========================================================
        # TITLE
        # =========================================================

        title_surf = self.font_title.render(
            "Word Scramble Arena",
            True,
            (245, 245, 245)
        )

        screen.blit(
            title_surf,
            (
                self.width // 2
                - title_surf.get_width() // 2,
                20
            )
        )

        # =========================================================
        # SCORE
        # =========================================================

        score_surf = self.font_msg.render(
            f"Score: {self.score}",
            True,
            (255, 220, 80)
        )

        screen.blit(
            score_surf,
            (
                self.width // 2
                - score_surf.get_width() // 2,
                60
            )
        )

        # =========================================================
        # TIMER TEXT
        # =========================================================

        timer_surf = self.font_msg.render(
            f"Time: {int(self.time_left)}s",
            True,
            (255, 255, 255)
        )

        screen.blit(
            timer_surf,
            (
                self.width // 2
                - timer_surf.get_width() // 2,
                90
            )
        )

        # =========================================================
        # TIMER BAR
        # =========================================================

        timer_width = 300
        timer_height = 15

        timer_x = (
            self.width // 2
            - timer_width // 2
        )

        timer_y = 115

        # Background
        pygame.draw.rect(
            screen,
            (70, 70, 70),
            (
                timer_x,
                timer_y,
                timer_width,
                timer_height
            ),
            border_radius=5
        )

        timer_ratio = (
            self.time_left / self.round_time
        )

        remaining_width = int(
            timer_width * timer_ratio
        )

        if remaining_width > 0:

            if self.time_left <= 5:
                timer_color = (240, 80, 80)

            elif self.time_left <= 10:
                timer_color = (240, 180, 60)

            else:
                timer_color = (80, 200, 100)

            pygame.draw.rect(
                screen,
                timer_color,
                (
                    timer_x,
                    timer_y,
                    remaining_width,
                    timer_height
                ),
                border_radius=5
            )

        # =========================================================
        # LETTER TILES
        # =========================================================

        for index, tile in enumerate(self.tiles):

            rect = tile["rect"]

            # If hint revealed this position,
            # show the correct secret letter.
            if index in self.revealed_positions:

                display_letter = self.secret_word[index]

                tile_color = (
                    60,
                    150,
                    80
                )

            else:

                display_letter = tile["letter"]

                if index == self.selected_tile:

                    tile_color = (
                        255,
                        200,
                        70
                    )

                else:

                    tile_color = (
                        60,
                        90,
                        130
                    )

            # Tile
            pygame.draw.rect(
                screen,
                tile_color,
                rect,
                border_radius=6
            )

            # Border
            pygame.draw.rect(
                screen,
                (220, 220, 220),
                rect,
                width=2,
                border_radius=6
            )

            # Letter
            letter_surface = self.font_tile.render(
                display_letter,
                True,
                (255, 255, 255)
            )

            screen.blit(
                letter_surface,
                (
                    rect.centerx
                    - letter_surface.get_width() // 2,
                    rect.centery
                    - letter_surface.get_height() // 2
                )
            )

        # =========================================================
        # INPUT BOX
        # =========================================================

        self.input_box.render(screen)

        # =========================================================
        # SUBMIT BUTTON
        # =========================================================

        pygame.draw.rect(
            screen,
            (50, 150, 85),
            self.submit_btn,
            border_radius=6
        )

        pygame.draw.rect(
            screen,
            (220, 220, 220),
            self.submit_btn,
            width=2,
            border_radius=6
        )

        submit_text = self.font_btn.render(
            "SUBMIT",
            True,
            (255, 255, 255)
        )

        screen.blit(
            submit_text,
            (
                self.submit_btn.centerx
                - submit_text.get_width() // 2,
                self.submit_btn.centery
                - submit_text.get_height() // 2
            )
        )

        # =========================================================
        # HINT BUTTON
        # =========================================================

        pygame.draw.rect(
            screen,
            (80, 100, 180),
            self.hint_btn,
            border_radius=6
        )

        pygame.draw.rect(
            screen,
            (220, 220, 220),
            self.hint_btn,
            width=2,
            border_radius=6
        )

        hint_text = self.font_btn.render(
            "HINT",
            True,
            (255, 255, 255)
        )

        screen.blit(
            hint_text,
            (
                self.hint_btn.centerx
                - hint_text.get_width() // 2,
                self.hint_btn.centery
                - hint_text.get_height() // 2
            )
        )

        # =========================================================
        # FEEDBACK
        # =========================================================

        feedback_surf = self.font_msg.render(
            self.feedback_msg,
            True,
            self.feedback_color
        )

        screen.blit(
            feedback_surf,
            (
                self.width // 2
                - feedback_surf.get_width() // 2,
                320
            )
        )
