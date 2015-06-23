function question_clicked(){
        //$(this).css("color", "blue")
        window.location.href = '/question/q_detail/'+this.id;
}

$(function(){
    $(".item").bind("click", question_clicked);
});

//マウスオーバーすると拡大する。これは使っていないけど残しておく
$(function() {
    $('.###') // change here
    .hover(
        function(){
            $(this).stop().animate({
                'width':'600px',//拡大で表示させておくサイズ
                'height':'335px',
                'marginTop':'45px'//トップのマージンをマイナスで指定す事で底辺を起点としていま
            },'fast');
        },
        function () {
            $(this).stop().animate({
                'width':'400px',//デフォルトで表示させておくサイズ
                'height':'200px',
                'marginTop':'0px'
            },'fast');
        }
    );
});
