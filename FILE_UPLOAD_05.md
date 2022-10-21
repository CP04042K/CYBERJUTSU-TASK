# FILE_UPLOAD level 05

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
            $mime_type = $_FILES["file"]["type"];
            if (!in_array($mime_type, ["image/jpeg", "image/png", "image/gif"])) {
                die("Hack detected");
            }
            $file = $dir . "/" . $_FILES["file"]["name"];
            move_uploaded_file($_FILES["file"]["tmp_name"], $file);
            $success = 'Successfully uploaded file at: <a href="/' . $file . '">/' . $file . ' </a><br>';
            $success .= 'View all uploaded file at: <a href="/' . $dir . '/">/' . $dir . ' </a>';
        } catch(Exception $e) {
            $error = $e->getMessage();
        }
    }
```

Khác với level 4, anh lập trình viên ở level này đã nâng cấp đoạn code kiểm tra file trước khi được upload để tránh bị mình RCE như bài trước:)
```
$mime_type = $_FILES["file"]["type"];
            if (!in_array($mime_type, ["image/jpeg", "image/png", "image/gif"])) {
                die("Hack detected");
            }
```
Trong đoạn code kiểm tra trên, giá trị `$_FILES["file"]["type"]` được gán vào biến `$mime_type`, đây là [MIME type](https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types) của file. Sau đó mime type này sẽ được check xem có nằm trong các kiểu mime type cho phép hay không, cụ thể là check xem mime type có phải là kiểu ảnh hay không.

## Vấn đề

Ở đây có 2 vấn đề, thứ nhất thật ra kết quả trả về từ hàm `session_id()` là một untrust data được kiểm soát bởi client. 
![](https://i.imgur.com/CgHjF3L.png)

Hàm `session_id()` sẽ trả về kết quả dựa trên giá trị của cookie `PHPSESSID`, trong trường hợp này là `dfacd091c5443055c3ae34525887ce95`. Nếu user thay đổi giá trị này thành `chanh` thì đường dẫn upload bây giờ sẽ thành `upload/chanh`, vậy nếu giá trị bị thay đổi thành `../` thì đường dẫn upload sẽ là: `upload/../`:
![](https://i.imgur.com/1tFsCv1.png)

Dẫn đến việc file được upload bây giờ không còn nằm trong các directory con của `upload` nữa mà giờ đây nằm ngay bên trong directory này, dẫn đến một lỗ hổng path traversal. Tuy nhiên trong trường hợp này thì không gây ảnh hưởng quá nghiêm trọng.

Vấn đề thứ 2 là mime type được lấy ra từ `$_FILES["file"]["type"]` thực chất là một untrust data và được lấy ra từ phần `Content-Type` trong request upload file:

![](https://i.imgur.com/hhY8BQT.png)

Vì nó nằm trong request gửi đi nên ta có thể kiểm soát nó, thay đổi mime type thành một trong những mime type được cho phép

## Tấn công

Đầu tiên ta upload một file php lên:
![](https://i.imgur.com/JEPABbB.png)

Không thành công do bị chặn, thử đổi content type lại thành `image/jpeg` và upload lại:

![](https://i.imgur.com/iHrJwTb.png)

Truy cập vào file vừa upload:

![](https://i.imgur.com/nU1TrWj.png)


Ok vậy là xong bài lab
