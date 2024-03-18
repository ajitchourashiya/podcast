import json

def summary_status(res):
    if res:
        filename = 'data/' + res + '_chapters.json'
        with open(filename, 'r') as f:
            data = json.load(f)

        chapters = data['chapters']
    
    return chapters

text = ''

print(' '.join([chapter['summary'] for chapter in summary_status('f34b30955229494a8745841798162f37')]))