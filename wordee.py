import argparse, os, random, requests, json, os, signal, sys, textwrap
from more_function import find_paragraph_in_news
from urllib.parse import urlparse, urlunparse
from googletrans import Translator
from GoogleNews import GoogleNews
from rich.console import Console
from rich.prompt import Prompt
import concurrent.futures

def clean_url(url, parameter="&ved"):
    index = url.find(parameter)
    if index != -1:
        return url[:index]
    else:
        return url

def asynchronous(func):
    async def wrapper(*args, **kwargs):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(func, *args, **kwargs)
            return future.result()

    return wrapper

def signal_handler(sig, frame):
    global exitOnCtrlC
    if exitOnCtrlC:
        console.print('\nYou pressed Ctrl+C again! Exiting.', style="red")
        sys.exit(0)
    else:
        console.print('\nYou pressed Ctrl+C!', style="red")
        exitOnCtrlC = True

def is_valid_file(parser, arg):
    if not os.path.exists(arg):
        parser.error("The file %s does not exist!" % arg)
    else:
        return open(arg, 'r')  # return an open file handle

def get_news_for_the_word(word):
    if word in wordNewsResultsCache:
        return wordNewsResultsCache[word]
    else:
        googlenews.clear()
        googlenews.search(word)
        newsResults = googlenews.results()
        wordNewsResultsCache[word] = newsResults
        return newsResults

def print_news_for_the_word_old(word):
    newsResults = get_news_for_the_word(word)
    console.print("Related news:", style="bold")
    for i, newsResult in enumerate(newsResults[:5]):
        title = newsResult["title"].replace(word.capitalize(), "[bold]"+word.capitalize()+"[/bold]")
        title = title.replace(word.lower(), "[bold]"+word+"[/bold]")
        # console.print(" %s. "%(i+1)+"[link="+newsResult["link"]+"]"+title)
        console.print(newsWrapper.fill("%s. "%(i+1)+title).replace("%s. "%(i+1), "%s. "%(i+1)+"[link="+newsResult["link"]+"]"))
    console.print("")

def print_news_for_the_word(word):
    newsResults = get_news_for_the_word(word)
    console.print("Related news:", style="bold")
    for i, newsResult in enumerate(newsResults[:3]):
        title = newsResult["title"].replace(word.capitalize(), "[blue bold]"+word.capitalize()+"[/blue bold]")
        title = title.replace(word.lower(), "[blue bold]"+word+"[/blue bold]")
        console.print(newsWrapper.fill("%s. "%(i+1)+title).replace("%s. "%(i+1), "%s. "%(i+1)+"[link="+clean_url(newsResult["link"])+"]"))

        if i == 2: 
            console.print("")
            content  = find_paragraph_in_news(clean_url(newsResult["link"]), word)
            highlighted_paragraph = content.replace(word.capitalize(), "[blue bold]"+word.capitalize()+"[/blue bold]")
            highlighted_paragraph = highlighted_paragraph.replace(word.lower(), "[blue bold]"+word+"[/blue bold]")
            console.print(highlighted_paragraph)

        console.print("")

def print_word_with_dictionary(word, wordDescription="", hideDictionary=False, translator=None, translateDestination=None, alwaysShowNews=None):
        if translator!=None:
            wordTranslation = translator.translate(word, dest=translateDestination)
            wordTranslated = wordTranslation.text

        if word in wordDictionaryResponseJSONCache:
            responseJSON = wordDictionaryResponseJSONCache[word]
            ok = True
        else:
            response = requests.get("https://api.dictionaryapi.dev/api/v2/entries/en/"+word)
            ok = response.ok
            responseJSON = json.loads(response.text)
            wordDictionaryResponseJSONCache[word] = responseJSON

        if alwaysShowNews:
            newsResults = get_news_for_the_word(word)

        # console.print(type(responseJSON) is list)

        # if args.phonetic and "phonetics" in responseJSON:
        #     phonetics = responseJSON["phonetics"]
        #     console.print("phonetics")
        #     # sourceUrl = None
        #     for phonetic in phonetics:
        #         if "audio" in phonetic:
        #             audio = phonetic["audio"]
        #             if audio == "":
        #                 continue
        #             mediaPlayer = vlc.MediaPlayer(audio)
        #             mediaPlayer.play()
        #             break

        if ok:
            if type(responseJSON) is list and len(responseJSON) > 0:
                responseJSON = responseJSON[0]
            if(hideDictionary):
                input("Press enter to show dictionary results...")
            os.system('clear')

            if translator!=None:
                console.print(word.capitalize()+" [magenta]"+wordTranslated+"[/magenta] "+wordDescription, style="markdown.h1")
            else:
                console.print(word.capitalize()+" "+wordDescription, style="markdown.h1")

            
            if "phonetic" in responseJSON:
                console.print(responseJSON["phonetic"], style="bright_magenta")
            else:
                console.print("phonetic not found", style="bright_magenta")

            if "meanings" in responseJSON:
                meanings = responseJSON["meanings"]
                for meaning in meanings:
                    if "partOfSpeech" in meaning:
                        console.print(textWrapper.fill(meaning["partOfSpeech"]), style="italic")
                    if "synonyms" in meaning:
                        synonyms = meaning["synonyms"]
                        if len(synonyms) > 0:
                            console.print(textWrapperDoubleIndents.fill(", ".join(synonyms)), style="green")
                    if "antonyms" in meaning:   
                        antonyms = meaning["antonyms"]
                        if len(antonyms) > 0:
                            console.print(textWrapperDoubleIndents.fill(", ".join(antonyms)), style="red")
                    if "definitions" in meaning:
                        definitions = meaning["definitions"]
                        for i, definition in enumerate(definitions):
                            if i >= 8:
                                break
                            console.print(textWrapperDoubleIndents.fill("%s. "%(i+1)+definition["definition"]))
                            if "example" in definition:
                                console.print(textWrapperDoubleIndents.fill("> "+definition["example"]), style="markdown.block_quote")
                    console.print("")
                console.print("> [link=https://www.google.com/search?q=define+"+word+"]🌎 Show the definition on google.[/link]\n")

            if alwaysShowNews:
                print_news_for_the_word(word)

        else:
            if(hideDictionary):
                input("Press enter to show dictionary results...")
            os.system('clear')
            
            if translator!=None:
                console.print(word.capitalize()+" [magenta]"+wordTranslated+"[magenta] "+wordDescription, style="markdown.h1")
            else:
                console.print(word.capitalize()+" "+wordDescription, style="markdown.h1")

            console.print("Status code: "+str(response.status_code), style="red")
            if "title" in responseJSON:
                console.print(textWrapper.fill(responseJSON["title"]), style="bold")
            if "message" in responseJSON:
                console.print(textWrapper.fill(responseJSON["message"]))
            if "resolution" in responseJSON:
                console.print(textWrapper.fill(responseJSON["resolution"]), style="bright_magenta")
            console.print("")
            console.print("> [link=https://www.google.com/search?q=define+"+word+"]🌎 Show the definition on google.[/link]\n")

            if alwaysShowNews:
                print_news_for_the_word(word)


def start():
    global exitOnCtrlC
    args = parser.parse_args()
    bookmarkedProbability = float(args.bookmarkedProbability)

    bookmarkedWordsFilename = os.path.splitext(args.filename.name)[0]+bookmarked_surfix+".txt"

    words = args.filename.read().splitlines()
    words = list(word.lower() for word in words if word)

    wordsHistory = []

    console.print("[bold]📖 Wordee[/bold]\nA random word picker with dictionary and news attached.\ncopyright©2022 magneticchen. Taiwan. GPLv3 License.\n")
    console.print(textWrapper.fill("Total "+str(len(words))+" words in the file."))
    console.print(textWrapper.fill("> "+args.filename.name), style="markdown.h1")
    # console.print(textWrapper.fill("> "+bookmarkedWordsFilename), style="markdown.h1")
    console.print("")

    translator = None
    if args.translateDestination:
        translator = Translator()
        console.print(textWrapper.fill(translator.translate("You have enabled the Translation.", dest=args.translateDestination).text))
        console.print(textWrapper.fill(translator.translate("Translation destionation: ", dest=args.translateDestination).text+"\""+args.translateDestination+"\""))
        console.print("")

    if os.path.isfile(bookmarkedWordsFilename):
        with open(bookmarkedWordsFilename, 'r+') as bookmarkedFile:
            bookmarkedWords = bookmarkedFile.read().splitlines()
            bookmarkedWords = list(word.lower() for word in bookmarkedWords if word)
    else:
        bookmarkedWords = []
    word = None
    wordIndex = -1

    def print_word_with_dictionary_and_surfix(hideDictionary=args.hideDictionary):
        if hideDictionary or word.lower() not in wordDictionaryResponseJSONCache:
            console.print(word.capitalize(), style="markdown.h1")
            
        dictionary_bookmarked_surfix = " [green bold]•[/green bold]" if word.lower() in bookmarkedWords else ""
        if wordIndex == -1:
            index_surfix = "(Not indexed)"
        else:
            index_surfix = "("+str(wordIndex+1)+" of "+str(len(words))+")"

        print_word_with_dictionary(word, index_surfix+dictionary_bookmarked_surfix, hideDictionary, translator, args.translateDestination, args.alwaysShowNews)

    while True:
        exitOnCtrlC = False

        if word == None:
            code = Prompt.ask("Actions: [[bold]R[/bold]]andom, [[bold]I[/bold]]nput a word, [[bold]H[/bold]]istory, [[bold]Q[/bold]]uit\n", default="R")
        elif wordIndex == -1:
            code = Prompt.ask("Actions: [[bold]R[/bold]]andom, [[bold]I[/bold]]nput a word, [[bold]H[/bold]]istory, [[bold]N[/bold]]ews, [[bold]Q[/bold]]uit\n", default="R")
        elif word.lower() not in bookmarkedWords:
            code = Prompt.ask("Actions: [[bold]R[/bold]]andom, [[bold]I[/bold]]nput a word, [[bold]H[/bold]]istory, [[bold]N[/bold]]ews, [[bold]B[/bold]]ookmark, [[bold]Q[/bold]]uit\n", default="R")
        else:
            code = Prompt.ask("Actions: [[bold]R[/bold]]andom, [[bold]I[/bold]]nput a word, [[bold]H[/bold]]istory, [[bold]N[/bold]]ews, Un[[bold]b[/bold]]ookmark, [[bold]Q[/bold]]uit\n", default="R")

        if code.lower() == "q":
            break

        elif code.lower() == "i":
            newWord = Prompt.ask("Word")
            if newWord == None or len(newWord) == 0:
                continue
            else:
                word = newWord

            if word.lower() in words:
                wordIndex = words.index(word.lower())
            else:
                wordIndex = -1
            wordsHistory.append(word)
            os.system('clear')
            print_word_with_dictionary_and_surfix()

        elif code.lower() == "h":
            console.print("")
            console.print("[bold]Historical reports[/bold]:")  
            if(len(wordsHistory)==0):
                console.print(" [bold]Viewed[/bold] none.")
            else:
                console.print(" [bold]Viewed[/bold] "+str(len(wordsHistory))+" words, last 5 items:")
                console.print(" > "+str(wordsHistory[-5:]))  
            if(len(bookmarkedWords)==0):
                console.print(" [bold]Bookmarked[/bold] none.")  
            else:
                console.print(" [bold]Bookmarked[/bold] "+str(len(bookmarkedWords))+" words, last 5 items:")
                console.print(" > "+str(bookmarkedWords[-5:]))  
            console.print("")    
            
        elif code.lower() == "n":
            if word == None or len(word) == 0:
                console.print("")
                console.print('Word not selected!', style="red")
            else:
                console.print("")
                print_news_for_the_word(word)

        elif code.lower() == "b":
            if word == None:
                console.print("Word not selected.", style="red")
            elif wordIndex == -1:
                console.print("Word not indexed in the words list.", style="red")
            elif word.lower() not in bookmarkedWords:
                with open(bookmarkedWordsFilename, 'w+') as bookmarkedFile:
                    bookmarkedWords.append(word.lower())
                    bookmarkedFile.write("\n".join(bookmarkedWords))
                    print_word_with_dictionary_and_surfix(False)
            else:
                with open(bookmarkedWordsFilename, 'w+') as bookmarkedFile:
                    bookmarkedWords.remove(word.lower())
                    bookmarkedFile.write("\n".join(bookmarkedWords))
                    print_word_with_dictionary_and_surfix(False)
        elif code.lower() == "r" or len(code) == 0:
            os.system('clear')
            if len(bookmarkedWords)>0 and random.random() < bookmarkedProbability:
                # console.print()
                word = random.choice(bookmarkedWords)
                wordIndex = bookmarkedWords.index(word)
            else:
                wordIndex = random.choice(range(len(words)))
                word = words[wordIndex]
            
            wordsHistory.append(word)
            print_word_with_dictionary_and_surfix()
        else:
            console.print("Unknown action \""+code+"\".", style="red")


if __name__ == "__main__":
    wordee_description = "📖 Wordee, a random word picker with dictionary and news attached."

    googlenews = GoogleNews(lang="en")
    console = Console()
    bookmarked_surfix = "_bookmarked"

    textWrapper = textwrap.TextWrapper(initial_indent=" ", subsequent_indent=" ")
    newsWrapper = textwrap.TextWrapper(width=90, initial_indent=" ", subsequent_indent=" ")
    textWrapperDoubleIndents = textwrap.TextWrapper(initial_indent="    ", subsequent_indent="    ")

    parser = argparse.ArgumentParser(description=wordee_description)

    parser.add_argument("-i", dest="filename", required=True,
                        help="Specify input text file.", metavar="FILE",
                        type=lambda x: is_valid_file(parser, x))

    parser.add_argument("--hide", dest="hideDictionary", action='store_true',
                        help="Hide the dictionary result. Until enter pressed.")

    # parser.add_argument("--phonetic", dest="phonetic", action='store_true',
    #                     help="Play phonetic sound.")

    parser.add_argument("--translate", dest="translateDestination", metavar="LANG",
            help="Translate destination language. For example \"ja\", \"ko\", \"zh-tw\".")

    parser.add_argument("--news", dest="alwaysShowNews", action='store_true',
            help="Always show the news related to the word. Can be a little bit slower.")

    parser.add_argument("--bookmarked", dest="bookmarkedProbability", nargs='?', metavar="FLOAT",
            help="Specify probability to pick next random word from bookmarked list.", const=1, type=float, default=0)

    exitOnCtrlC = False
    wordDictionaryResponseJSONCache = {}
    wordNewsResultsCache = {}

    signal.signal(signal.SIGINT, signal_handler)

    start()
    # print_news_for_the_word_old('Rigor')
    # print_news_for_the_word('Rigor')