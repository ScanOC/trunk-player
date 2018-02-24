// Global Setup

// Live PlayBack, try and play next newest transmission
live_play_back = 1;
// Live Update, pull new transmissions from site
live_update = 1;

active_play=1;
// Is the page curently being built
buildpage_running = 0;
currently_playing=0;
last_call = 0;
// Set base name from settings
var page_title = js_config.SITE_TITLE;
first_load = 1;
first_play = 1;
seen = [];
curr_id_list = [];
curr_file_list = [];
curr_tg_list = [];
curr_tg_slug_list = [];
var force_page_rebuild = 0;
var base_api_url = "/api_v1/";
var api_url = null;
var url_params = null;
var pagination_older_url = null;
var pagination_newer_url = null;
var muted_tg = {};
var show_limit_warning = true;

var base_audio_url = js_config.AUDIO_URL_BASE;

var buildpage_running = 0;

update_unit_url = "";
unit_submit_action = "";

function update_scan_list() {
    start_socket();   
    buildpage();
}

function start_scanner() {
    play_clip(base_audio_url + 'point1sec.mp3', 0, 0);
    $(".stop-btn").show();
    $(".start-btn").hide();
}

function stop_scanner() {
    $("#jquery_jplayer_1").jPlayer("stop");
    active_play = 0;
    $(".active-trans").removeClass("active-trans");
    $(".stop-btn").hide();
    $(".start-btn").show();
    $(document).prop('title', page_title);
}

function mute_click(tg) {
    if (muted_tg[tg]) {
        muted_tg[tg] = false;
        $('.mute-tg-' + tg).removeClass('mute-mute ');
    } else {
        muted_tg[tg] = true;
        $('.mute-tg-' + tg).addClass('mute-mute ');
    }
    live_update = 1; // Let page update to show the mute
    buildpage();
}

function update_pagination_links() {
    pagination_html = "";
    if(pagination_newer_url) {
        pg_array = pagination_newer_url.split( '?' );
        new_url = window.location.pathname + '?' + pg_array[1];
        home_url = window.location.pathname;
        pagination_html = '<button onclick="url_change(\'' + home_url + '\')">Current</button>';
        pagination_html += '<button onclick="url_change(\'' + new_url + '\')">Newer</button>';
    }
    if(pagination_older_url) {
        pg_array = pagination_older_url.split( '?' );
        new_url = window.location.pathname + '?' + pg_array[1];
        pagination_html += '<button onclick="url_change(\'' + new_url + '\')">Older</button>';
        $("#anoymous_time_warn").hide();
    } else {
        if(show_limit_warning) {
            $("#anoymous_time_warn").show();
        }
    }
    //$('#pagination').html(pagination_html);
    return pagination_html;
}
function update_api_url() {
    url_params = document.location.search;
    pathArray = window.location.pathname.split( '/' );
    pathArray.shift();
    if(pathArray[0] == "inc") {
        show_limit_warning = false;
    } else {
        show_limit_warning = true;
    }
    if(pathArray[0] == "scan2") {
      pathArray[0] = "scan";
    }
    if(pathArray[0] == "userscan") {
        // Build TGs from select box
        tg_array = $('.tg-multi-select').select2("val");
        if(tg_array) {
          api_url = base_api_url + "tg/" + tg_array.join('+');
        } else {
          api_url = null;
        }
    } else {
        api_url = base_api_url + pathArray.join('/');
    }
    if(api_url && url_params) {
        api_url = api_url + url_params;
    }
    //start_socket(); // reconnect with new talkgroups
}

function url_change(new_url) {
    clearpage();
    // Simple funcation to change url and rebuild the page
    var stateObj = { foo: "bar" };
    window.history.pushState(stateObj, page_title, new_url);
    //window.history.pushState(.object or string., .Title., ./new-url.);
    $("#jquery_jplayer_1").jPlayer("stop");
    force_page_rebuild = 1;
    first_load = 1;
    first_play = 1;
    buildpage();
    return false;
}

function clearpage() {
    if(buildpage_running == 1) {
       return false;
    }
    $('#main-data-table').html("<p style='text-align: center'><img src='/static/radio/img/loader.gif' />");
    $('#pagination').html("");
}

function update_menu() {
    // ScanList Header
    url = '/api_v1/menuscanlist/';
    new_html_live = '';
    new_html = '';
    count = 0;
    $.getJSON(url, function(data) {
        for (var a in data.results) {
            new_html_live += '<li><a href="/scan/' + data.results[a].scan_slug + '/" onclick="return url_change(\'/scan/' + data.results[a].scan_slug + '/\');">' + data.results[a].scan_description + '</a></li>';
            new_html += '<li><a href="/scan/' + data.results[a].scan_slug + '/">' + data.results[a].scan_description + '</a></li>';
            count++;
        }
        if(count == 0) {
            new_html += '<li><a href="/scan/default/">Default</a></li>';
        }
        a  = '<li class="divider"></li>';
        a += '<li><a href="/userscan/">Custom Scan List</a></li>';
        new_html_live += a;
        new_html += a;
        $('#menu-scanlist-live').html(new_html_live);
        $('#menu-scanlist').html(new_html);
    });

    // TalkGroup Header
    url2 = '/api_v1/menutalkgrouplist/';
    new_html2_live = '';
    new_html2 = '';
    $.getJSON(url2, function(data) {
        for (var a in data.results) {
            new_html2_live += '<li><a href="/tg/' + data.results[a].tg_slug + '/" onclick="return url_change(\'/tg/' + data.results[a].tg_slug + '/\');">' + data.results[a].tg_name + '</a></li>';
            new_html2 += '<li><a href="/tg/' + data.results[a].tg_slug + '/">' + data.results[a].tg_name + '</a></li>';
        }
        a  = '<li class="divider"></li>';
        a += '<li><a href="/talkgroups/">List All Talkgroups</a></li>';
        new_html2_live += a
        new_html2 += a
        $('#menu-talkgrouplist-live').html(new_html2_live);
        $('#menu-talkgrouplist').html(new_html2);
    });


}

var last_ajax;
var last_message;

function updatemessage() {
    message_url = "/api_v1/message/"
    hide_message = true
    $.getJSON(message_url, function(data) {
        if(data.count > 0) {
            for (var a in data.results) {
                curr_message = data.results[a];
                if(data.results[a]['mesg_type'] == 'A') {
                    new_msge_data = data.results[a]['mesg_html']
                    if(last_message != new_msge_data) {
                        hide_message = false
                        $( "#main-message" ).html(data.results[a]['mesg_html']);
                        last_message = new_msge_data;
                    $("#main-message" ).show()
                    } 
                    /* Make sure its visable even if its not new */
                }
            }
        } else {
           last_message = ""
           $( "#main-message" ).hide()
        }
    })
    .fail(function() {
        last_message = ""
        $( "#main-message" ).hide()
    });
}


function buildpage() {
    if(buildpage_running == 1 || live_update == 0) {
       return false;
    }
    buildpage_running = 1;
    update_api_url();
    if( ! api_url) {
        buildpage_running = 0;
        return false;
    }
    if(last_ajax) {
        // Cancel any pending ajax calls
        last_ajax.abort();
    }
    //updatemessage();
    last_ajax = $.getJSON(api_url, function(data) {
      //console.log("Checking for new calls")
      //console.log("Last Call " + last_call + " New last " + data.results[0].pk)
      $("#anoymous_time_warn").hide();
      $("#no_trans").hide();
      if(data.count > 0) {
      $("#foot-play-button").show();
      if ( live_update == 1 && ( data.results[0].pk != last_call || force_page_rebuild == 1 )) {
      force_page_rebuild = 0;
      var new_html = '';
      new_id_list = [];
      new_file_list = [];
      new_tg_list = [];
      new_tg_slug_list = [];
      count=0;
      for (var a in data.results) {
          curr_results = data.results[a];
          curr_id = curr_results.pk;
          file_ext = "mp3"
          if (data.results[a].audio_file_type) {
              file_ext = data.results[a].audio_file_type
          }

          new_id_list.unshift(data.results[a].pk);
          new_file_list.unshift(data.results[a].audio_url + data.results[a].audio_file + "." + file_ext);
          new_tg_list.unshift(data.results[a].tg_name);
          new_tg_slug_list.unshift(data.results[a].talkgroup_info.slug);
          button_type = "btn-default";
          if(currently_playing == data.results[a].pk) {
              button_type = "active-trans"
          }
          tg_muted="";
          if (muted_tg[data.results[a].talkgroup_info.slug]) {
            tg_muted="mute-mute ";
          }

          new_html += '<div id="row-' + curr_id + '" class="row grad">';
          if(data.results[a].audio_file) {
              new_html += '<div class="top-data"><button aria-label="Play" id="gl-player-action-' + curr_id + '" onclick="click_play_clip(\'' + curr_results.audio_url + curr_results.audio_file + '.' + curr_results.audio_file_type + '\', ' + curr_id + '); return false;" class="player-action glyphicon glyphicon-play" aria-hidden="false"></button><span class="talk-group ' + tg_muted + ' talk-group-' + curr_results.talkgroup_info.slug + '">' + data.results[a].talkgroup_info.alpha_tag + '</span> <span class="talk-group-descr">' + curr_results.talkgroup_info.description + ' </span><span class="tran-length">' + curr_results.print_play_length + '</span><span class="tran-start-time">' + curr_results.local_start_datetime + '</span></div>';
          } else {
              new_html += '<div class="top-data"><button class="old-transmission glyphicon glyphicon-ban-circle" data-toggle="modal" data-target="#old-transmission-modal"></button> <span class="talk-group ' + tg_muted + ' talk-group-' + curr_results.talkgroup_info.slug + '">' + data.results[a].talkgroup_info.alpha_tag + '</span> <span class="talk-group-descr">' + curr_results.talkgroup_info.description + ' </span><span class="tran-length">' + curr_results.print_play_length + '</span><span class="tran-start-time">' + curr_results.local_start_datetime + '</span></div>';
          }
          new_html += '<div class="unit-data"><span class="unit-id-1 unit-list">';
          new_unit_list = data.results[a].units.reverse();
          has_units = false;
          for (unit in data.results[a].units) {
              has_units = true;
              if(data.results[a].units[unit].description) {
                  new_html += data.results[a].units[unit].description + ', ';
              } else {
                  if(js_config.radio_change_unit) {
                      //new_html += '?<a href="/admin/radio/unit/' + data.results[a].units[unit].pk + '/change/">' + data.results[a].units[unit].dec_id + '</a>, ';
                      new_html += '?<a href="/unitupdate/' + data.results[a].units[unit].pk + '/" data-toggle="modal" data-target="#unitupdatemodal">' + data.results[a].units[unit].dec_id + '</a>, ';
                  } else {
                      new_html += '?' + data.results[a].units[unit].dec_id + ', ';
                  }
              }
          }
          if(has_units) {
            // Drop last ,
            new_html  = new_html.slice(0, -2);
          }
          new_html += '</span>';
          if(data.results[a].audio_file) {
          new_html += '<span class="tran-menu">';
          new_html += '<div class="btn-group">';
          new_html += '<a class="btn dropdown-toggle tran-menu-a" data-toggle="dropdown" href="#">';
          new_html += '<i class="fa fa-list-ul" aria-hidden="false" title="Call Menu"></i>';
          new_html += '</a>';
          new_html += '<ul class="dropdown-menu pull-right">';
          new_html += '<li><a href="/tg/' + curr_results.talkgroup_info.slug + '/"><i class="fa fa-filter fa-fw" aria-hidden="true"></i> Hold on TalkGroup</a></li>';
          new_html += '<li><a href="#" onclick="return mute_click(\'' + data.results[a].talkgroup_info.slug + '\');"><i class="fa fa-volume-off fa-fw"></i> Mute TalkGroup</a></li>'; 
          //if(js_config.radio_change_unit) {
          //  new_html += '<li><a data-toggle="modal" data-target="#myModalNorm"><i class="fa fa-pencil fa-fw"></i> Edit Unit ID</a></li>';
          //}
          if(js_config.download_audio) {
              new_html += '<li><a href="/audio_download/' + curr_results.slug + '/"><i class="fa fa-download fa-fw" aria-hidden="true"></i> Download audio file</a></li>';
          }
          new_html += '<li><a href="/audio/' + curr_results.slug + '/"><i class="fa fa-info-circle fa-fw" aria-hidden="true"></i> Details</a></li>';
          //new_html += '<li class="divider"></li>';
          //new_html += '<li><a href="#"><i class="fa fa-trash-o fa-fw"></i> Flag for delete</a></li>';
          new_html += '</ul>';
          new_html += '</div>';
          new_html += '</span>';
          }
          new_html += '</div>';
          new_html += '</div>';
      }
      curr_id_list = new_id_list;
      curr_file_list = new_file_list;
      curr_tg_list = new_tg_list;
      curr_tg_slug_list = new_tg_slug_list;
      pagination_older_url = data.next;
      pagination_newer_url = data.previous;
      new_html += '<div>';
      new_html += update_pagination_links()
      new_html += '</div>';
      $('#main-data-table').html(new_html);
      $("#row-" + currently_playing).addClass('active-trans ');
      //update_pagination_links();
      }
      last_call = data.results[0].pk;
      first_load = 0;
      } else {
        $("#no_trans").show();
        if(show_limit_warning) {
            $("#anoymous_time_warn").show();
        }
        $('#main-data-table').html("")
      }
    });
    buildpage_running = 0;
}

function click_play_clip(audio_file, audio_id){
    //$("#button_start_scanner").hide();
    reset_play_list(audio_id);
    play_clip(audio_file, audio_id);
    play_next();
    return true;
}

function play_clip(audio_file, audio_id){
      //$(".play-btn").removeClass('active-trans');
      currently_playing=audio_id;
      if(audio_id == 0) {
        //$("#button_start_scanner").removeClass('btn-default').addClass('btn-success ');
      } else {
        //$("#button_" + audio_id).removeClass('btn-default').addClass('btn-success ');
        $(".active-trans").removeClass("active-trans");
        $("#row-" + audio_id).addClass('active-trans ');
        // Remove anything that still shows playing
        // For now keep it a play button as clicking on it just re starts it
        //$(".glyphicon-pause").removeClass("glyphicon-pause").addClass("glyphicon-play ");
        //$("#gl-player-action-" + audio_id).removeClass("glyphicon-play").addClass("glyphicon-pause ");
      }
      // Google Analytics
      ga('send', 'event', 'Transmisison', 'play', audio_id);
      if(audio_file.substring(audio_file.length - 3) == "m4a") {
        $("#jquery_jplayer_1").jPlayer("setMedia", {
           m4a: audio_file,
        } );
      } else {
        $("#jquery_jplayer_1").jPlayer("setMedia", {
          mp3: audio_file,
        } );
      }
      $("#jquery_jplayer_1").jPlayer("play");
}

function reset_play_list(audio_id){
    seen.length = 0; // Clear the array
    found_me = 0;
    for (var r_id in curr_id_list) {
        if(found_me == 0) {
            seen.push(curr_id_list[r_id]);
        }
        if(curr_id_list[r_id] == audio_id) {
            found_me = 1;
        }
    }
}

function play_next() {
    if(active_play == 0){
        return false;
    }
    for (var r_id in curr_id_list) {
        if ( seen.indexOf( curr_id_list[r_id] ) < 0 ) {
            if ( currently_playing == 0) {
              seen.push(curr_id_list[r_id]);
              // See if we are muted
              if(muted_tg[curr_tg_slug_list[r_id]]) {
                 return;
              }
              //play_clip(audio_file, audio_id){
              mp3 = curr_file_list[r_id];
              if(first_load == 0 && first_play == 0) { // Dont play them all on first load
                  tmp_title = '>>' + curr_tg_list[r_id] + '<< ' + page_title;
                  document.title = tmp_title;
                  play_clip(mp3, curr_id_list[r_id]);
              }
            }
        }
    }
    if(first_load == 0) {
      first_play = 0;
    }
 }

function setup_player() {
      $("#jquery_jplayer_1").jPlayer({
       ready: function () {
       },
       ended: function() {
           active_play=1;
           $('.active-trans').removeClass('active-trans');
           //$("#row-" + currently_playing).removeClass('active-trans');
           // Just keep it a play button
           //$('.glyphicon-pause').removeClass("glyphicon-pause").addClass("glyphicon-play ");
           //$("#gl-player-action-" + audio_id).removeClass("glyphicon-pause").addClass("glyphicon-play");
           //$("#button_start_scanner").hide();
           currently_playing=0;
           $(document).prop('title', page_title);
           $(".stop-btn").show();
           $(".start-btn").hide();
       },
       swfPath: "https://jplayer.org/latest/dist/jplayer/",
       solution: "html,flash",
       supplied: "mp3, m4a",
       remainingDuration: true,
       errorAlerts: true,
       warningAlerts: true,
       volume: 1,
       cssSelectorAncestor: "",
       cssSelector: {
          title: "#title",
          play: "#jp1_play",
          pause: "#jp1_pause",
          stop: "#jp1_stop",
          mute: "#jp1_mute",
          unmute: "#jp1_unmute",
          currentTime: "#jp1_c_time",
         duration: "#jp1_duration"
       }
      });
      $("#jquery_jplayer_1").bind($.jPlayer.event.error + ".myProject", function(event) { 
          console.log("Error Event: type = " + event.jPlayer.error.type);
          active_play=1;
          $("#button_" + currently_playing).removeClass('active-trans');
          currently_playing=0;
          $(document).prop('title', page_title);
      });
  }

function unit_edit_post_setup1() {
    $("#unitupdatemodal").on("show.bs.modal", function(e) {
        var link = $(e.relatedTarget);
        //$(this).find(".modal-body").load(link.attr("href"));
        $(this).find(".modal-content").load(link.attr("href"));
    });
}

function unit_edit_post_setup() {
    $('#update-unit-form').off('submit');
    $('#update-unit-form').trigger("reset");
    $('#update-unit-form').on('submit', function(e){
    e.preventDefault();
    $.ajax({
      url : $(this).attr('action'),
      type: "POST",
      data : $(this).serialize(),
      success: function(data){
           //alert("Successfully submitted.")
           force_page_rebuild = 1;
           buildpage();
           $('#unitupdatemodal').modal('hide');
      }
    });
  });
}


$(document).ready(function(){ 
    if($(".tg-multi-select").length) {
        $(".tg-multi-select").select2();
    }
    $(".stop-btn").hide();
    setup_player();
    //updatemessage();
    updatemessage()
    setInterval(updatemessage, 30000);
    play_clip(base_audio_url + "point1sec.mp3", 0, 0);
    first_load = 1;
    buildpage();
    unit_edit_post_setup1();
    //setInterval(buildpage, 2000);
    play_next();
    setInterval(play_next, 500);
    update_menu();

    //first_load = 0;

    // Disable updating when a transmission menu is clicked, reenable after 5 second timeout
    $(document).on('click', 'a.tran-menu-a', function() {
        live_update = 0;
                setTimeout(function() {
            live_update = 1;
            buildpage();
        },5000);
    });
});

window.onfocus = function() {
    force_page_rebuild = 1;
    buildpage();
};

function play_from_start() {
    // Play entire page from start/bottom
    first_load = 0;
    first_play = 0;
    seen = [];
    play_next();
}

