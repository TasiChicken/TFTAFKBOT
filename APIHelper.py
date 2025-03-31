import requests
import warnings
from urllib3.exceptions import InsecureRequestWarning
import winHelper
from time import sleep
import base64

# Filter out the InsecureRequestWarning
warnings.filterwarnings("ignore", category=InsecureRequestWarning)

class LocalhostAPI:
    GET = requests.get
    POST = requests.post
    DELETE = requests.delete
    
    params = {'verify': False}

    def __init__(self, port):
        self.port = port

    def send_request(self, method, cmd: str, json=None):
        # Package parameters into a dictionary
        self.params['url'] = f"https://127.0.0.1:{self.port}{cmd}"

        if json is not None:
            self.params['json'] = json

        response = method(**self.params)
        if response.status_code // 100 == 2:
            response.encoding = "utf-8"
        return response

class LCUAPI():
    def __init__(self, port, token):
        self.Api = LocalhostAPI(port)

        temp = base64.b64encode((f"riot:{token}").encode())
        self.Api.params['headers'] = { "Authorization" : f"Basic {temp.decode()}" }
    
    def create_lobby(self):
        for i in range(5):
            # Try to exit lobby
            self.Api.send_request(method=LocalhostAPI.DELETE, cmd="/lol-lobby/v2/lobby")
            sleep(1)

            # Create TFT lobby
            print('Creating lobby')
            # TODO
            #self.Api.send_request(method=LocalhostAPI.POST, cmd="/lol-lobby/v2/lobby", json={"queueId": 6100})
            self.Api.send_request(method=LocalhostAPI.POST, cmd="/lol-lobby/v2/lobby", json={"queueId": 1090})
            sleep(1)

            # Check if is in a lobby
            statusCode = self.Api.send_request(method=LocalhostAPI.GET, cmd="/lol-lobby/v2/lobby").status_code
            sleep(1)
            
            if statusCode // 100 == 2:
                return
        raise TimeoutError('Cannot create lobby')
    
    def join_queue(self):
        # Joinin match queue
        for i in range(5):
            print('Joining match queue')
            self.Api.send_request(method=LocalhostAPI.POST, cmd="/lol-lobby/v2/lobby/matchmaking/search")
            winHelper.hide_window_for_sec(winHelper.CLIENT_WINDOW, 1)

            state = self.Api.send_request(method=LocalhostAPI.GET, cmd="/lol-lobby/v2/lobby/matchmaking/search-state").json()['searchState']
            winHelper.hide_window_for_sec(winHelper.CLIENT_WINDOW, 1)

            if state != 'Invalid':
                return

        raise TimeoutError('Cannot join queue')

    def accept_match(self):
        # Loop until matched
        while True:
            print("waiting for game matched")
            
            # Get matching state
            state = self.Api.send_request(method=LocalhostAPI.GET, cmd="/lol-lobby/v2/lobby/matchmaking/search-state").json()['searchState']
            winHelper.hide_window_for_sec(winHelper.CLIENT_WINDOW, 1)

            # If matchmaking found
            if state == 'Found':
                # Accept
                self.Api.send_request(method=LocalhostAPI.POST, cmd="/lol-matchmaking/v1/ready-check/accept")
                winHelper.hide_window_for_sec(winHelper.CLIENT_WINDOW, 1)
                
                # Wait for all summoners to accept 
                while True :
                    print('waiting for all accepted')

                    # Get matching state
                    state = self.Api.send_request(method=LocalhostAPI.GET, cmd="/lol-lobby/v2/lobby/matchmaking/search-state").json()['searchState']
                    winHelper.hide_window_for_sec(winHelper.CLIENT_WINDOW, 1)
                    
                    if state == 'Invalid':
                        print('Matched')
                        return
                    
                    # not successful
                    elif state == 'Searching':
                        break
    
    def exit_match(self):
        # eixt the match
        print("exit the game")
        self.Api.send_request(method=LocalhostAPI.POST, cmd="/lol-gameflow/v1/early-exit")
        winHelper.hide_window_for_sec(winHelper.CLIENT_WINDOW, 3)

        # kill the game window
        print("kill game window")
        winHelper.killTask(winHelper.GAME_EXE)
        winHelper.hide_window_for_sec(winHelper.CLIENT_WINDOW, 3)