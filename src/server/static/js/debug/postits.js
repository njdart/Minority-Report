$(function() {

    var table = $('.postitsTable');
    var canvasesLists = $('.postitsList');
    var coordUnpackRegexp = /^\(?\s*([0-9]{1,6})[,.:\- ]+([0-9]{1,6})\s*\)?$/g;

    var addPostitToTable = function(postit) {
        var row = $('<tr></tr>').data(postit);
    
        // Canvas ID
        row.append($('<td class="postitsTable-postitId"></td>')
            .append($('<a></a>')
                .text(postit.id)
                .attr('target', '_blank')
                .attr('href', '/api/postit/' + postit.id)));
    
        // Canvas
        row.append($('<td></td>')
            .append($('<input type="text" class="form-control postitsTable-canvasId">')
                .val(postit.canvas)));

        // Corners
        row.append($('<td></td>')
            .append($('<div class="form-group"></div>')
                .append($('<label>TopLeft as (x,y)</label>'))
                .append($('<input type="text" class="form-control postitsTable-topLeft" placeholder="(x,y)">')
                    .val('(' + postit.topLeft.x + ',' + postit.topLeft.y + ')')))
            .append($('<div class="form-group"></div>')
                .append($('<label>TopRight as (x,y)</label>'))
                .append($('<input type="text" class="form-control postitsTable-topRight" placeholder="(x,y)">')
                    .val('(' + postit.topRight.x + ',' + postit.topRight.y + ')')))
            .append($('<div class="form-group"></div>')
                .append($('<label>BottomRight as (x,y)</label>'))
                .append($('<input type="text" class="form-control postitsTable-bottomRight" placeholder="(x,y)">')
                    .val('(' + postit.bottomRight.x + ',' + postit.bottomRight.y + ')')))
            .append($('<div class="form-group"></div>')
                .append($('<label>BottomLeft as (x,y)</label>'))
                .append($('<input type="text" class="form-control postitsTable-bottomLeft" placeholder="(x,y)">')
                    .val('(' + postit.bottomLeft.x + ',' + postit.bottomLeft.y + ')'))));

        // Colour
        row.append($('<td></td>')
            .append($('<input type="text" class="form-control postitsTable-colour" placeholder="orange">')));

        // Save + Remove Button
        row.append($('<td></td>')
            .append($('<button type="submit" class="btn btn-primary postitsTable-save">Save</button>'))
            .append($('<button type="submit" class="btn btn-danger postitsTable-remove">Remove</button>')));
    
        table.append(row);
        canvasesLists.append($('<option class="postitsList-postit"></option>')
            .attr('value', postit.id)
            .text(postit.id))
    };

    // CREATE
    $('.postitsTable-add').click(function() {
        var row = $(this).parent().parent();

        var canvas = row.find('.postitsTable-add_canvas').val();
        var colour = row.find('.postitsTable-add_colour').val() || 'orange';
        var topLeft = coordUnpackRegexp.exec(row.find('.postitsTable-add_topLeft').val());
        var topRight = coordUnpackRegexp.exec(row.find('.postitsTable-add_topRight').val());
        var bottomRight = coordUnpackRegexp.exec(row.find('.postitsTable-add_bottomRight').val());
        var bottomLeft = coordUnpackRegexp.exec(row.find('.postitsTable-add_bottomLeft').val());

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

        console.log(corners)

        socket.emit('create_postit', canvas, colour, corners);
    });

    socket.on('create_postit', function(canvas) {
        addPostitToTable(canvas);
        $('.postitsTable-add_canvas').val('');
        $('.postitsTable-add_colour').val('');
        $('.postitsTable-add_topLeft').val('');
        $('.postitsTable-add_topRight').val('');
        $('.postitsTable-add_bottomRight').val('');
        $('.postitsTable-add_bottomLeft').val('');
    });

    // READ
    socket.on('get_postits', function (postits) {

        table.empty();
        $('.postitsList-postit').remove();

        postits.forEach(addPostitToTable);
    });

    // UPDATE
    $(document).on('click', '.postitsTable-save', function() {
        var row = $(this).parent().parent();
        var id = row.find('.postitsTable-postitId').text();
        var canvas = row.find('.postitsTable-canvas').val();
        var colour = row.find('.postitsTable-colour').val();
        var topLeft = row.find('.postitsTable-topLeft').val();
        var topRight = row.find('.postitsTable-topRight').val();
        var bottomRight = row.find('.postitsTable-bottomRight').val();
        var bottomLeft = row.find('.postitsTable-bottomLeft').val();

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

        socket.emit('update_postit', id, image, derivedFrom, derivedAt, corners);
        socket.once('update_postit', function(postit) {
            row.data(postit);
            row.find('.postitsTable-canvas').val(postit.canvas);
            row.find('.postitsTable-colour').val(postit.colour);
            row.find('.postitsTable-topLeft').val('(' + postit.topLeft.x + ',' + postit.topLeft.y + ')');
            row.find('.postitsTable-topRight').val('(' + postit.topRight.x + ',' + postit.topRight.y + ')');
            row.find('.postitsTable-bottomRight').val('(' + postit.bottomRight.x + ',' + postit.bottomRight.y + ')');
            row.find('.postitsTable-bottomLeft').val('(' + postit.bottomLeft.x + ',' + postit.bottomLeft.y + ')');
            $('option[value="' + canvas.id + '"').text(canvas.id);
        });
    });

    // DELETE
    $(document).on('click', '.postitsTable-remove', function() {
        var row = $(this).parent().parent();
        var id = row.find('.postitsTable-postitId').text();

        socket.emit('delete_postit', id);
        socket.once('delete_postit', function(success) {
            if (success) {
                row.remove();
                $('option[value="' + id + '"').remove();
            }
        })
    });

    socket.emit('get_postits');
});