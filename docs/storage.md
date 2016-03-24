# Storage

This document details how a canvas is stored in JSON. JSON was used as it is human readable and easy to manipulate if things go wrong. 

We decided to store the whole raw image as a base64 encoded string. Whist this increases storage size, it allows some features:
 - all the data is stored in a single file (ease of transport and modification)
 - reproducibility - as the whole frame and it's transformations to a canvas are stored, reviews and alterations can be carried out after-the-fact

```json
[

    // A frame
    {
        // UUID for the Snapshot
        "uuid": "de305d54-75b4-431b-adb2-eb6b9e546014",

        // The UUID of the canvas this follows from (or null)
        // May be used in future for branching?
        "derivedFrom": "f357862e-14b5-40c3-ae8b-a9460fa5c90d",
        "derivedAt": "2016-03-18T15:15:25.972Z",

        // The size of the extracted canvas used (IE the whiteboard)
        // In Pixels. NOTE: These may not produce a perfect rectangle
        "canvas": {
            "top-left": {
                "x": 10,
                "y": 10,
            },
            
            "top-right": {
                "x": 4150,
                "y": 10
            },
            
            "bottom-left": {
                "x": 10,
                "y": 3110
            },
            
            "bottom-right": {
                "x": 4150,
                "y": 3110
            }
        }

        // Tranformation to apply to the canvas
        // see http://docs.opencv.org/2.4.1/modules/calib3d/doc/camera_calibration_and_3d_reconstruction.html#cv.CalibrateCamera2
        "transformation": [
            [?, 0, ?],
            [0, ?, ?],
            [0, 0, 1]
        ],

        // The canvas picture in base64?
        "pixels": "?",
      
        // Size of the raw image
        "width": 4160,
        "height": 3120,
            

        // A list of postits in the canvas
        "postits": [
            {
                // a colour (could be user defined, friendly colour name or hex)
                "colour": "red",
    
                // A UUID for a postit
                "uuid": "787e2dab-8490-47db-af36-5ce800d902fe",
    
                // Coordinates the postit was found on the canvas
                // Top left of postit bounding box relative to top left of the canvas (not image!)
                "x": 0,
                "y": 0,
    
                // The size of the postit bounding box
                "height": 10,
                "width": 10,
    
                // If the posit was a physical (Not projected) postit or not, if the postit was
                // removed, but not binned then this should be true.
                "isPhysical": true
            },
            ...
        ],
    
        "connections": [
            {
                // Starting coords ( Start and end coords may be unnessecary?)
                "x1": 0,
                "y1": 0,
    
                // Ending coords
                "x2": 100,
                "y2": 100,
    
                // UUID of the "start" postit
                "from": "787e2dab-8490-47db-af36-5ce800d902fe",
    
                // UUID of the "end" postit
                "to": "ca389acc-f180-4007-b46d-420f1eeace25",
    
                // the type of line IE line, arrow, dashed, cardinality
                // may be usefull in future? default should be line
                "type": "line"
            },
            ...
        ]
    }
]
```