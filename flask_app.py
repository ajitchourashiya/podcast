from flask import Flask, render_template, request, redirect, url_for
from apis import save_transcript_episodes
import json

app = Flask(__name__)

ep_id = ''


@app.route('/')
def index():
    return render_template('index.html', ep_id=ep_id)


def process_summary(episode_id):    
    save_transcript_episodes(episode_id, auto_chapters=True)
    # time.sleep(200)
    return episode_id


@app.route('/summary', methods=['POST'])
def get_summary():
    global ep_id
    episode_id = request.form['episode_id']

    if episode_id:
        ep_id = episode_id
        r = process_summary(episode_id)
        return redirect(url_for('summary_status', res=r))

    return render_template('index.html', error_msg='Please Enter an episode id.')


@app.route('/summary/<res>')
def summary_status(res):
    if res:
        filename = 'data/' + res + '_chapters.json'
        with open(filename, 'r') as f:
            data = json.load(f)

        chapters = data['chapters']
        podcast_title = data['podcast_title']
        episode_title = data['episode_title']
        thumbnail = data['episode_thumbnail']
        full_text = data['full_text']
        link_url = data['link']

        return render_template(
            'summary.html',
            podcast_title=podcast_title,
            episode_title=episode_title,
            thumbnail=thumbnail,
            chapters=chapters,
            full_text=full_text,
            link_url=link_url
        )

    return render_template('status.html')


def get_clean_time(start_ms):
    seconds = int((start_ms / 1000) % 60)
    minutes = int((start_ms / (1000 * 60)) % 60)
    hours = int((start_ms / (1000 * 60 * 60)) % 24)
    if hours > 0:
        start_t = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    else:
        start_t = f"{minutes:02d}:{seconds:02d}"

    return start_t


app.jinja_env.filters['get_clean_time'] = get_clean_time

if __name__ == "__main__":
    app.run(debug=True)
