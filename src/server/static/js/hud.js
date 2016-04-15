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
  console.log(received, "\n");
  idToPostitCoords = {};

  for (var i = 0; i < received.postits.length; i++) {
    //console.log(received.postits[i]);
    drawPostit(received.postits[i]);
  }

  for (var j = 0; j < received.connections.length; j++) {
    var conn = received.connections[j];
    //console.log(conn);
    //drawConnection(conn)
  }

  $.each(received.connections, function(id1, conns)
  {
    $.each(conns, function(_, id2)
    {
      //console.log("links: ", id1, id2);
      drawConnection(idToPostitCoords[id1], idToPostitCoords[id2]);
    });
  });

 /* $.each(idToPostitCoords, function(id, coords)
  {
    console.log(id, coords["x"], coords["y"]);
    console.log(coords);
  });*/
  
  console.log("FINISHED");
  
}

function drawPostit(p)
{
  sX = (p.realX/displayWidth)*scaleFactor;
  sY = (p.realY/displayHeight)*scaleFactor;
  hudContext.fillStyle = p.colour;
  //hudContext.rect(sY, sX, POSTIT_SIZE, POSTIT_SIZE)
  //console.log("Coords - x: " + sX + ", y: " + sY);
  hudContext.stroke();
  hudContext.fillRect(sY, sX, POSTIT_SIZE, POSTIT_SIZE);
  idToPostitCoords[p.postitId] = {"x":sX, "y":sY};
}

function drawConnection(postitCoords1, postitCoords2)
{
  console.log(postitCoords1, postitCoords2);
  hudContext.lineWidth = 5;
  hudContext.moveTo(postitCoords1["y"] + POSTIT_SIZE/2, postitCoords1["x"] + POSTIT_SIZE/2);
  hudContext.lineTo(postitCoords2["y"] + POSTIT_SIZE/2, postitCoords2["x"] + POSTIT_SIZE/2);
  hudContext.stroke();
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
