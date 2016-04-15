var socket = io();

var POSTIT_SIZE = 100;


socket.on("getAll", processResponse);
socket.emit("getAll", []);


var hudContext;
var displayHeight;
var displayWidth;
var scaleFactor;

var latestReceived;

var idToPostitCoords = {}

$(function()
{
  //setup canvas in window
  hudContext = document.getElementById("hudCanvas").getContext("2d");
  resetCanvasSize();
});

function processResponse(received)
{
  latestReceived = received;
  console.log(latestReceived, "\n");
  idToPostitCoords = {};

  mapPostits();


  drawPostits();

  drawConnections();

 /* $.each(idToPostitCoords, function(id, coords)
  {
    console.log(id, coords["x"], coords["y"]);
    console.log(coords);
  });*/
  
  console.log("FINISHED");
  
}

function drawPostits()
{
  $.each(latestReceived.postits, function(_, p){
    hudContext.fillStyle = p.colour;
    //hudContext.stroke();
    hudContext.fillRect(idToPostitCoords[p.postitId]["y"], idToPostitCoords[p.postitId]["x"], POSTIT_SIZE, POSTIT_SIZE);
  });
}

function drawConnections()
{
  $.each(latestReceived.connections, function(postitId1, conns)
  {
    $.each(conns, function(_, postitId2)
    {
      console.log(postitId1, postitId2);
      hudContext.lineWidth = 5;
      hudContext.strokeStyle = "#000000";
      hudContext.moveTo(idToPostitCoords[postitId1]["y"] + POSTIT_SIZE/2, idToPostitCoords[postitId1]["x"] + POSTIT_SIZE/2);
      hudContext.lineTo(idToPostitCoords[postitId2]["y"] + POSTIT_SIZE/2, idToPostitCoords[postitId2]["x"] + POSTIT_SIZE/2);
      hudContext.stroke();
    });
  });
}

function mapPostits()
{
  idToPostitCoords = {};
  $.each(latestReceived.postits, function(_, p){
    sX = (p.realX/displayWidth)*scaleFactor;
    sY = (p.realY/displayHeight)*scaleFactor;
    idToPostitCoords[p.postitId] = {"x":sX, "y":sY};
  });
}

function resetCanvasSize()
{
  displayHeight = $(window).innerHeight()-21;
  displayWidth = $(window).innerWidth()-21;
  scaleFactor = Math.min(displayWidth, displayHeight);

  hudContext.canvas.height = displayHeight;
  hudContext.canvas.width = displayWidth;
  console.log("displayWidth: " + displayWidth);
  console.log("displayHeight: " + displayHeight);
  console.log("SF: " + scaleFactor);
}

$(window).resize(function() {
  resetCanvasSize()
  for (var i = 0; i < latestReceived.postits.length; i++)
  {
    drawPostit(latestReceived.postits[i]);
  }
});
