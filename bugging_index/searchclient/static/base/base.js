$(function () {
    // 搜索关键词,默认显示第1页
    $('input.search-bt').click(function () {
        var kw1 = $("input.search-in").val();
        // var pg1 = $("input#jump-to").val();
        var url_ = window.location.pathname;
        window.location.href = url_ + "?kw=" + kw1 + "&pg=1"
    })

    // 跳转页面
    $("button.jump-btn").click(function () {
        var url_ = window.location.pathname
        var kw1 = $("input.search-in").val();
        var pg1 = $("input#jump-to").val();
        window.location.href = url_ + "?kw=" + kw1 + "&pg=" + pg1
    })

    // 搜索框的回车事件
    $('input.search-in').bind('keypress', function (event) {


        if (event.keyCode == 13) {
            var kw1 = $("input.search-in").val();
            // var pg1 = $("input#jump-to").val();
            var url_ = window.location.pathname;
            window.location.href = url_ + "?kw=" + kw1 + "&pg=1";
        }

    });


})
