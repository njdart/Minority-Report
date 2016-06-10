# This document describes the database schema and how it is used to store information

## Terminology:
See ```README.md``` in the root of the project for definitions

## Tables

### User

Column | Properties           | Description
-------|----------------------|------------
ID     | Primary Key Not null |
Name   | Not null             | Name of the user

### Session

Column      | Properties           | Description
------------|----------------------|------------
ID          | Primary Key Not null |
Name        | Text Not Null        | A User specified name
Description | Text Not Null        | A User specified description

### Instance Configuration

Column       | Properties                                        | Description
-------------|---------------------------------------------------|------------
id           | Primary Key Not null                              |
sessionId    | Text Not Null, Foreign Key References Session(id) | Relates this instance to a session story
userId       | Text Not Null, Foreign Key References User(id)    | Relates this instance to a user
topLeftX     | Text Not Null                                     | The following Fields describe the projectionable area Within a calibration image, but the image is not stored
topLeftY     | Text Not Null                                     | 
topRightX    | Text Not Null                                     |
topRightY    | Text Not Null                                     |
bottomRightX | Text Not Null                                     |
bottomRightY | Text Not Null                                     |
bottomLeftX  | Text Not Null                                     |
bottomLeftY  | Text Not Null                                     |
cameraHost   | Text Not Null                                     | Connection Properties for a camera
kinectHost   | Text Not Null                                     | Connection Properties for a kinect
cameraPort   | Intege Not Null                                   | Connection Properties for a camera
kinectPort   | Intege Not Null                                   | Connection Properties for a kinect

### Image

### Canvas

### StickyNote

## Connection
