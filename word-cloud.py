import os
import json
import string
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS
from pathlib import Path
from IPython.display import clear_output


def prepare_data(path):
    """
    Find and processes message files and return a dictionary in the form:
    'user_messages[user_fullname]: (number_of_messages, all_messages_combined)'    

    path: a path to directories exported from Facebook
    """

    # Create a list with the paths to the message files
    json_files = []
    for file_path in Path(path).rglob('message_*.json'):
        json_files.append(file_path)

    # Create a dictionary to return   
    user_messages = {}
    n = len(json_files)
    i = 0
    for json_file in json_files:
        with open(json_file) as f:
            data = json.load(f)
        for message in data['messages']:
            if 'content' in message.keys():
                user = message['sender_name'].encode('latin_1').decode('utf-8')
                content = message['content'].encode('latin_1').decode('utf-8')
                if user in user_messages.keys():
                    user_messages[user][0] += 1
                    user_messages[user][1] += ' ' + content
                else:
                    user_messages[user] = [1, content]
        # Print the number of analyzed files and the work progress
        i += 1
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f'Number of analyzed files: {n}')
        print('Progress: ' + '{:.0%}'.format(i / n))

    return user_messages


def get_user(user_messages):
    """
    Display users with the most activity and get and return the full username.

    user_messages: a dictionary in a specific form
    """

    # Make a list with user activity
    user_activity = []
    for k, v in user_messages.items():
        user_activity.append((k, v[0]))
    user_activity.sort(reverse=True, key=lambda x: x[1])

    # Display the 10 users with the most activity
    print('\n10 most active users:')
    i = 1
    for user, n in user_activity:
        print(f'[{i}] {user} - {n} messages')
        if i == 10:
            break
        i += 1

        # Get the user's fullname or position in the most activity list
    while True:
        print(f'\nEnter any full username (example: {user_activity[0][0]}) or type one of the numbers listed above.')
        print('Type \'q\' for quit')
        input_user = input()

        if input_user == 'q':
            break

        if input_user in user_messages.keys():
            return input_user

        try:
            user = user_activity[int(input_user) - 1][0]
        except:
            pass
        else:
            return user

        print("Wrong user.")


def prepare_text(user_messages, user):
    """
    Prepare user messages to create a word cloud.

    user_messages: a dictionary in a specific form
    user: a fullname of user
    """

    text = user_messages[user][1]
    # Remove punctuation marks
    text = text.translate(str.maketrans('', '', string.punctuation))

    tokens = text.lower().split()
    for token in tokens:
        # Remove https links
        if 'https' in token or len(token) == 1:
            tokens.remove(token)
    text = " ".join(tokens)

    return text


def make_wordcloud(text, user, use_stopwords=True):
    """
    Create a word cloud and save it to a file.

    text: prepared text for analysis
    user: a fullname of user
    use_stopwords: True for stopwords use 
    """
    if use_stopwords:
        # Use the default stopwords list from the library
        stopwords = set(STOPWORDS)
        # Use the user's stopwords file if it exists
        if os.path.exists('my-stopwords.txt'):
            with open('my-stopwords.txt') as f:
                my_stopwords = set(f.read().split("\n"))
            stopwords = stopwords.union(my_stopwords)

    wordcloud = WordCloud(width=800, height=800,
                          background_color='white',
                          stopwords=stopwords,
                          min_font_size=10).generate(text)

    # Plot and save a word cloud image                      
    plt.figure(figsize=(8, 8), facecolor=None)
    plt.imshow(wordcloud)
    plt.axis("off")
    plt.tight_layout(pad=0)
    plt.savefig(f'word-clouds/word-cloud-{user.replace(" ", "_").lower()}.png')


def main():
    user_messages = prepare_data('data')
    user = get_user(user_messages)
    if user:
        print(f'\nPlease wait a while, the word cloud for {user} is being generated…')
        text = prepare_text(user_messages, user)
        make_wordcloud(text, user)
        print(f'\nWord cloud for {user} successfully generated.')

main()