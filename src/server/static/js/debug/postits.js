var postitsTable = $('.postits-tableBody');
var postits = [];

function updatePostits() {
    console.log('Updating Postits');
    $('.postits-PostitRow').remove();
    var template = $('.postits-tableBody > .postits-row_template');

    postits.forEach(function(postit) {
        var tr = template.clone();
        tr.removeClass('table-row_template');
        tr.addClass('postits-postitRow');

        $(tr).insertBefore(postitsTable.children().last());
        tr.find('.postits-id').text(postit.id);
        tr.find('.postits-image').attr('src', 'api/postit/' + postit.id);
        tr.find('.postits-x').val(postit.realX);
        tr.find('.postits-y').val(postit.realY);
        tr.find('.postits-width').val(postit.width);
        tr.find('.postits-height').val(postit.height);

        tr.find('.postits-keystone-x1').val(postit.keystone1X);
        tr.find('.postits-keystone-y1').val(postit.keystone1Y);
        tr.find('.postits-keystone-x2').val(postit.keystone2X);
        tr.find('.postits-keystone-y2').val(postit.keystone2Y);
        tr.find('.postits-keystone-x3').val(postit.keystone3X);
        tr.find('.postits-keystone-y3').val(postit.keystone3Y);
        tr.find('.postits-keystone-x4').val(postit.keystone4X);
        tr.find('.postits-keystone-y4').val(postit.keystone4Y);
    });
}

// Show Postit
body.on('click', '.postits-id', function() {
    $(this).parent().find('.postits-image').toggle()
});

socket.on('getPostits', function(data) {
    console.log('GetPostits', arguments);
    postits = data;
    updatePostits();
});

socket.on('autoExtractPostits', function() {
    console.log('autoExtractPostits', arguments);
    socket.emit('getPostits');
});

socket.emit('getPostits');
