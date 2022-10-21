# FILE_UPLOAD level 04

Một trang web có chức năng cho phép user upload file và lưu trữ nó lên server, ngoài ra ta có thể xem được source code của trang web. Thử xem source code của trang web thì thấy đầu tiên một đường dẫn upload sẽ được tạo dựa trên sesion của user:
```
session_start();
if (!isset($_SESSION['dir'])) {
    $_SESSION['dir'] = 'upload/' . session_id();
}
$dir = $_SESSION['dir'];
if ( !file_exists($dir) )
    mkdir($dir);
```

Tiếp là câu if để kiểm tra xem có file được upload lên hay không, nếu có thì sẽ move file đó đến đường dẫn `dir` được khởi tạo ban đầu. Sau khi upload thành công thì sẽ hiển thị lên link dẫn đến file đã upload. Khối if này cũng là đoạn code xử lý chính của web:

```
if(isset($_FILES["file"])) {
    $error = '';
    $success = '';
    try {
        $filename = $_FILES["file"]["name"];
        $extension = end(explode(".", $filename));
        if (in_array($extension, ["php", "phtml", "phar"])) {
            die("Hack detected");
        }
        $file = $dir . "/" . $filename;
        move_uploaded_file($_FILES["file"]["tmp_name"], $file);
        $success = 'Successfully uploaded file at: <a href="/' . $file . '">/' . $file . ' </a><br>';
        $success .= 'View all uploaded file at: <a href="/' . $dir . '/">/' . $dir . ' </a>';
    } catch(Exception $e) {
        $error = $e->getMessage();
    }
```

Khác với level 3, anh lập trình viên ở level này đã nâng cấp đoạn code kiểm tra file trước khi được upload để tránh bị mình RCE như bài trước:)
```
$extension = end(explode(".", $filename));
if (in_array($extension, ["php", "phtml", "phar"])) {
    die("Hack detected");
}
```
Tác dụng của hàm `explode()` là để tách các phần trong một chuỗi ngăn cách bởi một ký tự (trong trường hợp này là dấu chấm `.`) và trả về một mảng chứa các phần đó. Hàm `end()` sẽ trả về phần tử cuối cùng của một mảng. Giả sử file được upload lên là `shell.a.php` thì phần code `explode(".", $filename)` sẽ trả về `["shell", "php"]` và `end(explode(".", $filename))` sẽ trả về `php`. Phần đuôi file này sau đó được đưa vào hàm `in_array` để kiểm tra xem nó có nằm trong một trong 3 đuôi là `["php", "phtml", "phar"]` hay không, nếu có thì sẽ dừng thực thi và trả về đoạn text `Hack detected`

## Vấn đề

Ở đây có 1 vấn đề, thứ nhất thật ra kết quả trả về từ hàm `session_id()` là một untrust data được kiểm soát bởi client. 
![](https://i.imgur.com/CgHjF3L.png)

Hàm `session_id()` sẽ trả về kết quả dựa trên giá trị của cookie `PHPSESSID`, trong trường hợp này là `dfacd091c5443055c3ae34525887ce95`. Nếu user thay đổi giá trị này thành `chanh` thì đường dẫn upload bây giờ sẽ thành `upload/chanh`, vậy nếu giá trị bị thay đổi thành `../` thì đường dẫn upload sẽ là: `upload/../`:
![](https://i.imgur.com/CaDa37t.png)

Dẫn đến việc file được upload bây giờ không còn nằm trong các directory con của `upload` nữa mà giờ đây nằm ngay bên trong directory này, dẫn đến một lỗ hổng path traversal. Tuy nhiên trong trường hợp này thì không gây ảnh hưởng quá nghiêm trọng.

## Giả thuyết

Ở bài này thì đoạn code kiểm tra đã không còn dễ dàng như lần trước nữa, theo config của server thì server sẽ chỉ nhận diện và thực thi các đoạn script php chứa trong các file có đuôi php, phar hoặc phtml, với việc sử dụng blacklist để chặn cả 3 extension này thì ta không thể tìm một extension thay thế được. Như ta đã biết thì việc dùng hàm `end()` cũng sẽ chặn việc bypass theo kiểu upload một file "có nhiều extension" như `shell.a.php`.

Tuy nhiên mình có nảy ra một ý tưởng, như ta biết thì file .htaccess là file dùng để nói cho server biết cách mà nó nên xử lý các http request. Ví dụ như ta có thể dùng htaccess để chặn user truy cập vào các đường dẫn không mong muốn, mỗi file htaccess được up trong directory nào thì sẽ chỉ có tác dụng với directory đó, ví dụ file `/upload/.htaccess` sẽ chỉ áp dụng cho đường dẫn `upload` chứ không áp dụng cho `/upload/a`. 

Giả thuyết mà mình đặt ra là liệu ta có thể upload một file .htaccess để nói cho server biết rằng nếu gặp một file có đuôi ví dụ như `phpaa` thì nó sẽ thực thi như một file php thay vì trả về plaintext

## Tấn công

Để kiểm chứng giả thuyết trên thì mình tìm từ khóa "htaccess set execute php file" và tìm thấy một bài viết:
https://asreshashank.medium.com/execute-php-scripts-into-html-file-by-modifying-htaccess-file-8517ed1e2066

Mình biết được rằng để đạt được giả thuyết của mình thì ta có thể dùng một file htaccess có nội dung như sau: 
```
AddType application/x-httpd-php .blabla
```
Ở đây .blabla là đuôi file mà khi được truy cập vào thì server sẽ thực thi nó như một php script. Ok cùng thử thoi

upload file .htaccess:
![](https://i.imgur.com/o3xGFRN.png)

upload file .blabla:
![](https://i.imgur.com/cDJ50WF.png)
Và kết quả:
![](https://i.imgur.com/rb57a3K.png)

Ok vậy là xong bài lab
