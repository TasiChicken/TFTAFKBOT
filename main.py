import time
from APIHelper import Method, LCUAPI, LocalhostAPI

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
        time.sleep(1)
        lcuAPI = LCUAPI.createInstance()
    liveAPI = LocalhostAPI('2999')
    
    while True:
        lcuAPI.make_match()

        waitUntilDead(liveAPI)

        lcuAPI.exit_match()

if __name__ == "__main__":
    main()