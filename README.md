# Minority Report

## About

This project started as a Year in Industry/gap year project whilst working at [Cambridge Consultants](http://www.cambridgeconsultants.com/). The aim of the project was to reproduce some of the human-computer interactions displayed in the film of the same name. A key problem of many development environments is transferring information from a lo-fidelity physical world where we all interact to a hi-fidelity digital world where many of us work.

### The Problem

> Fidelity
> The degree of exactness with which something is copied or reproduced; Adherence to fact or detail.

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

### Camera

### Server

### Client

### Kinect

### Model

