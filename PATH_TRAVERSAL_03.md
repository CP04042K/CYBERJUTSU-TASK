# PATH_TRAVERSAL level 03 

Đây là một trang web cho phép upload hình ảnh vào một album, cùng nhìn vào phần code xử lý upload trong file `index.php`:

```
<?php

    // Create store place for each user (we place this in /usr/upload for easily handle)
    session_start();
    if (!isset($_SESSION['dir'])) {

        $_SESSION['dir'] = '/usr/upload/' . bin2hex(random_bytes(16));
    }
    $dir = $_SESSION['dir'];

    if ( !file_exists($dir) )
        mkdir($dir);

    if(isset($_FILES["files"]) && $_POST['album'] !="" ) {
        try {

            //Create Album
            $album = $dir . "/" . strtolower($_POST['album']);
            if ( !file_exists($album))
                mkdir($album);

            //Count Files
            $files = $_FILES['files'];
            $count = count($files["name"]);
            
            // Save files to user's directory
            for ($i = 0; $i < $count; $i++) {
                
                $newFile = $album . "/" . $files["name"][$i];

                move_uploaded_file($files["tmp_name"][$i], $newFile);
            }

       } catch(Exception $e) {
            $error = $e->getMessage();
         }
    }
?>
```

Đầu tiên thì một thư mục mới sẽ được tạo cho mỗi lần upload, và gán vào `$_SESSION['dir']`. Thư mục này có đường dẫn gốc là `/usr/upload/` và sau đó được nối vào `bin2hex(random_bytes(16))` để tạo ra một thư mục ngẫu nhiên, nếu thư mục này chưa tồn tại thì sẽ tiến hành tạo mới:
```
session_start();
if (!isset($_SESSION['dir'])) {

    $_SESSION['dir'] = '/usr/upload/' . bin2hex(random_bytes(16));
}
$dir = $_SESSION['dir'];

if ( !file_exists($dir) )
    mkdir($dir);
```

Tiếp đó là kiểm tra, xem trong POST data có chứa file và `album` không, nếu có thì sẽ thực hiện các bước:
* Tạo thư mục với tên `$dir` + `album`
* Đếm số file upload lên
* Upload tất cả file vào thư mục đã tạo

```
if(isset($_FILES["files"]) && $_POST['album'] !="" ) {
        try {

            //Create Album
            $album = $dir . "/" . strtolower($_POST['album']);
            if ( !file_exists($album))
                mkdir($album);

            //Count Files
            $files = $_FILES['files'];
            $count = count($files["name"]);
            
            // Save files to user's directory
            for ($i = 0; $i < $count; $i++) {
                
                $newFile = $album . "/" . $files["name"][$i];

                move_uploaded_file($files["tmp_name"][$i], $newFile);
            }

       } catch(Exception $e) {
            $error = $e->getMessage();
         }
    }
```

Ngoài ra trong challenge này còn có một yếu tố cần chú ý đến, đó là 2 file config `000-default.conf` và `apache2.conf`, 2 file này là 2 file config của apache dùng để nói cho apache biết cách handle các http request.

Ở file `000-default.conf` ta chú ý đến phần:
```
# CHANGELOG: if request to /upload/* then serve /usr/upload/*
Alias "/upload/" "/usr/upload/"
```

Như phần comment đã trình bày thì dòng config này nói apache là nếu client truy cập vào thư mục `/upload/` thì trả cho nó nội dung của file tương ứng trong thư mục `/usr/upload/` (giống như một symlink)

Ở file `apache2.conf` ta chú ý đến đoạn:
```
# CHANGELOG: disable execution of php code in upload folder and safely return content-type
<Directory "/usr/upload/">
        AllowOverride None
        Require all granted

        <FilesMatch ".*">
                SetHandler None
        </FilesMatch>

        Header set Content-Type application/octet-stream

        <FilesMatch ".+\.jpg$">
                Header set Content-Type image/jpeg
        </FilesMatch>
        <FilesMatch ".+\.png$">
                Header set Content-Type image/png
        </FilesMatch>
        <FilesMatch ".+\.(html|txt|php)">
                Header set Content-Type text/plain
        </FilesMatch>
</Directory>
```

Đoạn config này **sẽ được áp dụng trong phạm vi thư mục `/usr/upload/`**, như trong comment có nói thì nó sẽ vô hiệu hóa việc thực thi code php trong thư mục này (thay vì thực thi thì trả về văn bản thuần)

Tóm lại cách tổ chức của web là: user upload lên thư mục `/usr/upload`, tạo alias từ `/upload/` đến `/usr/upload` để user truy cập được vào file mình đã upload, cuối cùng là vô hiệu hóa việc thực thi code php trong thư mục `/usr/upload` để tránh bị upload file php độc hại.

## Vấn đề

Ở đây `$_POST['album']` là một untrust data và lại được nối trực tiếp với `$dir` để tạo thư mục upload mà qua một cơ chế kiểm tra nào:

![](https://i.imgur.com/CYTm3MI.png)

=> Ta có thể truyền vào ký tự `../` để kiểm soát việc file chuẩn bị upload sẽ được upload vào thư mục nào. Như đã biết thì tromg thư mục `/usr/upload` và các thư mục con sẽ bị vô hiệu hóa thực thi php

![](https://i.imgur.com/OyXiozt.png)

## Ý tưởng

Vậy nên ta cần tìm một thư mục thỏa 2 điều kiện
* Nằm ngoài `/usr/upload` 
* Có thể ghi được bằng quyền của user hiện tại (phải có quyền ghi thì mới upload được)

Còn một yếu tố nữa mà mình chưa nhắc đến, đó là file docker:

![](https://i.imgur.com/HVcbsyI.png)

Để ý thấy thư mục `/var/www/html` đã được cấp quyền ghi, ta có thể ghi được vào thư mục này. Trong thực tế nếu không có file docker ta có thể thử ghi vào nhiều thư mục khác nhau cho đến khi được thì thôi :) 


## Tấn công

Với những gì mình đã nói ở trên, thì post data của ta sẽ thành:

![](https://i.imgur.com/0r8Y0VE.png)

3 ký tự `../` dùng để di chuyển về thư mục root `/`, từ đó đi đến đường dẫn `/var/www/html/`

![](https://i.imgur.com/QBKxLtj.png)


Vậy là ta đã xong bài lab!
