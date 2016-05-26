var hudContext;
var latestCanvas;

var userId;
var sessionId;

var POSTIT_SIZE = 100;

$(function() {
    //var hudCanvas = $('.hudCanvas');
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
                    console.log("HUD initial canvas received");
                    if(canvas == null){
                        console.log("(Received canvas is empty, not calling resizeCanvas() and redrawCanvas())");
                    }
                    else {
                        console.log(canvas);
                        latestCanvas = canvas;
                        resizeCanvas();
                    }
                });

                socket.emit('get_latest_canvas_by_session', sessionId);
            });

            socket.on("create_canvas", function(canvas){
                console.log("create_canvas message received");
                if(canvas == null){
                    console.log("(Received canvas is empty, not calling resizeCanvas() and redrawCanvas())");
                }
                else {
                    //console.log(canvas);
                    //latestCanvas = canvas;
                    //resizeCanvas();

                    //create_canvas isn't working properly, so we just use get_latest_canvas_by_session
                    console.log("Requesting latest canvas");
                    socket.emit('get_latest_canvas_by_session', sessionId);
                }
            });
        }
    } else {
        console.error('Local Storage Not Available!');
    }
});


function resizeCanvas() {
    console.log("resizeCanvas(): resizing canvas");
    hudContext.canvas.height = $(window).height();
    hudContext.canvas.width = $(window).width();
    redrawCanvas(); //should probably be somewhere else, but this works...
}

function clearCanvas(){
    console.log("clearCanvas(): clearing canvas");
    hudContext.clearRect(0, 0, hudContext.canvas.width, hudContext.canvas.height);
}

function drawCanvasBin()
{
    console.log("drawCanvasBin(): drawing bin area");
    hudContext.fillStyle = "#333333";
    hudContext.fillRect(0,0,205,205);
    hudContext.fillStyle = "#000000";
    hudContext.fillRect(0,0,200,200);
    drawing = new Image();
    drawing.src = "/static/assets/recycle.png";
    hudContext.drawImage(drawing, 0,0);
}

function redrawCanvas() {
    hudContext.strokeWidth = 10;
    hudContext.lineWidth = 10;
    console.log("redrawCanvas(): redrawing canvas");
    drawCanvasBin();

    if(latestCanvas.postits == undefined || latestCanvas.postits == null)
    {
        console.log("redrawCanvas(): No postits on canvas");
    }
    else
    {
        console.log("redrawCanvas(): mapping " + latestCanvas.postits.length + " postit ids to coords");
        postitIdToCoords = {};
        $.each(latestCanvas.postits, function(index, postit)
        {
           postitIdToCoords[postit.id] = postit.displayPos;
        });
    }

    if(latestCanvas.connections == undefined || latestCanvas.connections == null)
    {
        console.log("redrawCanvas(): No connections on canvas");
    }
    else
    {
        console.log("redrawCanvas(): drawing " + latestCanvas.connections.length + " connections");
        $.each(latestCanvas.connections, function(index, connection)
        {
            console.log("   connection from " + connection.start + " to " + connection.finish);
            hudContext.strokeStyle = "#0000FF";
            hudContext.beginPath();
            hudContext.moveTo(postitIdToCoords[connection.start].x + POSTIT_SIZE/2, postitIdToCoords[connection.start].y + POSTIT_SIZE/2);
            hudContext.lineTo(postitIdToCoords[connection.finish].x + POSTIT_SIZE/2, postitIdToCoords[connection.finish].y + POSTIT_SIZE/2);
            hudContext.closePath();
            hudContext.stroke();
        });
    }

    if(latestCanvas.postits == undefined || latestCanvas.postits == null)
    {
        console.log("redrawCanvas(): No postits on canvas");
    }
    else
    {
        console.log("redrawCanvas(): drawing " + latestCanvas.postits.length + " postits");
        $.each(latestCanvas.postits, function (index, postit) {
            console.log("   postit at (" + postit.displayPos.x + "," + postit.displayPos.y + ")");
            hudContext.fillStyle = "#000000";
            if (postit.physicalFor == userId) {
                hudContext.strokeStyle = "#00FF00";
            }
            else
            {
                hudContext.strokeStyle = "#FFFF00";
            }
            hudContext.fillRect(postit.displayPos.x, postit.displayPos.y, POSTIT_SIZE, POSTIT_SIZE);
            hudContext.strokeRect(postit.displayPos.x, postit.displayPos.y, POSTIT_SIZE, POSTIT_SIZE);
        });
    }
}

function setCanvasBlack() {
    console.log("setCanvasBlack(): setting canvas background black");
    $(".hudCanvas").addClass("blackCanvas");
}

function setCanvasWhite() {
    console.log("setCanvasWhite(): setting canvas background white");
    $(".hudCanvas").removeClass("blackCanvas");
}
