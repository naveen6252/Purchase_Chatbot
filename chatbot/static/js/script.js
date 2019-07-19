$(function () {

    $(".passEye").click(function () {
        if ($(this).prev().attr("type") == "password") {
            $(this).prev().attr("type", "text");
            $(this).removeClass("glyphicon-eye-close");
            $(this).addClass("glyphicon-eye-open");

        } else {
            $(this).addClass("glyphicon-eye-close");
            $(this).removeClass("glyphicon-eye-open");
            $(this).prev().attr("type", "password");
        }
    });

    $(".QuestionList .tabNextBtn").click(function () {
        if ($(this).parent().parent().prev().find('select').val() != -1) {
            $(this).parent().parent().parent().next().siblings().removeClass("active");
            $(this).parent().parent().parent().next().addClass("active");
        }
        //else {
        //    $(this).parent().parent().prev().find('select').parent().append')
        //}
    });

    $(".QuestionList:last-child .tabNextBtn").click(function () {
        if ($(this).parent().parent().prev().find('select').val() != -1) {
            var id = "#" + $(this).parent().parent().parent().parent().attr("id");
            $(".RiskCalculator").find("a[href='" + id + "']").parent().next().find("a").trigger("click");
        }
    });

    $(".QuestionList .tabPrevBtn").click(function () {
        $(this).parent().parent().parent().prev().siblings().removeClass("active");
        $(this).parent().parent().parent().prev().addClass("active");
    });

    $(".QuestionList:first-child .tabPrevBtn").click(function () {
        var id = "#" + $(this).parent().parent().parent().parent().attr("id");
        $(".RiskCalculator").find("a[href='" + id + "']").parent().prev().find("a").trigger("click");
    });

    $(".RiskCalculator .nav-tabs li a").click(function () {
        $(".RiskCalculator .nav-tabs li").removeClass("disTableCell");
        $(this).parent().prev().addClass("disTableCell");
    });

    $(".myAccountAcc .panel-title a").click(function () {
        var curr = $(this);
        if ($(this).hasClass("collapsed")) {
            $(this).parent().parent().parent().siblings().addClass("hide");
            $(".myAccountHeading i").removeClass("hide");
        } else {
            setTimeout(function () {
                curr.parent().parent().parent().siblings().removeClass("hide");
                $(".myAccountHeading i").addClass("hide");
            }, 200);
        }
    });

    $(".myAccountHeading").click(function () {
        $(".myAccountAcc .panel-default").each(function () {
            if ($(this).find(".panel-title a").hasClass("collapsed")) {
                //$(this).parent().parent().parent().siblings().addClass("hide");
            } else {
                $(this).find(".panel-title a").click();
            }
        });
    });

    /*$('[data-toggle="tooltip"]').tooltip();

    var owl = $(".owl-carousel");
    $(".owl-carousel").owlCarousel({
        autoplay: true,
        loop: true,
        margin: 10,
        nav: true,
        responsive: {
            0: {
                items: 3
            },
            1000: {
                items: 5
            },
            1200: {
                items: 7
            }
        }
    });*/


    $('.owl-carousel').on('mouseover', function (e) {
        owl.trigger('stop.owl.autoplay');
    });
    $('.owl-carousel').on('mouseleave', function (e) {
        owl.trigger('play.owl.autoplay');
    });

    $(".addNewConditionBtn").click(function () {
        $(".addNewCondition").toggleClass("active");
        if ($(this).text() == "Add more Conditions") {
            $(this).text("Close More Condition");
        } else {
            $(this).text("Add more Conditions");
        }

    });

    $("#reviewPopup").click(function (e) {
        $("#gainReviewPopup").modal("show");
    });

    $("#ciaRecommendationsPopup").click(function (e) {
        $("#ciaRecommendations").modal("show");
    });

    $(".owl-carousel .owl-nav .owl-prev,.owl-carousel .owl-nav .owl-next").text("");

    $(".owl-carousel .owl-item").hover(function () {
        var leftOffset = $(this).find(".hoverOnSlider").offset().left;
        var boxWid = $(this).find(".hoverOnSlider").width();
        var windWidth = $(window).width();
        var left = ($(window).width() - boxWid);
        $(this).find(".hoverOnSlider").parent().parent().addClass("arrowShow");
        if (windWidth > (leftOffset + boxWid)) {

        } else {
            $(this).find(".hoverOnSlider").css("left", (windWidth - (leftOffset + boxWid + 40)));
        }
    }, function () {
        $(this).find(".hoverOnSlider").css("left", 0);
        $(this).find(".hoverOnSlider").parent().parent().removeClass("arrowShow");
    });


    $(".rightSection").on("click", ".moveDownUp", function () {
        //var data=$(this).parent().parent().parent().html();
        var menu = $(this).parent().html();
        var data = $(this).parent().parent().next();
        $(".btmMenuList").append("<li>" + menu + "</li>");
        $(".detailContainer").append(data);
        $(this).parent().parent().parent().remove();
    });

    $(".bottomnavContainer").on("click", ".moveDownUp", function () {
        var menu = $(this).parent().html();
        var id = $(this).prev().attr("href");
        var data = $(".detailContainer").find(id).html();

        $(".rightSection #accordion2").append("<div class='panel panel-default'><div class='panel-heading'><h4 class='panel-title'>" + menu + "</h4></div><div class='panel-collapse collapse' id=" + id.replace("#", "") + ">" + data + "</div>");

        $(".detailContainer").find(id).remove();
        $(this).parent().remove();
    });

    /*======Old Js=========*/

    options = {
        revert: false,
        stack: ".activityTab",
        containment: ".contentSection"
    };

    $(".resizable").resizable();
    window.onresize = dosomething;

    $(".navigation span").click(function () {
        if (!$(this).hasClass("active")) {
            $(".navigation span").removeClass("active");
            $(this).addClass("active");
        } else {
            if ($(this).hasClass("options")) {

            } else {
                $(this).removeClass("active");
            }
        }
    });


    $(".navContainer .searchPanel input").keydown(function (e) {
        if (e.keyCode == 13) {
            $("#ticketSearchPopup").modal("show");
        }
    });

    $("#reviewPopup").click(function (e) {
        $("#gainReviewPopup").modal("show");
    });

    $(".navContainer .searchPanel i").click(function (e) {
        $("#ticketSearchPopup").modal("show");
    });

    $(".leftSection .leftTab li a").click(function () {
        $(".leftSection .menuContainer .navigationSlider").removeClass("active");
        var id = $(this).attr("data-id");
        if (!$(this).parent().hasClass("active")) {
            $(this).parent().addClass("active").siblings().removeClass("active");

            //$(id).height($(window).height() - 123);
            $(".leftSection .menuContainer .leftPanelNavigation .firstMenuLeftSide, .leftSection .menuContainer .leftPanelNavigation .secMenuLeftSide").height(($(window).height() / 2) - 130);

            $(id).addClass("active");
            if ($(window).width() < 992) {
                $(".centerSection").width($(window).width() - 70);
            } else {
                $(".centerSection").width($(window).width() - 247 - 66);
            }
        } else {
            $(this).parent().removeClass("active").siblings().removeClass("active");
            $(id).removeClass("active");
            if ($(window).width() > 991) {
                $(".centerSection").width($(window).width() - 70);
            }
        }
    });

    $(".rightSection .rightTab, #btmNavigation").on("click", "li", function () {
        $(".rightSection .menuContainer .navigationSlider").removeClass("active");
        var id = $(this).attr("data-id");
        if (!$(this).hasClass("active")) {
            $(id).addClass("active");
            $(this).addClass("active").siblings().removeClass("active");
        } else {
            $(this).removeClass("active").siblings().removeClass("active");
            $(id).removeClass("active");
        }
    });


    $(window).on("load resize orientationchange", function () {
        setTimeout(function () {
            $(".centerSection .containerSection").css({
                height: $(window).height() - 210
            });

            $(".discussionSection,.leftContentSection").css({
                height: $(window).height() - 245
            });

            $(".discussionBox .messageBox").css({
                height: $(window).height() - 437
            });

            $(".rightSection .menuContainer .navigationSlider, .menuContainer .navigationSlider ,.rightTab").css({
                height: $(window).height() - 172
            });


            $(".centerSection").css({
                width: $(window).width() - 66 - $(".leftSection").width()
            });
            //alert($(document).width());
        }, 100);

        if ($(window).width() < 768) {
            $(".draggable").draggable("disable");
        } else {
            $(".draggable").draggable(options);
        }
    });


    $("body").click(function (e) {
        if ($(e.target).parent().hasClass("options")) {
            $(".activityTab").css("z-index", "0");
            $(e.target).parentsUntil(".activityTab").parent().css("z-index", "5");
        } else {
            //alert(!$(e.target).parentsUntil(".option").parent().hasClass("options"));
            if ($(e.target).parentsUntil(".option").parent().hasClass("options")) {

            } else {
                $('.navigation span').removeClass('active');
                //$(e.target).parentsUntil(".option").parent().hasClass("options").addClass("active")
            }
        }
    });

    $(".leftPanelNavigation ul li > span").click(function () {
        $(this).parent().toggleClass("active");
    });

    $("#rightNavigation li").each(function () {
        if ($(this).hasClass("recActivity")) {
            $(this).css("margin-top", "77px");
        } else {
            $(this).next().css("margin-top", $(this).width() - 10);
        }
    });

    $(".closeCurrentPanel").click(function () {
        $(".menuContainer .navigationSlider").removeClass("active");
        $(".leftSection ul li").removeClass("active");

        $(".centerSection").width($(window).width() - 70);
    });

    $("body").on("click", ".navigationSlider .headerSection .rightcloseCurrentPanel", function () {
        if ($(this).parentsUntil(".toolBoxSection").parent().attr("class") == "toolBoxSection") {
            $(".detailContainer .navigationSlider").removeClass("active");
        } else {
            $(".menuContainer .navigationSlider").removeClass("active");
            $(".centerSection").width($(window).width() - 68);
        }
        var id = "#" + $(this).parentsUntil(".navigationSlider").parent().attr("id").replace("Detail", "");

        $(id).toggleClass("active");
    });

    $(".expand").click(function () {
        $(this).parentsUntil(".content").parent().parent().toggleClass("expanded");
        $(this).toggleClass("active");
        $(this).find("i").toggleClass("glyphicon-resize-small");
        $(this).parentsUntil(".activityTab ").parent().css("z-index", 20);
        if ($(this).parentsUntil(".content").parent().parent().hasClass("expanded")) {
            $(".expanded .content").css({
                width: $(".containerSection").width() - 10,
                height: $(".containerSection").height(),
                left: (-($(".expanded .content").offset().left - $(".contentSection").offset().left) + 5),
                top: (-($(".expanded .content").offset().top - $(".contentSection").offset().top))
            });
        } else {
            $(this).parentsUntil(".activityTab").parent().css({
                zIndex: 5,
                left: 0,
                top: 0
            });
            $(".activityTab .content").css({
                width: "auto",
                height: "auto",
                left: 0,
                top: 0
            });
        }
    });

    $(".minimize").click(function () {
        $(this).parent().next().next().toggleClass("minimizedContent");
    });

});

function dosomething() {

    var totWid = $(document).width();
    var restWid = (totWid - $(".ui-resizable-resizing").width());
    if ($(".leftSection,.centerSection").hasClass("ui-resizable-resizing")) {
        if (!$(".leftSection").hasClass("ui-resizable-resizing")) {

        }
        if (!$(".centerSection").hasClass("ui-resizable-resizing")) {
            if ($(".leftSection").hasClass("ui-resizable-resizing")) {
                restWid = (restWid - 60);
            }
            $(".centerSection").width(restWid);
        }

        if (!$(".rightSection").hasClass("ui-resizable-resizing") && !$(".leftSection").hasClass("ui-resizable-resizing")) {
            if ($(".centerSection").hasClass("ui-resizable-resizing")) {
                restWid = (restWid - $(".leftSection").width());
            }
            //$(".rightSection").width(restWid-125);
        }
    }


}
