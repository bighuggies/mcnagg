function get_HMS(time) {
    hours = Math.floor(time / 3600);
    minutes = Math.floor(time / 60) - hours * 60;
    seconds = time - (hours * 3600) - (minutes * 60);

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
    $('.divider.row').remove();
}


function remove_video(video_id) {
    $('div[data-video-id="' + video_id + '"]').hide(100);
}


function append_videos(videos) {
    $('.loading.row').remove();

    var video_template = '{{#videos}}<div class="video row" data-video-id="{{ video_id }}"><div class="video-thumbnail col-md-2"><a href="http://www.youtube.com/watch?v={{ video_id }}"><img width="120px" src="{{ thumbnail }}" alt="{{ title }} thumbnail"></a></div><div class="col-md-9"><h2 class="video-title-duration"><span class="video-title"><a href="http://www.youtube.com/watch?v={{ video_id }}">{{ title }}</a></span><span class="video-duration"> ({{#hms}}{{duration}}{{/hms}})</span></h2><p class="video-uploader-uploaded"><span class="video-uploader"><a href="http://www.youtube.com/{{ uploader }}">{{ uploader }}</a></span><span class="video-uploaded"> uploaded {{#fancy_time}}{{uploaded}}{{/fancy_time}}</span></p></div><div class="video-controls col-md-1"><div class="pull-right"><a href="#"> <i data-video-id="{{ video_id }}" class="icon-remove video-remove-control"></i></a></div></div></div><div class="divider row" data-video-id="{{ video_id }}"><div class="col-md-12"><hr class="video-divider"></div></div>{{/videos}}';

    var video_view = {
        videos: videos,
        fancy_time: function() {
            return function(text, render) {
                return get_fancy_time(render(text));
            };
        },
        hms: function() {
            return function(text, render) {
                return get_HMS(render(text));
            };
        }
    };

    $('#show-more').before($.mustache(video_template, video_view));
    $('#show-more').show();
}


function fetch_videos(query_data, callback) {
    $('.video-list').append('<div class="loading row"><div class="span9" style="text-align:center;padding-top:10px"><img class="loading-gif" src="static/img/loading.gif" /></div></div>');
    $('#show-more').hide('fast', function() {
        $.getJSON('/videos', query_data, callback);
    });
}


function options_submit(e) {
    e.preventDefault();

    var title_filter = $('#title-filter').val();
    var offset = $('.video.row').length;

    var query = {
        'offset': 0,
        'mindcrackers[]': get_mindcrackers(),
        'title_filter': title_filter ? title_filter : ''
    };

    remove_videos();

    fetch_videos(query, append_videos);
}


function show_more_videos(e) {
    e.preventDefault();

    var title_filter = $('#title-filter').val();
    var offset = $('.video.row').length;

    var query = {
        'offset': offset,
        'mindcrackers[]': get_mindcrackers(),
        'title_filter': title_filter ? title_filter : ''
    };

    fetch_videos(query, append_videos);
}


function get_mindcrackers() {
    return $('input[name="mindcrackers-select"]:checked').map(function(i, e){
        return $(e).val();
    }).get();
}


function select_all_mindcrackers(e) {
    e.preventDefault();

    $('input[name="mindcrackers-select"]').each(function(index, element) {
        $(element).prop('checked', true);
    });
}


function deselect_all_mindcrackers(e) {
    e.preventDefault();

    $('input[name="mindcrackers-select"]:checked').each(function(index, element) {
        $(element).prop('checked', false);
    });
}


$(document).ready(function() {
    $('#options-form').on('submit', options_submit);
    $('#show-more').on('click', show_more_videos);
    $('#select-all').on('click', select_all_mindcrackers);
    $('#deselect-all').on('click', deselect_all_mindcrackers);

    $('#feed-options').on('shown', function () {
        $("#feed-options-icon").removeClass("icon-chevron-down");
        $("#feed-options-icon").addClass("icon-chevron-up");
    });

    $('#feed-options').on('hidden', function () {
        $("#feed-options-icon").removeClass("icon-chevron-up");
        $("#feed-options-icon").addClass("icon-chevron-down");
    });

    $(".video-list").on('click', function(e) {
        if ($(e.target).hasClass('video-remove-control')) {
            remove_video($(e.target).data('video-id'));
        }
    });
});
