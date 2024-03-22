import time
from APIHelper import Method, LCUAPI, LocalhostAPI
import subprocess
import os

LAUCH_ARGS = "--launch-product=league_of_legends --launch-patchline=live"

def lanuchClient():
    # Open League of Legends client
    print('lauching client')
    subprocess.Popen(r'"C:\Riot Games\Riot Client\RiotClientServices.exe" --launch-product=league_of_legends --launch-patchline=live', shell=True)
    print('Waiting 30 sec for client lanuched completely')
    time.sleep(30)

def waitUntilDead(liveAPI):
    temp = liveAPI.send_request(Method.GET, '/liveclientdata/activeplayername')
    summonerName = temp.text.split('#')[0][1:]
    temp.close()

    while True:
        temp = liveAPI.send_request(Method.GET, '/liveclientdata/playerlist')
        jsonData = temp.json()
        temp.close()
        
        for entry in jsonData:
            if entry["summonerName"] == summonerName:
                if entry["isDead"]:
                    return
        
        # wait for next detect
        print("waiting for dying")
        time.sleep(10)

def main():
    lcuAPI = LCUAPI.createInstance()
    while lcuAPI is None:
        lanuchClient()
        lcuAPI = LCUAPI.createInstance()
    liveAPI = LocalhostAPI('2999')
    
    while True:
        while True:
            if lcuAPI.create_lobby():
                break
            os.system('taskkill /F /IM "LeagueClient.exe"')
            lanuchClient()

        lcuAPI.make_match()
        waitUntilDead(liveAPI)
        lcuAPI.exit_match()

if __name__ == "__main__":
    main()