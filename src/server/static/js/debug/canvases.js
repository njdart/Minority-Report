var canvasesTable = $('.canvases-tableBody');
var canvases = [];

function updateCanvases() {
    console.log('Updating Canvases');
    $('.canvases-canvasRow').remove();
    var template = $('.canvases-tableBody > .canvases-row_template');

    canvases.forEach(function(canvas) {
        var tr = template.clone();
        tr.removeClass('table-row_template');
        tr.addClass('canvases-canvasRow');

        $(tr).insertBefore(canvasesTable.children().last());
        tr.find('.canvases-id').text(canvas.id);
        tr.find('.canvases-image').attr('src', 'api/canvas/' + canvas.id);
        tr.find('.canvases-derivedFrom').val(canvas.derivedFrom);
        tr.find('.canvases-derivedAt').val(new Date(canvas.derivedAt));

        tr.find('.canvases-topLeftX').val(canvas.canvasTopLeftX);
        tr.find('.canvases-topLeftY').val(canvas.canvasTopLeftY);

        tr.find('.canvases-topRightX').val(canvas.canvasTopRightX);
        tr.find('.canvases-topRightY').val(canvas.canvasTopRightY);

        tr.find('.canvases-topLeftX').val(canvas.canvasTopLeftX);
        tr.find('.canvases-topLeftY').val(canvas.canvasTopLeftY);

        tr.find('.canvases-bottomLeftX').val(canvas.canvasBottomLeftX);
        tr.find('.canvases-bottomLeftY').val(canvas.canvasBottomLeftY);

        tr.find('.canvases-bottomRightX').val(canvas.canvasBottomRightX);
        tr.find('.canvases-bottomRightY').val(canvas.canvasBottomRightY);

        $('.canvas-select').append($('<option></option>')
            .attr('value', canvas.id)
            .text(canvas.id))
    });
}


body.on('click', '.canvases-add', function() {
    var row = $(this).parent().parent();

    var properties = {
        image: row.find('.canvases-image').val(),
        derivedFrom: row.find('.canvases-derivedFrom').val(),
        derivedAt: row.find('.canvases-derivedAt').val(),
        canvasTopLeftX: row.find('.canvases-topLeftX').val(),
        canvasTopLeftY: row.find('.canvases-topLeftY').val(),
        canvasTopRightX: row.find('.canvases-topRighttX').val(),
        canvasTopRightY: row.find('.canvases-topRighttY').val(),
        canvasBottomLeftX: row.find('.canvases-bottomLeftX').val(),
        canvasBottomLeftY: row.find('.canvases-bottomLeftY').val(),
        canvasBottomRightX: row.find('.canvases-bottomRightX').val(),
        canvasBottomRightY: row.find('.canvases-bottomRightY').val()
    };

    console.log(properties);

    // socket.emit('addCanvas', properties);
});

body.on('click', '.canvases-remove', function() {
    var row = $(this).parent().parent();
    var properties = {
        id: row.find('.canvases-id').text()
    };
    console.log('Deleting Canvas', properties);
    // socket.emit('deleteImage', properties);
});

body.on("click", ".force-canvas-send", function() {
    socket.emit("updateCanvas", {});
});

// Show canvas
body.on('click', '.canvases-id', function() {
    $(this).parent().find('.canvases-image').toggle()
});

body.on('click', '.canvases-extractPostits', function() {
    var canvasId = $(this).parent().parent().find('.canvases-id').text()
    console.log('AutoExtracting postits from canvas id', canvasId);
    socket.emit('autoExtractPostits', canvasId);
})

socket.on('getCanvases', function(data) {
    console.log('getCanvases', arguments);
    canvases = data;
    updateCanvases();
});

socket.on('autoExtractCanvases', function(data) {
    console.log('autoExtractCanvases', arguments);
    socket.emit('getPostits')
})
socket.emit('getCanvases');
