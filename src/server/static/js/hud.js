var hudContext;
var latestCanvas;

var userId;
var sessionId;

var allowDrawCircle = true;

var POSTIT_SIZE = 115;

var OFFSET = POSTIT_SIZE/2;

var virtualPostitImages = {};

$(function() {
    //var hudCanvas = $('.hudCanvas');
    var splash = $('.localStorageUnset');

    if (typeof(Storage) !== 'undefined') {
       userId = localStorage.getItem('userId');
       sessionId = localStorage.getItem('sessionId');
       console.log("userId: " + userId);
       console.log("sessionId: " + sessionId);
       checkCanvasSize();
        if (!userId || !sessionId) {
            console.error('Either userId or sessionId was not set:', userId, sessionId);
        } else {
            hudContext = document.getElementById("hudCanvas").getContext("2d");
            var socket = io();
            splash.hide();

            $(window).on("resize", function(){
               resizeCanvas();
               checkCanvasSize();
            });

            socket.on("body_detected", function(){
                $("#body-detect-indicator").show();
            });

            socket.on("body_not_detected", function(){
                $("#body-detect-indicator").hide();
            });

            socket.on("show_loading", showLoading);

            socket.on("draw_circle", drawCircle);

            socket.on('connect', function() {
                socket.on('get_latest_canvas_by_session', function(canvas) {
                    console.log("HUD initial canvas received");
                    if(canvas == null){
                        console.log("(Received canvas is empty, not calling resizeCanvas() and redrawCanvas())");
                    }
                    else {
                        console.log(canvas);
                        latestCanvas = canvas;

                        //clear virtual postit local cache
                        //get all virtual postits from new canvas and to cache
                        clearStorage(["instanceConfigurationId", "sessionId", "userId"]);
                        virtualPostitImages = {};
                        $.each(latestCanvas.postits, function(index, postit)
                        {
                           if (latestCanvas.physicalFor != userId)
                           {
                               var i = new Image();
                               i.onload = function(evt)
                               {
                                   console.log("       EXPERIMENTAL: drawing virtual " + evt.currentTarget.height + "x" + evt.currentTarget.width + " postit at (" + postit.displayPos.x + "," + postit.displayPos.y + ")");
                                   if (postit.physicalFor == null || postit.physicalFor == "None")
                                   {
                                       //virtual for noone
                                       hudContext.strokeStyle = "#00FF00";
                                   }
                                   else
                                   {
                                       //physical for someone else
                                       hudContext.strokeStyle = "#FF0000";
                                   }
                                   hudContext.strokeWidth = 20;
                                   hudContext.strokeRect(postit.displayPos.x - evt.currentTarget.width/2, postit.displayPos.y - evt.currentTarget.height/2, evt.currentTarget.width, evt.currentTarget.height);
                                   hudContext.drawImage(evt.currentTarget, postit.displayPos.x - evt.currentTarget.width/2, postit.displayPos.y - evt.currentTarget.height/2);
                               }
                               i.src = "/api/postit/" + postit.id;
                               virtualPostitImages[postit.id] = i;
                           }
                        });

                        allowDrawCircle = true;
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

            socket.on("blank_canvas_black", function (instanceConfigurationId) {
                if(instanceConfigurationId == localStorage["instanceConfigurationId"])
                {
                    console.log("received blank_canvas_black message, blacking out canvas");
                    setCanvasBlack();
                    clearCanvas();
                }
                else
                {
                    console.log("received blank_canvas_message, not for this client ("+ localStorage.getItem("instanceConfigurationId") + ") - target: " + instanceConfigurationId);
                }
            });

            socket.on("blank_canvas_white", function (instanceConfigurationId) {
                if(instanceConfigurationId == localStorage["instanceConfigurationId"])
                {
                    console.log("received blank_canvas_white message, whiting out canvas");
                    setCanvasWhite();
                    clearCanvas();
                }
                else
                {
                    console.log("received blank_canvas_message, not for this client ("+ localStorage.getItem("instanceConfigurationId") + ") - target: " + instanceConfigurationId);
                }
            });
        }
    } else {
        console.error('Local Storage Not Available!');
    }
});

function drawCircle(obj) {
    if (allowDrawCircle)
    {
        x = obj.x;
        y = obj.y;
        console.log("received draw_circle: (" + x + ", " + y + ")");
        clearCanvas();
        redrawCanvas();
        hudContext.beginPath();
        hudContext.arc(x, y, POSTIT_SIZE, 0, 2 * Math.PI, false);
        hudContext.fillStyle = 'rgba(0,255,0,0.5)';
        hudContext.fill();
        hudContext.lineWidth = 5;
        hudContext.strokeStyle = '#003300';
        hudContext.stroke();
    }
    else
    {
        console.log("received draw_circle, but ignoring");
    }
}

function checkCanvasSize() {
    if($(window).height() != 1080)
    {
        console.error("Window height " + $(window).height() + " is suboptimal");
    }
    else
    {
        console.log("Window height optimal");
    }

    if($(window).width() != 1920)
    {
        console.error("Window width " + $(window).width() + " is suboptimal");
    }
    else
    {
        console.log("Window width optimal");
    }
}

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
    hideLoading();
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
            hudContext.moveTo(postitIdToCoords[connection.start].x + POSTIT_SIZE/2 - OFFSET, postitIdToCoords[connection.start].y + POSTIT_SIZE/2 - OFFSET);
            hudContext.lineTo(postitIdToCoords[connection.finish].x + POSTIT_SIZE/2 - OFFSET, postitIdToCoords[connection.finish].y + POSTIT_SIZE/2 - OFFSET);
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
                //postit is physical for this user
                hudContext.strokeStyle = "#00FF00";
                hudContext.fillRect(postit.displayPos.x - OFFSET, postit.displayPos.y - OFFSET, POSTIT_SIZE, POSTIT_SIZE);
                hudContext.strokeRect(postit.displayPos.x - OFFSET, postit.displayPos.y - OFFSET, POSTIT_SIZE, POSTIT_SIZE);
            }
            else
            {
                //virtual for all users
                /*postitImage = new Image();
                postitImage.src = "";
                postitImage.onload = function(evt){
                    console.log("       drawing virtual " + evt.currentTarget.height + "x" + evt.currentTarget.width + " postit at (" + postit.displayPos.x + "," + postit.displayPos.y + ")");
                    if (postit.physicalFor == null || postit.physicalFor == "None")
                    {
                        //virtual for noone
                        hudContext.strokeStyle = "#00FF00";
                    }
                    else
                    {
                        //physical for someone else
                        hudContext.strokeStyle = "#FF0000";
                    }
                    hudContext.strokeWidth = 20;
                    hudContext.strokeRect(postit.displayPos.x - evt.currentTarget.width/2, postit.displayPos.y - evt.currentTarget.height/2, evt.currentTarget.width, evt.currentTarget.height);
                    hudContext.drawImage(evt.currentTarget, postit.displayPos.x - evt.currentTarget.width/2, postit.displayPos.y - evt.currentTarget.height/2);
                };*/
                //postitImage.src = "/api/postit/" + postit.id;
                //postitImage.src = "data:image/jpg;base64," + localStorage.getItem(postit.id);
/*
                var currentTarget = virtualPostitImages[postit.id];
                console.log("       drawing virtual " + currentTarget.height + "x" + currentTarget.width + " postit at (" + postit.displayPos.x + "," + postit.displayPos.y + ")");
                if (postit.physicalFor == null || postit.physicalFor == "None")
                {
                    //virtual for noone
                    hudContext.strokeStyle = "#00FF00";
                }
                else
                {
                    //physical for someone else
                    hudContext.strokeStyle = "#FF0000";
                }
                hudContext.strokeWidth = 20;
                hudContext.strokeRect(postit.displayPos.x - currentTarget.width/2, postit.displayPos.y - currentTarget.height/2, currentTarget.width, currentTarget.height);
                hudContext.drawImage(currentTarget, postit.displayPos.x - currentTarget.width/2, postit.displayPos.y - currentTarget.height/2);*/
            }

        });
    }
}

var drawImageOnCanvas = function(image, x, y) {
    console.log("drawImageOnCanvas(): drawing image with size " + image.height + "x" + image.width + " to canvas at (" + x + "," + y + ")");
    hudContext.drawImage(image, x, y);
}

function setCanvasBlack() {
    allowDrawCircle = false;
    console.log("setCanvasBlack(): setting canvas background black");
    $(".hudCanvas").addClass("blackCanvas");
}

function setCanvasWhite() {
    allowDrawCircle = false;
    console.log("setCanvasWhite(): setting canvas background white");
    $(".hudCanvas").removeClass("blackCanvas");
}

function showLoading() {
    allowDrawCircle = false;
    console.log("showLoading(): setting loader show");
    $(".loader").show();
}

function hideLoading() {
    console.log("hideLoading(): setting loader hide");
    $(".loader").hide();
}
