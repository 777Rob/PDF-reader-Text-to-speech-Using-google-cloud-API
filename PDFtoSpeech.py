import os
import re
from pydub import AudioSegment
"""
IMPORT YOU GOOGLE_APPLICATION_CREDENTIALS !!!!
It's crucial for program to work properly :)
Some times faces issues merging audiofiles!! 
"""
os.environ[
    "GOOGLE_APPLICATION_CREDENTIALS"] = r"PATH TO YOUR GOOGLE APPLICATION CREDENTIALS"


def clear_text(text):
    text = text.lower()
    text = re.sub(r'[^\x00-\x7f]',r'', text)
    return text


def combine_audio(audio_files, output_file):
    """
    Combines multiple audio files into one audio file
    Needs to be completed!!!!! 
    :param audio_files: list of audio files
    :param output_file: output file
    :return:
    """
    # create a list of audio segments
    audio_segments = []
    for audio_file in audio_files:
        audio_segments.append(AudioSegment.from_file(audio_file))

    # combine the audio segments
    combined = audio_segments[0]
    for i in range(1, len(audio_segments)):
        combined = combined.append(audio_segments[i], crossfade=100)

    # save the audio
    combined.export(output_file, format='mp3')


def read_pdf(file_name):
    """
    This function takes in a pdf file and returns a text file
    """
    import PyPDF2

    pdf_file = open(file_name, 'rb')
    pdf_reader = PyPDF2.PdfFileReader(pdf_file)
    pdf_text = ''

    for page in range(pdf_reader.numPages):
        page_object = pdf_reader.getPage(page)
        page_text = page_object.extractText()
        pdf_text += clear_text(page_text)

    create_dir(re.sub(r"\.pdf$", "", file_name))

    with open(re.sub(r"\.pdf$", "", file_name) + "_full.txt", "w", encoding="utf-8") as f:
        f.write(pdf_text)
        f.close()

    return


def create_dir(dir_name):
    if not os.path.exists(dir_name):
        os.mkdir(dir_name)
    os.chdir(dir_name)


def split_text(file_name):
    """
        Split text in to 5000 character chunks
        """
    with open(re.sub(r"\.pdf$", "", file_name) + "_full.txt", "r", encoding="utf-8") as f:
        full_text = f.read()
        text_list = []

        for i in range(0, len(full_text), 5000):
            text_list.append(full_text[i:i + 5000])

            part_name = re.sub(r"\.pdf$", "", file_name) + f"_{i}.txt"
            with open(part_name, "w", encoding="utf-8") as f2:
                f2.write(full_text[i:i + 5000])
                f2.close()

        f.close()
    return text_list


def synthesize_text(text, i):
    """Synthesizes speech from the input string of text."""
    from google.cloud import texttospeech

    success = False
    while not success:
        try:
            client = texttospeech.TextToSpeechClient()

            input_text = texttospeech.SynthesisInput(text=text)

            # Note: the voice can also be specified by name.
             # Names of voices can be retrieved with client.list_voices().
            # noinspection PyTypeChecker
            voice = texttospeech.VoiceSelectionParams(
                name="en-US-Wavenet-I",
                language_code="en-US",
                ssml_gender=texttospeech.SsmlVoiceGender.MALE,
                )

            # noinspection PyTypeChecker
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3
            )

            response = client.synthesize_speech(
                 request={"input": input_text, "voice": voice, "audio_config": audio_config}
            )

            # The response's audio_content is binary.
            with open(f"output{i}.mp3", "wb") as out:
                out.write(response.audio_content)
                print(f'Audio content written to file "output{i}.mp3"')
            success = True
            return response.audio_content
        except:
            print("Call failed!")
            success = False


def read_text(file_name):
    with open(file_name, "r", encoding="utf-8") as f:
        return f.read()


if __name__ == '__main__':

    file_name = input("Enter the file name:")
    audio_files = []
    read_pdf(file_name)
    text_list = split_text(file_name)
    for i in range(len(text_list)):
        text = text_list[i]
        audio_files.append(synthesize_text(text, i))
    combine_audio(audio_files, "Full.mp3") 
    
