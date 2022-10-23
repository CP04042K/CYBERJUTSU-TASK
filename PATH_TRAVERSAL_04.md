# PATH_TRAVERSAL level 04 

Đây là trang web chơi game flappy bird, nó cho phép đăng nhập để chơi mà lưu điểm, trong phần profile còn có thể upload avatar. Code của nó khá nhiều nên mình sẽ chỉ tóm tắt những thứ quan trọng.

File `db.php` có nhiệm vụ kết nối csdl và chứa các hàm dùng để tương tác csdl, file `index.php` thực hiện hiển thị bảng điểm, file `navbar.php` chứa bảng điều hướng, file `register.php` có chức năng giúp người dùng đăng ký qua username, file `game.php` thì nhận vào một input bằng get param `game` và truyền vào câu `include`.

Ở đây đoạn code cần chú ý gồm những đoạn sau đây: 
* Đoạn code upload trong `profile.php`:
```
if (isset($_FILES["fileUpload"])) {
    // Always store as avatar.jpg
    move_uploaded_file($_FILES["fileUpload"]["tmp_name"], "/usr/upload/" . $_SESSION["name"] . "/avatar.jpg");
    $response = "Success";
}
```
* Đoạn code trong `game.php` gồm 2 dòng sau:

![](https://i.imgur.com/mUK0NPn.png)

## Vấn đề

Code khá dễ đọc, cũng có comment lại để giải thích nữa, nếu để ý file `game.php` thì sẽ thấy server nhận vào một post request để submit score lên server, tại server post data được nối thẳng vào hàm `update_point` trong `db.php` mà không qua bước kiểm tra nào, vậy có khi nào đoạn này dính SQLi hong?

Thật ra nếu thử google về `prepare statement` ta sẽ biết rằng đây là một trong những biện pháp hữu hiệu để chống SQLi => đoạn này sẽ không bị SQLi.


Ở một chỗ khác cũng trong file `game.php` ta có đoạn get parameter `game` được nối thẳng vào câu `include` mà không qua cơ chế kiểm tra nào. Như các bạn hẳn đều nhận ra, dữ liệu lấy từ `$_GET['game']` là một untrust data được cung cấp bởi client, việc nối thẳng nó vào câu `include` có thể giúp một hacker đọc một file bất kì. Thay vì `?game=fatty-bird-1.html` thì một hacker có thể ghi là `?game=test.html`, lúc này file đang được đọc sẽ nằm ở:
```
./views/test.html
```
Ở đây dấu `.` đại diện cho thư mục hiện tại (thư mục `/var/www/html`)

Nếu hacker ghi là `?game=../../../../etc/passwd` thì file được đọc sẽ là:
```
./views/../../../../etc/passwd 
=> /var/www/html/views/../../../../etc/passwd 
=> /etc/passwd
```
![](https://i.imgur.com/3gmINWB.png)

Nhưng mục tiêu ở đây là RCE, mình nghĩ một số bạn cũng sẽ nghĩ như mình, làm sao mà từ việc đọc một file có thể dẫn đến việc bị RCE được ta?

## Ý tưởng

Để hack cái gì thì phải hiểu rõ nó, mình thử google để tìm hiểu về `include`:

![](https://i.imgur.com/OjZwV32.png)

Tác dụng của `include` là lấy nội dung của một file và **thực thi nó như code PHP**, có một điểm cần chú ý đó là `include` sẽ tự nhận dạng code php trong cặp dấu `<?php ?>`, không quan trọng đuôi hay định dạng file đó là gì, chỉ cần có cặp dấu trên thì các nội dung trong cặp dấu đó sẽ được thực thi như code php.

![](https://i.imgur.com/eaYHnMz.png)

Ok nhưng mà giờ làm sao để lợi dụng được điều này nhỉ. Mình bắt đầu nghĩ theo hướng liệu có nơi nào mà input của mình sẽ được ghi lại hay không, vâng đó chính là file avatar mà ban nãy ta có thể upload lên

Vì ở phần upload không có phần kiểm tra nội dung thì nên chắc chắn ta có thể upload file lên trơn tru. Dù cho luôn được lưu bằng đuôi jpg nhưng cái quan trọng nằm ở nội dung của nó nên không có gì phải lo cả :3

## Tấn công

Đầu tiên là upload avatar có chứa script php:

![](https://i.imgur.com/f0rZ4vw.png)

Sau đó là include đến file avatar này, vì username mình tạo là test nên đường dẫn sẽ là `/upload/test/avatar.jpg`, theo như file config thì `/upload` sẽ là alias của `/usr/upload` nên đường dẫn file avatar sẽ là `/usr/upload/test/avatar.jpg`. Vì ta đang ở `var/www/html/views` nên ta sẽ dùng 4 kí tự `../` để về root `/` và truy cập đến `/usr/upload/test/avatar.jpg`. Kết quả:

![](https://i.imgur.com/wTA5RPG.png)

Thu về kết quả của câu lệnh `ls`, phần đọc flag các bạn chỉ cần thay lệnh thành `cat /secret.txt` là được.

Thật ra muốn đọc flag thì từ đầu có thể dùng path traversal để đọc cũng được, nhưng các anh muốn mình làm theo hướng này nên mình RCE rồi mới đọc flag :3

Vậy là ta đã xong bài lab!
