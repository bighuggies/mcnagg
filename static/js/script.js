var videos_per_page = 30;

$('#feed-options').on('shown', function () {
    $("#feed-options-icon").removeClass("icon-chevron-down");
    $("#feed-options-icon").addClass("icon-chevron-up");
});


$('#feed-options').on('hidden', function () {
    $("#feed-options-icon").removeClass("icon-chevron-up");
    $("#feed-options-icon").addClass("icon-chevron-down");
});


$('#options-cancel').on('click', function() {
    $('#feed-options').trigger('hidden');
});


function replace_videos(videos) {
    $('.video.row').remove();
    append_videos(videos);
}


function append_videos(videos) {
    var video_template = '{{#videos}}<div class="video row" data-video-id="{{video_id}}"><div class="video-thumbnail span3"><a href="http://www.youtube.com/watch?v={{ video_id }}"><img src="{{thumbnail}}" alt="{{ title }} thumbnail"></a></div><div class="video-info span9"><div class="well"><h2 class="video-title"><a href="http://www.youtube.com/watch?v={{ video_id }}">{{ title }}</a></h2><h3 class="video-uploader"><a href="http://www.youtube.com/{{ uploader }}">{{ uploader }}</a></h3><p>{{#truncate}}{{ description }}{{/truncate}}<a class="expand-description" href="#">...</a></p><span>{{ duration }}</span><p>{{ uploaded }}</p></div></div></div>{{/videos}}';

    var video_view = {
        videos: videos,
        truncate: function() {
            return function(text, render) {
                return render(text).substring(0, 300);
            };
        }
    };

    $('.tab-pane.active').append($.mustache(video_template, video_view));
}


function fetch_videos(query_data, callback) {
    $.getJSON('/videos', query_data, callback);
}


function options_submit(e) {
    e.preventDefault();

    var num_videos = $('#number-videos').val();

    var query = {
        'num-videos': num_videos,
        'offset': 0,
        'mindcrackers[]': get_mindcrackers()
    };
    
    fetch_videos(query, replace_videos);
}


function show_more(e) {
    e.preventDefault();

    var num_videos = $('#number-videos').val();
    var offset = $('.video.row').length;

    var query = {
        'num-videos': num_videos,
        'offset': offset,
        'mindcrackers[]': get_mindcrackers()
    };
    
    fetch_videos(query, append_videos);
}


function get_mindcrackers() {
    var checkboxes = $('.mindcrackers-select input:checked');
    var mindcrackers = [];

    checkboxes.each(function(index, checkbox) {
        mindcrackers.push($(checkbox).val());
    });

    return mindcrackers;
}


function expand_description(e) {
    console.log('expanding');
    e.preventDefault();

    video_id = $(e.target).parents('.video.row').attr('data-video-id');
    yt_api_url = 'https://gdata.youtube.com/feeds/api/videos/' + video_id + '?v=2&alt=jsonc';

    $.getJSON(yt_api_url, function(data, textStatus) {
        $(e.target).parent().replaceWith('<p class="video-description">' + data.data.description + '</p>');
    });
}


function bind_event_handlers() {
    $('#options-submit').on('click', options_submit);
    $('.show-more').on('click', show_more);
    $(".expand-description").on('click', expand_description);
}


bind_event_handlers();