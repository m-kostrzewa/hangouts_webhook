# Hangouts webhook

## Reasoning

We wanted to setup a trigger for external services (e.g. slack) for opening a 
hangouts meeting on our conf room PC, which is behind firewall.

## How it works

Uses
* public webhook proxy (using Ultrahook) to circumvent firewall
* Google Chrome browser in debug mode to open arbitrary tabs and eval
JavaScript
* mpg123 to play a sound when the webhook is triggered

# Installation

## Ultrahook

Register a [http://www.ultrahook.com](Ultrahook) account. Then install:

```
gem install ultrahook
```

## Chromote

[Checkout chromote on github](https://github.com/iiSeymour/chromote)

```
pip install chromote
```

## mpg123 (optional)

```
apt-get install mpg123
```

# Deployment

Get ultrahook API key by registering there. Then:

```
echo "api_key: $MY_API_KEY" > ~/.ultrahook
```

Start chrome in debugging mode:

```
google-chrome --remote-debugging-port=9222
```

Then just

```
python hangouts_webhook.py --hangouts_url "https://hanuts.google.com/hangouts/_/comp.com/our_room" 
    --subdomain "operator" --mp3_filepath "./MainScreenTurnOn.mp3" --port 5000 --click_delay 3
```

`--subdomain` is an arbitrary endpoint name for webhook proxy.

# Testing/using

Try POSTing anything to ultrahook endpoint:

```
curl -X POST http://$SUBDOMAIN.$MY_NAMESPACE.ultrahook.com -v
```
where:
* `$SUBDOMAIN` - an endpoint name that you specified when the script.
* `$MY_NAMESPACE` - the thing that was provided during ultrahook account
registration.