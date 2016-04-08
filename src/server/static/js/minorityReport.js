var socket = io();

var POSTIT_SIZE = 100;
var width = $(window).width()-50, height = $(window).height()-50;
var scaleFactor = Math.max(width, height) * 175;

console.log("width: " + width);
console.log("height: " + height);
console.log("SF: " + scaleFactor);


socket.on("getAll", processResponse);
socket.emit("getAll", []);

var svg = d3.select('body').append('svg')
    .attr('width', width)
    .attr('height', height);


function processResponse(received)
{
  console.log(received)
  //var received = $.parseJSON(jsonData);
  var idToIndex = new Array();
  $.each(received.postits, function(index, note)
  {
    //console.log(index, note);
    idToIndex[note.postitId] = index;
  });

  var nodes = [];

  var links = [
      //{ source: 0, target: 1 },
      //{ source: 1, target: 0 }
  ];

  $.each(received.postits, function(index, note)
  {
    console.log(note);
    nodes.push({fixed:true, x:scaleFactor/note.realX, y:scaleFactor/note.realY});
    //note image?
    if (note.connections.length > 0)
    {
      $.each(note.connections, function(index, connectionId)
      {
        console.log("Connection index:" + index, connectionId);
        links.push({source: idToIndex[note.postitId], target: idToIndex[connectionId]});
      });
    }
  });

  console.log(links);

  var force = d3.layout.force()
    .size([width, height])
    .nodes(nodes)
    .links(links);

  force.linkDistance(width/2);

  var link = svg.selectAll('.link')
    .data(links)
    .enter().append('line')
    .attr('class', 'link');

  var node = svg.selectAll('.node')
    .data(nodes)
    .enter().append('rect')
    .attr('class', 'node')
    .attr("width", POSTIT_SIZE)
    .attr("height", POSTIT_SIZE);

  force.on('end', function() {

    // When this function executes, the force layout
    // calculations have concluded. The layout will
    // have set various properties in our nodes and
    // links objects that we can use to position them
    // within the SVG container.

    // First let's reposition the nodes. As the force
    // layout runs it updates the `x` and `y` properties
    // that define where the node should be centered.
    // To move the node, we set the appropriate SVG
    // attributes to their new values. We also have to
    // give the node a non-zero radius so that it's visible
    // in the container.

    node.attr('x', function(d) { return d.x; })
        .attr('y', function(d) { return d.y; });

    // We also need to update positions of the links.
    // For those elements, the force layout sets the
    // `source` and `target` properties, specifying
    // `x` and `y` values in each case.

    link.attr('x1', function(d) { return d.source.x; })
        .attr('y1', function(d) { return d.source.y; })
        .attr('x2', function(d) { return d.target.x; })
        .attr('y2', function(d) { return d.target.y; });

  });

  force.start();
}
