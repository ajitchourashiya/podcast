import requests
import time
import json
import pprint
from api_secrets import API_KEY_ASSEMBLY_AI, API_KEY_LISTEN_NOTES

upload_endpoint = "https://api.assemblyai.com/v2/upload"
transcript_endpoint = "https://api.assemblyai.com/v2/transcript"


listen_notes_episode_endpoint = "https://listen-api.listennotes.com/api/v2/episodes"
test_endpoint = "https://listen-api.listennotes.com/api/v2/episodes"
listen_notes_headers = {'X-ListenAPI-Key': API_KEY_LISTEN_NOTES}

headers_auth_only = {
    'authorization': API_KEY_ASSEMBLY_AI
}

headers = {
    'authorization': API_KEY_ASSEMBLY_AI,
    'content-type': "application/json"
}

CHUNK_SIZE = 1024 * 1024 * 5  # 5MB


def get_episode_audio_url(episode_id):
    url = listen_notes_episode_endpoint + "/" + episode_id
    response = requests.request('GET', url, headers=listen_notes_headers)
    data = response.json()
    # pprint.pprint(data)

    audio_url = data['audio']
    episode_thumbnail = data['thumbnail']
    podcast_title = data['podcast']['title']
    episode_title = data['title']
    link_url = data['link']
    return audio_url, episode_thumbnail, podcast_title, episode_title, link_url


def upload(filename):
    def read_file(fname):
        with open(fname, 'rb') as f:
            while True:
                data = f.read(CHUNK_SIZE)
                if not data:
                    break
                yield data

    upload_response = requests.post(
        url=upload_endpoint,
        headers=headers_auth_only,
        data=read_file(filename)
    )
    return upload_response.json()['upload_url']


def transcribe(audio_url, auto_chapters=False):
    transcript_request = {
        'audio_url': audio_url,
        'auto_chapters': auto_chapters
    }

    transcript_response = requests.post(
        url=transcript_endpoint,
        json=transcript_request,
        headers=headers
    )

    return transcript_response.json()['id']


def poll(transcript_id):
    polling_endpoint = transcript_endpoint + '/' + transcript_id
    polling_response = requests.get(
        url=polling_endpoint,
        headers=headers
    )
    return polling_response.json()


def get_transcription_result_url(url, auto_chapters):
    transcript_id = transcribe(url, auto_chapters)
    while True:
        data = poll(transcript_id)
        if data['status'] == 'completed':
            return data, None
        elif data['status'] == 'error':
            return data, data['error']

        print('Waiting 60 seconds...')
        time.sleep(60)


def save_transcript(url, title, sentiment_analysis=False):
    data, error = get_transcription_result_url(url, sentiment_analysis)

    if data:
        filename = title + '.txt'
        with open(filename, 'w') as f:
            f.write(data['text'])

        if sentiment_analysis:
            filename = title + '_sentiment.json'
            with open(filename, 'w') as f:
                sentiments = data['sentiment_analysis_results']
                json.dump(sentiments, f, indent=4)
        print('Transcript Saved!')
        return True
    elif error:
        print("Error!! ", error)
        return False


def save_transcript_episodes(episode_id, auto_chapters=False):
    audio_url, episode_thumbnail, podcast_title, episode_title, link_url = get_episode_audio_url(episode_id)
    data, error = get_transcription_result_url(audio_url, auto_chapters)

    # pprint.pprint(data)
    if data:
        filename = episode_id + '.txt'
        with open(filename, 'w') as f:
            f.write(data['text'])

        chapters_filename = 'data/' + episode_id + '_chapters.json'
        with open(chapters_filename, 'w') as f:
            chapters = data['chapters']

            episode_data = {
                'chapters': chapters,
                'episode_thumbnail': episode_thumbnail,
                'episode_title': episode_title,
                'podcast_title': podcast_title,
                'full_text': data['text'],
                'link': link_url
            }
            json.dump(episode_data, f)
            print('Transcript Saved!!')
            return True
    elif error:
        print("Error!! ", error)
        return False


# print(get_episode_audio_url('336ca4734df9473e86f1f938492586b6'))
