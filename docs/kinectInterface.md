# Kinect communication protocols

## Introduction

This document specifies the protocol by which the KinectClient application shall
communicate with the Minority Report server application.

(I wrote most of this way too formally pls ignore)

## Overview

The data required from the Kinect sensor during normal operation is currently
limited to body tracking data, specifically including the minimum bounding box
of every tracked body and the position and type of gestures performed by tracked
bodies.

Additionally, during calibration of the system, the Kinect sensor shall provide
a colour image within which the outline of the whiteboard (canvas) shall be
detected by the Minority Report application. The coordinates of this outline
shall be sent back to the KinectClient application.

Body tracking data will be communicated using a coordinate system relative to
the canvas.

## Calibration stuff

Kinect application's web server runs on port 8080. Send GET request to `/calibrate`
and you will receive a colour image in PNG format.

Issue a POST request to `/calibrate` with the following JSON as the body:

```
{
	"points": [
		[ int, int ],
		[ int, int ],
		[ int, int ],
		[ int, int ]
	],

	"instanceID": string
}
```

The points array MUST contain four arrays, which MUST contain two integers each. The
scale is pixels.

The response to that POST request will echo the instance ID:

```
{
	"instanceID": string
}
```

Unless you mess up the request, in which case you won't get JSON at all but receive error 200
with some error message as the body.

<del>
### Body data requests

The URL `/kinect/bodyTracking` is the endpoint which KinectClient shall send POST
requests to. A request body shall contain JSON data, and shall take the following
format:

```
{
    "timestamp": Timestamp,

    "bodies": [
        {BoundingBox},
        {BoundingBox},
        ...
    ],

    "gestures": [
        {Gesture},
        {Gesture},
        ...
    ]
}
```

There shall be no minimum for the number of objects held in either the `bodies`
or `gestures` arrays. Additionally, it shall not be required for both arrays to
be present in a single request.

No restriction shall be placed on the frequency of body data requests made by
the KinectClient.

### `Timestamp` object

This is an ISO 8601 compliant string denoting the time at which the request
was made, e.g. `"2016-03-18T14:02:56.541Z"`.

### `BoundingBox` object

```
{
    "bodyIndex": 0,

    "topLeft": {
        "x": 100,
        "y": 100
    },

    "bottomRight": {
        "x": 500,
        "y": 500
    }
}
```

The `bodyIndex` item is a value from 0 - 5 denoting the index of the body as
given by the Kinect sensor API. This would allow for a body to be tracked
across multiple frames.

### `Gesture` object

```
{
    "type": "grab",
    "origin": {
        "x": 100,
        "y": 100
    }
}
```

The gesture types are yet to be determined and shall not be documented in this
document.

### Body data responses

Upon making a POST request to `/kinect/bodyTracking` with data in the format
specified above, the server shall send a response with status code 200 and the
following data:

```
{
    "status": Status,
    "actionRequired": Action
}
```

The `Status` and `Action` objects are strings which will take certain values
(not yet determined).
</del>
