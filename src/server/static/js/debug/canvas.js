$(function() {

    var table = $('.canvasesTable');
    var canvasesLists = $('.canvasList');
    var coordUnpackRegexp = /^\(?\s*([0-9]{1,6})[,.:\- ]+([0-9]{1,6})\s*\)?$/g;

    var addCanvasToTable = function(canvas) {
        var row = $('<tr></tr>').data(canvas);
    
        // Canvas ID
        row.append($('<td class="canvasesTable-canvasId"></td>')
            .text(canvas.id));

        // Session
        row.append($('<td></td>')
            .append($('<div class="form-group"></div>')
                .append($('<label>Session</label>'))
                .append($('<input type="text" class="form-control canvasesTable-sessionId">')
                    .val(canvas.session))));

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

        // Size
        row.append($('<td></td>')
            .append($('<div class="form-group"></div>')
                .append($('<label>Size as (width,height)</label>'))
                .append($('<input type="text" class="form-control canvasesTable-size" placeholder="(1920,1080)">')
                    .val('(' + canvas.width + ',' + canvas.height + ')'))));
    
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

        var session = row.find('.canvasesTable-add_session').val();
        var derivedFrom = row.find('.canvasesTable-add_derivedFrom').val();
        var derivedAt = row.find('.canvasesTable-add_derivedAt').val();
        derivedAt = (derivedAt) ? new Date(derivedAt) : new Date();
        var size = coordUnpackRegexp.exec(row.find('.canvasesTable-add_size').val());

        var width = (size) ? size[1] : 1920;
        var height = (size) ? size[2] : 1080;
        socket.emit('create_canvas', session, derivedAt, derivedFrom, width, height);
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
        var session = row.find('.canvasesTable-sessionId').val();
        var derivedFrom = row.find('.canvasesTable-derivedFrom').val();
        var derivedAt = new Date(row.find('.canvasesTable-derivedAt').val());
        var size = coordUnpackRegexp.exec(row.find('.canvasesTable-size').val());

        var width = (size) ? size[1] : 1920;
        var height = (size) ? size[2] : 1080;

        socket.emit('update_canvas', id, session, derivedFrom, derivedAt, width, height);
        socket.once('update_canvas', function(canvas) {
            row.data(canvas);
            row.find('.canvasesTable-sessionId').val(canvas.session);
            row.find('.canvasesTable-derivedFrom').val(canvas.derivedFrom);
            row.find('.canvasesTable-derivedAt').val(new Date(canvas.derivedAt).toISOString());
            row.find('.canvasesTable-size').val('(' + canvas.width + ',' + canvas.height + ')');
            $('option[value="' + canvas.id + '"').text(canvas.id);
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