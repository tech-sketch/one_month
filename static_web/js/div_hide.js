window.onload = function(){
    Box = document.getElementById("javascriptBox");        // 「id="javascriptBox"」をBox変数に格納
    Push = document.getElementById("javascriptPush");    // 「id="javascriptPush"」をPush変数に格納
    Box.style.display = 'none'; // Box変数のstyleを「display: none;」にする
 
    // Push変数がクリックされた場合
    Push.onclick = function(){
        // 「id="javascriptBox"」が「display: block;」の場合、クリックすると「display: none;」にする。
        // また「id="javascriptBox"」が「display: none;」の場合、クリックすると「display: block;」にする。
        Box.style.display = Box.style.display == 'block' ? 'none' : 'block';
    }
}