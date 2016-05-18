$(function() {

    var table = $('.canvasesTable');
    var canvasesLists = $('.canvasList');
    var coordUnpackRegexp = /^\(?\s*([0-9]{1,6})[,.:\- ]+([0-9]{1,6})\s*\)?$/g;

    var addCanvasToTable = function(canvas) {
        var row = $('<tr></tr>').data(canvas);
    
        // Canvas ID
        row.append($('<td class="canvasesTable-canvasId"></td>')
            .append($('<a></a>')
                .text(canvas.id)
                .attr('target', '_blank')
                .attr('href', '/api/canvas/' + canvas.id)));
    
        // Image
        row.append($('<td></td>')
            .append($('<input type="text" class="form-control canvasesTable-imageId">')
                .val(canvas.image)));
    
        // Derivations
        row.append($('<td></td>')
            .append($('<div class="form-group"></div>')
                .append($('<label>Derived From Canvas</label>'))
                .append($('<input type="text" class="form-control canvasesTable-derivedFrom" placeholder="None">')
                    .val(canvas.derivedFrom)))
            .append($('<div class="form-group"></div>')
                .append($('<label>Derived At</label>'))
                .append($('<input type="text" class="form-control canvasesTable-derivedAt" placeholder="Now">')
                    .val(new Date(canvas.derivedAt).toISOString()))));

        // Corners
        row.append($('<td></td>')
            .append($('<div class="form-group"></div>')
                .append($('<label>TopLeft as (x,y)</label>'))
                .append($('<input type="text" class="form-control canvasesTable-topLeft" placeholder="(x,y)">')
                    .val('(' + canvas.topLeft.x + ',' + canvas.topLeft.y + ')')))
            .append($('<div class="form-group"></div>')
                .append($('<label>TopRight as (x,y)</label>'))
                .append($('<input type="text" class="form-control canvasesTable-topRight" placeholder="(x,y)">')
                    .val('(' + canvas.topRight.x + ',' + canvas.topRight.y + ')')))
            .append($('<div class="form-group"></div>')
                .append($('<label>BottomRight as (x,y)</label>'))
                .append($('<input type="text" class="form-control canvasesTable-bottomRight" placeholder="(x,y)">')
                    .val('(' + canvas.bottomRight.x + ',' + canvas.bottomRight.y + ')')))
            .append($('<div class="form-group"></div>')
                .append($('<label>BottomLeft as (x,y)</label>'))
                .append($('<input type="text" class="form-control canvasesTable-bottomLeft" placeholder="(x,y)">')
                    .val('(' + canvas.bottomLeft.x + ',' + canvas.bottomLeft.y + ')'))));
    
        // Save + Remove Button
        row.append($('<td></td>')
            .append($('<button type="submit" class="btn btn-primary canvasesTable-save">Save</button>'))
            .append($('<button type="submit" class="btn btn-danger canvasesTable-remove">Remove</button>')));
    
        table.append(row);
        canvasesLists.append($('<option class="canvasList-canvas"></option>')
            .attr('value', canvas.id)
            .text(canvas.id))
    };

    // CREATE
    $('.canvasesTable-add').click(function() {
        var row = $(this).parent().parent();

        var image = row.find('.canvasesTable-add_image').val();
        var derivedFrom = row.find('.canvasesTable-add_derivedFrom').val();
        var derivedAt = row.find('.canvasesTable-add_derivedAt').val();
        derivedAt = (derivedAt) ? new Date(derivedAt) : new Date();
        var topLeft = coordUnpackRegexp.exec(row.find('.canvasesTable-add_topLeft').val());
        var topRight = coordUnpackRegexp.exec(row.find('.canvasesTable-add_topRight').val());
        var bottomRight = coordUnpackRegexp.exec(row.find('.canvasesTable-add_bottomRight').val());
        var bottomLeft = coordUnpackRegexp.exec(row.find('.canvasesTable-add_bottomLeft').val());

        var corners = {
            topLeft: {
                x: (topLeft) ? topLeft[1] : null,
                y: (topLeft) ? topLeft[2] : null
            },
            topRight: {
                x: (topRight) ? topRight[1] : (bottomRight) ? bottomRight[1] : null,
                y: (topRight) ? topRight[2] : (topLeft) ? topLeft[2] : null
            },
            bottomLeft: {
                x: (bottomLeft) ? bottomLeft[1] : (topLeft) ? topLeft[1] : null,
                y: (bottomLeft) ? bottomLeft[2] : (bottomRight) ? bottomRight[2] : null
            },
            bottomRight: {
                x: (bottomRight) ? bottomRight[1] : null,
                y: (bottomRight) ? bottomRight[2] : null
            }
        };

        socket.emit('create_canvas', image, derivedAt, derivedFrom, corners);
    });

    socket.on('create_canvas', function(canvas) {
        addCanvasToTable(canvas);
        $('.canvasesTable-add_image').val('');
        $('.canvasesTable-add_derivedFrom').val('');
        $('.canvasesTable-add_derivedAt').val('');
        $('.canvasesTable-add_topLeft').val('');
        $('.canvasesTable-add_topRight').val('');
        $('.canvasesTable-add_bottomRight').val('');
        $('.canvasesTable-add_bottomLeft').val('');
    });

    // READ
    socket.on('get_canvases', function (canvases) {

        table.empty();
        $('.canvasList-canvas').remove();

        canvases.forEach(addCanvasToTable);
    });

    // UPDATE
    $(document).on('click', '.canvasesTable-save', function() {
        var row = $(this).parent().parent();
        var id = row.find('.canvasesTable-canvasId').text();
        var image = row.find('.canvasesTable-imageId').val();
        var derivedFrom = row.find('.canvasesTable-derivedFrom').val();
        var derivedAt = new Date(row.find('.canvasesTable-derivedAt').val());
        var topLeft = row.find('.canvasesTable-topLeft').val();
        var topRight = row.find('.canvasesTable-topRight').val();
        var bottomRight = row.find('.canvasesTable-bottomRight').val();
        var bottomLeft = row.find('.canvasesTable-bottomLeft').val();

        var corners = {
            topLeft: {
                x: (topLeft) ? topLeft[1] : null,
                y: (topLeft) ? topLeft[2] : null
            },
            topRight: {
                x: (topRight) ? topRight[1] : (bottomRight) ? bottomRight[1] : null,
                y: (topRight) ? topRight[2] : (topLeft) ? topLeft[2] : null
            },
            bottomLeft: {
                x: (bottomLeft) ? bottomLeft[1] : (topLeft) ? topLeft[1] : null,
                y: (bottomLeft) ? bottomLeft[2] : (bottomRight) ? bottomRight[2] : null
            },
            bottomRight: {
                x: (bottomRight) ? bottomRight[1] : null,
                y: (bottomRight) ? bottomRight[2] : null
            }
        };

        socket.emit('update_canvas', id, image, derivedFrom, derivedAt, corners);
        socket.once('update_canvas', function(canvas) {
            row.data(canvas);
            row.find('.canvasesTable-imageId').val(canvas.imageId);
            row.find('.canvasesTable-derivedFrom').val(canvas.derivedFrom);
            row.find('.canvasesTable-imageId').val(new Date(canvas.derivedAt).toISOString());
            row.find('.canvasesTable-topLeft').val('(' + canvas.topLeft.x + ',' + canvas.topLeft.y + ')');
            row.find('.canvasesTable-topRight').val('(' + canvas.topRight.x + ',' + canvas.topRight.y + ')');
            row.find('.canvasesTable-bottomRight').val('(' + canvas.bottomRight.x + ',' + canvas.bottomRight.y + ')');
            row.find('.canvasesTable-bottomLeft').val('(' + canvas.bottomLeft.x + ',' + canvas.bottomLeft.y + ')');
            $('option[value="' + image.id + '"').text(image.id);
        });
    });

    // DELETE
    $(document).on('click', '.canvasesTable-remove', function() {
        var row = $(this).parent().parent();
        var id = row.find('.canvasesTable-canvasId').text();

        socket.emit('delete_canvas', id);
        socket.once('delete_canvas', function(success) {
            if (success) {
                row.remove();
                $('option[value="' + id + '"').remove();
            }
        })
    });

    socket.emit('get_canvases');
});