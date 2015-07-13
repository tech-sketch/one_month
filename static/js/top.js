function question_clicked(){
        //$(this).css("color", "blue")
        window.location.href = '/dotchain/q_detail/' + this.id;
}

$(function(){
    $(".item").bind("click", question_clicked);
});


$(function() {
    /**
     * それぞれのタブをクリックしたとき開きたい要素がどれになるかはHTMLの方に書くようにしたので、Javascriptの方は1行でよい
     * id="tabs"の中のhrefが#panel何々となっているa要素をクリックすると
     * classがpanelとなっているdivを全部非表示にして、クリックしたタブのハッシュと同じIDの要素だけをフェードインして表示
     * return false で onclick="return false" と同様にデフォルトのイベント処理は抑制
     */
    $('#tabs a[href^="#panel"]').click(function(){
        $("#tabs .panel").hide();
        $(this.hash).fadeIn();
        return false;
    });
    //わざと1つ目を表示させておくことができます
    $('#tabs a[href^="#panel"]:eq(0)').trigger('click');
});

