$('#feed-options').on('shown', function () {
    $("#feed-options-icon").removeClass("icon-chevron-down");
    $("#feed-options-icon").addClass("icon-chevron-up");
});

$('#feed-options').on('hidden', function () {
    $("#feed-options-icon").removeClass("icon-chevron-up");
    $("#feed-options-icon").addClass("icon-chevron-down");
});

$('#filter-submit').on('click', function (e) {
    e.preventDefault();
    // console.log($('.tab-pane.active .video.row .video-uploader a').attr('href'));

    var checkboxes = $('.mindcrackers-select input:checked');
    var to_view = [];

    checkboxes.each(function(index, checkbox) {
        to_view.push($(checkbox).val());
        // to_view[$(checkbox).val()] = true;
    });

    var query = "mindcrackers=";

    $(to_view).each(function(index, m) {
        query += m;

        if(index !== to_view.length -1)
            query += ",";
    });

    console.log(query);
    
    $.getJSON('/filter', query, function(data, textStatus) {
        console.log(data);
        videos = data;

        $('.video.row').remove();

        var video_template = '{{#videos}}<div class="video row"><div class="video-thumbnail span2"><a href="http://www.youtube.com/watch?v={{ video_id }}"><img src="{{thumbnail}}" alt="{{ title }} thumbnail"></a></div><div class="video-info span10"><h2 class="video-title"><a href="http://www.youtube.com/watch?v={{ video_id }}">{{ title }}</a></h2><h3 class="video-uploader"><a href="http://www.youtube.com/{{ uploader }}">{{ uploader }}</a></h3><p>{{#truncate}}{{ description }}{{/truncate}}<a href="#">...</a></p><span>{{ duration }}</span><p>{{ uploaded }}</p></div></div>{{/videos}}';

        var video_view = {
            videos: videos,
            truncate: function() {
                return function(text, render) {
                    return render(text).substring(0, 300);
                };
            }
        };

        $('.tab-pane.active').append($.mustache(video_template, video_view));
    });
});

$(".expand-description").on('click', function(e) {
    e.preventDefault();

    video_id = $(e.target).parents('.video.row').attr('data-video-id');
    console.log(video_id);
    yt_api_url = 'https://gdata.youtube.com/feeds/api/videos/' + video_id + '?v=2&alt=jsonc';

    $.getJSON(yt_api_url, function(data, textStatus) {
        console.log(data.data.description + ' ' + textStatus);
        $(e.target).parent().replaceWith(data.data.description);
    });
});