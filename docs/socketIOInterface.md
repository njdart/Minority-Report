
# Server

## Broadcast events:
Responses that may be emitted by the server

###### ```updateCanvasGraph```
Emit a json representation of the graph, where the UUIDs can be requested later. 
```javascript
{CanvasObject}
```

## Response events:
Requests that are accepted by the server. Responses will be emitted with the same name eg on ```getPostit``` will also emit ```getPostit```

###### ```getPostits``` 
Requests postits from its UUID and canvas UUID:

```javascript
[
  {RequestPostitObject},
  {RequestPostitObject},
  ...
]
```

will return:

```javascript
{
    {RequestPostitObject}: {PostitObject},
    {RequestPostitObject}: {PostitObject},
    ...
}
```
###### ```getCanvas```
Request a canvas from its uuid. Same data structure as updateCanvasGraph

will return:

```javascript
{CanvasObject}
```

###### ```getSettings```
Request current camera, model and kinect settings

```javascript
{SettingsObject}
```

###### ```setSetting```
Set a setting value (only one)
```javascript
{
  "key": "value"
}
```

###### ```getCanvasTree```
Return the canvas tree/history
```javascript
{
  GUID: {
    "derivedFrom": GUID,
    "derivedAt": "YYYY-mm-DDTHH:MM:SS.SSSZ"
  }
}
```

## Definitions
Definitions of above comments

##### ```PostitObject```
```javascript
{
    "id": GUID,
    "realX": int,
    "realY": int,
    "width": int,
    "height": int,
    "colour": string,
    "image": string // represents URL
}
```

##### ```ConnectionObject```
```javascript
{
    "to": GUID,
    "from": GUID,
    "type": string // as of now only "line" supported
}
```

##### ```CanvasObject```
```javascript
{
    "id": GUID,
    "timestamp": "YYYY-mm-DDTHH:MM:SS.SSSZ",
    "width": int,
    "height", int,
    "postits": [
        PostitObject,
        PostitObject,
        ...
    ]
    "connections": [
        ConnectionObject,
        ConnectionObject,
        ...
    ]
}
```

##### ```RequestPostitObject```
```javascript
{
    "canvas": GUID,
    "id": GUID
}
```

##### ```SettingsObject```
```javascript
{
    "settingName": {
      "value": AnyType,
      "allowedValues": {OptionObject}
    }
}
```

##### ```OptionObject```
```javascript
{
    type: extra_type_info
}
```

Values for `type` with `extra_type_info`:
Field
  : Description of field
Radio
  : Options for Radio box
Checkbox
  : Text to display beside checkbox

## Samples
Example JSONs of the requests and responses

###### ```updateCanvasGraph```
Emit a json representation of the graph, where the UUIDs can be requested later. 
```javascript
{
    "id": "de305d54-75b4-431b-adb2-eb6b9e546014",
    "timestamp": "2016-03-18T14:02:56.541Z",
    "width": 3000,
    "height", 1500,
    "postits": [
        {
            "id": "23a29456-5ded-4b66-b3f0-178b7afdc0e7",
            "realX": 10,
            "realY": 10,
            "width": 100,
            "height": 100,
            "colour": "red",
            "image": "/images/23a29456-5ded-4b66-b3f0-178b7afdc0e7"
        },
        {
            "id": "36afb67b-c127-4fb8-b795-b917c4099742",
            "realX": 10,
            "realY": 10,
            "width": 100,
            "height": 100,
            "colour": "red",
            "image": "/images/36afb67b-c127-4fb8-b795-b917c4099742"
        },
        {
            "id": "3fb558b4-5c5c-42a1-98db-84267c470a47",
            "realX": 10,
            "realY": 10,
            "width": 100,
            "height": 100,
            "colour": "green",
            "image": "/images/3fb558b4-5c5c-42a1-98db-84267c470a47"
        }
    ]
    "connections": [
        {
            "to": "3fb558b4-5c5c-42a1-98db-84267c470a47",
            "from": "36afb67b-c127-4fb8-b795-b917c4099742",
            "type": "line"
        },
        {
            "to": "23a29456-5ded-4b66-b3f0-178b7afdc0e7",
            "from": "36afb67b-c127-4fb8-b795-b917c4099742",
            "type": "line"
        }
    ]
}
```

## Response events:
Requests that are accepted by the server. Responses will be emitted with the same name eg on ```getPostit``` will also emit ```getPostit```

###### ```getPostits``` 
Requests postits from its UUID and canvas UUID:

```javascript
[
    {
        "canvas": "de305d54-75b4-431b-adb2-eb6b9e546014",
        "id": "23a29456-5ded-4b66-b3f0-178b7afdc0e7"
    }
]
```

will return:

```javascript
{
    {
        "canvas": "de305d54-75b4-431b-adb2-eb6b9e546014",
        "id": "23a29456-5ded-4b66-b3f0-178b7afdc0e7"
    } :
    {
        "id": "23a29456-5ded-4b66-b3f0-178b7afdc0e7",
        "realX": 10,
        "realY": 10,
        "width": 100,
        "height": 100,
        "colour": "red",
        "image": "/images/23a29456-5ded-4b66-b3f0-178b7afdc0e7"
    }
}
```
###### ```getCanvas```
Request a canvas from its uuid. Same data structure as updateCanvasGraph
```javascript
{
    "id": "de305d54-75b4-431b-adb2-eb6b9e546014",
    "timestamp": "2016-03-18T14:02:56.541Z",
    "width": 3000,
    "height", 1500,
    "postits": [
        {
            "id": "23a29456-5ded-4b66-b3f0-178b7afdc0e7",
            "realX": 10,
            "realY": 10,
            "width": 100,
            "height": 100,
            "colour": "red",
            "image": "/images/23a29456-5ded-4b66-b3f0-178b7afdc0e7"
        },
        {
            "id": "36afb67b-c127-4fb8-b795-b917c4099742",
            "realX": 10,
            "realY": 10,
            "width": 100,
            "height": 100,
            "colour": "red",
            "image": "/images/36afb67b-c127-4fb8-b795-b917c4099742"
        },
        {
            "id": "3fb558b4-5c5c-42a1-98db-84267c470a47",
            "realX": 10,
            "realY": 10,
            "width": 100,
            "height": 100,
            "colour": "green",
            "image": "/images/3fb558b4-5c5c-42a1-98db-84267c470a47"
        }
    ]
    "connections": [
        {
            "to": "3fb558b4-5c5c-42a1-98db-84267c470a47",
            "from": "36afb67b-c127-4fb8-b795-b917c4099742",
            "type": "line"
        },
        {
            "to": "23a29456-5ded-4b66-b3f0-178b7afdc0e7",
            "from": "36afb67b-c127-4fb8-b795-b917c4099742",
            "type": "line"
        }
    ]
}
```

###### ```getCanvasTree```
Return the canvas tree/history
```javascript
{
  "de305d54-75b4-431b-adb2-eb6b9e546014": {
    "derivedFrom": "401180a8-3d21-419f-a997-eafa68a2d57b",
    "derivedAt": "2016-03-18T15:15:25.972Z"
  }
}
```