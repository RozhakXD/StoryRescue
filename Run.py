import json, re, requests, time, random, string, sys, os
from rich import print as putStrLn
from urllib.parse import urlparse
from rich.console import Console
from requests.exceptions import RequestException

REELS, LINK, MAKSIMUM = [], [], 0

def Archive_Stories(session: str, cookies: str):
    session.headers.update(
        {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Cookie': '{}'.format(cookies),
            'Host': 'www.instagram.com',
            'Purpose': 'prefetch',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Sec-Purpose': 'prefetch;prerender',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
        }
    )
    response = session.get('https://www.instagram.com/archive/stories/', verify=True, allow_redirects=True)
    csrf_token = re.search(r'"csrf_token":"(.*?)"', response.text)
    if csrf_token != None:
        X_CSRFToken = (csrf_token.group(1))
    else:
        csrf_token = re.search(r'csrftoken=(.*?);', str(cookies))
        X_CSRFToken = (csrf_token.group(1) if csrf_token else '')
    return (
        X_CSRFToken
    )

def Reels_Ids(cookies: str):
    with requests.Session() as session:
        X_CSRFToken = Archive_Stories(session=session, cookies=cookies)
        session.headers.update(
            {
                'Referer': 'https://www.instagram.com/archive/stories/',
                'X-CSRFToken': '{}'.format(X_CSRFToken),
                'X-Requested-With': 'XMLHttpRequest',
                'Host': 'www.instagram.com',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-origin',
                'X-ASBD-ID': '129477',
                'Accept': '*/*',
                'X-IG-App-ID': '936619743392459',
                'X-IG-WWW-Claim': '0',
            }
        )
        timezone_offset = (-time.timezone if time.localtime().tm_isdst == 0 else -time.altzone)
        response2 = session.get('https://www.instagram.com/api/v1/archive/reel/day_shells/?timezone_offset={}'.format(timezone_offset), verify=True)

        if '"status":"ok"' in str(response2.text) and '"items":[]' not in str(response2.text):
            json_response = json.loads(response2.text)
            for z in json_response['items']:
                archiveDay = z['id']
                REELS.append(f'{archiveDay}')
                putStrLn(f"[bold white][[bold green]*[bold white]] Mengumpulkan[bold green] {archiveDay}[bold white]!     ", end='\r')
                time.sleep(0.05)

            if '"max_id":null,' not in str(response2.text):
                max_id = json_response['max_id'] # Jangan Menggunakan NEXT_MAX_ID, Jika Error / Story Anda Sedikit!
                Next_Reels_Ids(session=session, cookies=cookies, max_id=max_id)
            return ('null')
        elif '/accounts/login/' in str(response2.text):
            putStrLn("\n[bold white][[bold red]![bold white]][bold red] Login Diperlukan!")
            sys.exit(0)
        else:
            putStrLn("\n[bold white][[bold red]![bold white]][bold red] Tidak Ada Arsip Story Yang Ditemukan!")
            sys.exit(0)

def Next_Reels_Ids(session: str, cookies: str, max_id: str):
    timezone_offset = (-time.timezone if time.localtime().tm_isdst == 0 else -time.altzone)
    response3 = session.get('https://www.instagram.com/api/v1/archive/reel/day_shells/?timezone_offset={}&max_id={}'.format(timezone_offset, max_id), verify=True)
    if '"status":"ok"' in str(response3.text) and '"items":[]' not in str(response3.text):
        json_response = json.loads(response3.text)
        for z in json_response['items']:
            archiveDay = z['id']
            REELS.append(f'{archiveDay}')
            putStrLn(f"[bold white][[bold green]*[bold white]] Mengumpulkan[bold green] {archiveDay}[bold white]!     ", end='\r')
            time.sleep(0.05)
        if '"max_id":null,' not in str(response3.text):
            max_id = json_response['max_id']
            Next_Reels_Ids(session=session, cookies=cookies, max_id=max_id)
        return ('null')
    else:
        return ('null')
    
def Kumpulkan_Story(cookies: str, reel_ids: str, videos: bool):
    with requests.Session() as session:
        X_CSRFToken = Archive_Stories(session=session, cookies=cookies)
        session.headers.update(
            {
                'Referer': 'https://www.instagram.com/archive/stories/',
                'X-CSRFToken': '{}'.format(X_CSRFToken),
                'X-Requested-With': 'XMLHttpRequest',
                'Host': 'www.instagram.com',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-origin',
                'X-ASBD-ID': '129477',
                'Accept': '*/*',
                'X-IG-App-ID': '936619743392459',
                'X-IG-WWW-Claim': '0',
            }
        )
        response2 = session.get('https://www.instagram.com/api/v1/feed/reels_media/?reel_ids={}'.format(reel_ids), verify=True)
        if '"candidates":' in response2.text:
            json_response = json.loads(response2.text)
            candidate_url = re.findall("{'candidates': \\[{'width': .*?, 'height': .*?, 'url': '(.*?)'}", str(json_response))
            for url in candidate_url:
                if str(url) in LINK:
                    continue
                else:
                    LINK.append(f'{url}')
                    putStrLn(f"[bold white][[bold green]*[bold white]] Mengumpulkan[bold green] {len(LINK)}[bold white] Foto!     ", end='\r')
                    time.sleep(0.05)
            if bool(videos) == True:
                BaseURL = re.findall(r'FBQualityClass="(?:hd|.*?)" FBQualityLabel="(?:720p|.*?)"><BaseURL>(.*?)</BaseURL>', str(json_response))
                for url in BaseURL:
                    clean_url = url.replace('amp;', '')
                    if str(clean_url) in LINK:
                        continue
                    elif 'mp4?_nc_cat=' in str(clean_url):
                        continue
                    else:
                        LINK.append(f'{clean_url}')
                        putStrLn(f"[bold white][[bold green]*[bold white]] Mengumpulkan[bold green] {len(LINK)}[bold white] Video!     ", end='\r')
                        time.sleep(0.05)
                return ('null')
            else:
                return ('null')
        else:
            return ('null')
        
def Unduh_Story(url: str, directory_name: str):
    global MAKSIMUM
    try:
        with requests.Session() as session:
            session.headers.update(
                {
                    'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive',
                    'Host': '{}'.format(urlparse(url=url).netloc),
                    'Referer': 'https://www.instagram.com/',
                    'Sec-Fetch-Site': 'cross-site',
                    'Sec-Fetch-Dest': 'image',
                    'Sec-Fetch-Mode': 'no-cors',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
                }
            )

            file_name = ''.join(random.choices(string.ascii_letters + string.digits, k=9))
            response = session.get(url=url, allow_redirects=True, verify=True)

            file_extension = ('mp4' if '.mp4' in str(url) else 'jpg')
            with open(f'{directory_name}{file_name}.{file_extension}', 'wb') as binary_file:
                binary_file.write(response.content)
            return ('null')
    except (RequestException) as e:
        if int(MAKSIMUM) >= 3:
            return ('null')
        else:
            putStrLn(f"[bold white][[bold red]![bold white]][bold red] {str(e).title()}!")
            MAKSIMUM += 1

def Main():
    global MAKSIMUM
    putStrLn("""[bold blue]   _____ _                   _____                           
  / ____| |                 |  __ \                          
 | (___ | |_ ___  _ __ _   _| |__) |___  ___  ___ _   _  ___ 
  \___ \| __/ _ \| '__| | | |  _  // _ \/ __|/ __| | | |/ _ \ 
  ____) | || (_) | |  | |_| | | \ \  __/\__ \ (__| |_| |  __/
 |_____/ \__\___/|_|   \__, |_|  \_\___||___/\___|\__,_|\___|
                        __/ |[bold green] Save Your Stories Forever[/]
                       |___/""") # Coded by Rozhak
    cookies = Console().input("\n[bold white][[bold green]?[bold white]] Your Cookies: ")
    if 'sessionid=' in cookies:
        collect_video = Console().input("[bold white][[bold green]?[bold white]] Sertakan Video (Y/N): ")
        file_name = ('Temporary/Tautan.json')
        putStrLn("[bold white]")
        videos = (True if collect_video.lower() == 'y' else False)
        Reels_Ids(cookies=cookies)
        if len(REELS) != 0:
            for reel_ids in REELS:
                Kumpulkan_Story(cookies=cookies, reel_ids=reel_ids, videos=videos)

            with open(f'{file_name}', 'w') as json_file:
                json.dump(LINK, json_file, indent=4)

            putStrLn(f"[bold white][[bold green]*[bold white]] Berhasil Menyimpan Tautan Story!     ", end='\r')
            time.sleep(2.5)

            putStrLn(f"[bold white]                                              ", end='\r')
            putStrLn(f"[bold white][[bold green]*[bold white]] Jumlah Story:[bold green] {len(LINK)}")
            putStrLn(f"[bold white][[bold green]*[bold white]] File Story:[bold green] {file_name}")
            directory_name = Console().input("[bold white][[bold green]?[bold white]] Folder (Ex:[bold green] Penyimpanan/[bold white]): ")

            if os.path.exists(directory_name):
                putStrLn("[bold white]")
                LOOPING = 1
                for url in LINK:
                    MAKSIMUM = 0
                    putStrLn(f"[bold white][[bold green]{LOOPING}[bold white]] Mengunduh[bold blue] {url}[bld white]!")
                    Unduh_Story(url=url, directory_name=directory_name)
                    LOOPING += 1
                Console().input("\n[bold white][[bold green]Selesai[bold white]]")
                sys.exit(1)
            else:
                putStrLn("[bold white][[bold red]![bold white]][bold yellow] Anda Membatalkan Penguhduhan!")
                sys.exit(1)
        else:
            putStrLn("\n[bold white][[bold red]![bold white]][bold red] Tidak Ada Arsip Story Yang Ditemukan!")
            sys.exit(0)
    else:
        putStrLn("[bold white][[bold red]![bold white]][bold red] Cookies Yang Anda Masukan Salah!")
        sys.exit(0)

if __name__=='__main__':
    try:
        for FOLDERS in ['Penyimpanan', 'Temporary']:
            os.makedirs(f'{FOLDERS}', exist_ok=True)
        os.system('git pull')
        Main()
    except (KeyboardInterrupt):
        sys.exit(0)