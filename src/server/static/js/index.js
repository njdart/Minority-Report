$(function() {
    $('#loginModal').modal({
        keyboard: false,
        backdrop: 'static',
        show: true
    });

    var socket = io(),
        image,
        canvas,
        postits = [],

        wholeImage = "http://media4.popsugar-assets.com/files/2014/08/08/878/n/1922507/caef16ec354ca23b_thumb_temp_cover_file32304521407524949.xxxlarge/i/Funny-Cat-GIFs.jpg",
        canvasImage = "http://i.huffpost.com/gen/1975176/images/o-SLEEPY-CAT-WATERMELON-facebook.jpg";

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
    socket.emit('get_instance_configurations')

    $('#modalCanvas').css('background-image', wholeImage);

    function updateCanvas() {
        wholeImage = image.last().id;
    }

    function updateCanvas() {
        canvasImage = canvas.last().id;
    }

    function updatePostits() {

    }

    socket.on('getImages', function(data) {
        console.log('getImages', arguments);
        image = data;
        updateImages();
    });

    socket.on('getCanvases', function(data) {
        console.log('getCanavses', arguments);
        canvas = data;
        updateCanavs();
    });

    socket.on('getPostits', function(data) {
        console.log('getPostits', arguments);
        postits = data;
        updatePostits();
    });


    $("#editCanvasBtn").on("click", function() {

        console.log('#editCanvasBtn Click');
        socket.emit('getImages');

        //adds the correct image
        $("#modalImage").attr("src", wholeImage);

        //remove draggable from image
        $("img").on("dragstart", function(event){
            event.preventDefault();
        });

        // draggable canvas objects
        var stage = new createjs.Stage("modalCanvas");
        stage.mouseMoveOutside = true;

        var topLeft = new createjs.Shape(),
            topRight = new createjs.Shape(),
            botLeft = new createjs.Shape(),
            botRight = new createjs.Shape();

        topLeft.graphics.beginFill("red").drawCircle(0,0,5);
        topRight.graphics.beginFill("red").drawCircle(0,0,5);
        botLeft.graphics.beginFill("red").drawCircle(0,0,5);
        botRight.graphics.beginFill("red").drawCircle(0,0,5);

        var topLeftDragger = new createjs.Container(),
            topRightDragger = new createjs.Container(),
            botLeftDragger = new createjs.Container(),
            botRightDragger = new createjs.Container();

        var addChildren = function() {
            topLeftDragger.addChild(topLeft);
            topRightDragger.addChild(topRight);
            botLeftDragger.addChild(botLeft);
            botRightDragger.addChild(botRight);
            stage.addChild(topLeftDragger);
            stage.addChild(topRightDragger);
            stage.addChild(botLeftDragger);
            stage.addChild(botRightDragger);
        };

        var createLines = function() {
            var c = $("#modalCanvas")[0];
            var ctx = c.getContext("2d");
            ctx.beginPath();
            ctx.moveTo(x1, y1);
            ctx.lineTo(x2, y1);
            ctx.lineTo(x2, y2);
            ctx.lineTo(x1, y2);
            ctx.lineTo(x1, y1);
        };

        var setCornerPositions = function() {
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

        topLeftDragger.on("pressmove", function(evt) {
            evt.currentTarget.x = evt.stageX;
            evt.currentTarget.y = evt.stageY;
            stage.update();
            createLines(20, 20, 40, 60);
        });

        topRightDragger.on("pressmove", function(evt) {
            evt.currentTarget.x = evt.stageX;
            evt.currentTarget.y = evt.stageY;
            stage.update();
            //createLines()
        });

        botLeftDragger.on("pressmove", function(evt) {
            evt.currentTarget.x = evt.stageX;
            evt.currentTarget.y = evt.stageY;
            stage.update();
            console.log("bottomLeftDrag", this.id);
        });

        botRightDragger.on("pressmove", function(evt) {
            evt.currentTarget.x = evt.stageX;
            evt.currentTarget.y = evt.stageY;
            stage.update();
            console.log("bottomRightDragger", this.id);
        });

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
        });
    });

    $("#lineChange").on("click", function() {
        //the canvas image
        $("#modalImage").attr("src", canvasImage);
    });

    $("#startBtn").on("click", function(){
        var selectedUserId = $(".usersList").val();
        var selectedSessionId = $(".sessionsList").val();
        var selectedInstanceConfiguration = $(".instanceConfigurationsList").val();
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

        if(selectedInstanceConfiguration == "")
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

        if (selectedUserId != "" && selectedSessionId != "" && selectedInstanceConfiguration != "") {
            localStorage.setItem('user', selectedUserId);
            localStorage.setItem("session", selectedSessionId);
            localStorage.setItem("instanceConfiguration", selectedInstanceConfiguration);
            $('#loginModal').modal('hide');
        }
    })
});
