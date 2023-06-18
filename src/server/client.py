from tkinter import Tk, Frame, Scrollbar, Label, END, Entry, Text, VERTICAL, Button, messagebox
from src.config.Config import Config
from src.server.game import Game
import socket
import pygame
import threading  # for multiple proccess
import src.server.network as network

################# Chatroom ###################################################
class GUI:
    client_socket = None
    last_received_message = None

    def __init__(self, master):
        self.root = master
        self.chat_transcript_area = None
        self.name_widget = None
        self.enter_text_widget = None
        self.join_button = None
        self.initialize_socket()
        self.initialize_gui()
        self.listen_for_incoming_messages_in_a_thread()

    def initialize_socket(self):
        # initialazing socket with TCP and IPv4
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        remote_ip = '192.168.32.1'  # IP address
        remote_port = 430  # TCP port
        self.client_socket.connect((remote_ip, remote_port))

    def initialize_gui(self):  # GUI initializer
        self.root.title("Socket Chat")
        self.root.resizable(0,0)
        self.display_chat_box()
        self.display_name_section()
        self.display_chat_entry_box()

    def listen_for_incoming_messages_in_a_thread(self):
        thread = threading.Thread(target=self.receive_message_from_server, args=( self.client_socket,))
        thread.start()

    def receive_message_from_server(self, so):
        while True:
            buffer = so.recv(256)
            if not buffer:
                break
            message = buffer.decode('utf-8')

            if "joined" in message:
                user = message.split(":")[1]
                message = user + " has joined"
                self.chat_transcript_area.insert('end', message + '\n')
                self.chat_transcript_area.yview(END)
            else:
                self.chat_transcript_area.insert('end', message + '\n')
                self.chat_transcript_area.yview(END)

        so.close()

    def display_name_section(self):
        frame = Frame()
        Label(frame, text='Enter your name:', font=("Helvetica", 16)).pack(side='left', padx=10)
        self.name_widget = Entry(frame, width=50, borderwidth=2)
        self.name_widget.pack(side='left', anchor='e')
        self.join_button = Button(frame, text="Join", width=10, command=self.on_join).pack(side='left')
        frame.pack(side='top', anchor='nw')

    def display_chat_box(self):
        frame = Frame()
        Label(frame, text='Chat Box:', font=("Serif", 12)).pack(side='top', anchor='w')
        self.chat_transcript_area = Text(frame, width=60, height=10, font=("Serif", 12))
        scrollbar = Scrollbar(frame, command=self.chat_transcript_area.yview, orient=VERTICAL)
        self.chat_transcript_area.config(yscrollcommand=scrollbar.set)
        self.chat_transcript_area.bind('<KeyPress>', lambda e: 'break')
        self.chat_transcript_area.pack(side='left', padx=10, fill='y')
        scrollbar.pack(side='right', fill='y')
        frame.pack(side='top')

    def display_chat_entry_box(self):
        frame = Frame()
        Label(frame, text='Enter message:', font=("Serif", 12)).pack(side='top', anchor='w')
        self.enter_text_widget = Text(frame, width=60, height=3, font=("Serif", 12))
        self.enter_text_widget.pack(side='left', pady=15)
        self.enter_text_widget.bind('<Return>', self.on_enter_key_pressed)
        frame.pack(side='top')

    def on_join(self):
        name = self.name_widget.get()
        self.g = StartGame() # connection is established
        if len(name) == 0:
            messagebox.showerror("Enter your name", "Enter your name to send a message")
            return
        self.name_widget.config(state='disabled')
        self.client_socket.send(name.encode('utf-8'))
        self.client_socket.send( ("joined:" + name).encode('utf-8'))
        t3 = threading.Thread(target=self.g.ConnectGame, args=(name,))
        t3.start()

    def on_enter_key_pressed(self, event):
        if len(self.name_widget.get()) == 0:
            messagebox.showerror("Enter your name", "Enter your name to send a message")
            return
        self.send_chat()
        self.clear_text()

    def clear_text(self):
        self.enter_text_widget.delete(1.0, 'end')

    def send_chat(self):
        senders_name = self.name_widget.get().strip() + ": "
        data = self.enter_text_widget.get(1.0, 'end').strip()
        message = (senders_name + data).encode('utf-8')
        self.chat_transcript_area.insert('end', message.decode('utf-8') + '\n')
        self.chat_transcript_area.yview(END)
        # send written message to the server
        self.client_socket.send(message)
        self.enter_text_widget.delete(1.0, 'end')
        return 'break'

    # def on_close_window(self):
    #     if messagebox.askokcancel("Quit", "Do you want to quit?"):
    #         self.root.destroy()
    #         self.client_socket.close()
    #         exit(0)

###################### Game #######################################################

class StartGame:

    server = network.Network()
    run = True

    def restartMoves(self):
        keys = pygame.key.get_pressed()
        move = [False, False]
        if keys[pygame.K_r]:
            move[0] = True

        if keys[pygame.K_q]:
            move[1] = True
        return move

    def moves(self):
        keys = pygame.key.get_pressed()
        move = [False, False, False, False, True]

        if keys[pygame.K_w]:
            move[0] = True

        if keys[pygame.K_s]:
            move[1] = True

        if keys[pygame.K_a]:
            move[2] = True

        if keys[pygame.K_d]:
            move[3] = True

        if keys[pygame.K_ESCAPE]:
            move[4] = False

        return move

    def ConnectGame(self ,name):
        pygame.init()
        config = Config()
        current_id = self.server.connect(name)
        players = self.server.send("get")

        game = Game()
        game.screen = pygame.display.set_mode((game.assets.width, game.assets.height))
        pygame.display.set_caption("Car Racing")
        assets = [(game.assets.track, (0, 0)), (game.assets.start, (502, 160)), (game.assets.borders, (0, 0))]
        game.constDraw()
        start = True
        win = False
        sendEndInfo = True

        cur_players = next((x for x in players if x.id == current_id))

        while self.run:

            pygame.time.Clock().tick(config.FPS)

            if start and cur_players.connection == config.playersNumer:
                players = self.server.send("temp")
                cur_players = next((x for x in players if x.id == current_id))
                start_ticks = pygame.time.get_ticks()
                game.constDraw()
                while True:
                    seconds = (pygame.time.get_ticks() - start_ticks) / 1000
                    if seconds > 5:
                        break
                    game.draw(game.screen, assets, cur_players.lab)
                    for p in players:
                        game.drawCar(game.loadCar(p.id), p.angle, p.position)
                    game.draw_counter(int(seconds))
                    pygame.display.update()
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            self.run = False
                game.constDraw()

                data = "time"
                players = self.server.send(data)
                start = False

            keys = pygame.key.get_pressed()

            data = "move"
            for m in self.moves():
                data += " " + str(m)

            players = self.server.send(data)
            if not players:
                break
            cur_players = next((x for x in players if x.id == current_id))
            game.draw(game.screen, assets, cur_players.lab)

            for p in players:
                game.drawCar(game.loadCar(p.id), p.angle, p.position)

            if cur_players.win and not start:
                game.drawWinner(cur_players.name)
                keys = self.restartMoves()
                if keys[0]:
                    players = self.server.send("restart")
                    start = True

                if keys[1]:
                    self.run = False
                game.draw_end_game_info()

            # If client close game
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.run = False
                    self.server.send("Quit")


            pygame.display.update()

        self.server.disconnect()
        pygame.quit()
        quit()


if __name__ == '__main__':
    root = Tk()  # Chat application window
    gui = GUI(root)

    # If client closed chat window
    def on_close_window():
        gui.g.run=False
        gui.client_socket.send(("Quit").encode('utf-8'))
        gui.g.server.disconnect()
        root.destroy()


    root.protocol("WM_DELETE_WINDOW", on_close_window)
    root.mainloop()



