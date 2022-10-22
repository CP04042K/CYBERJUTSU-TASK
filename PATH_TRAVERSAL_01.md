# PATH_TRAVERSAL level 01 

Đây là một trang web xem hình ảnh, mỗi khi bấm vào nút view ở một ảnh nào đó thì ta sẽ bị điều hướng đến đường dẫn `/loadImage.php` và tại đây sẽ xem được đường dẫn đó. Thử xem source code của trang web, tại file `index.php` thì chỉ có code HTML thông thường, phần code xử lý chính của bài nằm ở file `loadImage.php`, đoạn code của file:

```
<?php 
$file_name = $_GET['file_name'];
$file_path = '/var/www/html/images/' . $file_name; 
if (file_exists($file_path)) {
    header('Content-Type: image/png');
    readfile($file_path);
}
else { // Image file not found
    echo " 404 Not Found";
}
```

Đầu tiên dữ liệu đầu vào là tên file được truyền vào paramater `file_name` và được truyền vào biến `$file_name`. Tiếp đó được nối với path `/var/www/html/images/`, đường dẫn file sau đó sẽ được kiểm tra bằng hàm `file_exists` xem có tồn tại không, nếu có thì đọc file bằng hàm `readfile`, nếu không thì trả về 404.

## Vấn đề

Vì dữ liệu lấy ra từ `$_GET['file_name']` là một untrust data được kiểm soát bởi client, thêm vào đó là không có cơ chế kiểm tra gì nên ta có thể tùy ý đọc bất cứ file nào của server.
```
/loadImage.php?file_name=motfilenaodokhac.blabla
```

Nhưng như trong code thì tên file được nối vào sau đường dẫn `/var/www/html/images/`, vậy nghĩa là ta chỉ đang đọc được các file nằm trong directory `/var/www/html/images/` thôi, vậy phải làm sao để đọc được một file bất kì trong các thư mục khác của server?

Như ta biết, ở terminal của linux nếu ta gõ `cd ../` thì nó sẽ đổi workdir của ta về thư mục cha. 

![](https://i.imgur.com/XUiPVFB.png)

Vậy ta có thể đùng ký tự này để đọc các file khác trong cùng server không nhỉ?

## Tấn công

Lấy trường hợp ta muốn đọc file `/etc/passwd`, phải làm sao để ta có thể đến được thư mục root `/` để từ đó truy cập vào thư mục `etc` và đọc file `passwd`:

![](https://i.imgur.com/2iG4IlR.png)

Như hình trên ta thấy, ta cần sử dụng ký tự `../` 4 lần để về lại thư mục root `/`, vậy ta sẽ có payload ban đầu là `../../../../`. Tiếp đến ta cần truy cập vào file `passwd` nằm trong directory `etc`, vậy payload sẽ thành `../../../../etc/passwd`, cùng thử payload này:

```
/loadImage.php?file_name=../../../../etc/passwd
```

Ta nhận về một ảnh lỗi, đây là do dòng code `header('Content-Type: image/png');` đã set Content-Type thành kiểu ảnh, dẫn đến trình duyệt cố gắng parse nội dung file trả về là ảnh, thử view source của trang vừa trả về:

![](https://i.imgur.com/WDEGnxq.png)

Vậy là ta đã xong bài lab!
