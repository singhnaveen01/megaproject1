import speech_recognition as sr
import webbrowser
import pyttsx3
import openai
import os
import pygame
import logging
import pywhatkit
import requests
from gtts import gTTS
import musiclibrary  # Ensure this is a real file/dictionary

# OpenAI API Key
openai.api_key = "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"

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("jarvis.log"),
        logging.StreamHandler()
    ]
)

# Text-to-Speech using gTTS + pygame
def speak(text):
    try:
        logging.info(f"Speaking: {text}")
        tts = gTTS(text)
        tts.save('temp.mp3')
        pygame.mixer.init()
        pygame.mixer.music.load('temp.mp3')
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            continue
        pygame.mixer.music.unload()
        os.remove("temp.mp3")
    except Exception as e:
        logging.error(f"TTS failed: {e}")

# AI response using OpenAI
def aiprocess(command):
    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a virtual assistant named Jarvis. Answer briefly and helpfully"},
                {"role": "user", "content": command}
            ]
        )
        response = completion.choices[0].message.content
        logging.info(f"OpenAI response: {response}")
        return response
    except Exception as e:
        logging.error(f"OpenAI processing error: {e}")
        return "I'm sorry, I couldn't connect to OpenAI."

# Get news headlines
def get_news():
    api_key = "adbd1016e2044e8eb822aedeb976ddac"
    url = f"https://newsapi.org/v2/top-headlines?country=in&apiKey={api_key}"
    response = requests.get(url).json()

    if not response.get("articles"):
        url = f"https://newsapi.org/v2/everything?q=India&sortBy=publishedAt&language=en&apiKey={api_key}"
        response = requests.get(url).json()

    articles = response.get("articles", [])[:5]
    if not articles:
        return "Sorry, no news articles found."

    headlines = [article["title"] for article in articles]
    return ". ".join(headlines)

# Get weather report
import requests
import logging

def get_weather(city="Jaipur"):
    api_key = "ed78b1b3108add54e00f20b2a04ba510"  # Replace with your actual API key

    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        logging.info(f"Requesting weather for {city}")
        
        response = requests.get(url)
        data = response.json()

        # Check if API response was successful
        if data.get("cod") != 200:
            error_message = data.get("message", "Unknown error.")
            logging.warning(f"Weather API error: {error_message}")
            return f"Could not retrieve weather for '{city}': {error_message}"

        # Extract weather data
        temp = data["main"]["temp"]
        description = data["weather"][0]["description"].capitalize()
        humidity = data["main"]["humidity"]
        wind_speed = data["wind"]["speed"]

        # Format the weather report
        report = (
            f"The weather in {city} is currently {description}. "
            f"The temperature is {temp}°C, humidity is {humidity}%, "
            f"and wind speed is {wind_speed} meters per second."
        )

        logging.info(f"Weather data retrieved: {report}")
        return report

    except Exception as e:
        logging.error(f"Exception in get_weather: {e}")
        return "Sorry, I couldn't get the weather information right now."


# Process commands
def processCommand(c):
    try:
        c = c.lower()
        if "open google" in c:
            webbrowser.open("https://google.com")
        elif "open facebook" in c:
            webbrowser.open("https://facebook.com")
        elif "open linkedin" in c:
            webbrowser.open("https://linkedin.com")
        elif "open youtube" in c:
            webbrowser.open("https://youtube.com")
        elif "give me the news" in c:
            speak("Here are the top news headlines:")
            news = get_news()
            speak(news)
        elif "weather" in c:
            words = c.split()
            if "in" in words:
                city_index = words.index("in") + 1
                city = words[city_index] if city_index < len(words) else "Jaipur"
            else:
                city = "Jaipur"
            weather_report = get_weather(city)
            speak(weather_report)
        elif c.startswith("play music") or c.startswith("play song"):
            song_name = c.replace("play music", "").replace("play song", "").strip()
            speak(f"Playing {song_name} on YouTube.")
            pywhatkit.playonyt(song_name)
        else:
            output = aiprocess(c)
            speak(output)
    except Exception as e:
        logging.error(f"Command processing failed: {e}")
        speak("Something went wrong while processing the command.")

# Main execution
if __name__ == "__main__":
    speak("Initializing Jarvis...")
    logging.info("Jarvis started.")

    while True:
        try:
            recognizer = sr.Recognizer()
            with sr.Microphone() as source:
                logging.info("Listening for wake word...")
                recognizer.adjust_for_ambient_noise(source, duration=1)
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)

            try:
                word = recognizer.recognize_google(audio, language="en-US").lower()
                logging.info(f"Heard: {word}")

                if "jarvis" in word:
                    speak("Hello sir, how can I help you?")

                    try:
                        with sr.Microphone() as source:
                            logging.info("Listening for your command now...")
                            recognizer.adjust_for_ambient_noise(source, duration=1)
                            audio = recognizer.listen(source, timeout=8, phrase_time_limit=6)

                        try:
                            command = recognizer.recognize_google(audio, language="en-US")
                            logging.info(f"Command: {command}")
                            processCommand(command)

                        except sr.UnknownValueError:
                            logging.warning("Sorry, I couldn't understand what you said.")
                            speak("Sorry, I didn't catch that.")
                        except sr.RequestError as e:
                            logging.error(f"Google Speech API error: {e}")
                            speak("There was an error with speech recognition.")

                    except Exception as e:
                        logging.error(f"Failed to capture command: {e}")
                        speak("I had trouble hearing your command.")

            except sr.UnknownValueError:
                logging.warning("Wake word not recognized.")
            except sr.RequestError as e:
                logging.error(f"Speech Recognition API error: {e}")

        except Exception as e:
            logging.error(f"Unexpected error: {e}")


# import speech_recognition as sr
# import webbrowser
# import pyttsx3
# import openai
# import os
# import openai


# openai.api_key = "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"
# import pygame
# import os
# import logging
# import pywhatkit
# import requests
# from gtts import gTTS
# import musiclibrary  # Ensure this is a real file/dictionary

# #  Logging setup
# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s - %(levelname)s - %(message)s",
#     handlers=[
#         logging.FileHandler("jarvis.log"),
#         logging.StreamHandler()
#     ]
# )

# #  Text-to-Speech using gTTS + pygame
# def speak(text):
#     try:
#         logging.info(f"Speaking: {text}")
#         tts = gTTS(text)
#         tts.save('temp.mp3')
#         pygame.mixer.init()
#         pygame.mixer.music.load('temp.mp3')
#         pygame.mixer.music.play()
#         while pygame.mixer.music.get_busy():
#             continue
#         pygame.mixer.music.unload()
#         os.remove("temp.mp3")
#     except Exception as e:
#         logging.error(f"TTS failed: {e}")

# #  AI response using OpenAI
# def aiprocess(command):
#     try:
#         openai.api_key = "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"
#         completion = openai.ChatCompletion.create(
#             model="gpt-3.5-turbo",
#             messages=[
#                 {"role": "system", "content": "You are a virtual assistant named Jarvis. Answer briefly and helpfully."},
#                 {"role": "user", "content": command}
#             ]
#         )
#         response = completion.choices[0].message.content
#         logging.info(f"OpenAI response: {response}")
#         return response
#     except Exception as e:
#         logging.error(f"OpenAI processing error: {e}")
#         return "I'm sorry, I couldn't connect to OpenAI."
# def get_news():
#     api_key = "adbd1016e2044e8eb822aedeb976ddac"
    
#     # Try top headlines from India
#     url = f"https://newsapi.org/v2/top-headlines?country=in&apiKey={api_key}"
#     response = requests.get(url).json()

#     # If empty, try everything search
#     if not response.get("articles"):
#         url = f"https://newsapi.org/v2/everything?q=India&sortBy=publishedAt&language=en&apiKey={api_key}"
#         response = requests.get(url).json()

#     articles = response.get("articles", [])[:5]
#     if not articles:
#         return "Sorry, no news articles found."

#     headlines = [article["title"] for article in articles]
#     return ". ".join(headlines)#  Handle commands
# import requests

# def get_weather(city="Jaipur"):
#     api_key = "ed78b1b3108add54e00f20b2a04ba510" 

#     try:
#         url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
#         response = requests.get(url)
#         data = response.json()

#         if data["cod"] != 200:
#             return f"City '{city}' not found or invalid API key."

#         temp = data["main"]["temp"]
#         description = data["weather"][0]["description"]
#         humidity = data["main"]["humidity"]
#         wind = data["wind"]["speed"]

#         report = (
#             f"The weather in {city} is {description}. "
#             f"The temperature is {temp}°C, humidity is {humidity}%, "
#             f"and wind speed is {wind} meters per second."
#         )
#         return report

#     except Exception as e:
#         return f"Error retrieving weather data: {e}"

# def processCommand(c):
#     try:
#         c = c.lower()
#         if "open google" in c:
#             webbrowser.open("https://google.com")
#         elif "open facebook" in c:
#             webbrowser.open("https://facebook.com")
#         elif "open linkedin" in c:
#             webbrowser.open("https://linkedin.com")
#         elif "open youtube" in c:
#             webbrowser.open("https://youtube.com")
#         elif " give me the news" in c:
#             speak("Here are the top news headlines:")
#             news = get_news()
#             speak(news)
#         elif "weather" in c.lower():
#     # Try to extract city name
#            words = c.lower().split()
#            if "in" in words:
#             city_index = words.index("in") + 1
#            if city_index < len(words):
#             city = words[city_index]
#            else:
#             city = "Jaipur"
#         else:
#          city = "Jaipur"  # Default city

#         weather_report = get_weather(city)
#         speak(weather_report)


#        elif c.startswith("play music") or c.startswith("play song"):
#           song_name = c.replace("play music", "").replace("play song", "").strip()
#           speak(f"Playing {song_name} on YouTube.")
#           pywhatkit.playonyt(song_name)
#           else:
#             output = aiprocess(c)
#             speak(output)
#     except Exception as e:
#         logging.error(f"Command processing failed: {e}")
#         speak("Something went wrong while processing the command.")

# #  Main execution
# if __name__ == "__main__":
#     speak("Initializing Jarvis...")
#     logging.info("Jarvis started.")

#     while True:
#         try:
#             recognizer = sr.Recognizer()
#             with sr.Microphone() as source:
#                 logging.info("Listening for wake word...")
#                 recognizer.adjust_for_ambient_noise(source, duration=1)
#                 audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)

#             try:
#                 word = recognizer.recognize_google(audio, language="en-US").lower()
#                 logging.info(f"Heard: {word}")
#                 if "jarvis" in word:
#                     speak("Hello sir, how can I help you?")
#                     with sr.Microphone() as source:
#                         logging.info("Listening for command...")
#                         recognizer.adjust_for_ambient_noise(source)
#                         audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
#                     command = recognizer.recognize_google(audio, language="en-US")
#                     logging.info(f"Command: {command}")
#                     processCommand(command)

#             except sr.UnknownValueError:
#                 logging.warning("Speech not recognized.")
#             except sr.RequestError as e:
#                 logging.error(f"Speech Recognition API error: {e}")

#         except Exception as e:
#             logging.error(f"Unexpected error: {e}")


# # import speech_recognition as sr
# # import webbrowser
# # import pyttsx3
# # import openai
# # import pygame
# # import os 
# # import logging

# # import musiclibrary
# # from gtts import gTTS
# # logging.basicConfig(
# #     level=logging.INFO,
# #     format="%(asctime)s - %(levelname)s - %(message)s",
# #     handlers=[
# #         logging.FileHandler("jarvis.log"),
# #         logging.StreamHandler()
# #     ]
# # )



# # # pip install pocketsphinx

# # recognizer=sr.Recognizer()
# # engine= pyttsx3.init()
# # def speak(text):
# #     engine.say(text)
# #     engine.runAndWait()
# # def speak(text):
   
# #     tts = gTTS(text)
# #     tts.save('temp.mp3')

# # # Initialize pygame mixer
# #     pygame.mixer.init()

# # # Load your mp3 file
# #     pygame.mixer.music.load('temp.mp3')

# # # Play the file
# #     pygame.mixer.music.play()

# #   # Keep the program running until the music finishes
# #     while pygame.mixer.music.get_busy():
# #       continue
# #     pygame.mixer.music.unload()
# #     os.remove("temp.mp3")
# #   #  except Exception as e;
# #   #   logging.error(f"TTS failed:{e}")

               

# # def aiprocess(command):
# #    client = OpenAI(api_key="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",
# #    )

# #    completion= client.chat.completion.create(
# #     model = "gpt-3.5-turbo",
# #     messages=[
# #         { "role":"system","content":"you are a vitrtual assistent named jarvvis skilled in general task like alexa and google,give short response"},
# #         {"role":"user","content":command}
# #     ]
# # )
   
# #    response = completion.choices[0].message.content
# #    logging.info(f"OpenAI response: {response}")
# #    return response
# #    except Exception as e:
# #       logging.error(f"OpenAI processing error: {e}")
# #       return "I'm sorry, I couldn't connect to OpenAI."
# # def processCommand(c):
# #     if "open google" in c.lower():
# #       webbrowser.open("https://google.com")
# #     elif "open facebook" in c.lower():
# #       webbrowser.open("https://facebook.com")
# #     elif "open linkdin" in c.lower():
# #       webbrowser.open("https://linkdin.com")
# #     elif "open youtube" in c.lower():
# #       webbrowser.open("https://youtube.com")
# #     elif c.lower().startswith("play"):
# #        song=c.lower().split(" ")[1]
# #        link =musiclibrary.music[song]
       
# #        if link:
# #                 webbrowser.open(link)
# #        else:
# #                 speak("Sorry, I couldn't find that song.")
# #     # elif "news" c.lower()
# #     else:
# #        output=aiprocess(c)
# #        speak(output)
# #     except Exception as e:
# #         logging.error(f"Command processing failed: {e}")
# #         speak("Something went wrong while processing the command.")

# #       #  let open ai to handle the request
# # if __name__ == "__main__":
# #     speak("initializing Jarvis.....")
# # while True:
# #     # listen for the wake word "jarvis"
# #     # obtain audio from the microphone
    
   
# #     try:
# #         r = sr.Recognizer()
    

# #         print("recognizing....")
# #         with sr.Microphone() as source:
# #            logging.info("Listening for the wake word…")
# #            r.adjust_for_ambient_noise(source, duration=1)
# #            audio = r.listen(source, timeout=5, phrase_time_limit=5)
# #         try:
# #             word = r.recognize_google(audio, language="en-US").lower()
# #             print("Heard:", word)

# #         if  "jarvis" in word:
# #             speak("Hello sir, how can I help you?")
# #             with sr.Microphone() as source:
# #                logging.info("jarvis activated..")
# #                recognizer.adjust_for_ambient_noise(source)
# #                audio = r.listen(source, timeout=2, phrase_time_limit=1)

# #             command = r.recognize_google(audio, language="en-US")
# #             logging.info("Command:", command)
# #             processCommand(command)

# #     except sr.UnknownValueError:
# #                 logging.warning("Speech not recognized.")
# #     except sr.RequestError as e:
# #                 logging.error(f"Speech Recognition API error: {e}")
# #     except Exception as e:
# #             logging.error(f"Unexpected error: {e}")
