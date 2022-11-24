from PyQt5.QtWidgets import QApplication, QMainWindow, QInputDialog, QVBoxLayout, QLabel, \
    QPushButton, QGroupBox, QWidget
from PyQt5.QtGui import QFont, QPainter, QColor, QPixmap
from PyQt5.QtCore import QRect, QSize, Qt, QTimer, QUrl
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from functools import partial
from random import randrange
from snk import Screen
import json
import sys
import source


class App(QMainWindow):
    def __init__(self):
        super(App, self).__init__()

        # ----- SETUP ----- #

        self.ui = Screen()
        self.ui.setupUi(self)

        # ---------- Just for the annoying "outside init" highlights ----------- #

        self.delete = None
        self.easy_score = None
        self.player_btn_layout = None
        self.player_name = None
        self.reset = None
        self.select = None
        self.medium_score = None
        self.layoutWidget = None
        self.extreme_score = None
        self.hard_score = None
        self.highscore_label = None
        self.score_label = None
        self.player_buttons = None
        self.player_card = None

        # --------------------- OPEN PLAYERS DOCUMENT ---------------------- #

        try:
            with open("Data/Players.json", "r") as data:
                self.players = json.load(data)

                if self.players["Selected"] != "None":  # If there are players in the data
                    self.current_player = self.players["Players"][self.players["Selected"]]["Name"]
                else:
                    self.current_player = "None"

        except FileNotFoundError:
            self.players = {"Selected": "None", "Players": {}}
            self.current_player = "None"

        # ----------- IF IT EXIST CREATE USER CARDS FOR EACH PLAYER -------- #
        else:
            self.ui.current_player.setText(f"Selected Player:\n{self.current_player}")
            self.create_card()

        # ----------- FOR GAME MUSIC ---------- #

        self.main_menu_music = QMediaPlaylist()
        self.game_music = QMediaPlaylist()

        url1 = QUrl.fromLocalFile("./Musics/Kubbi - Up In My Jam.mp3")
        url2 = QUrl.fromLocalFile("./Musics/Kubbi - Digestive biscuit.mp3")

        self.main_menu_music.addMedia(QMediaContent(url1))
        self.game_music.addMedia(QMediaContent(url2))

        self.main_menu_music.setPlaybackMode(QMediaPlaylist.Loop)
        self.game_music.setPlaybackMode(QMediaPlaylist.Loop)

        self.music = QMediaPlayer()

        self.play_music()

        # ----------------------- VARIABLES ---------------------- #

        # Current scores and difficulty
        self.score = 0
        self.highscore = 0
        self.difficulty = "Easy"

        # Direction of the snake
        self.direction = "Right"
        self.last_move = "Right"  # This will prevent going backwards and colliding with itself
        self.speed = 1000
        self.replace_food = False

        # These will be used to draw the snake and food
        self.canvas = None
        self.painter = None

        # This will be used to stop timer
        self.timer = True
        self.time = 3  # This will be a count-down

        # Snake and food coordinates
        self.snake = [[240, 200], [220, 200], [200, 200]]
        self.food = [343, 343]

        # --------------- BUTTONS --------------- #

        self.ui.about.clicked.connect(self.about)
        self.ui.players.clicked.connect(self.players_page)
        self.ui.play.clicked.connect(self.difficulties)
        self.ui.easy.clicked.connect(self.play)
        self.ui.medium.clicked.connect(self.play)
        self.ui.hard.clicked.connect(self.play)
        self.ui.extreme.clicked.connect(self.play)
        self.ui.add_player.clicked.connect(self.add_player)
        self.ui.volume.clicked.connect(self.play_music)

        # Navigation
        self.ui.back_player.clicked.connect(self.main_menu)
        self.ui.back_about.clicked.connect(self.main_menu)
        self.ui.back_difficulty.clicked.connect(self.main_menu)

    # --------------------------------------------------------------------------------------------------------------- #
    # -------------------------------------------------- NAVIGATION ------------------------------------------------- #
    # --------------------------------------------------------------------------------------------------------------- #

    # ------------------------ MAIN MENU ------------------------ #

    def main_menu(self):
        self.ui.stackedWidget.setCurrentIndex(0)

    # -------------------- CHOOSE DIFFICULTY -------------------- #

    def difficulties(self):
        self.ui.stackedWidget.setCurrentIndex(1)

    # ----------------------- ABOUT PAGE ------------------------ #

    def about(self):
        self.ui.stackedWidget.setCurrentIndex(4)

    # ---------------------- PLAYERS PAGE ----------------------- #

    def players_page(self):
        self.ui.stackedWidget.setCurrentIndex(3)
        self.create_card()

    # --------------------------------------------------------------------------------------------------------------- #
    # ----------------------------------------------------- MUSIC ---------------------------------------------------- #
    # --------------------------------------------------------------------------------------------------------------- #

    def play_music(self):
        if self.ui.volume.isChecked():
            self.music.stop()
        else:
            if self.ui.stackedWidget.currentIndex() != 2:
                self.music.setPlaylist(self.main_menu_music)
            else:
                self.music.setPlaylist(self.game_music)
            self.music.play()

    # --------------------------------------------------------------------------------------------------------------- #
    # ----------------------------------------------------- PLAY ---------------------------------------------------- #
    # --------------------------------------------------------------------------------------------------------------- #

    # ------------------------ KEY EVENTS -------------------------- #

    def keyPressEvent(self, event):

        # ----- Up, Down, Right, Left > It should not move exactly opposite size. ------ #

        if event.key() == Qt.Key_Up and self.last_move != "Down":
            self.direction = "Up"
        elif event.key() == Qt.Key_Down and self.last_move != "Up":
            self.direction = "Down"
        elif event.key() == Qt.Key_Left and self.last_move != "Right":
            self.direction = "Left"
        elif event.key() == Qt.Key_Right and self.last_move != "Left":
            self.direction = "Right"

    # ------------------------ PAINT EVENTS -------------------------- #

    def paintEvent(self, event):

        # ---------------- Create a QPixmap object and painter, then paint ------------------ #

        self.canvas = QPixmap(708, 708)
        self.ui.game_area.setPixmap(self.canvas)
        self.painter = QPainter(self.ui.game_area.pixmap())
        self.painter.begin(self)

        self.painter.setPen(Qt.white)
        self.painter.drawRect(19, 19, 662, 662)
        self.painter.setPen(Qt.black)

        self.place_food()
        self.draw_snake()

        self.painter.end()

    # ---------------------- PLACE FOOD RANDOMLY ---------------------- #

    def place_food(self):

        self.painter.setBrush(QColor(255, 0, 0, 255))  # Red

        # If the food is close to the head of snake in the direction redraw the food.

        if self.direction == "Right":
            if self.food[0] - self.snake[0][0] <= 10 and abs(self.snake[0][1] - self.food[1]) <= 10:
                self.replace_food = True

        elif self.direction == "Left":
            if self.snake[0][0] - self.food[0] <= 10 and abs(self.snake[0][1] - self.food[1]) <= 10:
                self.replace_food = True

        elif self.direction == "Up":
            if self.snake[0][1] - self.food[1] <= 10 and abs(self.food[0] - self.snake[0][0]) <= 10:
                self.replace_food = True

        else:
            if self.food[1] - self.snake[0][1] <= 10 and abs(self.food[0] - self.snake[0][0]) <= 10:
                self.replace_food = True

        # ----- More difficult the game, closer the food to the edges ------ #

        if self.replace_food:
            if self.difficulty == "Easy":
                self.food = [randrange(63, 623, 20), randrange(63, 623, 20)]
            elif self.difficulty == "Medium":
                self.food = [randrange(43, 643, 20), randrange(43, 643, 20)]
            else:
                self.food = [randrange(23, 663, 20), randrange(23, 663, 20)]
            self.replace_food = False
            self.score += 1
            self.calculate_scores()
            self.extend()  # Extend the snake

        self.painter.drawEllipse(self.food[0], self.food[1], 15, 15)  # Place the food

    # ------------------------- DRAW SNAKE ------------------------- #

    def draw_snake(self):

        self.painter.setBrush(QColor(20, 130, 40, 255))  # Green
        # self.painter.setPen(Qt.NoPen)  # Uncomment this line if you don't want squares in snake

        for i in self.snake:  # Draw rectangle for each part of the snake
            self.painter.drawRect(i[0], i[1], 20, 20)

    # ------------------------- EXTEND SNAKE ----------------------- #

    def extend(self):
        self.snake.insert(0, (self.snake[0]))  # Insert the head to index 0

    # -------------------------- MOVE SNAKE ------------------------- #

    def move_snake(self):

        # From the tail to the head make all parts follow each other.
        # The last part will be in the second last part's position, etc.
        for i in range((len(self.snake) - 1), 0, - 1):
            x = self.snake[i-1][0]
            y = self.snake[i-1][1]
            self.snake[i] = [x, y]

        # Change the coordinates
        if self.direction == "Right":
            self.snake[0][0] += 20
            self.last_move = "Right"
        elif self.direction == "Down":
            self.snake[0][1] += 20
            self.last_move = "Down"
        elif self.direction == "Left":
            self.snake[0][0] -= 20
            self.last_move = "Left"
        elif self.direction == "Up":
            self.snake[0][1] -= 20
            self.last_move = "Up"

        # Check collisions every time the snake moves
        self.check_state()

        if self.timer:
            QTimer.singleShot(self.speed, self.move_snake)

    # -------------------------- CALCULATE SCORES ------------------------- #

    def calculate_scores(self):

        # Change highscore if necessary
        if self.score > self.highscore:
            self.highscore = self.score

        # Write scores
        self.ui.score.setText(f"Score: {self.score}")

        if self.players['Selected'] == "None":
            self.ui.highscore.setText(f"Highscore: None")
        else:
            self.ui.highscore.setText(f"Highscore: {self.highscore} [{self.difficulty}]")

    # ------------------- CHECK COLLISION ------------------------- #

    def check_state(self):

        # --------- IF SNAKE'S HEAD HIT THE WALLS ---------- #

        if self.snake[0][0] < 20 or 660 < self.snake[0][0]:
            self.game_over()
            self.timer = False
        if self.snake[0][1] < 20 or 660 < self.snake[0][1]:
            self.game_over()
            self.timer = False

        # --------- IF SNAKE'S HEAD HIT ITSELF -------------- #
        for i in range(1, len(self.snake)):
            if self.snake[0] == self.snake[i]:
                self.game_over()
                self.timer = False

    # ------------------- TIMER BEFORE THE GAME STARTS ------------------- #

    def timer_feedback(self):

        self.ui.feedback.setHidden(False)

        # Change a label's text every second until it's zero.
        self.ui.feedback.setText(str(self.time))
        self.time -= 1

        if self.time > -1:
            self.play_music()  # Play game music

        if self.time > -2:
            QTimer.singleShot(1000, self.timer_feedback)

        else:  # Start moving the snake and hide the label
            self.ui.feedback.setHidden(True)
            self.time = 3
            self.move_snake()

    # ------------- GAME OVER FEEDBACK AND RESET EVERYTHING AFTER GAME ------------------- #

    def game_over(self):

        # Change label text to game over and show the label for 3 seconds
        self.ui.feedback.setText("GAME OVER!")
        self.ui.feedback.setHidden(False)

        self.time -= 1
        if self.time > -1:
            QTimer.singleShot(1000, self.game_over)

        else:  # Turn back to main menu and reset everything.

            self.ui.feedback.setHidden(True)

            # Change the player's highscore if a player is selected
            if self.players['Selected'] != "None":
                if self.highscore > self.players['Players'][self.players['Selected']]["Scores"][self.difficulty]:
                    self.players['Players'][self.players['Selected']]["Scores"][self.difficulty] = self.highscore
                    self.players['Players'][self.players['Selected']]["Scores"]["Highscore"] = \
                        (self.players['Players'][self.players['Selected']]["Scores"]["Easy"] +
                         self.players['Players'][self.players['Selected']]["Scores"]["Medium"] +
                         self.players['Players'][self.players['Selected']]["Scores"]["Hard"] +
                         self.players['Players'][self.players['Selected']]["Scores"]["Extreme"]) // 4
                    self.update_data()

            self.score = 0
            self.highscore = 0
            self.difficulty = "Easy"

            self.direction = "Right"
            self.speed = 1000
            self.replace_food = False

            self.canvas = None
            self.painter = None

            self.timer = True
            self.time = 3

            self.snake = [[240, 200], [220, 200], [200, 200]]
            self.food = [343, 343]

            self.ui.stackedWidget.setCurrentIndex(0)
            self.play_music()

    # -------------------------- PLAY PAGE ------------------------- #

    def play(self):

        sender = self.sender()

        # Which buttons we used to come here will change difficulty and speed of the snake
        if sender.text() == "EASY":
            self.difficulty = "Easy"
            self.speed = 60
        elif sender.text() == "MEDIUM":
            self.difficulty = "Medium"
            self.speed = 55
        elif sender.text() == "HARD":
            self.difficulty = "Hard"
            self.speed = 40
        else:
            self.difficulty = "Extreme"
            self.speed = 30

        # Write player's highscore if a player is selected
        if self.players['Selected'] != "None":
            self.highscore = self.players['Players'][self.players['Selected']]["Scores"][self.difficulty]

        self.calculate_scores()  # Change score texts before the game starts
        self.ui.stackedWidget.setCurrentIndex(2)  # Bring the page and show timer

        self.timer_feedback()  # Timer

    # --------------------------------------------------------------------------------------------------------------- #
    # --------------------------------------------------- PLAYERS --------------------------------------------------- #
    # --------------------------------------------------------------------------------------------------------------- #

    # ----------------------- UPDATE DATA ----------------------- #

    def update_data(self):
        with open("Data/Players.json", "w") as data:
            json.dump(self.players, data, indent=4)

    # ------------------------- ADD PLAYER ---------------------- #

    def add_player(self):

        # ------ Length of player number is the index number of new player ------ #
        index = str(len(self.players["Players"]))

        # ------ Ask user for the player name ------- #
        text, ok = QInputDialog.getText(self, 'Add Player', 'What is your player name?')

        # If accepted add the player, update data and recreate cards.
        if ok:
            self.players['Players'][index] = {
                "Name": text,
                "Scores": {"Easy": 0, "Medium": 0, "Hard": 0, "Extreme": 0, "Highscore": 0}
            }
            self.update_data()
            self.create_card()

        else:
            pass

    # ----------------------- DELETE PLAYER -------------------- #

    def delete_player(self, m):

        # Delete the player
        self.players["Players"].pop(str(m), None)

        if self.players["Players"] == {}:

            self.current_player = "None"
            self.players["Selected"] = "None"

        else:

            # --------------- Re-Indexing the players ------------------ #

            # Let's say you delete player 0, and then when you try to delete player 1 it will crush. Because the button
            # will have an index of 0, but we deleted player 0. Se we will change index of all players.

            index = 0
            players = {"Selected": "0", "Players": {}}

            for i, player in self.players["Players"].items():  # Re index
                players["Players"][str(index)] = player
                index += 1

            self.players = players  # Now there is no number missing, it starts from 0 and increases 1 by 1.

            # Set the current player to "0"
            self.current_player = self.players["Players"]["0"]["Name"]
            self.players["Selected"] = "0"

        # Change selected player text
        self.ui.current_player.setText(f"Selected Player:\n{self.current_player}")

        # Update Players.json and recreate cards
        self.update_data()
        self.create_card()

    # ------------------------ RESET PLAYER --------------------- #

    def reset_player(self, m):

        # Reset the player's scores
        self.players["Players"][str(m)]["Scores"] = {"Easy": 0, "Medium": 0, "Hard": 0, "Extreme": 0, "Highscore": 0}

        # Update Players.json and recreate cards
        self.update_data()
        self.create_card()

    # ----------------------- SELECT PLAYER --------------------- #

    def select_player(self, m):

        # Change current player
        self.current_player = self.players['Players'][str(m)]['Name']

        # Update Players.json
        self.players["Selected"] = str(m)
        self.update_data()

        # Change Selected Used text
        self.ui.current_player.setText(f"Selected Player:\n{self.current_player}")

    # ---------------------------- CREATE PLAYER CARDS -------------------------- #

    def create_card(self):

        # ------- Every time this function is called, clean and recreate the cards ------ #

        for i in reversed(range(1, self.ui.verticalLayout.count())):  # Starts from 1 because there is Add Player card.
            self.ui.verticalLayout.itemAt(i).widget().deleteLater()

        # ---- There isn't going very much thing here. Just a for loop that creates cards for each player ---- #
        # Using "partial" module I separated button functions.

        index = 0  # This is for indexing buttons, so that each button can have an ID
        font = QFont()

        for i, player in self.players["Players"].items():

            font.setPointSize(9)
            font.setBold(True)
            font.setWeight(75)

            # ------------- PLAYER CARD -------------- #

            self.player_card = QGroupBox(self.ui.scroll_widget)
            self.player_card.setTitle("Player")
            self.player_card.setMinimumSize(QSize(551, 171))
            self.player_card.setMaximumSize(QSize(551, 171))
            self.player_card.setFont(font)
            self.player_card.setStyleSheet(
                "QGroupBox {border: 1px solid black; border-radius: 10px; margin-top: 10px; "
                "background-color: rgb(25, 108, 153); color: white;}\n"
                "QGroupBox::title {subcontrol-origin: margin; left: 50px; padding: 0px 5px 0px 5px;}\n"
                "")

            font.setFamily("Segoe UI")
            font.setPointSize(10)

            # ------------- LABEL FOR BUTTONS -------------- #

            self.player_buttons = QLabel(self.player_card)
            self.player_buttons.setGeometry(QRect(400, 30, 131, 121))
            self.player_buttons.setStyleSheet("background-image: url(:/Images/Images/players.png);")
            self.player_buttons.setText("")

            # ------------- SCORE LABEL -------------- #

            self.score_label = QLabel(self.player_card)
            self.score_label.setGeometry(QRect(160, 30, 231, 71))
            self.score_label.setStyleSheet("border: 0; background-color: rgb(90, 173, 217);")
            self.score_label.setText("")

            # ------------- PLAYER NAME LABEL -------------- #

            self.player_name = QLabel(self.player_card)
            self.player_name.setFont(font)
            self.player_name.setGeometry(QRect(20, 30, 131, 121))
            self.player_name.setStyleSheet("border: 0; background-color: rgb(90, 173, 217);")
            self.player_name.setAlignment(Qt.AlignCenter)
            self.player_name.setText(player["Name"])

            # ------------- HIGHSCORE LABEL -------------- #

            self.highscore_label = QLabel(self.player_card)
            self.highscore_label.setGeometry(QRect(160, 110, 231, 41))
            self.highscore_label.setFont(font)
            self.highscore_label.setStyleSheet("border: 0; background-color: rgb(90, 173, 217);")
            self.highscore_label.setAlignment(Qt.AlignCenter)
            self.highscore_label.setText(f"Highscore: {player['Scores']['Highscore']}")

            # ------------- EASY SCORE LABEL -------------- #

            self.easy_score = QLabel(self.player_card)
            self.easy_score.setGeometry(QRect(160, 40, 111, 21))
            self.easy_score.setFont(font)
            self.easy_score.setAlignment(Qt.AlignCenter)
            self.easy_score.setText(f"Easy: {player['Scores']['Easy']}")

            # ------------- HARD SCORE LABEL -------------- #

            self.hard_score = QLabel(self.player_card)
            self.hard_score.setGeometry(QRect(160, 70, 111, 21))
            self.hard_score.setFont(font)
            self.hard_score.setAlignment(Qt.AlignCenter)
            self.hard_score.setText(f"Hard: {player['Scores']['Hard']}")

            # ------------- MEDIUM SCORE LABEL -------------- #

            self.medium_score = QLabel(self.player_card)
            self.medium_score.setGeometry(QRect(270, 40, 121, 21))
            self.medium_score.setFont(font)
            self.medium_score.setAlignment(Qt.AlignCenter)
            self.medium_score.setText(f"Medium: {player['Scores']['Medium']}")

            # ------------- EXTREME SCORE LABEL -------------- #

            self.extreme_score = QLabel(self.player_card)
            self.extreme_score.setGeometry(QRect(270, 70, 121, 21))
            self.extreme_score.setFont(font)
            self.extreme_score.setAlignment(Qt.AlignCenter)
            self.extreme_score.setText(f"Extreme: {player['Scores']['Extreme']}")

            # ------------- LAYOUT WIDGET -------------- #

            self.layoutWidget = QWidget(self.player_card)
            self.layoutWidget.setGeometry(QRect(410, 40, 111, 101))

            # ------------- PLAYER BUTTONS LAYOUT -------------- #

            self.player_btn_layout = QVBoxLayout(self.layoutWidget)
            self.player_btn_layout.setContentsMargins(0, 0, 0, 0)

            font.setPointSize(7)

            # ------------- SELECT BUTTON -------------- #

            self.select = QPushButton(self.layoutWidget)
            self.select.setFont(font)
            self.player_btn_layout.addWidget(self.select)
            self.select.setText("SELECT")
            self.select.clicked.connect(partial(self.select_player, index))

            # ------------- RESET BUTTON -------------- #

            self.reset = QPushButton(self.layoutWidget)
            self.reset.setFont(font)
            self.player_btn_layout.addWidget(self.reset)
            self.reset.setText("RESET")
            self.reset.clicked.connect(partial(self.reset_player, index))

            # ------------- DELETE BUTTON -------------- #

            self.delete = QPushButton(self.layoutWidget)
            self.delete.setFont(font)
            self.player_btn_layout.addWidget(self.delete)
            self.delete.setText("DELETE")
            self.delete.clicked.connect(partial(self.delete_player, index))

            # Add card to the layout
            self.ui.verticalLayout.addWidget(self.player_card, 0, Qt.AlignHCenter)

            index += 1  # Increase the index number


def application():
    window = QApplication(sys.argv)
    win = App()
    win.show()
    sys.exit(window.exec_())


application()
