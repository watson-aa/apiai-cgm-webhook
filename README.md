# Api.ai - webhook implementation in Python

This is a webhook implementation that gets Api.ai classification JSON (i.e. a JSON output of Api.ai /query endpoint) and returns a fulfillment response.

More info about Api.ai webhooks could be found here:
[Api.ai Webhook](https://docs.api.ai/docs/webhook)

# Deploy to:
[![Deploy to Heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

# What does the service do?
It's a Continuous Glucose Monitor information fulfillment service that uses [Nightscout Web Monitor](https://github.com/nightscout/cgm-remote-monitor).

The service packs the result in the Api.ai webhook-compatible response JSON and returns it to Api.ai.

Requests need to contain a valid CGM URL and an entity to return.  There are multiple entity options:

| entity | purpose | sample response |
|--------|---------|-----------------|
|sgv|Curren sensor glucose value|"Sensor glucose value is currently 201."|
|sgvDir|Current sensor glucose value and direction|"Sensor glucose value is currently 201 and the direction is unknown."|
|sgvToday|Sensor glucose value trends for today|"Today, the lowest sensor glucose value was 174 at 10:40PM, and the highest was 295 at 12:30AM."|
|sgvYesterday|Sensor glucose value trends for yesterday|"Yesterday, the lowest sensor glucose value was 175 at 12:42PM, and the highest was 316 at 06:00PM."|

Sample request:
```json
{
  "id": "a70eb278-5aee-4fc7-bcb2-3b8444b42385",
  "timestamp": "2016-12-23T22:19:42.411Z",
  "result": {
    "source": "agent",
    "resolvedQuery": "What is the current glucose level?",
    "action": "cgm",
    "actionIncomplete": false,
    "parameters": {
      "cgmUrl": "https://my_cgm_server.com/api/v1/entries",
      "entity": "sgvDir"
    },
    "contexts": [

    ],
    "metadata": {
      "intentId": "133cee9a-f62e-44ee-b8f8-d73669b6ab3c",
      "webhookUsed": "true",
      "webhookForSlotFillingUsed": "false",
      "intentName": "current glucose level"
    },
    "fulfillment": {
      "speech": "I'm sorry, Dave. I'm afraid I can't do that.",
      "messages": [
        {
          "type": 0,
          "speech": "I'm sorry, Dave.  I'm afraid I can't do that."
        }
      ]
    },
    "score": 0.63
  },
  "status": {
    "code": 206,
    "errorType": "partial_content",
    "errorDetails": "Webhook call failed. Error message: org.springframework.web.client.HttpServerErrorException: 503 Service Unavailable ErrorId: 60042fca-9622-4e5a-a4d0-340c0f7803f6"
  },
  "sessionId": "23cffb0b-b4a3-44c1-893e-58546bf6cec5"
}
```
