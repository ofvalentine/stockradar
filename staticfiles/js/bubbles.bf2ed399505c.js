function createBubbles (data) {

  $("#bubbles-container").empty();

  // CREATE DEFS FOR GRADIENTS AND BLUR
  var defs = d3.select("#bubbles-container").append("defs");

  // BIND DATA AND DRAG BEHAVIOUR
  var bubble = d3.select("#bubbles-container")
    .selectAll("circle")
    .data(data)
    .enter()
    .append("g")
    .call(d3.drag()
      .on("start", dragstarted)
      .on("drag", dragged)
      .on("end", dragended));

  // CREATE BUBBLE
  bubble.append("circle")
    .attr("class", "bubble")
    .attr("r", function (d) { return d.frequency; })
    .on("click", function (d) {
      $('#articles-notice-text').hide();
      $('#articles-container').css("display", "flex");

      for (var i=0; i < 6; i++) {
        // TIME SINCE FETCHING ARTICLE
        var now = new Date();
        var timestamp = new Date(d.articles[i][3]);
        interval = now.getTime() - timestamp.getTime();
        minutesPassed = Math.floor(interval / 1000 / 60);
        $('#timestamp-'+i).html('Retrieved ' + minutesPassed + ' minutes ago');

        // PASS KEYWORDS TO HTML
        $('#keywords-container-'+i).empty();
        d.articles[i][2].forEach(keyword => { 
          $('#keywords-container-'+i).append('<h6 class="keywords">' + keyword + '</h6>');
        });

        // PASS SOURCE + TITLE TO HTML
        $('#source-'+i).html(d.articles[i][0]);
        $('#title-'+i).html(d.articles[i][1]);
        $('#link-'+i).attr("href", d.articles[i][4]);
      }
      $('html, body').animate({ scrollTop: $('#articles-container').offset().top }, 1000);
    });

  // TEXT SETTINGS
  bubble
    .append("text")
    .text(function (d) { return d.name; })
    .attr("class", "name")
    .attr("font-size", function (d) { return d.frequency / 6; });

  // SET BUBBLE ANIMATION + INTERACTION
  var simulation = d3.forceSimulation()
    .force("x", d3.forceX().strength(xStrength).x(xForce))
    .force("y", d3.forceY().strength(yStrength).y(yForce))
    .force("center", d3.forceCenter().x(xForce).y(yForce))
    .force("charge", d3.forceManyBody().strength(0.5))
    .force("collide", d3.forceCollide().strength(.4).radius(function (d) { return d.frequency + 5; }).iterations(0.5));

  // DRAG FUNCTIONS
  function dragstarted(d) {
    if (!d3.event.active) simulation.alphaTarget(0.03).restart();
    d.fx = d.x;
    d.fy = d.y;
  }
  function dragged(d) {
    d.fx = d3.event.x;
    d.fy = d3.event.y;
  }
  function dragended(d) {
    if (!d3.event.active) simulation.alphaTarget(0.03);
    d.fx = null;
    d.fy = null;
  }

  // START BUBBLE ANIMATION
  simulation.nodes(data).on("tick", function (d) {
    bubble.attr("cx", function (d) { return d.x; })
      .attr("cy", function (d) { return d.y; });
  });
  simulation.on("tick", function (e) {
    bubble.attr("transform", function (d) { return "translate(" + d.x + "," + d.y + ")"; });
  });
}