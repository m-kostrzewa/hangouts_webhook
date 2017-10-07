# coding: utf8

# ^ we need this encoding because javascript payload needs to handle Polish
# chrome settings

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from chromote import Chromote
import subprocess
import time
import argparse

parser = argparse.ArgumentParser(description="Joins Hangouts meeting upon "
                                             "recieving POST request")
parser.add_argument('--hangouts_url', type=str,
                    help='hangouts URL')
parser.add_argument('--subdomain', type=str, default="operator",
                    help='arbitrary ultrahook subdomain')
parser.add_argument('--mp3_filepath', type=str, default="MainScreenTurnOn.mp3",
                    help='mp3 sound to play when triggered')
parser.add_argument('--port', type=int, default=5000,
                    help='listen port')
parser.add_argument('--click_delay', type=int, default=3,
                    help='Hangouts join button click delay [seconds]')
args = parser.parse_args()

# I'm bad at JS. This is based on:
# http://userscripts-mirror.org/scripts/review/161893
# https://codepen.io/svinkle/pen/wqchm
CLICK_JOIN_BUTTON_JS = """
var buttons = document.querySelectorAll('div[role="button"]');
var join_btn = Object.values(buttons).filter(function(x) { 
    return x.innerText == "Dołącz" || x.innerText == "Join"
})[0];
function simulateMouseEvent(node, eventType) {
    var event = node.ownerDocument.createEvent("MouseEvents");
    event.initMouseEvent(eventType,
        true, // can bubble
        true, // cancellable
        node.ownerDocument.defaultView,
        1, // clicks
        50, 50, // screen coordinates
        50, 50, // client coordinates
        false, false, false, false, // control/alt/shift/meta
        0, // button,
        node
    );
    node.dispatchEvent(event);
}
function simulateClick(node) {
    simulateMouseEvent(node, 'mousedown');
    simulateMouseEvent(node, 'mouseup');
}
simulateClick(join_btn);
"""


def main():
    try:
        run_webhook_proxy()
        server = HTTPServer(('', args.port), WebhookReceiver)
        server.serve_forever()
    except KeyboardInterrupt:
        server.socket.close()


def run_webhook_proxy():
    # Assumes that ~/.ultrahook contains:
    # "api_key: $YOUR_ULTRAHOOK_API_KEY"
    subprocess.Popen("ultrahook {} {}".format(args.subdomain, args.port),
                      shell=True)
    # btw dunno why this doesn't work:
    #subprocess.Popen(["ultrahook", args.subdomain, str(args.port)],
    #                 shell=True)


class AlreadyInHangoutsException(Exception):
    pass


class WebhookReceiver(BaseHTTPRequestHandler):

    def do_POST(self):
        try:
            t = get_tab()
            play_join_sound()
            navigate_to_hangouts(t)
            time.sleep(args.click_delay)
            join_hangouts_meeting(t)
        except AlreadyInHangoutsException:
            pass
        finally:
            self.send_response(200)

def play_join_sound():
    try:
        subprocess.Popen(['mpg123', '-q', args.mp3_filepath])
    except:
        # oh noes, no sound will play :'( but let's continue
        pass

def get_tab():
    chrome = Chromote()
    for t in chrome.tabs:
        if t.url == args.hangouts_url:
            print("Already in hangouts session")
            raise AlreadyInHangoutsException
    return chrome.tabs[0]

def navigate_to_hangouts(t):
    t.set_url(args.hangouts_url)

def join_hangouts_meeting(t):
    t.evaluate(CLICK_JOIN_BUTTON_JS)

if __name__ == '__main__':
    main()
