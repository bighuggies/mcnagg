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


function get_HMS(time) {
    hours = Math.floor(time / 3600);
    minutes = Math.floor(time / 60) - hours * 60;
    seconds = time - (hours * 3600) - (minutes * 60);

    console.log((hours > 0 ? hours + ':' : '') + minutes + ':' + (seconds > 10 ? seconds : '0' + seconds));

    return((hours > 0 ? hours + ':' : '') + (minutes > 10 ? minutes + ':' : '0' + minutes + ':') + (seconds > 10 ? seconds : '0' + seconds));
}


function get_fancy_time(date) {
    milliseconds = Date.now() - Date.parse(date);

    if (milliseconds < 0) {
        return('Some time in the future');
    }

    var seconds = milliseconds / 1000;
    var minutes = seconds / 60;
    var hours = seconds / 60 / 60;
    var days = seconds / 60 / 60 / 24;
    var months = days / 30;

    var deltas = [seconds, minutes, hours, days, months];
    var units = ['second', 'minute', 'hour', 'day', 'month'];
    var plural = false;
    var fuzzy_delta = 0;
    var unit_index = 0;

    $(deltas).each(function(i, delta) {
        if (Math.floor(delta) > 0) {
            fuzzy_delta = Math.floor(delta);
            unit_index = i;
        }
    });

    if (fuzzy_delta > 1) {
        plural = true;
    }

    return(fuzzy_delta + ' ' + units[unit_index] + ((plural === true) ? 's' : '') + ' ago');
}


function remove_videos() {
    $('.video.row').remove();
}


function append_videos(videos) {
    $('.loading.row').remove();

    var video_template = '{{#videos}}<div class="video row" data-video-id="{{video_id}}"><div class="video-thumbnail span3"><a href="http://www.youtube.com/watch?v={{ video_id }}"><img src="{{thumbnail}}" alt="{{ title }} thumbnail"></a></div><div class="video-info span9"><div class="well"><h2 class="video-title"><a href="http://www.youtube.com/watch?v={{ video_id }}">{{ title }}</a></h2><h3 class="video-uploader"><a href="http://www.youtube.com/{{ uploader }}">{{ uploader }}</a></h3><p>{{#truncate}}{{ description }}{{/truncate}}<a class="expand-description" href="#">... (read more)</a></p><span>{{#hms}}{{ duration }}{{/hms}}</span><p>Uploaded {{#fancy_time}}{{ uploaded }}{{/fancy_time}}</p></div></div></div>{{/videos}}';

    var video_view = {
        videos: videos,
        truncate: function() {
            return function(text, render) {
                return render(text).substring(0, 300);
            };
        },
        fancy_time: function() {
            return function(text, render) {
                return get_fancy_time(render(text));
            };
        },
        hms: function() {
            return function(text, render) {
                console.log(text + ' ' + render(text));
                return get_HMS(render(text));
            };
        }
    };

    $('.tab-pane.active').append($.mustache(video_template, video_view));

    bind_event_handlers();
}


function fetch_videos(query_data, callback) {
    $('.tab-pane.active').append('<div class="loading row"><div class="span12" style="text-align:center;padding-top:10px"><img class="loading-gif" src="static/img/loading.gif" /></div></div>');

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
    
    remove_videos();

    fetch_videos(query, append_videos);
}


function show_more_videos(e) {
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
    e.preventDefault();

    video_id = $(e.target).parents('.video.row').attr('data-video-id');
    yt_api_url = 'https://gdata.youtube.com/feeds/api/videos/' + video_id + '?v=2&alt=jsonc';

    $.getJSON(yt_api_url, function(data, textStatus) {
        $(e.target).parent().replaceWith('<p class="video-description">' + data.data.description + ' <a href="#" class="truncate-description">(read less)</a></p>');
        bind_event_handlers();
    });

}

function truncate_description(e) {
    e.preventDefault();
    console.log('truncating ' + $(e.target).parent().val());
    $(e.target).parent().replaceWith('<p class="video-description">' + $(e.target).parent().text().substring(0, 300) + '<a class="expand-description" href="#">... (read more)</a></p>');
    bind_event_handlers();
}


function bind_event_handlers() {
    $('#options-submit').on('click', options_submit);
    $('.show-more').on('click', show_more_videos);
    $('.expand-description').on('click', expand_description);
    $('.truncate-description').on('click', truncate_description);
}


bind_event_handlers();
