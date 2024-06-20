import streamlit as st
import assemblyai as aai
import requests
import os
import tempfile
import re
import json

# AssemblyAI API key
aai.settings.api_key = "b5b3e501c6284d9dad9190aca9a4bc15"

def upload_file_to_assemblyai(file_path):
    headers = {'authorization': aai.settings.api_key}
    response = requests.post('https://api.assemblyai.com/v2/upload',
                             headers=headers,
                             files={'file': open(file_path, 'rb')})
    return response.json()['upload_url']

def transcribe_file(file_url):
    config = aai.TranscriptionConfig(
        word_boost=["Robert Bonsall", "Harpaul", "Schumb", "Stromgren", "CCW", "Shourbaji", "James Neidig", "Neidig"],
        boost_param="default",
        speaker_labels=True,
        disfluencies=True,
    )
    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe(file_url, config=config)
    return transcript

def save_plain_transcript(transcript):
    return "\n".join([f"{utt.speaker.strip()}: {utt.text.strip()}" for utt in transcript.utterances])

def handle_upload_and_transcription(file):
    file_id = f"{file.name}_{file.size}"
    transcript_cache_path = f"transcript_cache_{file_id}.json"

    if os.path.exists(transcript_cache_path):
        st.write("Found existing transcript. Loading...")
        with open(transcript_cache_path, 'r') as cache_file:
            cached_data = json.load(cache_file)
        return cached_data['temp_file_path'], cached_data['plain_transcript']

    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.name)[1]) as temp_file:
        temp_file.write(file.getbuffer())
        temp_file_path = temp_file.name

    st.write("Uploading the file to AssemblyAI...")
    file_url = upload_file_to_assemblyai(temp_file_path)
    st.write("File uploaded successfully!")
    
    st.write("Transcribing the file...")
    transcript = transcribe_file(file_url)
    st.write("Transcription completed!")
    
    plain_transcript = save_plain_transcript(transcript)

    with open(transcript_cache_path, 'w') as cache_file:
        json.dump({
            'temp_file_path': temp_file_path,
            'plain_transcript': plain_transcript
        }, cache_file)
    
    return temp_file_path, plain_transcript

def format_transcript_to_ascii(input_text):
    lines_per_page = 28
    max_line_length = 57
    formatted_lines = []
    line_number = 1

    def format_line(number, content, is_speaker):
        if number <= 9:
            number_str = f" {number}"
        else:
            number_str = f"{number}"
        
        spacing = "             " if is_speaker else "   "
        return f"{number_str}{spacing}{content}"

    for line in input_text.split('\n'):
        words = line.split()
        current_line = ""
        is_speaker_line = True
        is_first_word = True

        for word in words:
            if len(current_line) + len(word) + (5 if is_first_word and is_speaker_line else 1) > max_line_length:
                formatted_line = format_line(line_number, current_line.strip(), is_speaker_line)
                formatted_lines.append(formatted_line)
                current_line = word
                line_number += 1
                is_speaker_line = False
                is_first_word = True
                if line_number > lines_per_page:
                    formatted_lines.append("\f\n\n\n")
                    line_number = 1
            else:
                if current_line:
                    if is_first_word and is_speaker_line:
                        current_line += "     "  # 5 spaces between speaker and first word
                    else:
                        current_line += " "
                current_line += word
                is_first_word = False

        if current_line:  # Add any remaining text in the current line
            formatted_line = format_line(line_number, current_line.strip(), is_speaker_line)
            formatted_lines.append(formatted_line)
            line_number += 1
            if line_number > lines_per_page:
                formatted_lines.append("\f\n\n\n")
                line_number = 1

    return "\n".join(formatted_lines)

# Streamlit Interface
st.title("Enhanced Transcription and Formatting Service")

uploaded_file = st.file_uploader("Upload an audio or video file", type=["mp3", "m4a", "wav", "mp4", "mpeg", "avi", "mov"])

if uploaded_file is not None:
    with st.spinner('Processing...'):
        temp_file_path, initial_transcript = handle_upload_and_transcription(uploaded_file)
    
    st.success("Transcription completed!")

    # Media player
    st.subheader("Media Player")
    file_extension = os.path.splitext(uploaded_file.name)[1].lower()
    
    if file_extension in ['.mp3', '.wav', '.m4a']:
        st.audio(temp_file_path)
    elif file_extension in ['.mp4', '.avi', '.mov', '.mpeg']:
        st.video(temp_file_path)
    else:
        st.write("Unsupported media format for playback in browser.")

    # Find and Replace
    st.subheader("Find and Replace")
    find_text = st.text_input("Find:")
    replace_text = st.text_input("Replace with:")
    
    # Editable transcript
    st.subheader("Edit Transcript")
    edited_transcript = st.text_area("Edit the transcript below:", value=initial_transcript, height=300)

    if st.button("Apply Find and Replace"):
        edited_transcript = re.sub(re.escape(find_text), replace_text, edited_transcript, flags=re.IGNORECASE)
        st.text_area("Updated Transcript:", value=edited_transcript, height=300)

    if st.button("Format Transcript"):
        formatted_transcript = format_transcript_to_ascii(edited_transcript)

        st.subheader("Formatted Transcript")
        st.text_area("Formatted ASCII Transcript:", value=formatted_transcript, height=300)

        st.download_button(
            label="Download Formatted Transcript",
            data=formatted_transcript,
            file_name="formatted_transcript.txt",
            mime="text/plain"
        )

    # Note: We're not deleting the temp file here to allow for transcript caching