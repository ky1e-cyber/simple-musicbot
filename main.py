import yt_dlp, os, csv, telebot, init_list
from typing import List, Dict, Tuple
from config import TOKEN, LIB_DIR, LIBLIST_FILE

bot = telebot.TeleBot(TOKEN)

if not os.path.isfile(LIBLIST_FILE):
    init_list.init()

ydl_opts = {
    'format': 'm4a/bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'm4a',
    }],
    "paths": {"home": LIB_DIR},
    "ignoreerrors": True
}

extractor = yt_dlp.YoutubeDL(ydl_opts)

class addToList:
    def __init__(self, list_path:str, columns:List[str]):
        self.path = list_path
        self.columns = columns
    def __call__(self, func):
        def _wrapper(element:Dict) -> Tuple[int, Dict]:
            with open(self.path, "r") as f:
                r = csv.DictReader(f, self.columns)
                rows_list = list(r)
            print(rows_list)
            for idx, existing_row in enumerate(rows_list[1::], start = 1):
                if existing_row["id"] == element["id"]:
                    if not os.path.isfile(existing_row["path"]):
                        row_list.pop(idx)
                        break
                    return 0, existing_row

            error_code, row = func(element)
            if error_code:
                return error_code, row

            with open(self.path, "w") as f:
                w = csv.DictWriter(f, self.columns)
                w.writerows(rows_list + [row])
            return error_code, row
        return _wrapper


@addToList(LIBLIST_FILE, ["id", "name", "path"])
def getAudioFile(element:Dict[str, str]) -> Tuple[int, Dict[str, str]]: ## (error_code, dict[keys: id, name, path]
    error_code = extractor.download([element["original_url"]])
    row = {"id": element["id"], "name": element["title"], "path": "none"}
    if error_code:
        return error_code, row
    old_path, new_path = map(lambda name: os.path.join(LIB_DIR, name), (f"{element['title']} [{element['id']}].m4a", f"{element['title']}.m4a"))
    os.rename(old_path, new_path)
    row["path"]  = new_path
    return error_code, row


@bot.message_handler(commands=['pdl', 'playlistdl', "playlistdownload"])
def playlistDlHandler(message):    
    url = message.text.split()[1]
    try:
        info = extractor.extract_info(url, download=False)##["entries"]
        entries = info["entries"]
    except:
        bot.reply_to(message, "An error occured while extracting info about playlist")
        return
    not_downloaded = []
    for e in entries:
        error_code, row = getAudioFile(e)
        if error_code:
            not_downloaded.append(e['title'])
            continue
        with open(row["path"], "rb") as file:
            bot.send_audio(message.chat.id, file)
    if len(not_downloaded) > 0:
        bot.reply_to(message, "Haven't been downloaded: " + " ".join(not_downloaded))


bot.infinity_polling()