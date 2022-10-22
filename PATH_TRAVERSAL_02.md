# PATH_TRAVERSAL level 02 

Đây là một trang web xem hình ảnh, mỗi khi bấm vào nút view ở một ảnh nào đó thì ta sẽ bị điều hướng đến đường dẫn `/loadImage.php` và tại đây sẽ xem được đường dẫn đó. Thử xem source code của trang web, tại file `index.php` thì chỉ có code HTML thông thường, phần code xử lý chính của bài nằm ở file `loadImage.php`, đoạn code của file:

```
<?php 
$file = $_GET['file'];
if (strpos($file, "..") !== false)
    die("Hack detected");
if (file_exists($file)) {
    header('Content-Type: image/png');
    readfile($file);
}
else { // Image file not found
    echo " 404 Not Found";
}?>
```

Đầu tiên dữ liệu đầu vào là tên file được truyền vào paramater `file` và được truyền vào biến `$file`, sau đó được kiểm tra xem trong tên file có chứa `..` nhằm tránh bị backdir về các directory cha như bài trước. Đường dẫn file sau đó sẽ được kiểm tra bằng hàm `file_exists` xem có tồn tại không, nếu có thì đọc file bằng hàm `readfile`, nếu không thì trả về 404.

## Vấn đề

Vì dữ liệu lấy ra từ `$_GET['file']` là một untrust data được kiểm soát bởi client:
```
/loadImage.php?file_name=motfilenaodokhac.blabla
```
Tuy nhiên lần này anh "nập trình viên" đã đặt một bước kiểm tra ký tự `..` để tránh bị tấn công như bài trước. Nhưng khác với bài trước là không có đường dẫn nào được nối vào trước tên file cả, nên lần này ta không cần phải back về các directory cha như bài trước mà ta có thể truy cập trực tiếp vào root directory `/`, sau đó có truy cập đến đường dẫn `etc` và cuối cùng là đến file `passwd`.

## Tấn công

Với những gì mình đã nói ở trên, thì payload của ta sẽ thành:
```
/loadImage.php?file_name=/etc/passwd
```

![](https://i.imgur.com/c3jCHb8.png)

Vậy là ta đã xong bài lab!
