$(function() {
    // 搜索关键词,默认显示第1页
    $('input.search-bt').click(function() {
        var kw1 = $("input.search-in").val();
        var url_ = window.location.pathname;
        window.location.href = url_ + "?kw=" + kw1 + "&pg=1"
    });

    // 跳转页面
    $("button.jump-btn").click(function() {
        var url_ = window.location.pathname;
        var kw1 = $("input.search-in").val();
        var pg1 = $("input#jump-to").val();
        window.location.href = url_ + "?kw=" + kw1 + "&pg=" + pg1
    });

    // 搜索框的回车事件
    $('input.search-in').bind('keypress', function(event) {
        if (event.keyCode == 13) {
            var kw1 = $("input.search-in").val();
            var url_ = window.location.pathname;
            window.location.href = url_ + "?kw=" + kw1 + "&pg=1";
        }

    });

    // 删除一条记录
    $(".del_record").click(function(e) {
        var url = window.location.pathname;
        var id = $(this).attr("uin");
        $.ajax({
            method: "delete",
            contentType: "application/json",
            url: "http://192.168.10.60:8080" + url + "/" + id,
            success: function(result) {
                if (result.code == 200) {
                    alert("Done");
                    location.reload()
                } else {
                    alert("删除失败:暂时关闭删除功能,请联系管理员开启.")
                }
            }
        })
    });

    // 备份数据库的ajax
    $("a#backup-db").click(function() {
        $.ajax({
            method: "get",
            contentType: "application/json",
            url: "http://192.168.10.60:8080/sys/backup",
            beforeSend: function() {
                $("a#backup-db").html("处理中...")
                    // $("a#backup-db").attr("style", "display:none")
            },
            complete: function() {
                // $("a#backup-db").removeAttr("style")
                $("a#backup-db").html("备份数据库")
            },
            success: function(res) {
                if (res.code == 200) {
                    alert(res.msg)
                } else {
                    alert(res.msg)
                }
            }
        })
    });

    // 还原数据库  init/db
    $("a#init-db").click(function() {
        $.ajax({
            method: "get",
            contentType: "application/json",
            url: "http://192.168.10.60:8080/sys/init/db",
            beforeSend: function() {
                $("a#init-db").html("处理中...")
            },
            complete: function() {
                $("a#init-db").html("还原数据库")
            },
            success: function(res) {
                if (res.code == 200) {
                    alert(res.msg)
                } else {
                    alert(res.msg)
                }
            }
        })
    });

    //重建错误列表索引 reverse-index/err
    $("a#rebuild-err-index").click(function() {
        $.ajax({
            method: "get",
            contentType: "application/json",
            url: "http://192.168.10.60:8080/sys/reverse-index/err",
            beforeSend: function() {
                $("a#rebuild-err-index").html("处理中...")
            },
            complete: function() {
                $("a#rebuild-err-index").html("重建Error List索引")
            },
            success: function(res) {
                if (res.code == 200) {
                    alert(res.msg)
                } else {
                    alert(res.msg)
                }
            }
        })
    });


    //重建疑难q and a 列表索引  reverse-index/qa
    $("a#rebuild-qa-index").click(function() {
        $.ajax({
            method: "get",
            contentType: "application/json",
            url: "http://192.168.10.60:8080/sys/reverse-index/qa",
            beforeSend: function() {
                $("a#rebuild-qa-index").html("处理中...")

            },
            complete: function() {
                $("a#rebuild-qa-index").html("重建Q and A索引")
            },
            success: function(res) {
                if (res.code == 200) {
                    alert(res.msg)
                } else {
                    alert(res.msg)
                }
            }
        })
    });

    // 添加其他的函数

});