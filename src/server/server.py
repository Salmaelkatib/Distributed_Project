import time
from random import randint
from timeit import default_timer as timer
import socket
import threading
import _pickle as pickle
import pygame

from src.server.database import firebase

from src.config.Config import Config
from src.server.game import Game , IntializeGame
from src.server.player import Player
from src.server.clientInfo import ClientInfo


db=firebase.database()
class server:

    clients_list = []
    last_received_message = ""

    def __init__(self):
        self.start = timer()
        self.game = Game()
        self.game_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # this will allow you to immediately restart a TCP server
        self.game_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.chat_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.chat_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.HOST_NAME = socket.gethostname()
        self.SERVER_IP = socket.gethostbyname(self.HOST_NAME)
        self.init = IntializeGame()
        self.config = Config()
        self.time = 0
        self.win = False
        self.winner = None
        self.playersId = [1, 2, 3, 4]
        self.func()


    def func(self):
        try:
            # try to connect to chat and game socket
            self.chat_socket.bind((self.SERVER_IP , 430))
            self.game_socket.bind((self.SERVER_IP , 420))

        except socket.error as e:
            print(str(e))
            print("[SERVER] Server could not start")
            quit()
        self.game_socket.listen()
        self.chat_socket.listen(2)
        print(f"[SERVER] Server Started with local ip {self.SERVER_IP}")
        print("Chat socket is waiting for connection")

        while True:
            client = so, (ip, port) = self.chat_socket.accept()
            self.add_to_clients_list(client)
            print('Connected to ', ip, ':', str(port))
            t2 = threading.Thread(target=self.receive_messages, args=(so,))
            t2.start()
            flag = True
            while flag:
                host, addr = self.game_socket.accept()
                print("[CONNECTION] Connected to:", addr)

                self.init.connections += 1
                if self.init.connections <= self.config.playersNumer:
                    self.t1 = threading.Thread(target=self.threaded_client, args=(host, self.playersId.pop(0)))
                    self.t1.start()
                    flag=False
                    print()
    def reconnect(self, _id):
        self.t1.join()
        game_host, game_addr = self.game_socket.accept()
        print("[CONNECTED AGAIN] Connected to:", game_addr)
        tnew = threading.Thread(target=self.threaded_client, args=(game_host, _id,))
        tnew.start()

    def threaded_client(self, conn, _id):
        data = conn.recv(16)
        name = data.decode("utf-8")

        # If a client has connected before then retreive his data from database
        players =db.child("Players").shallow().get().val()
        Flag = False
        if players:
            for i in players:
                if i == name:
                    Flag = True
                    p = db.child("Players").child(name).get().val()
                    player = Player(self.game, self, self.init, self.config, _id, p["position"], p["max_speed"], p["turn"])
                    self.game.players.append(player)
                    clientsList = ClientInfo(self.config, player.id, player.position, p["angle"], p["speed"],
                                             p["max_speed"], p["acceleration"], p["breaks"], p["turn"], p["lab"], player.rect, 0,
                                             self.game.showTimer, self.game.positionTimer, p["win"], self.winner,self.init.connections)
                    self.init.addPlayer(clientsList)

        if not Flag:
            # If a new client is connected
            print("[LOG]", name, "connected to the server.")
            player = Player(self.game, self, self.init, self.config, _id, None, self.config.player['speed'],self.config.player['turn'])
            self.game.players.append(player)

            clientsList = ClientInfo(self.config, player.id, player.position, player.angle, player.speed, player.max_speed,
                                     player.acceleration, player.breaks, player.turn, player.lab, player.rect, 0,
                                     self.game.showTimer, self.game.positionTimer, self.win, self.winner,
                                     self.init.connections)
            data = {
                "id": player.id,
                "position": player.position,
                "angle": player.angle,
                "speed": player.speed,
                "max_speed": player.max_speed,
                "acceleration": player.acceleration,
                "breaks": player.breaks,
                "turn": player.turn,
                "lab": player.lab,
                # "rect": player.rect,
                "time": 0,
                "showTimer": self.game.showTimer,
                "posTimer": self.game.positionTimer,
                "win": self.win,
                "winner": self.winner,
                "connection": self.init.connections
            }
            db.child("Players").child(name).set(data)

            self.init.addPlayer(clientsList)

        start_time = time.time()
        conn.send(str.encode(str(_id)))
        restart = False
        run = True
        while run:
            try:
                data = conn.recv(1024)

                if not data:
                    break
                self.time = (pygame.time.get_ticks() - start_time)
                data = data.decode("utf-8")
                # look for specific commands from received data
                if data.split(" ")[0] == "move":
                    m, s = divmod(int(self.time / 1000), 60)
                    if int(s) == self.game.countTimer and not self.game.showTimer:
                        self.game.showTimer = True
                        self.game.positionTimer = self.config.timer['positon'][randint(0, 2)]
                        # self.game.positionTimer = self.config.timer['positon'][0]

                    split_data = data.split(" ")
                    key = []
                    for i in range(1, len(split_data)):
                        key.append(split_data[i])

                    if key[4] == 'False':
                        run = False

                    if self.init.connections <= self.config.playersNumer:

                        player.onServer(key)
                        #run = player.onServer(key)

                        if player.lab == self.config.labs:
                            self.win = True
                            self.winner = name
                            self.init.connections = 0

                        if restart:
                            self.win = False
                            self.winner = None
                            restart = False
                        clientsList.updateValues(player.id, player.position, player.angle, player.speed, player.max_speed,
                                                 player.acceleration, player.breaks, player.turn, player.lab,
                                                 player.rect, self.time - player.bonusTime, self.game.showTimer,
                                                 self.game.positionTimer, self.win, self.winner, self.init.connections)
                        updated_data = {
                            "id": player.id,
                            "position": player.position,
                            "angle": player.angle,
                            "speed": player.speed,
                            "max_speed": player.max_speed,
                            "acceleration": player.acceleration,
                            "breaks": player.breaks,
                            "turn": player.turn,
                            "lab": player.lab,
                            # "rect": player.rect,
                            "time": self.time - player.bonusTime,
                            "showTimer": self.game.showTimer,
                            "posTimer": self.game.positionTimer,
                            "win": self.win,
                            "winner": self.winner,
                            "connection": self.init.connections
                        }
                        db.child("Players").child(name).update(updated_data)

                    else:
                        clientsList.updateValues(player.id, player.position, player.angle, player.speed, player.max_speed,
                                                 player.acceleration, player.breaks, player.turn, player.lab,
                                                 player.rect, 0, False,
                                                 None, self.win, self.winner, self.init.connections)
                        updated_data = {
                            "id": player.id,
                            "position": player.position,
                            "angle": player.angle,
                            "speed": player.speed,
                            "max_speed": player.max_speed,
                            "acceleration": player.acceleration,
                            "breaks": player.breaks,
                            "turn": player.turn,
                            "lab": player.lab,
                            # "rect": player.rect,
                            "time": 0,
                            "showTimer": False,
                            "posTimer": None,
                            "win": self.win,
                            "winner": self.winner,
                            "connection": self.init.connections
                        }
                        db.child("Players").child(name).update(updated_data)

                elif data.split(" ")[0] == "time":
                    start_time = pygame.time.get_ticks()
                    self.time = (pygame.time.get_ticks() - start_time)
                    clientsList.updateValues(player.id, player.position, player.angle, player.speed, player.max_speed,
                                             player.acceleration, player.breaks, player.turn, player.lab, player.rect,
                                             self.time - player.bonusTime, self.game.showTimer, self.game.positionTimer,
                                             self.win, self.winner, self.init.connections)
                    updated_data = {
                        "id": player.id,
                        "position": player.position,
                        "angle": player.angle,
                        "speed": player.speed,
                        "max_speed": player.max_speed,
                        "acceleration": player.acceleration,
                        "breaks": player.breaks,
                        "turn": player.turn,
                        "lab": player.lab,
                        # "rect": player.rect,
                        "time": self.time - player.bonusTime,
                        "showTimer": self.game.showTimer,
                        "posTimer": self.game.positionTimer,
                        "win": self.win,
                        "winner": self.winner,
                        "connection": self.init.connections
                    }
                    db.child("Players").child(name).update(updated_data)

                elif data.split(" ")[0] == "restart":
                    restart = True
                    player.restart()
                    start_time = pygame.time.get_ticks()
                    self.game.countTimer = self.config.timer['countTimer']
                    self.game.showTimer = False
                    self.game.positionTimer = None
                    self.time = 0
                    self.init.connections += 1
                    clientsList.updateValues(player.id, player.position, player.angle, player.speed, player.max_speed,
                                             player.acceleration, player.breaks, player.turn, player.lab, player.rect,
                                             self.time - player.bonusTime, self.game.showTimer, self.game.positionTimer,
                                             self.win, self.winner, self.init.connections)
                    updated_data = {
                        "id": player.id,
                        "position": player.position,
                        "angle": player.angle,
                        "speed": player.speed,
                        "max_speed": player.max_speed,
                        "acceleration": player.acceleration,
                        "breaks": player.breaks,
                        "turn": player.turn,
                        "lab": player.lab,
                        # "rect": player.rect,
                        "time": self.time - player.bonusTime,
                        "showTimer": self.game.showTimer,
                        "posTimer": self.game.positionTimer,
                        "win": self.win,
                        "winner": self.winner,
                        "connection": self.init.connections
                    }
                    db.child("Players").child(name).update(updated_data)

                elif data.split(" ")[0] == "Quit":
                    print("[DISCONNECT] Name:", name, ", Client Id:", _id, "disconnected")
                    self.playersId.append(_id)
                    self.playersId.sort()
                    self.init.connections -= 1

                    if clientsList in self.init.players:
                        self.init.removePlayer(clientsList)  # remove client information from players list
                        self.game.players.remove(player)

                    db.child("Players").child(name).remove()




                else:
                    clientsList.updateValues(player.id, player.position, player.angle, player.speed, player.max_speed,
                                             player.acceleration, player.breaks, player.turn, player.lab, player.rect,
                                             0, self.game.showTimer, self.game.positionTimer, self.win, self.winner,
                                             self.init.connections)
                    updated_data = {
                        "id": player.id,
                        "position": player.position,
                        "angle": player.angle,
                        "speed": player.speed,
                        "max_speed": player.max_speed,
                        "acceleration": player.acceleration,
                        "breaks": player.breaks,
                        "turn": player.turn,
                        "lab": player.lab,
                        # "rect": player.rect,
                        "time": 0,
                        "showTimer": self.game.showTimer,
                        "posTimer": self.game.positionTimer,
                        "win": self.win,
                        "winner": self.winner,
                        "connection": self.init.connections
                    }
                    db.child("Players").child(name).update(updated_data)


                conn.send(pickle.dumps(self.init.players))
                time.sleep(0.001)
            except :
                print("[LOST CONNECTION]Name:", name, "Reconnecting....")
                self.init.removePlayer(clientsList)  # remove client information from players list
                self.game.players.remove(player)
                conn.close()
                t3 = threading.Thread(target=self.reconnect, args=(_id,))
                t3.start()


        # When user disconnects
        print("[DISCONNECT] Name:", name, ", Client Id:", _id, "disconnected")
        self.playersId.append(_id)
        self.playersId.sort()
        self.init.connections -= 1

        if clientsList in self.init.players:
            self.init.removePlayer(clientsList)  # remove client information from players list
            self.game.players.remove(player)
        conn.close()  # close connection

    # function to receive new msgs
    def receive_messages(self, so):
        data = so.recv(16)
        name = data.decode("utf-8")
        while True:
            # initialize a buffer to receive clients msgs
            incoming_buffer = so.recv(256)
            if not incoming_buffer:
                break
            self.last_received_message = incoming_buffer.decode('utf-8')
            # send to all clients
            self.broadcast_to_all_clients(so)

            if self.last_received_message.split(" ")[0] == "Quit":
             db.child("Players").child(name).remove()

        so.close()

    # broadcast the message to all clients
    def broadcast_to_all_clients(self, senders_socket):
        for client in self.clients_list:
            socket, (ip, port) = client
            if socket is not senders_socket:
                socket.sendall(self.last_received_message.encode('utf-8'))


    def add_to_clients_list(self, client):
        if client not in self.clients_list:
            self.clients_list.append(client)


server()
