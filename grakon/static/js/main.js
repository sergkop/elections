$(function(){
    //$("form.uniForm").uniform();
    //$(".gr-side-item h4 i, .gr-login-info a").tipsy({gravity: 'n', opacity: .8});

    $("input[placeholder], textarea[placeholder]").placeholder();

    // Default tipsy settings
    $.fn.tipsy.defaults.delayIn = 150;
    $.fn.tipsy.defaults.delayOut = 200;
    $.fn.tipsy.defaults.fade = true;
    $.fn.tipsy.defaults.opacity = 0.6;
});

function get_cookie(name){
    var cookie_value = null;
    if (document.cookie && document.cookie!="") {
        var cookies = document.cookie.split(";");
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + "=")) {
                cookie_value = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookie_value;
}

// TODO: use list to set buttons (?)
function create_dialog(id, width, height, title, cancel_btn_title, buttons){
    $(function(){
        if (cancel_btn_title)
            buttons[cancel_btn_title] = function(){$("#"+id).dialog("close");};

        $("#"+id)
                .removeClass("hidden")
                .dialog({autoOpen: false, width: width, height: height, modal: true,
                        title: title, buttons: buttons})
                .dialog("close");
    });
}

// TODO: what if response is not successful?
// Shortcut used to send post requests from dialogs.
// If post response is "ok", provided function is performed and dialog is closed.
// Otherwise alert with error message appears.
// If form_id is specified, params is updated with form data.
function post_shortcut(url, params, on_success, reload_page, form_id){
    return function(){
        params["csrfmiddlewaretoken"] = get_cookie("csrftoken");
        if (form_id){
            // TODO: this may not work with complex form fields
            _.each($("#"+form_id).serializeArray(), function(field){
                params[field.name] = field.value;
            });
        }
        $.post(url, params, function(data){
            if (data=="ok"){
                on_success();
                if (reload_page)
                    window.location.reload();
            } else
                alert(data);
        });
    }
}

function login_dialog_init(){
    $("#login_dialog").dialog("open");
    $('#login_form [name="csrfmiddlewaretoken"]').val(get_cookie("csrftoken"));

    _gaq.push(["_trackEvent", "login", "open_dialog"]);
}

function prevent_enter_in_form(selector){
    $(selector).keydown(function(event){
        if(event.keyCode == 13) {
            event.preventDefault();
            return false;
        }
    });
}

function role_remove_btn(li){
    var remove_btn = $("<span/>")
            .attr("title", "Удалить роль")
            .addClass("side_list_btn ui-icon ui-icon-close")
            .tipsy({gravity: 'n'})
            .click(function(){
                var li = $(this).parent();
                li.css("background-color", "#D9BDFF");

                var confirmation = confirm("Вы действительно хотите удалить эту роль");
                li.css("background-color", "#FFFFFF");

                if (confirmation)
                    $.post("/remove_role", {"role_id": li.attr("role_id"), "csrfmiddlewaretoken": get_cookie("csrftoken")}, function(data){
                        if (data != "ok")
                            alert(data);
                        else
                            li.remove()
                    });
            })
            .prependTo($(li));
}
