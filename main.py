from time import sleep
from APIHelper import LCUAPI, LocalhostAPI as Api
from datetime import datetime
import traceback
import winHelper

def waitUntilDead(liveAPI: Api):
    summonerName = liveAPI.send_request(Api.GET, '/liveclientdata/activeplayername').text.split('#')[0][1:]
    sleep(1)

    while True:
        jsonData = liveAPI.send_request(method=Api.GET, cmd='/liveclientdata/playerlist').json()
        
        for entry in jsonData:
            if entry["summonerName"] == summonerName:
                if entry["isDead"]:
                    return
        
        # wait for next detect
        print("waiting for dying")
        sleep(10)

def main():
    while True:
        try:
            pt = winHelper.getPortAndToken()
            lcuAPI = LCUAPI(port=pt[0], token=pt[1])
            liveAPI = Api('2999')
            
            winHelper.mute_application(winHelper.RENDER_EXE)
            while True:
                lcuAPI.exit_match()
                
                lcuAPI.create_lobby()
                lcuAPI.join_queue()
                lcuAPI.accept_match()
                
                print('Wait 15 min')
                winHelper.hide_window_for_sec(winHelper.GAME_WINDOW, 5)
                winHelper.mute_application(winHelper.GAME_EXE)
                winHelper.hide_window_for_sec(winHelper.CLIENT_WINDOW)
                winHelper.hide_window_for_sec(winHelper.GAME_WINDOW, 900)

                waitUntilDead(liveAPI)
        except KeyboardInterrupt:
            winHelper.show()
            exit()
        except:
            with open('log.txt', 'a') as logFile:
                logFile.write(datetime.now().strftime("[%Y-%m-%d %H:%M:%S]"))
                logFile.write('\n')
                logFile.write(traceback.format_exc())
                logFile.write('\n')
            winHelper.lanuchClient()

if __name__ == "__main__":
    main()