# FILE_UPLOAD level 03

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
            if ($extension === "php") {
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

Khác với level 2, anh lập trình viên ở level này đã nâng cấp đoạn code kiểm tra file trước khi được upload để tránh bị mình RCE như bài trước:)
```
$extension = end(explode(".", $filename));
if ($extension === "php") {
    die("Hack detected");
}
```
Tác dụng của hàm `explode()` là để tách các phần trong một chuỗi ngăn cách bởi một ký tự (trong trường hợp này là dấu chấm `.`) và trả về một mảng chứa các phần đó. Hàm `end()` sẽ trả về phần tử cuối cùng của một mảng. Giả sử file được upload lên là `shell.a.php` thì phần code `explode(".", $filename)` sẽ trả về `["shell", "php"]` và `end(explode(".", $filename))` sẽ trả về `php`. Mục đích của đoạn code là để kiểm tra xem đuôi file upload lên có phải là `php` hay không, nếu phải thì sẽ dừng thực thi và trả về đoạn text `Hack detected`

## Vấn đề

Ở đây có 2 vấn đề, thứ nhất thật ra kết quả trả về từ hàm `session_id()` là một untrust data được kiểm soát bởi client. 
![](https://i.imgur.com/CgHjF3L.png)

Hàm `session_id()` sẽ trả về kết quả dựa trên giá trị của cookie `PHPSESSID`, trong trường hợp này là `dfacd091c5443055c3ae34525887ce95`. Nếu user thay đổi giá trị này thành `chanh` thì đường dẫn upload bây giờ sẽ thành `upload/chanh`, vậy nếu giá trị bị thay đổi thành `../` thì đường dẫn upload sẽ là: `upload/../`:
![](https://i.imgur.com/GfMTKql.png)

Dẫn đến việc file được upload bây giờ không còn nằm trong các directory con của `upload` nữa mà giờ đây nằm ngay bên trong directory này, dẫn đến một lỗ hổng path traversal. Tuy nhiên trong trường hợp này thì không gây ảnh hưởng quá nghiêm trọng.

Vấn đề thứ 2,  mình đặt giả thuyết cho phần kiểm tra đuôi file là ngoài sử dụng đuổi file là `php` thì liệu ta có thể sử dụng đuôi file nào khác mà server vẫn nhận diện là script php và thực thi hay không

## Tấn công

Với giả thuyết đã đặt ra, mình lên trang https://book.hacktricks.xyz (đây là một trang khá hay và được recommend rất nhiều) và tìm kiếm về file upload, mình tìm ra các extension khác có thể được sử dụng thay cho `php`. Để kiểm chứng thử thì mình thử up một file `.phar` chứa shell script lên để thử:
![](https://i.imgur.com/BYqcAM8.png)

Và kết quả:

![](https://i.imgur.com/QwN5APP.png)

Vậy là ta đã hoàn thành bài lab
