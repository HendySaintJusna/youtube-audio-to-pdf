import sys
sys.path.insert(0, 'ebookcreate/packages')
import moviepy.editor
import speech_recognition as sr 
from fpdf import FPDF
import os 
from pydub import AudioSegment
from pydub.silence import split_on_silence
import random
from yt_dlp import YoutubeDL
import string




sentences = []

try:
	link = input("Write the youtube link : ")
	ydl_opts = {'outtmpl': './medias/video.mp4'}
	with YoutubeDL(ydl_opts) as ydl:
		ydl.download(link)
except:
	print("ERROR : There is a problem with the copied link")



video = moviepy.editor.VideoFileClip("./medias/video.mp4")
audio = video.audio
letters = string.ascii_lowercase
audio_name = ''.join(random.choice(letters) for i in range(10)) + '.wav'
audio.write_audiofile("./medias/"+audio_name)




# create a speech recognition object
r = sr.Recognizer()

# a function to recognize speech in the audio file
# so that we don't repeat ourselves in in other functions
def transcribe_audio(path):
    # use the audio file as the audio source
    with sr.AudioFile(path) as source:
        audio_listened = r.record(source)
        # try converting it to text
        text = r.recognize_google(audio_listened)
    return text

# a function that splits the audio file into chunks on silence
# and applies speech recognition
def get_large_audio_transcription_on_silence(path):
    """Splitting the large audio file into chunks
    and apply speech recognition on each of these chunks"""
    # open the audio file using pydub
    sound = AudioSegment.from_file(path)  
    # split audio sound where silence is 500 miliseconds or more and get chunks
    chunks = split_on_silence(sound,
        # experiment with this value for your target audio file
        min_silence_len = 500,
        # adjust this per requirement
        silence_thresh = sound.dBFS-14,
        # keep the silence for 1 second, adjustable as well
        keep_silence=500,
    )
    folder_name = "audio-chunks"
    # create a directory to store the audio chunks
    if not os.path.isdir(folder_name):
        os.mkdir(folder_name)
    whole_text = ""
    # process each chunk 
    for i, audio_chunk in enumerate(chunks, start=1):
        # export audio chunk and save it in
        # the `folder_name` directory.
        chunk_filename = os.path.join(folder_name, f"chunk{i}.wav")
        audio_chunk.export(chunk_filename, format="wav")
        # recognize the chunk
        try:
            text = transcribe_audio(chunk_filename)
        except sr.UnknownValueError as e:
            print("Error:", str(e))
        else:
            text = f"{text.capitalize()}. "
            print("Sentence added:", text)
            sentences.append(text)
            whole_text += text
    # return the text for all chunks detected
    return whole_text


print("PLEASE, WAIT UNTIL ALL SENTENCES HAVE BEEN ADDED IN THE PDF...")
alltext = get_large_audio_transcription_on_silence('./medias/'+audio_name)
words = alltext.split()
with open('./medias/text.txt', 'w') as f:
	count_words = 0
	for word in words:
		if count_words < 16:
			f.write(word+" ")
			count_words+=1
		else:
			f.write("\n")
			count_words = 0


#Build PDF
pdf = FPDF()
ln_number = round(len(alltext.split())/15)
pdf.add_page()
pdf.set_font("Arial", size = 10)
f = open("./medias/text.txt", "r")
all_folder_file_pdf = os.listdir('./pdf') 
for x in f:
    pdf.cell(200, 10, txt = x, ln = ln_number, align = 'C')

pdfname = (len(all_folder_file_pdf))+1
pdf.output("./pdf/transcription_"+str(pdfname)+".pdf")  

#delete materials
video.close()
f.close()
os.remove('./medias/'+audio_name)
os.remove('./medias/video.mp4')
os.remove('./medias/text.txt')
all_folder_file_chunk = os.listdir('./audio-chunks')
for x in all_folder_file_chunk:
	if ".wav" in x:
		os.remove('./audio-chunks/'+x)

print("ALL SENTENCES HAVE BEEN ADDED. GO LOOK IN THE PDF FOLDER!")