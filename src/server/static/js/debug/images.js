var imagesTable = $('.images-tableBody');
var images = [];

function updateImages() {
    console.log('Updating Images');
    $('.images-imageRow').remove();
    var template = $('.images-tableBody > .table-row_template');

    images.forEach(function(image) {
        var tr = template.clone();
        tr.removeClass('table-row_template');
        tr.addClass('images-imageRow');

        $(tr).insertBefore(imagesTable.children().last());
        tr.find('.images-id').text(image.id);
        tr.find('.images-image').attr('src', 'api/image/' + image.id);
        tr.find('.images-timestamp').val(new Date(image.timestamp).toISOString());

        $('.image-select').append($('<option></option>')
            .attr('value', image.id)
            .text(image.id))
    });
}
function storeUriInCache () {
    var uri = $('.imageUri').val();

    if(typeof(Storage) !== "undefined") {
        localStorage.setItem('cameraUri', uri);
        console.log('Setting URI local storage to', uri);
    } else {
        console.error('Browser does not support Local Storage');
    }
}

body.on('click', '.imageFromUriBtn', function () {
    storeUriInCache();
    socket.emit('addImageFromUri', $('.imageUri').val());
});

body.on('click', '.focusImageBtn', function() {
    storeUriInCache();
    socket.emit('cameraFocus', $('.imageUri').val());
});

body.on('click', '.getCameraProperties', function() {
    storeUriInCache();
    socket.emit('getCameraProperties', $('.imageUri').val());
});

body.on('click', '.setCameraProperties', function() {
    storeUriInCache();
    socket.emit('setCameraProperties', $('.imageUri').val(), $('.cameraSettings').text());
});

body.on("click", ".force-canvas-send", function()
{
    socket.emit("updateCanvas", {});
});

body.on('focusout', '.images-timestamp', function(){
    var children = $(this).parent().parent();

    var properties = {
        id: children.find('.images-id').text(),
        timestamp: children.find('.images-timestamp').val()
    };

    console.log(properties);

    socket.emit('updateImage', properties)
});

body.on('click', '.images-add', function() {
    var row = $(this).parent().parent();
    console.log(row);
    var files = row.find('.images-file').prop('files');
    var ts = row.find('.images-timestamp').val();
    console.log("Timestamp:", ts)

    var properties = {
        timestamp: new Date(ts).toISOString()
    };

    if (properties.timestamp && files.length > 0) {
        properties.timestamp = new Date(properties.timestamp);
        var file = files[0];
        properties.name = file.name;

        var fr = new FileReader();
        fr.addEventListener('loadend', function() {
            console.log('fr loaded, file is', fr.result.byteLength, 'bytes long');
            properties.file = fr.result;
            socket.emit('addImage', properties);
        });
        fr.addEventListener('progress', function(event) {
            console.log('fr progress', (100 * (event.loaded/event.total)), '%');
        });

        fr.readAsArrayBuffer(file);
    } else {
        console.log('Not uploading, missing details');
        return
    }

    console.log(properties);
});

// on user delete button
body.on('click', '.images-remove', function() {
    var row = $(this).parent().parent();
    var properties = {
        id: row.find('.images-id').text()
    };
    console.log('Deleting image', properties);
    socket.emit('deleteImage', properties);
});

// Show image
body.on('click', '.images-id', function() {
    $(this).parent().find('.images-image').toggle()
});

body.on('click', '.images-extractCanvas', function() {
    var imageId = $(this).parent().parent().find('.images-id').text();
    console.log('Extract Canvas', imageId);
    socket.emit('autoExtractCanvas', imageId);
});

socket.on('autoExtractCanvas', function(data) {
    console.log('autoExtractCanvases', arguments)
    socket.emit('getCanvases');
});

socket.on('addImage', function() {
    console.log('addImage', arguments);
    $('.images-image_new').val('');
    socket.emit('getImages');
});

socket.on('getImages', function(data) {
    console.log('getImages', arguments);
    images = data;
    updateImages();
});

socket.on('updateImage', function(data) {
    console.log('updateTimestamp', arguments);
    socket.emit('getImages');
});

socket.on('deleteImage', function(data) {
    console.log('deleteImage', arguments);
    socket.emit('getImages');
});

socket.on('addImageFromUri', function(data) {
    console.log('addImageFromUri', arguments);
    socket.emit('getImages');
});

socket.on('getCameraProperties', function(data) {
    console.log('getCameraProperties', arguments);
    $('.cameraSettings').text(JSON.stringify(data, null, 2));
});

socket.on('cameraFocus', function(data) {
    console.log('cameraFocus got response', data);
    alert('Camera Focus ' + ((data) ? 'Success' : 'Failed' ));
});

socket.on('setCameraProperties', function(data) {
    console.log('setCameraProperties got response', data);
    alert('Set Camera Properties ' + ((data) ? 'Success' : 'Failed' ));
});

if(typeof(Storage) !== "undefined") {
    $('.imageUri').val(localStorage.getItem('cameraUri') || "http://localhost:8080");
}

socket.emit('getImages');
