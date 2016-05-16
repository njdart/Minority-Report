
var socket = io(),
    image,
    canvas,
    postits = [],

    wholeImage = "http://media4.popsugar-assets.com/files/2014/08/08/878/n/1922507/caef16ec354ca23b_thumb_temp_cover_file32304521407524949.xxxlarge/i/Funny-Cat-GIFs.jpg",
    canvasImage = "http://i.huffpost.com/gen/1975176/images/o-SLEEPY-CAT-WATERMELON-facebook.jpg";

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

    //remove draggabe from image
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
    /*
    var $selection = $("<div>").addClass("selection-box"),
        topLeft,
        topRight,
        width,
        height;

    $("#imageModalContent").on("mousedown", function(event){
        $selection.remove();

        // coordinates of mouse relative to image
        var xVal = event.pageX - $("#modalImage").offset().left + $("#modalImage").position().left;
        var yVal = event.pageY - $("#modalImage").offset().top + $("#modalImage").position().top;

        // add selection box to screen
        $selection.appendTo($("#imageModalContent"));

        $("#imageModalContent").on('mousemove', function(e) {
            var xPos = e.pageX - $("#modalImage").offset().left + $("#modalImage").position().left,
                yPos = e.pageY - $("#modalImage").offset().top + $("#modalImage").position().top,
                width  = Math.abs(xPos - xVal),
                height = Math.abs(yPos - yVal),
                new_x,
                new_y;

            //console.log(width.toString() + " " + height.toString());
            new_x = (xPos < xVal) ? (xVal - width) : xVal;
            new_y = (yPos < yVal) ? (yVal - height) : yVal;
            $selection.css({
                'width': width,
                'height': height,
                'top': new_y,
                'left': new_x
            });

        });

        $(document).on("mouseup", function(){
            $("#imageModalContent").off("mousemove");
        });
    });
    */

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
