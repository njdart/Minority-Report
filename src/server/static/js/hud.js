var hudContext;
var latestCanvas;

var userId;
var sessionId;

var allowDrawCircle = true;

var handColors = {
    0: {
        "leftFistOpen": "rgba(0,255,0,0.5)",
        "leftFistClosed": "rgba(0,128,0,0.5)",

        "rightFistOpen": "rgba(0,255,0,0.5)",
        "rightFistClosed": "rgba(0,128,0,0.5)"
    },
    1: {
        "leftFistOpen": "rgba(0,0,255,0.5)",
        "leftFistClosed": "rgba(0,0,128,0.5)",

        "rightFistOpen": "rgba(0,0,255,0.5)",
        "rightFistClosed": "rgba(0,0,128,0.5)"
    },
    2: {
        "leftFistOpen": "rgba(255,0,0,0.5)",
        "leftFistClosed": "rgba(128,0,0,0.5)",

        "rightFistOpen": "rgba(255,0,0,0.5)",
        "rightFistClosed": "rgba(128,0,0,0.5)"
    },
    3: {
        "leftFistOpen": "rgba(255,255,0,0.5)",
        "leftFistClosed": "rgba(128,128,0,0.5)",

        "rightFistOpen": "rgba(255,255,0,0.5)",
        "rightFistClosed": "rgba(128,128,0,0.5)"
    },
    4: {
        "leftFistOpen": "rgba(0,255,255,0.5)",
        "leftFistClosed": "rgba(0,128,128,0.5)",

        "rightFistOpen": "rgba(0,255,255,0.5)",
        "rightFistClosed": "rgba(0,128,128,0.5)"
    },
    5: {
        "leftFistOpen": "rgba(255,0,255,0.5)",
        "leftFistClosed": "rgba(128,0,128,0.5)",

        "rightFistOpen": "rgba(255,0,255,0.5)",
        "rightFistClosed": "rgba(128,0,128,0.5)"
    }
};

var STICKY_NOTE_SIZE_M = 0.077; // metres

if (localStorage["stickyNoteSize"] == undefined)
{
    localStorage.setItem("stickyNoteSize", 115);
    localStorage.setItem("stickyNoteOffset", localStorage["stickyNoteSize"] / 2);
}
var stickyNoteSize = localStorage["stickyNoteSize"];
var stickyNoteOffset = localStorage["stickyNoteOffset"];

var virtualStickyNoteImages = {};
var stickyNotesSelected = {};

var FULL_DEBUG_LOGS = false;

function debugLog(msg)
{
    if (FULL_DEBUG_LOGS)
    {
        console.log(msg);
    }
}

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

            socket.on('body_detected', function(configId){
                if(configId == localStorage["instanceConfigurationId"])
                {
                    $("#body-detect-indicator").show();
                }
            });

            socket.on('body_not_detected', function(configId){
                if(configId == localStorage["instanceConfigurationId"])
                {
                    $("#body-detect-indicator").hide();
                }
            });

            socket.on('show_loading', showLoading);

            socket.on('draw_circle', drawCircles);

            socket.on('note_selected', noteSelected);

            socket.on('note_deselected',noteDeselected);

            socket.on('move_sticky_note',noteMoved);

            socket.on('draw_canvas', drawCanvasHandler);

            socket.on("physical_canvas_dimensions", physicalCanvasDimensions);

            socket.on('connect', function() {
                socket.on('get_latest_canvas_by_session', function(canvas) {
                    console.log("canvas received");
                    if(canvas == null){
                        console.log("(Received canvas is empty, not calling resizeCanvas() and redrawCanvas())");
                    }
                    else {
                        debugLog(canvas);
                        latestCanvas = canvas;

                        //clear virtual stickyNote local cache
                        //get all virtual stickyNotes from new canvas and to cache
                        virtualStickyNoteImages = {};
                        $.each(latestCanvas.stickyNotes, function(index, stickyNote)
                        {
                           if (stickyNote.physicalFor != userId)
                           {
                               var i = new Image();
                               i.onload = function(evt)
                               {
                                   debugLog("       EXPERIMENTAL: drawing virtual " + evt.currentTarget.height + "x" + evt.currentTarget.width + " stickyNote at (" + stickyNote.displayPos.x + "," + stickyNote.displayPos.y + ")");
                                   if (stickyNote.physicalFor == null || stickyNote.physicalFor == "None")
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
                                   hudContext.strokeRect(stickyNote.displayPos.x - evt.currentTarget.width/2, stickyNote.displayPos.y - evt.currentTarget.height/2, evt.currentTarget.width, evt.currentTarget.height);
                                   hudContext.drawImage(evt.currentTarget, stickyNote.displayPos.x - evt.currentTarget.width/2, stickyNote.displayPos.y - evt.currentTarget.height/2);
                               }
                               i.src = "/api/stickyNote/" + stickyNote.id;
                               virtualStickyNoteImages[stickyNote.id] = i;
                               stickyNotesSelected[stickyNote.id] = false;
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

function drawCanvasHandler() {
    clearCanvas();
    redrawCanvas();
}

function physicalCanvasDimensions(json) {
    console.log(json);
    if (json.configID == localStorage["instanceConfigurationId"])
    {
        stickyNoteSize = Math.floor((STICKY_NOTE_SIZE_M / json.canvasWidth) * 1920.0);
        stickyNoteOffset = stickyNoteSize / 2;
        localStorage["stickyNoteSize"] = stickyNoteSize;
        localStorage["stickyNoteOffset"] = stickyNoteOffset;
        console.log("received canvas physical size: (" + json.canvasWidth + ", " + json.canvasHeight + ")");
        console.log("set sticky-note pixel width to: " + stickyNoteSize);
        console.log("redrawing");
        clearCanvas();
        redrawCanvas();
    }
}

function drawCircles(handStates) {
    if (allowDrawCircle && handStates.configID == localStorage["instanceConfigurationId"])
    {
        clearCanvas();
        redrawCanvas();
        $.each(handStates.handStates, function (index, state) {
            if (state.leftHandTracked)
            {
                debugLog("received hand state, ID " + state.skeletonID + ": left(" + state.leftHandX + ", " + state.leftHandY + ")");
                hudContext.beginPath();
                hudContext.arc(state.leftHandX, state.leftHandY, 100, 0, 2 * Math.PI, false);
                hudContext.fillStyle = state.leftFistClosed ? handColors[state.skeletonID].leftFistClosed : handColors[state.skeletonID].leftFistOpen;
                hudContext.fill();
                hudContext.lineWidth = 5;
                hudContext.strokeStyle = '#003300';
                hudContext.stroke();
                hudContext.closePath();
            }
            if (state.rightHandTracked)
            {
                debugLog("received hand state, ID " + state.skeletonID + ": right(" + state.rightHandX + ", " + state.rightHandY + ")");
                hudContext.beginPath();
                hudContext.arc(state.rightHandX, state.rightHandY, 100, 0, 2 * Math.PI, false);
                hudContext.fillStyle = state.rightFistClosed ? handColors[state.skeletonID].rightFistClosed : handColors[state.skeletonID].rightFistOpen;
                hudContext.fill();
                hudContext.lineWidth = 5;
                hudContext.strokeStyle = '#003300';
                hudContext.stroke();
                hudContext.closePath();
            }
        });
    }
    else
    {
        debugLog("received hand states, but ignoring");
    }
}

function noteSelected(noteID) {
    console.log("Note selected with ID: " + noteID);
    stickyNotesSelected[noteID] = true;
    clearCanvas();
    redrawCanvas();
}

function noteDeselected(noteID) {
    console.log("Note deselected with ID: " + noteID);
    stickyNotesSelected[noteID] = false;
    clearCanvas();
    redrawCanvas();
}

function noteMoved(noteMoveData) {
    for (var i = 0, len = latestCanvas.stickyNotes.length; i < len; i++)
    {
        if (latestCanvas.stickyNotes[i].id == noteMoveData.noteID)
        {
            latestCanvas.stickyNotes[i].displayPos.x = noteMoveData.handXPos;
            latestCanvas.stickyNotes[i].displayPos.y = noteMoveData.handYPos;
            debugLog("Note moved with ID: " + noteMoveData.noteID);
            break;
        }
    }
    clearCanvas();
    redrawCanvas();
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
    debugLog("resizeCanvas(): resizing canvas");
    hudContext.canvas.height = $(window).height();
    hudContext.canvas.width = $(window).width();
    redrawCanvas(); //should probably be somewhere else, but this works...
}

function clearCanvas(){
    debugLog("clearCanvas(): clearing canvas");
    hudContext.clearRect(0, 0, hudContext.canvas.width, hudContext.canvas.height);
}

function drawCanvasBin()
{
    debugLog("drawCanvasBin(): drawing bin area");
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
    debugLog("redrawCanvas(): redrawing canvas");
    hideLoading();
    drawCanvasBin();

    if (!latestCanvas)
    {
        console.log("No canvas to redraw.");
        return;
    }

    if(latestCanvas.stickyNotes == undefined || latestCanvas.stickyNotes == null)
    {
        console.log("redrawCanvas(): No stickyNotes on canvas");
    }
    else
    {
        debugLog("redrawCanvas(): mapping " + latestCanvas.stickyNotes.length + " stickyNote ids to coords");
        stickyNoteIdToCoords = {};
        $.each(latestCanvas.stickyNotes, function(index, stickyNote)
        {
           stickyNoteIdToCoords[stickyNote.id] = stickyNote.displayPos;
        });
    }

    if(latestCanvas.connections == undefined || latestCanvas.connections == null)
    {
        debugLog("redrawCanvas(): No connections on canvas");
    }
    else
    {
        debugLog("redrawCanvas(): drawing " + latestCanvas.connections.length + " connections");
        $.each(latestCanvas.connections, function(index, connection)
        {
            debugLog("   connection from " + connection.start + " to " + connection.finish);
            hudContext.strokeStyle = "#0000FF";
            hudContext.beginPath();
            hudContext.moveTo(stickyNoteIdToCoords[connection.start].x + stickyNoteSize/2 - stickyNoteOffset, stickyNoteIdToCoords[connection.start].y + stickyNoteSize/2 - stickyNoteOffset);
            hudContext.lineTo(stickyNoteIdToCoords[connection.finish].x + stickyNoteSize/2 - stickyNoteOffset, stickyNoteIdToCoords[connection.finish].y + stickyNoteSize/2 - stickyNoteOffset);
            hudContext.closePath();
            hudContext.stroke();
        });
    }

    if(latestCanvas.stickyNotes != undefined && latestCanvas.stickyNotes != null)
    {
        debugLog("redrawCanvas(): drawing " + latestCanvas.stickyNotes.length + " stickyNotes");
        $.each(latestCanvas.stickyNotes, function (index, stickyNote) {
            debugLog("   stickyNote at (" + stickyNote.displayPos.x + "," + stickyNote.displayPos.y + ")");
            hudContext.fillStyle = "#000000";
            if (stickyNote.physicalFor == userId) {
                //stickyNote is physical for this user
                hudContext.strokeStyle = "#00FF00";
                hudContext.fillRect(stickyNote.displayPos.x - stickyNoteOffset, stickyNote.displayPos.y - stickyNoteOffset, stickyNoteSize, stickyNoteSize);
                hudContext.strokeRect(stickyNote.displayPos.x - stickyNoteOffset, stickyNote.displayPos.y - stickyNoteOffset, stickyNoteSize, stickyNoteSize);
            }
            else
            {
                //virtual for this user
                /*stickyNoteImage = new Image();
                stickyNoteImage.src = "";
                stickyNoteImage.onload = function(evt){
                    console.log("       drawing virtual " + evt.currentTarget.height + "x" + evt.currentTarget.width + " stickyNote at (" + stickyNote.displayPos.x + "," + stickyNote.displayPos.y + ")");
                    if (stickyNote.physicalFor == null || stickyNote.physicalFor == "None")
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
                    hudContext.strokeRect(stickyNote.displayPos.x - evt.currentTarget.width/2, stickyNote.displayPos.y - evt.currentTarget.height/2, evt.currentTarget.width, evt.currentTarget.height);
                    hudContext.drawImage(evt.currentTarget, stickyNote.displayPos.x - evt.currentTarget.width/2, stickyNote.displayPos.y - evt.currentTarget.height/2);
                };*/
                //stickyNoteImage.src = "/api/stickyNote/" + stickyNote.id;
                //stickyNoteImage.src = "data:image/jpg;base64," + localStorage.getItem(stickyNote.id);

                var currentTarget = virtualStickyNoteImages[stickyNote.id];
                debugLog("       drawing virtual " + currentTarget.height + "x" + currentTarget.width + " stickyNote at (" + stickyNote.displayPos.x + "," + stickyNote.displayPos.y + ")");
                if (stickyNote.physicalFor == null || stickyNote.physicalFor == "None")
                {
                    //virtual for noone
                    if (stickyNotesSelected[stickyNote.id] == true)
                    {
                        //sticky note is selected
                        hudContext.strokeStyle = "#0000FF";
                    }
                    else
                    {
                        //sticky note is unselected
                        hudContext.strokeStyle = "#00FF00";
                    }
                }
                else
                {
                    //physical for someone else
                    hudContext.strokeStyle = "#FF0000";
                }
                hudContext.strokeWidth = 20;
                hudContext.strokeRect(stickyNote.displayPos.x - currentTarget.width/2, stickyNote.displayPos.y - currentTarget.height/2, currentTarget.width, currentTarget.height);
                hudContext.drawImage(currentTarget, stickyNote.displayPos.x - currentTarget.width/2, stickyNote.displayPos.y - currentTarget.height/2);
            }

        });
    }
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
