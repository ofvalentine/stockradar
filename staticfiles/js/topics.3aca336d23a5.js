var topicsPromise = d3.json('https://stockradar.herokuapp.com/api/topics/').then(function (data) {

  // GET DATA FROM API
  var topicKeywords = [];
  var i = 0;
  var compoundWords = {
    "wells": "fargo",
    "wall": "street",
    "hong": "kong",
    "jp": "morgan"
  };

  Object.entries(data).forEach(([topic, keywords]) => {
    $('#topics-list').append('<a class="topic" href="javascript:void(0);" id="' + i + '">' + topic + '</a>');
    topicKeywords[i] = [];
    keywords.forEach(([keyword, frequency, articles]) => {
      if (keyword in compoundWords) { keyword += " " + compoundWords[keyword]; }
      if (width < 768) { frequency = frequency*0.7; }
      topicKeywords[i].push({ name: keyword, frequency: frequency, articles: articles });
    });
    i++
  });
  
  $('.topic').hide();

  $(document).on("click", ".topic", function() {
    $('.topic').hide(300);
    $('#changing-text').html($(this).text());
    $('#restore-default').show();
    createBubbles(topicKeywords[$(this).attr('id')]);
    $('html, body').animate({ scrollTop: 0 }, 1000);
  });
});

function showTopics() {
  $('.topic').toggle(300);
}

$('#bubbles-container').click(function () {
  $('.topic').hide(300);
});
