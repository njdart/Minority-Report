$(function() {

    var table = $('.stickyNotesTable');
    var canvasesLists = $('.stickyNotesList');
    var coordUnpackRegexp = /^\(?\s*([0-9]{1,6})[,.:\- ]+([0-9]{1,6})\s*\)?$/g;

    var addstickyNoteToTable = function(stickyNote) {
        var row = $('<tr></tr>').data(stickyNote);
    
        // Canvas ID
        row.append($('<td class="stickyNotesTable-stickyNoteId"></td>')
            .append($('<a></a>')
                .text(stickyNote.id)
                .attr('target', '_blank')
                .attr('href', '/api/stickyNote/' + stickyNote.id)));
    
        // Canvas
        row.append($('<td></td>')
            .append($('<input type="text" class="form-control stickyNotesTable-canvasId">')
                .val(stickyNote.canvas)));

        // Corners
        row.append($('<td></td>')
            .append($('<div class="form-group"></div>')
                .append($('<label>TopLeft as (x,y)</label>'))
                .append($('<input type="text" class="form-control stickyNotesTable-topLeft" placeholder="(x,y)">')
                    .val('(' + stickyNote.topLeft.x + ',' + stickyNote.topLeft.y + ')')))
            .append($('<div class="form-group"></div>')
                .append($('<label>TopRight as (x,y)</label>'))
                .append($('<input type="text" class="form-control stickyNotesTable-topRight" placeholder="(x,y)">')
                    .val('(' + stickyNote.topRight.x + ',' + stickyNote.topRight.y + ')')))
            .append($('<div class="form-group"></div>')
                .append($('<label>BottomRight as (x,y)</label>'))
                .append($('<input type="text" class="form-control stickyNotesTable-bottomRight" placeholder="(x,y)">')
                    .val('(' + stickyNote.bottomRight.x + ',' + stickyNote.bottomRight.y + ')')))
            .append($('<div class="form-group"></div>')
                .append($('<label>BottomLeft as (x,y)</label>'))
                .append($('<input type="text" class="form-control stickyNotesTable-bottomLeft" placeholder="(x,y)">')
                    .val('(' + stickyNote.bottomLeft.x + ',' + stickyNote.bottomLeft.y + ')'))));

        // Colour
        row.append($('<td></td>')
            .append($('<input type="text" class="form-control stickyNotesTable-colour" placeholder="orange">')));

        // Save + Remove Button
        row.append($('<td></td>')
            .append($('<button type="submit" class="btn btn-primary stickyNotesTable-save">Save</button>'))
            .append($('<button type="submit" class="btn btn-danger stickyNotesTable-remove">Remove</button>')));
    
        table.append(row);
        canvasesLists.append($('<option class="stickyNotesList-stickyNote"></option>')
            .attr('value', stickyNote.id)
            .text(stickyNote.id))
    };

    var addStickyNoteCanvasGroupsToTable = function(stickyNotes) {
        var canvasIds = {};
        stickyNotes.forEach(function (current) {
            if (canvasIds[current.canvas] == undefined)
            {
                canvasIds[current.canvas] = [];
            }
            canvasIds[current.canvas].push(current);
        });

        console.log(canvasIds);

        //canvasIds.forEach(function (key, currentCanvasIdSet) {
        for (var canvasId in canvasIds){
            if(canvasIds.hasOwnProperty(canvasId)) {
                console.log("current set: " + canvasId);
                currentCanvasIdSet = canvasIds[canvasId];
                var row = $('<tr></tr>');
                currentCanvasIdSet.forEach(function (stickyNote) {
                    console.log(stickyNote);
                    // Canvas ID
                    row.append($('<td class="stickyNotesTable-stickyNoteId"></td>')
                        .append($('<a></a>')
                            .text(stickyNote.id)
                            .attr('target', '_blank')
                            .attr('href', '/api/stickyNote/' + stickyNote.id)));

                    // Canvas
                    row.append($('<td></td>')
                        .append($('<input type="text" class="form-control stickyNotesTable-canvasId">')
                            .val(stickyNote.canvas)));

                    // Corners
                    row.append($('<td></td>')
                        .append($('<div class="form-group"></div>')
                            .append($('<label>TopLeft as (x,y)</label>'))
                            .append($('<input type="text" class="form-control stickyNotesTable-topLeft" placeholder="(x,y)">')
                                .val('(' + stickyNote.topLeft.x + ',' + stickyNote.topLeft.y + ')')))
                        .append($('<div class="form-group"></div>')
                            .append($('<label>TopRight as (x,y)</label>'))
                            .append($('<input type="text" class="form-control stickyNotesTable-topRight" placeholder="(x,y)">')
                                .val('(' + stickyNote.topRight.x + ',' + stickyNote.topRight.y + ')')))
                        .append($('<div class="form-group"></div>')
                            .append($('<label>BottomRight as (x,y)</label>'))
                            .append($('<input type="text" class="form-control stickyNotesTable-bottomRight" placeholder="(x,y)">')
                                .val('(' + stickyNote.bottomRight.x + ',' + stickyNote.bottomRight.y + ')')))
                        .append($('<div class="form-group"></div>')
                            .append($('<label>BottomLeft as (x,y)</label>'))
                            .append($('<input type="text" class="form-control stickyNotesTable-bottomLeft" placeholder="(x,y)">')
                                .val('(' + stickyNote.bottomLeft.x + ',' + stickyNote.bottomLeft.y + ')'))));

                    // Colour
                    row.append($('<td></td>')
                        .append($('<input type="text" class="form-control stickyNotesTable-colour" placeholder="orange">')));

                    // Save + Remove Button
                    row.append($('<td></td>')
                        .append($('<button type="submit" class="btn btn-primary stickyNotesTable-save">Save</button>'))
                        .append($('<button type="submit" class="btn btn-danger stickyNotesTable-remove">Remove</button>')));

                    table.append(row);
                    canvasesLists.append($('<option class="stickyNotesList-stickyNote"></option>')
                        .attr('value', stickyNote.id)
                        .text(stickyNote.id))

                });
            }

        }
    };

    // CREATE
    $('.stickyNotesTable-add').click(function() {
        var row = $(this).parent().parent();

        var canvas = row.find('.stickyNotesTable-add_canvas').val();
        var colour = row.find('.stickyNotesTable-add_colour').val() || 'orange';
        var topLeft = coordUnpackRegexp.exec(row.find('.stickyNotesTable-add_topLeft').val());
        var topRight = coordUnpackRegexp.exec(row.find('.stickyNotesTable-add_topRight').val());
        var bottomRight = coordUnpackRegexp.exec(row.find('.stickyNotesTable-add_bottomRight').val());
        var bottomLeft = coordUnpackRegexp.exec(row.find('.stickyNotesTable-add_bottomLeft').val());

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

        socket.emit('create_stickyNote', canvas, colour, corners);
    });

    socket.on('create_stickyNote', function(canvas) {
        addstickyNoteToTable(canvas);
        $('.stickyNotesTable-add_canvas').val('');
        $('.stickyNotesTable-add_colour').val('');
        $('.stickyNotesTable-add_topLeft').val('');
        $('.stickyNotesTable-add_topRight').val('');
        $('.stickyNotesTable-add_bottomRight').val('');
        $('.stickyNotesTable-add_bottomLeft').val('');
    });

    // READ
    socket.on('get_stickyNotes', function (stickyNotes) {

        table.empty();
        $('.stickyNotesList-stickyNote').remove();

        stickyNotes.forEach(addstickyNoteToTable);
        //addstickyNoteCanvasGroupsToTable(stickyNotes);
    });

    // UPDATE
    $(document).on('click', '.stickyNotesTable-save', function() {
        var row = $(this).parent().parent();
        var id = row.find('.stickyNotesTable-stickyNoteId').text();
        var canvas = row.find('.stickyNotesTable-canvas').val();
        var colour = row.find('.stickyNotesTable-colour').val();
        var topLeft = row.find('.stickyNotesTable-topLeft').val();
        var topRight = row.find('.stickyNotesTable-topRight').val();
        var bottomRight = row.find('.stickyNotesTable-bottomRight').val();
        var bottomLeft = row.find('.stickyNotesTable-bottomLeft').val();

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

        socket.emit('update_stickyNote', id, image, derivedFrom, derivedAt, corners);
        socket.once('update_stickyNote', function(stickyNote) {
            row.data(stickyNote);
            row.find('.stickyNotesTable-canvas').val(stickyNote.canvas);
            row.find('.stickyNotesTable-colour').val(stickyNote.colour);
            row.find('.stickyNotesTable-topLeft').val('(' + stickyNote.topLeft.x + ',' + stickyNote.topLeft.y + ')');
            row.find('.stickyNotesTable-topRight').val('(' + stickyNote.topRight.x + ',' + stickyNote.topRight.y + ')');
            row.find('.stickyNotesTable-bottomRight').val('(' + stickyNote.bottomRight.x + ',' + stickyNote.bottomRight.y + ')');
            row.find('.stickyNotesTable-bottomLeft').val('(' + stickyNote.bottomLeft.x + ',' + stickyNote.bottomLeft.y + ')');
            $('option[value="' + canvas.id + '"').text(canvas.id);
        });
    });

    // DELETE
    $(document).on('click', '.stickyNotesTable-remove', function() {
        var row = $(this).parent().parent();
        var id = row.find('.stickyNotesTable-stickyNoteId').text();

        socket.emit('delete_stickyNote', id);
        socket.once('delete_stickyNote', function(success) {
            if (success) {
                row.remove();
                $('option[value="' + id + '"').remove();
            }
        })
    });

    socket.emit('get_stickyNotes');
});