function question_clicked(){
        //$(this).css("color", "blue")
        window.location.href = '/dotchain/q_detail/' + this.id;
}

$(function(){
    $(".my-card").bind("click", question_clicked);
});

