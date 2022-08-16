import datetime
import configparser
import pandas as pd
from tweepy import API, Cursor, OAuthHandler, TweepError #Tweepy 3.10

screen_name = 'YouTwitterUsername'

def api_auth_connect():
    # Read in configs
    configs = configparser.ConfigParser()
    configs.read('./config.ini')
    keys = configs['TWITTER']
    consumer_key = keys['CONSUMER_KEY'] 
    consumer_secret = keys['CONSUMER_SECRET'] 
    access_token = keys['ACCESS_TOKEN']
    access_secret = keys['ACCESS_SECRET']
# Authenticate Tweepy connection to Twitter API
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_secret)
#api = API(auth, wait_on_rate_limit=True)
    api = API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True, compression=True)
    return api

def setup_search(api):
    
    user_id = api.get_user(screen_name).id_str
    user_followers = api.get_user(user_id).followers_count

    ids = []
    for fid in Cursor(api.followers_ids, screen_name=screen_name, count=5000).items():
        ids.append(fid)

    info = []
    for i in range(0, len(ids), 100):
        try:
            chunk = ids[i:i+100]
            info.extend(api.lookup_users(user_ids=chunk))
        except:
            import traceback
            traceback.print_exc()
            print('Algo fue mal...')


    data = [x._json for x in info]
    df = pd.DataFrame(data)
    df = df[['screen_name']]
    df.to_csv('followers.csv', index=False)
    return user_followers

def procesamiento_seguidores(api, user_followers):
    with open('followersOld.csv', 'r') as t1, open('followers.csv', 'r') as t2:
        fileone = t1.readlines()[1:]
        filetwo = t2.readlines()[1:]

    with open('update.csv', 'w') as outFile:  

        e = datetime.datetime.now()

        outFile.write("-------------------------------------------\n")
        outFile.write("Números seguidores actuales " + screen_name+ " " + e.strftime("%Y-%m-%d %H:%M:%S")+ ": " + str(user_followers) + "\n-------------------------------------------\n")

        outFile.write("-------------------------------------------\n")
        outFile.write("Seguidores el 29 julio 1:20 AM: " + str(len(fileone)) + ". Nuevos seguidores desde entonces: " + "\n-------------------------------------------\n")
        
        for line in filetwo:

            if line not in fileone:
                user = api.get_user(line)
                id = user.id_str

                outFile.write("✅ " + line)

        outFile.write("-------------------------------------------\n")
        outFile.write("UnFollows, Cuentas borradas, suspendido permanentes desde el 28 julio 6:42 AM: \n-------------------------------------------\n")
    
        for line in fileone:
            try:
                if line not in filetwo:
                    user = api.get_user(line)
                    id = user.id_str

                    outFile.write(line.replace("\n","") + " >>>>>> " + "⭕ La cuenta existe pero el usuario dejó de seguirte o te bloqueó." + "\n")
        
            except TweepError as e:
                    response = "🔴 "+ e.response.text 
       
                    outFile.write(line.replace("\n","") + " >>>>>> " + response.replace('message', '').replace('code', '')
                .replace('{"errors":[{"":50,"":"', '')
                .replace('{"errors":[{"":63,"":"', '')
                .replace('"}]}','')+ "\n")

        outFile.write("-------------------------------------------\n")
        diferencia = user_followers + (-len(fileone))

        
        outFile.write("Diferencia: " + str(diferencia) + "\n-------------------------------------------\n")


api = api_auth_connect()
user_followers = setup_search(api)
procesamiento_seguidores(api, user_followers)

print("¡ANÁLISIS Y COMPARACIÓN FINALIZADA!")