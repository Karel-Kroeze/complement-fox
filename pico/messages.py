from http import stream_to_file, request
from i2s_audio import play_wav_file


def fetch_message(id: str) -> None:
    path = f"/sd/{id}.wav"
    url = f"http://fox.home.karel-kroeze.nl/messages/{id}.wav"

    print("=== NEW MESSAGE ===")
    print(url)

    # download message, add to list of messages
    stream_to_file(path, url)
    with open("/sd/messages.txt", mode="a") as f:
        f.write(id + "\n")

    # let c2 know we have received the message
    request(f"http://fox.home.karel-kroeze.nl/message/{id}/received")


def check_new_messages() -> None:
    new_messages = request("http://fox.home.karel-kroeze.nl/new").strip()

    if not new_messages or new_messages == '':
        print("<no new messages>\n")
        return

    for msg in new_messages.split("\n"):
        fetch_message(msg)


def play_new_message() -> None:
    with open("/sd/messages.txt", mode="rt") as f:
        messages: list[str] = f.readlines()

    if len(messages) > 0:
        message = messages.pop(0).strip()
        play_wav_file(f"/sd/{message}.wav")

        # rewrite message list without the played message
        with open("/sd/messages.txt", mode="w") as f:
            for other_message in messages:
                f.write(other_message)

        # let c2 know we have played the message
        request(f"http://fox.home.karel-kroeze.nl/message/{message}/played")


def num_received_messages() -> int:
    with open("/sd/messages.txt", mode="r") as f:
        return len(f.readlines())

