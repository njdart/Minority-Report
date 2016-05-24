var hudContext;

var POSTIT_SIZE = 100;

function resizeCanvas() {
    console.log("resizing")
    hudContext.canvas.height = $(window).height();
    hudContext.canvas.width = $(window).width();
}
var temp;
$(function() {
    var canvas = $('.hudCanvas');
    var splash = $('.localStorageUnset');
    hudContext = document.getElementById("hudCanvas").getContext("2d");
    $(window).on("resize", resizeCanvas);

    if (typeof(Storage) !== 'undefined') {

       var userId = localStorage.getItem('userId');
       var sessionId = localStorage.getItem('sessionId');
       console.log("userId: " + userId);
       console.log("sessionId: " + sessionId);

        if (!userId || !sessionId) {
            console.error('Either userId or sessionId was not set:', userId, sessionId);
        } else {
            var socket = io();
            splash.hide();

            socket.on('connect', function() {
                socket.on('get_latest_canvas_by_session', function(canvas) {
                    console.log(canvas);
                    temp = canvas;
                    resizeCanvas();
                    postitIdToCoords = {};
                    $.each(canvas.postits, function(index, postit){
                       postitIdToCoords[postit.id] = postit.displayPos;
                    });

                    $.each(canvas.connections, function(index, connection)
                    {
                        console.log("from " + connection.start + " to " + connection.stop);
                        hudContext.strokeStyle = "#00FF00";
                        hudContext.lineWidth = 10;
                        hudContext.beginPath();
                        hudContext.moveTo(postitIdToCoords[connection.start].x + POSTIT_SIZE/2, postitIdToCoords[connection.start].y + POSTIT_SIZE/2);
                        hudContext.lineTo(postitIdToCoords[connection.finish].x + POSTIT_SIZE/2, postitIdToCoords[connection.finish].y + POSTIT_SIZE/2);
                        hudContext.closePath();
                        hudContext.stroke();
                    });

                    $.each(canvas.postits, function(index, postit)
                    {
                        console.log(postit.displayPos);
                        hudContext.fillStyle = "#FF0000";
                        hudContext.fillRect(postit.displayPos.x, postit.displayPos.y, POSTIT_SIZE, POSTIT_SIZE);
                    });
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
