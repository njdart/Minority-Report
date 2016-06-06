$(function() {
    var table = $('.instanceConfigsTable');
    var instanceConfigurationsLists = $('.instanceConfigsList');
    var calibrationOverlay = $('.calibrationOverlay')
    // var coordUnpackRegexp = /^\(?\s*([0-9]{1,5})[,.:\- ]+([0-9]{1,5})\s*\)?$/g;
    var coordUnpackRegexp = /^\s*\(?\s*([0-9e.\-+]+)\s*,\s*([0-9e.\-+]+)\s*\)?/g;
    //coordUnpackRegexp.compile();

    var addInstanceConfigToTable = function(instanceConfiguration) {
        var row = $('<tr></tr>').data(instanceConfiguration);

        // Instance Config ID
        row.append($('<td class="instanceConfigsTable-configId"></td>')
            .text(instanceConfiguration.id));

        // details
        var form = $('<form></form>');
        form.append($('<div class="form-group"></div>')
            .append($('<label>Session</label>'))
            .append($('<input type="text" class="form-control instanceConfigsTable-sessionId" placeholder="Session ID">')
                .val(instanceConfiguration.sessionId)));

        form.append($('<div class="form-group"></div>')
            .append($('<label>User</label>'))
            .append($('<input type="text" class="form-control instanceConfigsTable-userId" placeholder="User ID">')
                .val(instanceConfiguration.userId)));

        var leftColumn = $('<div class="col-md-6"></div>');

        leftColumn.append($('<div class="form-group"></div>')
            .append($('<label>TopLeft as (x,y)</label>'))
            .append($('<input type="text" class="form-control instanceConfigsTable-topLeft" placeholder="(x, y)">')
                .val((instanceConfiguration.topLeft.x != null) ?
                        '(' + instanceConfiguration.topLeft.x + ',' + instanceConfiguration.topLeft.y + ')' :
                        '')));

        leftColumn.append($('<div class="form-group"></div>')
            .append($('<label>BottomLeft as (x,y)</label>'))
            .append($('<input type="text" class="form-control instanceConfigsTable-bottomLeft" placeholder="(x, y)">')
                .val((instanceConfiguration.bottomLeft.x != null) ?
                        '(' + instanceConfiguration.bottomLeft.x + ',' + instanceConfiguration.bottomLeft.y + ')' :
                        '')));

        leftColumn.append($('<div class="form-group"></div>')
            .append($('<label>KinectTopLeft as (x,y)</label>'))
            .append($('<input type="text" class="form-control instanceConfigsTable-kinectTopLeft" placeholder="(x, y)">')
                .val((instanceConfiguration.kinectTopLeft.x != null) ?
                        '(' + instanceConfiguration.kinectTopLeft.x + ',' + instanceConfiguration.kinectTopLeft.y + ')' :
                        '')));

        leftColumn.append($('<div class="form-group"></div>')
            .append($('<label>KinectBottomLeft as (x,y)</label>'))
            .append($('<input type="text" class="form-control instanceConfigsTable-kinectBottomLeft" placeholder="(x, y)">')
                .val((instanceConfiguration.kinectBottomLeft.x != null) ?
                        '(' + instanceConfiguration.kinectBottomLeft.x + ',' + instanceConfiguration.kinectBottomLeft.y + ')' :
                        '')));

        leftColumn.append($('<div class="form-group"></div>')
            .append($('<label>Camera Host</label>'))
            .append($('<input type="text" class="form-control instanceConfigsTable-cameraHost">')
                .val(instanceConfiguration.camera.host)));

        leftColumn.append($('<div class="form-group"></div>')
            .append($('<label>Kinect Host</label>'))
            .append($('<input type="text" class="form-control instanceConfigsTable-kinectHost">')
                .val(instanceConfiguration.kinect.host)));

        var rightColumn = $('<div class="col-md-6"></div>');

        rightColumn.append($('<div class="form-group"></div>')
            .append($('<label>TopRight as (x,y)</label>'))
            .append($('<input type="text" class="form-control instanceConfigsTable-topRight" placeholder="(x, y)">')
                .val((instanceConfiguration.topRight.x != null) ?
                        '(' + instanceConfiguration.topRight.x + ',' + instanceConfiguration.topRight.y + ')' :
                        '')));

        rightColumn.append($('<div class="form-group"></div>')
            .append($('<label>BottomRight as (x,y)</label>'))
            .append($('<input type="text" class="form-control instanceConfigsTable-bottomRight" placeholder="(x, y)">')
                .val((instanceConfiguration.bottomRight.x != null) ?
                        '(' + instanceConfiguration.bottomRight.x + ',' + instanceConfiguration.bottomRight.y + ')' :
                        '')));

        rightColumn.append($('<div class="form-group"></div>')
            .append($('<label>KinectTopRight as (x,y)</label>'))
            .append($('<input type="text" class="form-control instanceConfigsTable-kinectTopRight" placeholder="(x, y)">')
                .val((instanceConfiguration.kinectTopRight.x != null) ?
                        '(' + instanceConfiguration.kinectTopRight.x + ',' + instanceConfiguration.topRight.y + ')' :
                        '')));

        rightColumn.append($('<div class="form-group"></div>')
            .append($('<label>KinectBottomRight as (x,y)</label>'))
            .append($('<input type="text" class="form-control instanceConfigsTable-kinectBottomRight" placeholder="(x, y)">')
                .val((instanceConfiguration.kinectBottomRight.x != null) ?
                        '(' + instanceConfiguration.kinectBottomRight.x + ',' + instanceConfiguration.kinectBottomRight.y + ')' :
                        '')));

        rightColumn.append($('<div class="form-group"></div>')
            .append($('<label>Camera Port</label>'))
            .append($('<input type="text" class="form-control instanceConfigsTable-cameraPort">')
                .val(instanceConfiguration.camera.port)));

        rightColumn.append($('<div class="form-group"></div>')
            .append($('<label>Kinect Port</label>'))
            .append($('<input type="text" class="form-control instanceConfigsTable-kinectPort">')
                .val(instanceConfiguration.kinect.port)));

        form.append($('<div class="row"></div>')
            .append(leftColumn).append(rightColumn));

        row.append($('<td></td>').append(form));

        // Save + Remove Button
        row.append($('<td></td>')
            .append($('<button type="submit" class="btn btn-primary instanceConfigsTable-save">Save</button>'))
            .append($('<button type="submit" class="btn btn-danger instanceConfigsTable-remove">Remove</button>'))
            .append($('<button type="submit" class="btn btn-default instanceConfigsTable-calibrate">Calibrate</button>'))
            .append($('<span class="instanceConfigsTable-calibrateStatus" style="color:red;font-weight:bold"></span>')));

        table.append(row);
        instanceConfigurationsLists.append($('<option class="instanceConfigsTable-config"></option>')
            .attr('value', instanceConfiguration.id)
            .text(instanceConfiguration.id));
    };

    // CREATE
    $('.instanceConfigsTable-add').click(function() {
        var row = $(this).parent().parent();

        var topLeft = coordUnpackRegexp.exec(row.find('.instanceConfigsTable-add_topLeft').val());
        var topRight = coordUnpackRegexp.exec(row.find('.instanceConfigsTable-add_topRight').val());
        var bottomRight = coordUnpackRegexp.exec(row.find('.instanceConfigsTable-add_bottomRight').val());
        var bottomLeft = coordUnpackRegexp.exec(row.find('.instanceConfigsTable-add_bottomLeft').val());

        var kinectTopLeft = coordUnpackRegexp.exec(row.find('.instanceConfigsTable-add_kinectTopLeft').val());
        var kinectTopRight = coordUnpackRegexp.exec(row.find('.instanceConfigsTable-add_kinectTopRight').val());
        var kinectBottomRight = coordUnpackRegexp.exec(row.find('.instanceConfigsTable-add_kinectBottomRight').val());
        var kinectBottomLeft = coordUnpackRegexp.exec(row.find('.instanceConfigsTable-add_kinectBottomLeft').val());

        var data = {
            sessionId: row.find('.instanceConfigsTable-add_sessionId').val(),
            userId: row.find('.instanceConfigsTable-add_userId').val(),
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
            },
            kinectTopLeft: {
                x: (kinectTopLeft) ? kinectTopLeft[1] : null,
                y: (kinectTopLeft) ? kinectTopLeft[2] : null
            },
            kinectTopRight: {
                x: (kinectTopRight) ? kinectTopRight[1] : (kinectBottomRight) ? kinectBottomRight[1] : null,
                y: (kinectTopRight) ? kinectTopRight[2] : (kinectTopLeft) ? kinectTopLeft[2] : null
            },
            kinectBottomLeft: {
                x: (kinectBottomLeft) ? kinectBottomLeft[1] : (kinectTopLeft) ? kinectTopLeft[1] : null,
                y: (kinectBottomLeft) ? kinectBottomLeft[2] : (kinectBottomRight) ? kinectBottomRight[2] : null
            },
            kinectBottomRight: {
                x: (kinectBottomRight) ? kinectBottomRight[1] : null,
                y: (kinectBottomRight) ? kinectBottomRight[2] : null
            },
            camera: {
                host: row.find('.instanceConfigsTable-add_cameraHost').val() || 'localhost',
                port: row.find('.instanceConfigsTable-add_cameraPort').val() || 8080
            },
            kinect: {
                host: row.find('.instanceConfigsTable-add_kinectHost').val() || 'localhost',
                port: row.find('.instanceConfigsTable-add_kinectPort').val() || 8081
            }
        };

        if (data.sessionId &&
            data.userId &&
            data.camera.host &&
            data.camera.port &&
            data.kinect.host &&
            data.kinect.port) {

            socket.emit('create_instance_configuration', data);
        }
    });

    socket.on('create_instance_configuration', function(instanceConfig) {
        addInstanceConfigToTable(instanceConfig);
        $('.instanceConfigsTable-add_sessionId').val('');
        $('.instanceConfigsTable-add_userId').val('');
        $('.instanceConfigsTable-add_kinectHost').val('');
        $('.instanceConfigsTable-add_kinectPort').val('');
        $('.instanceConfigsTable-add_cameraHost').val('');
        $('.instanceConfigsTable-add_cameraPort').val('');
    });

    // READ
    socket.on('get_instance_configurations', function (instanceConfigs) {
        table.empty();
        $('.instanceConfigsList-instanceConfig').remove();

        instanceConfigs.forEach(addInstanceConfigToTable);
    });

    var updateInstanceConfigRow = function(instanceConfig) {
        var row = $(".instanceConfigsTable").find(':contains("' + instanceConfig.id + '")')
        row.find('.instanceConfigsTable-sessionId').val(instanceConfig.sessionId);
        row.find('.instanceConfigsTable-userId').val(instanceConfig.userId);
        row.find('.instanceConfigsTable-topLeft').val('(' + instanceConfig.topLeft.x + ',' + instanceConfig.topLeft.y + ')');
        row.find('.instanceConfigsTable-topRight').val('(' + instanceConfig.topRight.x + ',' + instanceConfig.topRight.y + ')');
        row.find('.instanceConfigsTable-bottomRight').val('(' + instanceConfig.bottomRight.x + ',' + instanceConfig.bottomRight.y + ')');
        row.find('.instanceConfigsTable-bottomLeft').val('(' + instanceConfig.bottomLeft.x + ',' + instanceConfig.bottomLeft.y + ')');
        row.find('.instanceConfigsTable-kinectTopLeft'    ).val('(' + instanceConfig.kinectTopLeft.x + ',' + instanceConfig.kinectTopLeft.y + ')');
        row.find('.instanceConfigsTable-kinectTopRight'   ).val('(' + instanceConfig.kinectTopRight.x + ',' + instanceConfig.kinectTopRight.y + ')');
        row.find('.instanceConfigsTable-kinectBottomRight').val('(' + instanceConfig.kinectBottomRight.x + ',' + instanceConfig.kinectBottomRight.y + ')');
        row.find('.instanceConfigsTable-kinectBottomLeft' ).val('(' + instanceConfig.kinectBottomLeft.x + ',' + instanceConfig.kinectBottomLeft.y + ')');
        row.find('.instanceConfigsTable-kinectHost').val(instanceConfig.kinect.host);
        row.find('.instanceConfigsTable-kinectPort').val(instanceConfig.kinect.port);
        row.find('.instanceConfigsTable-cameraHost').val(instanceConfig.camera.host);
        row.find('.instanceConfigsTable-cameraPort').val(instanceConfig.camera.port);
        $('option[value="' + instanceConfig.id + '"').text(instanceConfig.sessionId);

        if (!instanceConfig.calibSuccess)
        {
            row.find(".instanceConfigsTable-calibrateStatus").text("Calibration failed")
        }
   }

    // UPDATE
    $(document).on('click', '.instanceConfigsTable-save', function() {
        var row = $(this).parent().parent();

        var id = row.find('.instanceConfigsTable-configId').text();
        var topLeft = coordUnpackRegexp.exec(row.find('.instanceConfigsTable-topLeft').val());
        var topRight = coordUnpackRegexp.exec(row.find('.instanceConfigsTable-topRight').val());
        var bottomRight = coordUnpackRegexp.exec(row.find('.instanceConfigsTable-bottomRight').val());
        var bottomLeft = coordUnpackRegexp.exec(row.find('.instanceConfigsTable-bottomLeft').val());

        var kinectTopLeft = coordUnpackRegexp.exec(row.find('.instanceConfigsTable-kinectTopLeft').val());
        var kinectTopRight = coordUnpackRegexp.exec(row.find('.instanceConfigsTable-kinectTopRight').val());
        var kinectBottomRight = coordUnpackRegexp.exec(row.find('.instanceConfigsTable-kinectBottomRight').val());
        var kinectBottomLeft = coordUnpackRegexp.exec(row.find('.instanceConfigsTable-kinectBottomLeft').val());

        var data = {
            sessionId: row.find('.instanceConfigsTable-sessionId').val(),
            userId: row.find('.instanceConfigsTable-userId').val(),
            topLeft: {
                x: (topLeft) ? topLeft[1] : null,
                y: (topLeft) ? topLeft[2] : null
            },
            topRight: {
                x: (topRight) ? topRight[1] : null,
                y: (topRight) ? topRight[2] : null
            },
            bottomLeft: {
                x: (bottomLeft) ? bottomLeft[1] : null,
                y: (bottomLeft) ? bottomLeft[2] : null
            },
            bottomRight: {
                x: (bottomRight) ? bottomRight[1] : null,
                y: (bottomRight) ? bottomRight[2] : null
            },
            camera: {
                host: row.find('.instanceConfigsTable-cameraHost').val() || 'localhost',
                port: row.find('.instanceConfigsTable-cameraPort').val() || 8080
            },
            kinect: {
                host: row.find('.instanceConfigsTable-kinectHost').val() || 'localhost',
                port: row.find('.instanceConfigsTable-kinectPort').val() || 8081
            }
        };

        console.log(id, data);
        socket.emit('update_instanceConfig', id, data);
        socket.once('update_instanceConfig', updateInstanceConfigRow);
     });

    // DELETE
    $(document).on('click', '.instanceConfigsTable-remove', function() {
        var row = $(this).parent().parent();
        var id = row.find('.instanceConfigsTable-configId').text();

        socket.emit('delete_instance_configuration', id);
        socket.once('delete_instance_configuration', function(success) {
            if (success) {
                row.remove();
                $('option[value="' + id + '"').remove();
            }
        })
    });

    $(document).on('click', '.instanceConfigsTable-calibrate', function() {
        calibrationOverlay.css('visibility', 'visible')
        var row = $(this).parent().parent();
        var id = row.find('.instanceConfigsTable-configId').text();

        socket.emit('calibrate_instance_configuration', id);
    });

    $(document).on('click', '.toggle-kinect-enable', function() {
        socket.emit('toggle_kinect_enable');
    });

    socket.on('calibrate_instance_configuration', function(instanceConfiguration) {
        calibrationOverlay.css('visibility', 'hidden')
        updateInstanceConfigRow(instanceConfiguration);
    });

    socket.emit('get_instance_configurations');

});
