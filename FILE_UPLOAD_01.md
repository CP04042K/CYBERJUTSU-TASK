# FILE_UPLOAD level 01 

Một trang web có chức năng cho phép user upload file và lưu trữ nó lên server, ngoài ra ta có thể xem được source code của trang web. Thử xem source code của trang web thì thấy đầu tiên một đường dẫn upload sẽ được tạo dựa trên sesion của user:
```
session_start();
$dir = 'upload/' . session_id();
```

Tiếp là câu if để kiểm tra xem có file được upload lên hay không, nếu có thì sẽ move file đó đến đường dẫn `dir` được khởi tạo ban đầu. Sau khi upload thành công thì sẽ hiển thị lên link dẫn đến file đã upload. Khối if này cũng là đoạn code xử lý chính của web:
```
if(isset($_FILES["file"])) {
        $error = '';
        $success = '';
        try {
            $file = $dir . "/" . $_FILES["file"]["name"];
            move_uploaded_file($_FILES["file"]["tmp_name"], $file);
            $success = 'Successfully uploaded file at: <a href="/' . $file . '">/' . $file . ' </a><br>';
            $success .= 'View all uploaded file at: <a href="/' . $dir . '/">/' . $dir . ' </a>';
        } catch(Exception $e) {
            $error = $e->getMessage();
        }
    }
```

## Vấn đề

Ở đây có 2 vấn đề, thứ nhất thật ra kết quả trả về từ hàm `session_id()` là một untrust data được kiểm soát bởi client. 
![](https://i.imgur.com/CgHjF3L.png)

Hàm `session_id()` sẽ trả về kết quả dựa trên giá trị của cookie `PHPSESSID`, trong trường hợp này là `dfacd091c5443055c3ae34525887ce95`. Nếu user thay đổi giá trị này thành `chanh` thì đường dẫn upload bây giờ sẽ thành `upload/chanh`, vậy nếu giá trị bị thay đổi thành `../` thì đường dẫn upload sẽ là: `upload/../`:
![](https://i.imgur.com/X1U6I1c.png)

Dẫn đến việc file được upload bây giờ không còn nằm trong các directory con của `upload` nữa mà giờ đây nằm ngay bên trong directory này, dẫn đến một lỗ hổng path traversal. Tuy nhiên trong trường hợp này thì không gây ảnh hưởng quá nghiêm trọng.

Vấn đề thứ 2 là trong phần code xử lý upload không thực hiện kiểm tra kiểu file up lên, dẫn đến user có thể lợi dụng để upload các script độc hại. 

## Tấn công

Giả thuyết đặt ra là ta có thể upload lên một file php chứa script thực thi các os command để từ đó thực hiện RCE trang web.

![](https://i.imgur.com/uS05Py2.png)

File php đã được upload, truy cập vào đường dẫn để kiểm tra xem các file php up lên có được thực thi hay không 

![](https://i.imgur.com/sl1TWB9.png)

File php đã được thực thi, vậy là hoàn thành mục tiêu

