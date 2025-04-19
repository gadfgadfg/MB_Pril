import kivy
kivy.require('2.0.0')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button as KivyButton
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.dropdown import DropDown
from kivy.uix.filechooser import FileChooserIconView, FileChooserListView
from kivy.uix.colorpicker import ColorPicker
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.properties import StringProperty, ListProperty, ObjectProperty
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivy.graphics import Color
from kivy.graphics import Rectangle

from kivy.utils import get_color_from_hex
import matplotlib.pyplot as plt

import os
import platform
import webbrowser

from random import randint
from kivy.clock import Clock

import pygame
import random
import sys

IS_MOBILE = platform.system() != 'Windows' and platform.system() != 'Darwin'

CELL_SIZE = 20
GRID_WIDTH = 20
GRID_HEIGHT = 20
SCREEN_WIDTH = GRID_WIDTH * CELL_SIZE
SCREEN_HEIGHT = GRID_HEIGHT * CELL_SIZE + 100
SNAKE_COLOR = (0, 255, 0)
FOOD_COLOR = (255, 0, 0)
BG_COLOR = (0, 0, 0)
BUTTON_COLOR = (100, 100, 100)
BUTTON_TEXT_COLOR = (255, 255, 255)
FONT_SIZE = 36
FPS = 30

class Snake:
    def __init__(self):
        self.body = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = (1, 0)
        self.new_direction = (1, 0)

    def move(self):
        self.direction = self.new_direction
        head_x, head_y = self.body[0]
        new_head = (head_x + self.direction[0], head_y + self.direction[1])

        if not (0 <= new_head[0] < GRID_WIDTH and 0 <= new_head[1] < GRID_HEIGHT):
            return False

        if new_head in self.body[1:]:
            return False

        self.body.insert(0, new_head)
        self.body.pop()
        return True

    def grow(self):
        head_x, head_y = self.body[0]
        new_head = (head_x + self.direction[0], head_y + self.direction[1])
        self.body.insert(0, new_head)

    def set_direction(self, direction):
        if (direction[0] * -1, direction[1] * -1) != self.direction:
            self.new_direction = direction

    def draw(self, screen):
        for x, y in self.body:
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, SNAKE_COLOR, rect)


class Food:
    def __init__(self):
        self.x = random.randint(0, GRID_WIDTH - 1)
        self.y = random.randint(0, GRID_HEIGHT - 1)

    def draw(self, screen):
        rect = pygame.Rect(self.x * CELL_SIZE, self.y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(screen, FOOD_COLOR, rect)

    def respawn(self, snake):
        while True:
            self.x = random.randint(0, GRID_WIDTH - 1)
            self.y = random.randint(0, GRID_HEIGHT - 1)
            if (self.x, self.y) not in snake.body:
                break


class PygameButton:
    def __init__(self, x, y, width, height, text, action):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action

    def draw(self, screen):
        pygame.draw.rect(screen, BUTTON_COLOR, self.rect)
        text_surface = pygame.font.Font(None, FONT_SIZE).render(self.text, True, BUTTON_TEXT_COLOR)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.action()


def move_up():
    snake.set_direction((0, -1))


def move_down():
    snake.set_direction((0, 1))


def move_left():
    snake.set_direction((-1, 0))


def move_right():
    snake.set_direction((1, 0))


def exit_game():
    pygame.quit()
    sys.exit()

class ChatApp(App):
    def build(self):
        Window.set_title("Qwota Messenger")
        return ChatWindow()

class ChatWindow(BoxLayout):
    messages = ListProperty([])
    text_color = ListProperty([1, 1, 1, 1])
    message_area = ObjectProperty(None)
    text_input = ObjectProperty(None)
    snake_popup = None

    def __init__(self, **kwargs):
        print("ChatWindow __init__ kwargs:", kwargs)

        super().__init__(**kwargs)
        self.orientation = 'vertical'

        self.message_area = ScrollView(size_hint=(1, 0.8))
        self.message_layout = BoxLayout(orientation='vertical', size_hint_y=None)
        self.message_layout.bind(minimum_height=self.message_layout.setter('height'))
        self.message_area.add_widget(self.message_layout)

        self.input_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.2))

        self.text_input = TextInput(hint_text='Введите сообщение', multiline=False, size_hint_y=0.5)
        self.send_button = KivyButton(text='Отправить', size_hint_x=None, width=150, size_hint_y=0.5)
        self.send_button.bind(on_press=self.send_message)
        self.options_button = KivyButton(text='...', size_hint_x=None, width=150, size_hint_y=0.5)


        self.input_layout.add_widget(self.text_input)
        self.input_layout.add_widget(self.send_button)
        self.input_layout.add_widget(self.options_button)


        self.dropdown = DropDown()
        btn_image = KivyButton(text='Изображение', size_hint_y=None, height=44)
        btn_color = KivyButton(text='Выбрать цвет текста', size_hint_y=None, height=44)

        btn_image.bind(on_release=self.show_file_chooser)
        btn_color.bind(on_release=self.show_color_picker)

        self.dropdown.add_widget(btn_image)
        self.dropdown.add_widget(btn_color)

        self.options_button.bind(on_release=self.dropdown.open)
        self.dropdown.bind(on_dismiss=lambda event: setattr(self.options_button, 'state', 'normal'))

        self.add_widget(self.message_area)
        self.add_widget(self.input_layout)

    def send_message(self, instance):
        text = self.text_input.text
        if text:
            if text.startswith("%змейка"):
                self.open_snake_game()
            elif text.startswith("#"):
                self.search_yandex(text)
            else:
                self.messages.append(text)
                self.display_message(text)
            self.text_input.text = ''

    def display_message(self, text):
        message_layout = BoxLayout(orientation='horizontal', size_hint_y=None)
        message_layout.bind(minimum_height=message_layout.setter('height'))

        message_label = Label(text=text, size_hint_x=0.7, size_hint_y=None, halign='left', valign='top', text_size=(self.message_area.width * 0.6, None), color=self.text_color)
        message_label.bind(texture_size=message_label.setter('size'))
        message_layout.add_widget(message_label)

        edit_button = KivyButton(text='Редактировать', size_hint_x=0.15)
        delete_button = KivyButton(text='Удалить', size_hint_x=0.15)

        message_index = len(self.message_layout.children)

        edit_button.bind(on_press=lambda instance: self.edit_message(message_index))
        delete_button.bind(on_press=lambda instance: self.delete_message(message_index))

        message_layout.add_widget(edit_button)
        message_layout.add_widget(delete_button)

        self.message_layout.add_widget(message_layout)

        self.message_area.scroll_y = 0

    def edit_message(self, index):
       message_layout = self.message_layout.children[len(self.message_layout.children) - 1 - index]
       message_label = message_layout.children[2]

       original_text = message_label.text

       content = BoxLayout(orientation='vertical')
       input_text = TextInput(text=original_text, multiline=False)
       content.add_widget(input_text)

       ok_button = KivyButton(text='OK', size_hint_y=None, height=44)
       cancel_button = KivyButton(text='Отмена', size_hint_y=None, height=44)

       button_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=44)
       button_layout.add_widget(ok_button)
       button_layout.add_widget(cancel_button)

       content.add_widget(button_layout)

       popup = Popup(title='Редактировать сообщение', content=content, size_hint=(0.9, 0.9))

       ok_button.bind(on_press=lambda instance: self.update_message(index, input_text.text, popup))
       cancel_button.bind(on_press=popup.dismiss)

       popup.open()

    def update_message(self, index, new_text, popup):
        message_layout = self.message_layout.children[len(self.message_layout.children) - 1 - index]
        message_label = message_layout.children[2]
        message_label.text = new_text

        self.messages[index] = new_text

        popup.dismiss()

    def delete_message(self, index):
        message_layout = self.message_layout.children[len(self.message_layout.children) - 1 - index]

        self.message_layout.remove_widget(message_layout)

        del self.messages[index]

    def open_yandex_images(self, query):
        if query:
            query_encoded = query.replace(" ", "+")
            search_url = f'https://yandex.ru/images/search?text={query_encoded}'
            webbrowser.open(search_url)

    def search_yandex(self, query):
        if query.startswith("#"):
            self.open_yandex_images(query[1:])
        else:
            self.open_yandex_images(query)

    def show_file_chooser(self, instance):
        content = BoxLayout(orientation='vertical')
        if IS_MOBILE:
            file_chooser = FileChooserListView(path=os.path.expanduser("~"), filters=['*.png', '*.jpg','*.jpeg'])
        else:
            file_chooser = FileChooserIconView(path=os.path.expanduser("~"),filters=['*.png', '*.jpg', '*.jpeg'])

        cancel_button = KivyButton(text='Отмена', size_hint_y=None, height=44)
        select_button = KivyButton(text='Выбрать', size_hint_y=None, height=44)

        button_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=44)
        button_layout.add_widget(cancel_button)
        button_layout.add_widget(select_button)

        content.add_widget(file_chooser)
        content.add_widget(button_layout)

        popup = Popup(title='Выберите изображение', content=content, size_hint=(0.9, 0.9))

        cancel_button.bind(on_press=popup.dismiss)
        select_button.bind(on_press=lambda instance: self.send_image(file_chooser.selection, popup))

        popup.open()

    def send_image(self, file_paths, popup):
        if file_paths:
            file_path = file_paths[0]
            self.display_image(file_path)
            popup.dismiss()

    def display_image(self, file_path):
        image = Image(source=file_path, size_hint_y=None,
                      height=200)
        self.message_layout.add_widget(image)
        self.message_area.scroll_y = 0

    def show_color_picker(self, instance):
        color_picker = ColorPicker(color=self.text_color)
        content = BoxLayout(orientation='vertical')
        content.add_widget(color_picker)

        ok_button = KivyButton(text='OK', size_hint_y=None, height=44)
        content.add_widget(ok_button)

        popup = Popup(title='Выберите цвет текста', content=content, size_hint=(0.9, 0.9))
        ok_button.bind(on_press=lambda instance: self.set_text_color(color_picker.color, popup))
        popup.open()

    def set_text_color(self, color, popup):
        self.text_color = color
        popup.dismiss()

    def open_snake_game(self):
        pygame.init()
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Змейка")
        clock = pygame.time.Clock()
        font = pygame.font.Font(None, FONT_SIZE)

        global snake
        global food
        snake = Snake()
        food = Food()
        food.respawn(snake)

        button_width = 80
        button_height = 40
        button_x_start = SCREEN_WIDTH // 2 - (2 * button_width + 10)
        button_y = GRID_HEIGHT * CELL_SIZE + 20

        up_button = PygameButton(button_x_start + button_width + 10, button_y - button_height -10, button_width, button_height, "Вверх", move_up)
        down_button = PygameButton(button_x_start + button_width + 10, button_y + button_height + 10, button_width, button_height, "Вниз", move_down)
        left_button = PygameButton(button_x_start, button_y, button_width, button_height, "Влево", move_left)
        right_button = PygameButton(button_x_start + 2 * (button_width + 10), button_y, button_width, button_height, "Вправо", move_right)
        exit_button = PygameButton(SCREEN_WIDTH - button_width - 10, SCREEN_HEIGHT - button_height - 10, button_width, button_height, "Выход", exit_game)

        buttons = [up_button, down_button, left_button, right_button, exit_button]

        game_over = False
        score = 0
        game_speed = 5
        last_move_time = pygame.time.get_ticks()

        while not game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_over = True
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        snake.set_direction((0, -1))
                    elif event.key == pygame.K_DOWN:
                        snake.set_direction((0, 1))
                    elif event.key == pygame.K_LEFT:
                        snake.set_direction((-1, 0))
                    elif event.key == pygame.K_RIGHT:
                        snake.set_direction((1, 0))

                for button in buttons:
                    button.handle_event(event)

            current_time = pygame.time.get_ticks()
            if current_time - last_move_time > 1000 / game_speed:
                if not snake.move():
                    game_over = True
                last_move_time = current_time

                if snake.body[0][0] == food.x and snake.body[0][1] == food.y:
                    snake.grow()
                    food.respawn(snake)
                    score += 1
                    game_speed += 0.5

            screen.fill(BG_COLOR)

            snake.draw(screen)
            food.draw(screen)

            for button in buttons:
                button.draw(screen)

            score_text = font.render(f"Счет: {score}", True, (255, 255, 255))
            screen.blit(score_text, (10, 10))

            pygame.display.flip()
            clock.tick(FPS)

        pygame.quit()

if __name__ == '__main__':
    ChatApp().run()