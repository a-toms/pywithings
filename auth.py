import os
import webbrowser

import requests

redirect_uri = "https://tde.is"  # This must match the redirect URI you set in the Withings account webui.  I use tde.is because it's a domain I own.


def authenticate_with_withings():
    # Step: Generate the authorization URL
    auth_url = f"https://account.withings.com/oauth2_user/authorize2?response_type=code" \
               f"&client_id={os.environ['CLIENT_ID']}&scope=user.activity&redirect_uri={redirect_uri}&state=xyz"

    # Step: Open the authorization URL in the user's browser
    webbrowser.open(auth_url)

    # Step: Find the authorization code in the callback URL (code=<AUTH_CODE>), and then paste it into the console.
    auth_code = input(
        "Now, find and enter your authorization code below.\n"
        "This is the code that you will find in the callback URL between 'code=' and '&state'.\n"
        "You must first click to allow the app to access your data.\n "
        "\n> "
    )

    # Step: Exchange the authorization code for an access token.
    url = 'https://wbsapi.withings.net/v2/oauth2'
    data = {
        'action': 'requesttoken',
        'grant_type': 'authorization_code',
        'client_id': os.environ["CLIENT_ID"],
        'client_secret': os.environ["CLIENT_SECRET"],
        'code': auth_code,
        'redirect_uri': redirect_uri,
    }
    token_response = requests.post(url, data=data)

    if token_response.status_code == 200:
        token_data = token_response.json()
        print(f'{token_data = }')
        try:
            access_token = token_data['body']['access_token']
            refresh_token = token_data['body']['refresh_token']
            os.environ["ACCESS_TOKEN"] = access_token
            os.environ["REFRESH_TOKEN"] = refresh_token

            print(
                f"Authentication successful!\nAccess token={access_token}\nRefresh token={refresh_token}.\n"
                f"We added these to your local secrets.env file. You can now access your data with the Withings API."
            )
        except KeyError:
            print(f"Failed to get access token. Error: {token_response.text}")
            return "Authentication failed. Check the console for more details.", 400
    else:
        print(f"Failed to get access token. Error: {token_response.text}")
        return "Authentication failed. Check the console for more details.", 400


def add_client_credentials():
    """
    This function is used to add user API keys to the secrets.env file locally.
    This allows us to avoid re-entering the keys every time we run the script, while still keeping the keys private.
    """
    if os.path.isfile("secrets.env"):
        # Load the environment variables from the secrets.env file
        with open("secrets.env", "r") as f:
            for line in f:
                key, value = line.strip().split("=")
                os.environ[key] = value
        if "CLIENT_ID" in os.environ and "CLIENT_SECRET" in os.environ:
            print("Found CLIENT_ID and CLIENT_SECRET in secrets.env. Using those values.")
        else:
            input_client_details()

    else:
        input_client_details()


def input_client_details():
    CLIENT_ID = input("Please enter your CLIENT_ID (This is found in your Withings developer portal): ")
    CLIENT_SECRET = input("Please enter your CLIENT_SECRET (This is found in your Withings developer portal): ")
    with open("secrets.env", "a") as f:
        f.write(f"CLIENT_ID={CLIENT_ID}\n")
        f.write(f"CLIENT_SECRET={CLIENT_SECRET}\n")
        os.environ["CLIENT_ID"] = CLIENT_ID
        os.environ["CLIENT_SECRET"] = CLIENT_SECRET
        print("We added CLIENT_ID and CLIENT_SECRET to secrets.env locally.")


def write_secrets_to_file():
    """
    We use this function to write the secrets to the secrets.env file.
    This includes overwriting previous secrets.
    """
    with open("secrets.env", "w") as f:
        f.write(f"ACCESS_TOKEN={os.environ['ACCESS_TOKEN']}\n")
        f.write(f"REFRESH_TOKEN={os.environ['REFRESH_TOKEN']}\n")
        f.write(f"CLIENT_ID={os.environ['CLIENT_ID']}\n")
        f.write(f"CLIENT_SECRET={os.environ['CLIENT_SECRET']}\n")


if __name__ == "__main__":
    add_client_credentials()
    authenticate_with_withings()
    write_secrets_to_file()
