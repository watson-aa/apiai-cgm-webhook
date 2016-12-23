# Api.ai - webhook implementation in Python

This is a really simple webhook implementation that gets Api.ai classification JSON (i.e. a JSON output of Api.ai /query endpoint) and returns a fulfillment response.

More info about Api.ai webhooks could be found here:
[Api.ai Webhook](https://docs.api.ai/docs/webhook)

# Deploy to:
[![Deploy to Heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

# What does the service do?
It's a Continuous Glucose Monitor information fulfillment service that uses [Nightscout Web Monitor](https://github.com/nightscout/cgm-remote-monitor).

The service packs the result in the Api.ai webhook-compatible response JSON and returns it to Api.ai.

