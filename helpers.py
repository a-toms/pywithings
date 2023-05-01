import os


def load_secrets_into_environment():
    with open('secrets.env', 'r') as f:
        for line in f:
            key, value = line.strip().split('=')
            os.environ[key] = value
