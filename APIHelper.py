import os
import psutil
import base64
import requests
from enum import Enum
import warnings
from urllib3.exceptions import InsecureRequestWarning
import windowHelper

# Filter out the InsecureRequestWarning
warnings.filterwarnings("ignore", category=InsecureRequestWarning)

class Method(Enum):
    GET = requests.get
    POST = requests.post
    DELETE = requests.delete

class LocalhostAPI:
    def __init__(self, port):
        self.port = port
        self.headers = None

    def send_request(self, method: Method, cmd: str, json_data=None):
        response = method(
            url=f"https://127.0.0.1:{self.port}{cmd}",
            headers=self.headers,
            json=json_data,
            verify=False
        )

        if response.status_code // 100 == 2:
            response.encoding = "utf-8"
        return response

class LCUAPI(LocalhostAPI):
    @staticmethod
    def createInstance():
        data = None

        # Get data from client
        for process in psutil.process_iter():
            if process.name().removesuffix(".exe") == "LeagueClientUx":
                data = process.cmdline()
                break

        # If client was not found
        if data is None:
            print("lol client are not lanuched")
            return None

        # Extract port and token from data
        for param in data:
            info = param.split("=")
            if info[0] == "--remoting-auth-token":
                token = info[1]
            if info[0] == "--app-port":
                port = info[1]

        return LCUAPI(port, token)
            
    def __init__(self, port, token):
        self.port = port

        self.token = token
        temp = base64.b64encode((f"riot:{token}").encode())
        self.headers = { "Authorization":f"Basic {temp.decode()}" }
    
    def create_lobby(self):
        for i in range(5):
            # Try to exit lobby
            self.send_request(Method.DELETE, "/lol-lobby/v2/lobby").close()
            windowHelper.hide_window_for_sec(windowHelper.CLIENT_WINDOW, 1)

            # Create TFT lobby
            print('Creating lobby')
            self.send_request(Method.POST, "/lol-lobby/v2/lobby", {"queueId": 1090}).close()
            windowHelper.hide_window_for_sec(windowHelper.CLIENT_WINDOW, 1)

            # Check if is in a lobby
            temp = self.send_request(Method.GET, "/lol-lobby/v2/lobby")
            statusCode = temp.status_code
            temp.close()
            if statusCode // 100 == 2:
                return True
        return False
    
    def make_match(self):
        # Joinin match queue
        while True:
            print('Joining match queue')
            self.send_request(Method.POST, "/lol-lobby/v2/lobby/matchmaking/search").close()

            temp = self.send_request(Method.GET, "/lol-lobby/v2/lobby/matchmaking/search-state")
            state = temp.json()['searchState']
            temp.close()

            if state != 'Invalid':
                break

            windowHelper.hide_window_for_sec(windowHelper.CLIENT_WINDOW, 1)

        # Loop until matched
        while True:
            print("waiting for game matched")
            
            windowHelper.hide_window_for_sec(windowHelper.CLIENT_WINDOW, 3)
            
            # Get matching state
            temp = self.send_request(Method.GET, "/lol-lobby/v2/lobby/matchmaking/search-state")
            state = temp.json()['searchState']
            temp.close()

            # If matchmaking found
            if state == 'Found':
                # Accept
                temp = self.send_request(Method.POST, "/lol-matchmaking/v1/ready-check/accept")
                temp.close()
                
                # Wait for all summoners to accept 
                while(True):
                    print('waiting for all accepted')
                    windowHelper.hide_window_for_sec(windowHelper.CLIENT_WINDOW, 1)

                    # Get matching state
                    temp = self.send_request(Method.GET, "/lol-lobby/v2/lobby/matchmaking/search-state")
                    state = temp.json()['searchState']
                    temp.close()
                    
                    if state == 'Invalid':
                        print('Matched')
                        print('Wait 15 min')
                        windowHelper.hide_window_for_sec(windowHelper.CLIENT_WINDOW)
                        windowHelper.hide_window_for_sec(windowHelper.GAME_WINDOW, 900)
                        return
                    # not successful
                    elif state == 'Searching':
                        break
    
    def exit_match(self):
        # eixt the match
        print("exit the game")
        temp = self.send_request(Method.POST, "/lol-gameflow/v1/early-exit")
        print(temp.text)
        temp.close()
        # wait a while
        windowHelper.hide_window_for_sec(windowHelper.CLIENT_WINDOW, 3)

        # kill the 
        print("kill game window")
        os.system('taskkill /F /IM "League of Legends.exe"')
        windowHelper.hide_window_for_sec(windowHelper.CLIENT_WINDOW, 3)