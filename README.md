# Minority Report

## Rationale

This project started as a Year in Industry/gap year project whilst working at [Cambridge Consultants](http://www.cambridgeconsultants.com/). The aim of the project was to reproduce some of the human-computer interactions displayed in the film of the same name. A large amount of work done for technical (and non-technical) projects takes the form of sessions, discussions, planning and problem discovery on whiteboards. Whilst great for getting information out of our heads and disseminated, and providing a versatile medium for displaying and discussing problems, they can often get neglected or overlooked primarily due to their lack of easy replication.

This project aims to build a *proof-of-concept* demonstration of how a whiteboard could be captured, stored and manipulated with simple equipment and a interactions. 

### The Problem

We live in a physical word where we can see, touch and interact with the things around us. However, more and more design and planning is performed digitally, allowing us to save copies, branch, merge and distribute at the click of a button. This is beneficial for spreading information and asking the what-if questions while avoiding messy, unorganised data, but leads to a disconnect; interacting with the work can become difficult.

Sticky notes are a great way of organising and accumulating pieces of information, and when combined with a white board, they create an effective way for many forms of diagrams, graphs and interactions to be detailed in a way that is both easy to interact with and easy to understand. However, this information is often left to collect dust in the form of photographs, with the original board cleaned and re-purposed.

Digital solutions such as smart boards offer a way of more conveniently storing and replicating the data, at the expense of ease-of-use and interactivity (often in the form of missing or unavailable features). Combined with a highly technical world in which many of us live -- developing complex software, hardware, launching rockets and curing diseases -- these hurdles often mean that the digital solutions either require us to adapt to them or simply do not fit at all due to the technical nature of the content.

![Visualising the digital world](https://github.com/njdart/Minority-Report/raw/master/docs/res/understandingDigitalWorld.jpg)
 
### The Solution

The ideal solution would be to not change the way we work; use whiteboards and sticky notes, with pens, diagrams, graphs, keys, etc. and have the outcome represented by a computer while the user interacts with the digitisation process as little as possible.

Enter Minority Report. The ultimate goal of this ambitious project is to engineer a software tool which allows automatic and seamless digitisation of information created collaboratively in the physical world.

### TODO:

See issues
 
### Definitions

- A ```Session``` is a story or unique instance under which white boards, images and stickyNotes belong, a session has a name and a description
- A ```User``` is a person/location which can manipulate a session
- An ```Instance Configuration``` is a collection of setup-specific information, such as camera and kinect host/ports, and a definition of where within a series of images the projectable area lies
- A ```Canvas``` is a point in history along a ```Sessions``` story which relates to a session
- A ```StickyNote``` is either a physical, projected or user-defined location within a image, after it has undergone an instance configuration transformation and crop
- An ```Image``` is an image taken by a camera which will have applied to it an instance configuration transformation 
- A ```Connection``` is between two stickyNotes, containing line information such as type.
 
## Structure

### Inputs

#### Camera

Hosts images taken by the camera, which are used to capture the sticky notes and their connections.

#### Kinect

Hosts images from the Kinect camera, alerts server when board is obstructed and sends data on the location of human hands.

#### Server



#### Model



#### HUD



## How To Use

### Equipment

- A smartphone capable of 4k image capture
- A 1080p projector 
- A computer able to connect to the projector to display the HUD
- Microsoft Kinect 2
- Computer capable of using the Kinect
- Computer capable of running the server
- Whiteboard
- High saturation sticky-note
- Black board marker
- Tripod with grip to hold phone

### Setup

- Set projector facing whiteboard
- Set camera and Kinect to also face the whiteboard such that the projectable area can be seen by both 
- Run the Kinect client on the Kinect computer, with the Kinect attatched
- Run simple HTTP camera on phone
- Run minority_report.py on the server computer
- Go to [server IP]:8088/debug in a web browser
- Create a User and Session
- Create Instance Configuration with User, Session, Camera and Kinect host
- Go to [Server IP]:8080 on HUD computer and login as user to the session
- Select HUD and then make the window fullscreen on the projector
- From the debug screen select calibrate next to the instance configuration
- The system should now be ready for capturing the whiteboard

### Interactions

- A red square appears in the top right corner of the HUD when the Kinect can see an obstruction in front of the board
- When the obstruction is cleared the HUD will blank allowing the camera to take a clear picture of the board
- Sticky notes and connections can be added by the user at any time, but will only be capture when the user moves aside
- Connections are digitally indicated as a blue line
- Sticky notes:
    * A green box projected around them when they are physically on the board for the current user
    * A digital representation with a red border is projected when the note is physical on the board of another user connected to the same session
    * A digital representation with a green border is projected then the note in not physical for any user
- A sticky note when move on the board should automatically have its connections move 
- A stcky note that has been removed or falls off the board will be replaced by a digital representation.
- The Kinect can track the user's hands, diplaying them as circles
- By closing your hand while over a purely digital note, the note can be selected and moved around
- The area in the top left corner is a recycling bin, a sticky note placed here, physically or digitally, will be removed 