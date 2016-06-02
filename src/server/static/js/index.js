var pointCanvas;
var pointCanvasContext;
var stage;
var kinectStage;

var kinectImage;

var CANVAS_IMAGE_SCALE_FACTOR = 0.05;
$(function() {
    $('#loginModal').modal({
        keyboard: false,
        backdrop: 'static',
        show: true
    });

    stage = new createjs.Stage("rawPointRedefineCanvas");
    kinectStage = new createjs.Stage("rawPointKinectRedefineCanvas");

    $('#loginModal').on('hidden.bs.modal', function (e) {
        socket.emit('get_latest_image_id_by_instance_configuration',  localStorage["instanceConfigurationId"]);
    })

    /*$('#imageModal').on('show.bs.modal', function (e) {
        setTimeout(function(){
            ctx = document.getElementById("rawPointRedefineCanvas").getContext("2d");
            ctx.canvas.width = document.getElementById("canvasBackgroundRaw").clientWidth;
            ctx.canvas.height = document.getElementById("canvasBackgroundRaw").height;
            updateRawImage();
        }, 300);
    });*/

    var socket = io(),
        image,
        canvas,
        postits = []

    var RAW_IMAGE_PREFIX = "/api/image/";
    var KINECT_RAW_IMAGE_PREFIX = "http://10.0.0.2:8081/calibrate";
    var latestRawId = "";


    canvasImage = "http://i.huffpost.com/gen/1975176/images/o-SLEEPY-CAT-WATERMELON-facebook.jpg";

    socket.on("get_latest_image_id_by_instance_configuration", function (imageId) {
        latestRawId = imageId;
        updateRawImage();

        updateKinectRawImage();
        //other image updates here?
    });


    function updateRawImage()
    {
        $("#currentRaw").attr("src", RAW_IMAGE_PREFIX + latestRawId);
        //$("#canvasBackgroundRaw").attr("src", RAW_IMAGE_PREFIX + latestRawId);

        pointCanvas = document.getElementById("rawPointRedefineCanvas");
        pointCanvasContext = pointCanvas.getContext("2d");

        var img = new Image;

        img.onload = loadImgToStage;

        function loadImgToStage(event) {
            var image = event.target;
            var bitmap = new createjs.Bitmap(image);
            bitmap.cache(0,0,image.width,image.height, CANVAS_IMAGE_SCALE_FACTOR);
            var scaledBitmap = new createjs.Bitmap(bitmap.cacheCanvas);
            stage.addChild(scaledBitmap);
            stage.update();
        }

        img.src = RAW_IMAGE_PREFIX + latestRawId;
    }

    //socket.on('get_kinect_image_url', function (url) {
    //    $("#currentKinectRaw").attr("src", KINECT_RAW_IMAGE_PREFIX);
    //});

    function updateKinectRawImage()
    {
        $("#currentKinectRaw").attr("src", KINECT_RAW_IMAGE_PREFIX);
        var img = new Image();
        img.onload = loadImgToKinectStage;

        function loadImgToKinectStage(event) {
            var image = event.target;
            var bitmap = new createjs.Bitmap(image);
            bitmap.cache(0,0,image.width,image.height, CANVAS_IMAGE_SCALE_FACTOR);
            var scaledBitmap = new createjs.Bitmap(bitmap.cacheCanvas);
            kinectStage.addChild(scaledBitmap);
            kinectStage.update();
        }

        img.src = KINECT_RAW_IMAGE_PREFIX;
    }

    socket.on('get_users', function(users) {
        console.log(users)
        $('.usersList-user').remove();
        users.forEach(function(user) {
            $('.usersList')
                .append($('<option class="usersList-user"></option>')
                    .attr('value', user.id)
                    .text(user.name))
        })
    });
    socket.on('get_sessions', function(sessions) {
        console.log(sessions)
        $('.sessionsList-session').remove();
        sessions.forEach(function(session) {
            $('.sessionsList')
                .append($('<option class="sessionsList-session"></option>')
                    .attr('value', session.id)
                    .text(session.name))
        })
    });
    socket.on('get_instance_configurations', function(instanceConfigurations) {
        console.log(instanceConfigurations)
        $('.instanceConfigurationsList-instanceConfiguration').remove();
        instanceConfigurations.forEach(function(instanceConfiguration) {
            $('.instanceConfigurationsList')
                .append($('<option class="instanceConfigurationsList-instanceConfiguration"></option>')
                    .attr('value', instanceConfiguration.id)
                    .text(instanceConfiguration.id))
        })
    });

    socket.emit('get_users')
    socket.emit('get_sessions')
    socket.emit('get_instance_configurations');



    function updateCanvas() {
        canvasImage = canvas.last().id;
    }

    function updatePostits() {
        canvasImage = postits.last().id;
    }

    socket.on('getImages', function(data) {
        console.log('getImages', arguments);
        imageId = data;
        updateImages();
    });

    socket.on('getCanvases', function(data) {
        console.log('getCanavses', arguments);
        canvas = data;
        updateCanvas();
    });

    socket.on('getPostits', function(data) {
        console.log('getPostits', arguments);
        postits = data;
        updatePostits();
    });

    var setupPointCanvas = true;
    $("#editCanvasBtn").on("click", function() {

        console.log('#editCanvasBtn Click');
        //socket.emit('getImages');

        //adds the correct image
        //$("#modalImage").attr("src", RAW_IMAGE_PREFIX + latestRawId);
        if(setupPointCanvas)
        {
            setupPointCanvas = false;
            //remove draggable from image
            $("img").on("dragstart", function (event) {
                event.preventDefault();
            });

            // draggable canvas objects
            stage.mouseMoveOutside = true;

            var topLeft = new createjs.Shape(),
                topRight = new createjs.Shape(),
                botLeft = new createjs.Shape(),
                botRight = new createjs.Shape();

            //topLeft.graphics.beginFill("red").drawCircle(0, 0, 5);
            var lSize = 7;
            topLeft.graphics.beginStroke("red").lt(0,lSize).lt(0,0).lt(lSize,0);
            topRight.graphics.beginStroke("red").lt(-lSize,0).lt(0,0).lt(0,lSize);
            botLeft.graphics.beginStroke("red").lt(0,-lSize).lt(0,0).lt(lSize,0);
            botRight.graphics.beginStroke("red").lt(0,-lSize).lt(0,0).lt(-lSize,0);

            var topLeftDragger = new createjs.Container(),
                topRightDragger = new createjs.Container(),
                botLeftDragger = new createjs.Container(),
                botRightDragger = new createjs.Container();

            var addChildren = function () {
                topLeftDragger.name = "topLeft";
                topRightDragger.name = "topRight";
                botLeftDragger.name = "botLeft";
                botRightDragger.name = "botRight";
                topLeftDragger.addChild(topLeft);
                topRightDragger.addChild(topRight);
                botLeftDragger.addChild(botLeft);
                botRightDragger.addChild(botRight);
                stage.addChild(topLeftDragger);
                stage.addChild(topRightDragger);
                stage.addChild(botLeftDragger);
                stage.addChild(botRightDragger);
            };

            var createLines = function () {
                var c = $("#rawPointRedefineCanvas")[0];
                var ctx = c.getContext("2d");
                ctx.beginPath();
                ctx.moveTo(x1, y1);
                ctx.lineTo(x2, y1);
                ctx.lineTo(x2, y2);
                ctx.lineTo(x1, y2);
                ctx.lineTo(x1, y1);
            };

            var setCornerPositions = function () {
                addChildren();
                topLeftDragger.x = x1;
                topLeftDragger.y = y1;
                topRightDragger.x = x2;
                topRightDragger.y = y1;
                botLeftDragger.x = x1;
                botLeftDragger.y = y2;
                botRightDragger.x = x2;
                botRightDragger.y = y2;
            };

            var x1 = 20,
                x2 = 40,
                y1 = 20,
                y2 = 40;

            setCornerPositions();

            topLeftDragger.on("pressmove", function (evt) {
                evt.currentTarget.x = evt.stageX;
                evt.currentTarget.y = evt.stageY;
                stage.update();
                createLines(20, 20, 40, 60);
            });

            topRightDragger.on("pressmove", function (evt) {
                evt.currentTarget.x = evt.stageX;
                evt.currentTarget.y = evt.stageY;
                stage.update();
                //createLines()
            });

            botLeftDragger.on("pressmove", function (evt) {
                evt.currentTarget.x = evt.stageX;
                evt.currentTarget.y = evt.stageY;
                stage.update();
                //console.log("bottomLeftDrag", this.id);
            });

            botRightDragger.on("pressmove", function (evt) {
                evt.currentTarget.x = evt.stageX;
                evt.currentTarget.y = evt.stageY;
                stage.update();
                //console.log("bottomRightDragger", this.id);
            });
        }

        stage.update();

        $(".closeb").click(function() {
            $(".selection-box").remove();
        });

        $("#imageSave").click(function() {
            /*
            todo: passing topLeft, topRight, height, width to nic
            get the new canvas image from nic
            set the new image
            */
            values = {
                "topLeft":
                {
                    "x": Math.floor(stage.getChildByName("topLeft").x / CANVAS_IMAGE_SCALE_FACTOR),
                    "y": Math.floor(stage.getChildByName("topLeft").y / CANVAS_IMAGE_SCALE_FACTOR),
                },
                "topRight":
                {
                    "x": Math.floor(stage.getChildByName("topRight").x / CANVAS_IMAGE_SCALE_FACTOR),
                    "y": Math.floor(stage.getChildByName("topRight").y / CANVAS_IMAGE_SCALE_FACTOR),
                },
                "bottomLeft":
                {
                    "x": Math.floor(stage.getChildByName("botLeft").x / CANVAS_IMAGE_SCALE_FACTOR),
                    "y": Math.floor(stage.getChildByName("botLeft").y / CANVAS_IMAGE_SCALE_FACTOR),
                },
                "bottomRight":
                {
                    "x": Math.floor(stage.getChildByName("botRight").x / CANVAS_IMAGE_SCALE_FACTOR),
                    "y": Math.floor(stage.getChildByName("botRight").y / CANVAS_IMAGE_SCALE_FACTOR),
                }
            }
            console.log("sending new coords to server");
            console.log(values);
            socket.emit("update_instanceConfig_coords", localStorage.getItem("instanceConfigurationId"), values);
        });
    });

    var setupKinectPointCanvas = true;
    $("#editKinectCanvasBtn").on("click", function() {

        console.log('#editKinectCanvasBtn Click');
        if(setupKinectPointCanvas)
        {
            setupKinectPointCanvas = false;
            //remove draggable from image
            $("img").on("dragstart", function (event) {
                event.preventDefault();
            });

            // draggable canvas objects
            kinectStage.mouseMoveOutside = true;

            var topLeft = new createjs.Shape(),
                topRight = new createjs.Shape(),
                botLeft = new createjs.Shape(),
                botRight = new createjs.Shape();

            var lSize = 7;
            topLeft.graphics.beginStroke("red").lt(0,lSize).lt(0,0).lt(lSize,0);
            topRight.graphics.beginStroke("red").lt(-lSize,0).lt(0,0).lt(0,lSize);
            botLeft.graphics.beginStroke("red").lt(0,-lSize).lt(0,0).lt(lSize,0);
            botRight.graphics.beginStroke("red").lt(0,-lSize).lt(0,0).lt(-lSize,0);

            var topLeftDragger = new createjs.Container(),
                topRightDragger = new createjs.Container(),
                botLeftDragger = new createjs.Container(),
                botRightDragger = new createjs.Container();

            var addChildren = function () {
                topLeftDragger.name = "topLeft";
                topRightDragger.name = "topRight";
                botLeftDragger.name = "botLeft";
                botRightDragger.name = "botRight";
                topLeftDragger.addChild(topLeft);
                topRightDragger.addChild(topRight);
                botLeftDragger.addChild(botLeft);
                botRightDragger.addChild(botRight);
                kinectStage.addChild(topLeftDragger);
                kinectStage.addChild(topRightDragger);
                kinectStage.addChild(botLeftDragger);
                kinectStage.addChild(botRightDragger);
            };

            var createLines = function () {
                var c = $("#rawPointKinectRedefineCanvas")[0];
                var ctx = c.getContext("2d");
                ctx.beginPath();
                ctx.moveTo(x1, y1);
                ctx.lineTo(x2, y1);
                ctx.lineTo(x2, y2);
                ctx.lineTo(x1, y2);
                ctx.lineTo(x1, y1);
            };

            var setCornerPositions = function () {
                addChildren();
                topLeftDragger.x = x1;
                topLeftDragger.y = y1;
                topRightDragger.x = x2;
                topRightDragger.y = y1;
                botLeftDragger.x = x1;
                botLeftDragger.y = y2;
                botRightDragger.x = x2;
                botRightDragger.y = y2;
            };

            var x1 = 20,
                x2 = 40,
                y1 = 20,
                y2 = 40;

            setCornerPositions();

            topLeftDragger.on("pressmove", function (evt) {
                evt.currentTarget.x = evt.stageX;
                evt.currentTarget.y = evt.stageY;
                kinectStage.update();
                createLines(20, 20, 40, 60);
            });

            topRightDragger.on("pressmove", function (evt) {
                evt.currentTarget.x = evt.stageX;
                evt.currentTarget.y = evt.stageY;
                kinectStage.update();
            });

            botLeftDragger.on("pressmove", function (evt) {
                evt.currentTarget.x = evt.stageX;
                evt.currentTarget.y = evt.stageY;
                kinectStage.update();
            });

            botRightDragger.on("pressmove", function (evt) {
                evt.currentTarget.x = evt.stageX;
                evt.currentTarget.y = evt.stageY;
                kinectStage.update();
            });
        }

        kinectStage.update();

        $(".closeb").click(function() {
            $(".selection-box").remove();
        });

        $("#kinectImageSave").click(function() {
            values = {
                "topLeft":
                {
                    "x": Math.floor(kinectStage.getChildByName("topLeft").x / CANVAS_IMAGE_SCALE_FACTOR),
                    "y": Math.floor(kinectStage.getChildByName("topLeft").y / CANVAS_IMAGE_SCALE_FACTOR),
                },
                "topRight":
                {
                    "x": Math.floor(kinectStage.getChildByName("topRight").x / CANVAS_IMAGE_SCALE_FACTOR),
                    "y": Math.floor(kinectStage.getChildByName("topRight").y / CANVAS_IMAGE_SCALE_FACTOR),
                },
                "bottomLeft":
                {
                    "x": Math.floor(kinectStage.getChildByName("botLeft").x / CANVAS_IMAGE_SCALE_FACTOR),
                    "y": Math.floor(kinectStage.getChildByName("botLeft").y / CANVAS_IMAGE_SCALE_FACTOR),
                },
                "bottomRight":
                {
                    "x": Math.floor(kinectStage.getChildByName("botRight").x / CANVAS_IMAGE_SCALE_FACTOR),
                    "y": Math.floor(kinectStage.getChildByName("botRight").y / CANVAS_IMAGE_SCALE_FACTOR),
                }
            }
            console.log("sending new coords to server");
            console.log(values);
            socket.emit("update_instanceConfig_kinectCoords", localStorage.getItem("instanceConfigurationId"), values);
        });
    });

    $("#lineChange").on("click", function() {
        //the canvas image
        $("#modalImage").attr("src", canvasImage);
    });

    $("#startBtn").on("click", function(){
        var selectedUserId = $(".usersList").val();
        var selectedSessionId = $(".sessionsList").val();
        var selectedInstanceConfigurationId = $(".instanceConfigurationsList").val();
        var refresh = false;

        if(selectedUserId == "")
        {
            newUserName = $("#newUserNameBox").val();
            if(newUserName == "")
            {
                alert("Enter new username");
                return;
            }
            socket.emit("create_user", newUserName);
            refresh = true;
        }

        if(selectedSessionId == "")
        {
            newSessionName = $("#newSessionNameBox").val();
            newSessionDesc = $("#newSessionDescBox").val();
            if(newSessionName == "" || newSessionDesc == "")
            {
                alert("Enter new session details");
                return;
            }
            socket.emit("create_session", newSessionName, newSessionDesc);
            refresh = true;
        }

        if(selectedInstanceConfigurationId == "")
        {
            newCameraUri = $("#newCameraUriBox").val();
            newKinectUri = $("#newKinectUriBox").val();

            var details = {};
            details["camera"] = {};
            details["kinect"] = {};

            if(newCameraUri == "" || newKinectUri == "")
            {
                details["camera"]["host"] = "http://localhost";
                details["camera"]["port"] = "8088";
                details["kinect"]["host"] = "http://localhost";
                details["kinect"]["port"] = "8081";
            }
            else
            {
                details["camera"]["host"] = "http://" + newCameraUri.split("http://")[1].split(":")[0];
                details["camera"]["port"] = newCameraUri.split("http://")[1].split(":")[1];

                details["kinect"]["host"] = "http://" + newKinectUri.split("http://")[1].split(":")[0];
                details["kinect"]["port"] = newKinectUri.split("http://")[1].split(":")[1];
            }

            details["sessionId"] = selectedSessionId;
            details["userId"] = selectedUserId;
            
            socket.emit("create_instance_configuration", details);
            refresh = true;
        }

        if(refresh)
        {
            location.reload();
            return;
        }

        if (selectedUserId != "" && selectedSessionId != "" && selectedInstanceConfigurationId != "") {
            localStorage.setItem('userId', selectedUserId);
            localStorage.setItem("sessionId", selectedSessionId);
            localStorage.setItem("instanceConfigurationId", selectedInstanceConfigurationId);
            $('#loginModal').modal('hide');
        }
    })
});
