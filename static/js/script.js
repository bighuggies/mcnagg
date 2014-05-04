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
    $('.video').remove();
}


function remove_video(video_id) {
    $('.video[data-video-id="' + video_id + '"]').hide(100);
}


function append_videos(videos) {
    $('.video-list').append(videos);

    $('#show-more').show();
    $(".loading-gif").hide();
}


function fetch_videos(query_data, callback) {
    $(".loading-gif").show();

    $('#show-more').hide('fast', function() {
        $.get('/videos', query_data, callback);
    });
}


function options_submit(e) {
    e.preventDefault();

    var title_filter = $('#title-filter').val();

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
    var offset = $('.video').length;

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

    $('#feed-options').on('show.bs.collapse', function () {
        $("#feed-options-icon").removeClass("fa-chevron-down");
        $("#feed-options-icon").addClass("fa-chevron-up");
    });

    $('#feed-options').on('hide.bs.collapse', function () {
        $("#feed-options-icon").removeClass("fa-chevron-up");
        $("#feed-options-icon").addClass("fa-chevron-down");
    });

    $(".video-list").on('click', ".video-remove-control", function(e) {
        remove_video($(e.currentTarget).data('video-id'));
        e.preventDefault();
    });

    $(".video-list").on("click", ".show-description", function(e) {
        var $target = $(e.currentTarget);
        var $desc = $target.parent();

        $desc.css({"height": $desc[0].scrollHeight});

        $target.html('<i class="fa fa-caret-up"></i>');
        $target.toggleClass("hide-description show-description");

        e.preventDefault();
    });

    $(".video-list").on("click", ".hide-description", function(e) {
        var $target = $(e.currentTarget);
        var $desc = $target.parent();

        $desc.css({"height": "60px"});

        $target.html('<i class="fa fa-caret-down"></i>');
        $target.toggleClass("hide-description show-description");

        e.preventDefault();
    });
});
