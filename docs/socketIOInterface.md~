
# Server

## Broadcast events:
Responses that may be emitted by the server

###### ```updateCanvasGraph```
Emit a json representation of the graph, where the UUID's can be requested later. 
```json
{
  "canvasId": "de305d54-75b4-431b-adb2-eb6b9e546014",
  "timestamp": "2016-03-18T14:02:56.541Z",
  "postits": {
    "23a29456-5ded-4b66-b3f0-178b7afdc0e7": {
      "realX": 10,
      "realY": 10,
      "colour": "red",
      "connections": [
        "36afb67b-c127-4fb8-b795-b917c4099742",
        "3fb558b4-5c5c-42a1-98db-84267c470a47"
      ]
    },
    "36afb67b-c127-4fb8-b795-b917c4099742": {
      "realX": 10,
      "realY": 10,
      "colour": "red",
      "connections": [
        "23a29456-5ded-4b66-b3f0-178b7afdc0e7"
      ]
    }
  }
}
```

## Response events:
Requests that are accepted by the server. Responses will be emitted with the same name eg on ```getPostit``` will also emit ```getPostit```

###### ```getPostit``` 
Requests a postit from it's UUID and canvas UUID.

```json
[
  {
    "canvas": "de305d54-75b4-431b-adb2-eb6b9e546014",
    "id": "23a29456-5ded-4b66-b3f0-178b7afdc0e7"
  },
  ...
]
```

###### ```getCanvas```
Request a canvas from it's uuid. Same data structure as updateCanvasGraph
```json
{
  "id": "de305d54-75b4-431b-adb2-eb6b9e546014",
  "timestamp": "2016-03-18T14:02:56.541Z",
  "postits": {
    "23a29456-5ded-4b66-b3f0-178b7afdc0e7": {
      "realX": 10,
      "realY": 10,
      "colour": "red",
      "connections": [
        "36afb67b-c127-4fb8-b795-b917c4099742",
        "3fb558b4-5c5c-42a1-98db-84267c470a47"
      ]
    },
    "36afb67b-c127-4fb8-b795-b917c4099742": {
      "realX": 10,
      "realY": 10,
      "colour": "red",
      "connections": [
        "23a29456-5ded-4b66-b3f0-178b7afdc0e7"
      ]
    }
  }
}
```

###### ```getSettings```
Request current camera, model and kinect settings

```json
{
  "settingName": {
    "value": "...?",
    "options": [
      "..",
      ".."
    ]
  }
}
```

###### ```setSetting```
Set a setting value (only one)
```json
{
  "key": "value"
}
```

###### ```getCanvasTree```
Return the canvas tree/history
```json
{
  "de305d54-75b4-431b-adb2-eb6b9e546014": {
    "derivedFrom": "401180a8-3d21-419f-a997-eafa68a2d57b",
    "derivedAt": "2016-03-18T15:15:25.972Z",
    "derivedTo": "4484144e-d27f-4345-8713-9f5c9e9e1622"
  }
}
```