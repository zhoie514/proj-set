$(function () {
    // 搜索关键词,默认显示第1页
    $('input.search-bt').click(function () {
        var kw1 = $("input.search-in").val();
        // var pg1 = $("input#jump-to").val();
        var url_ = window.location.pathname;
        window.location.href = url_ + "?kw=" + kw1 + "&pg=1"
    });

    // 跳转页面
    $("button.jump-btn").click(function () {
        var url_ = window.location.pathname;
        var kw1 = $("input.search-in").val();
        var pg1 = $("input#jump-to").val();
        window.location.href = url_ + "?kw=" + kw1 + "&pg=" + pg1
    });

    // 搜索框的回车事件
    $('input.search-in').bind('keypress', function (event) {
        if (event.keyCode == 13) {
            var kw1 = $("input.search-in").val();
            // var pg1 = $("input#jump-to").val();
            var url_ = window.location.pathname;
            window.location.href = url_ + "?kw=" + kw1 + "&pg=1";
        }

    });

    // 删除一条记录
    $(".del_record").click(function (e) {
        var url = window.location.pathname;
        var id = $(this).attr("uin");
        $.ajax({
            method: "delete",
            contentType: "application/json",
            url: "http://192.168.10.60:80" + url + "/" + id,
            success: function (result) {
                if (result.code == 200) {
                    alert("Done");
                    location.reload()
                } else {
                    alert("发生错误,请刷新页面后重试")
                }
            }
        })
    });

    // 添加其他的函数

});
