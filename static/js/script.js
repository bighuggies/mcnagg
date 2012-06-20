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


function remove_video(e) {
    e.preventDefault();
    $(e.target).parents('.video.row').hide(100);
}



function append_videos(videos) {
    $('.loading.row').remove();
    $('#show-more').show();

    var video_template = '{{#videos}}<div class="video row" data-video-id="{{video_id}}"><div class="video-thumbnail span1"><a href="http://www.youtube.com/watch?v={{video_id}}"><img src="{{thumbnail}}" alt="{{title}} thumbnail"></a></div><div class="video-title-duration span9"><h2 class="video-title"><span class="video-title"><a href="http://www.youtube.com/watch?v={{video_id}}">{{title}}</a></span><span class="video-duration"> ({{#hms}}{{duration}}{{/hms}})</span></h2><p class="video-uploader-uploaded"><span class="video-uploader"><a href="http://www.youtube.com/{{ uploader }}">{{ uploader }}</a></span><span class="video-uploaded"> uploaded {{#fancy_time}}{{uploaded}}{{/fancy_time}}</span></p></div><div class="video-controls span2"><div class="pull-right"><a href="#"><i class="icon-remove video-remove-control"></i></a></div></div><div class="span12"><hr></div></div>{{/videos}}';

    var video_view = {
        videos: videos,
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

    $('.video-remove-control').on('click', remove_video);
}


function fetch_videos(query_data, callback) {
    $('.tab-pane.active').append('<div class="loading row"><div class="span12" style="text-align:center;padding-top:10px"><img class="loading-gif" src="static/img/loading.gif" /></div></div>');
    $('#show-more').hide('fast', function() {
            $.getJSON('/videos', query_data, callback);
    });
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


$('.video-remove-control').on('click', remove_video);
$('#options-submit').on('click', options_submit);
$('#show-more').on('click', show_more_videos);
