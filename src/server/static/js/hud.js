var hudContext;
var latestCanvas;

var userId;
var sessionId;

var POSTIT_SIZE = 100;

function resizeCanvas() {
    console.log("resizing");
    hudContext.canvas.height = $(window).height();
    hudContext.canvas.width = $(window).width();
}

function drawCanvasBin()
{
    hudContext.fillStyle = "#333333";
    hudContext.fillRect(0,0,205,205);
    hudContext.fillStyle = "#000000";
    hudContext.fillRect(0,0,200,200);
    drawing = new Image();
    drawing.src = "/static/assets/recycle.png";
    hudContext.drawImage(drawing, 0,0);
}

function redrawCanvas() {
    drawCanvasBin();
    postitIdToCoords = {};
    $.each(latestCanvas.postits, function(index, postit){
       postitIdToCoords[postit.id] = postit.displayPos;
    });

    $.each(latestCanvas.connections, function(index, connection)
    {
        console.log("from " + connection.start + " to " + connection.stop);
        hudContext.strokeStyle = "#0000FF";
        hudContext.lineWidth = 10;
        hudContext.beginPath();
        hudContext.moveTo(postitIdToCoords[connection.start].x + POSTIT_SIZE/2, postitIdToCoords[connection.start].y + POSTIT_SIZE/2);
        hudContext.lineTo(postitIdToCoords[connection.finish].x + POSTIT_SIZE/2, postitIdToCoords[connection.finish].y + POSTIT_SIZE/2);
        hudContext.closePath();
        hudContext.stroke();
    });

    $.each(latestCanvas.postits, function(index, postit)
    {
        console.log(postit.displayPos);
        if(postit.physicalFor == userId)
        {
            hudContext.fillStyle = "#00FF00";
        }
        else
        {
            hudContext.fillStyle = "#FFFF00";
        }

        hudContext.fillRect(postit.displayPos.x, postit.displayPos.y, POSTIT_SIZE, POSTIT_SIZE);
    });
}
$(function() {
    var canvas = $('.hudCanvas');
    var splash = $('.localStorageUnset');

    if (typeof(Storage) !== 'undefined') {

       userId = localStorage.getItem('userId');
       sessionId = localStorage.getItem('sessionId');
       console.log("userId: " + userId);
       console.log("sessionId: " + sessionId);

        if (!userId || !sessionId) {
            console.error('Either userId or sessionId was not set:', userId, sessionId);
        } else {
             hudContext = document.getElementById("hudCanvas").getContext("2d");
            $(window).on("resize", resizeCanvas);
            var socket = io();
            splash.hide();

            socket.on('connect', function() {
                socket.on('get_latest_canvas_by_session', function(canvas) {
                    console.log("New Canvas Received");
                    console.log(canvas);
                    latestCanvas = canvas;
                    resizeCanvas();
                    redrawCanvas();
                });

                socket.emit('get_latest_canvas_by_session', sessionId);
            });

        }
    } else {
        console.error('Local Storage Not Available!');
    }
});

function setCanvasBlack() {
    $(".hudCanvas").addClass("blackCanvas");
}

function setCanvasWhite() {
    $(".hudCanvas").removeClass("blackCanvas");
}
