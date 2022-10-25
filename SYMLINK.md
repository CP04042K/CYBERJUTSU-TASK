# SYMLINK 

Đây là trang web cho phép upload một file zip, sau đó giải nén nó vào lưu trữ vào server. Nhìn vào đoạn code giải nén:

```
if(isset($_FILES["file"])) {
    try {
        // Fixed: Dont save file to user's directory, only use tmp_name
        // unzip the file
        $name = '/tmp/name';
        move_uploaded_file($_FILES["file"]["tmp_name"], $name);

        $cmd = "unzip " . $name . " -d " . $dir;
        $debug = shell_exec($cmd);

        // Remove /usr/ from directory
        $user_dir = substr($dir, 5);
        $success = 'Successfully uploaded and unzip files into <a href="' . $user_dir . '/">' . $user_dir .'</a>';
    } catch(Exception $e) {
        $error = $e->getMessage();
    }
}
```
Tại câu lệnh unzip, ta thấy có có dùng hàm `shell_exec`, nhưng có vẻ như không có untrust data nào được đưa vào hàm này.
```
$cmd = "unzip " . $name . " -d " . $dir;
$debug = shell_exec($cmd);
```

Vì mục tiêu của bài là đọc được file bất kì trên server nên ta sẽ phải tìm ra cách để lợi dụng việc unzip để đọc file, nhưng làm sao để đạt được điều này nhỉ

## Ý tưởng

Như ta đã biết thì zip có khả năng nén symbolic link, và khi giải nén thì các symbolink link này sẽ được nối lại liên kết với file hiện tại trên server đó.

Nén thường:

![](https://i.imgur.com/lX4Jm7D.png)


Nén với option `-y` (chứa symlink):

![](https://i.imgur.com/tVUZHoj.png)

Như ta thấy thì trong file zip khi mở lên sẽ không thấy gì, thử dùng `cat` để xem nội dung:

![](https://i.imgur.com/C9VfUJ3.png)

Ta thấy được `/etc/passwd`, vậy khi zip ở dạng symlink thì tuy không hiển thị khi xem nhưng symlink vẫn nằm bên trong.

Vậy liệu nếu upload file zip này lên server thì khi giải nén ra, file đã giải nén cho được link đến `/etc/passwd` không, cùng kiểm chứng nào

## Tấn công

Upload file `test.zip` lên server

![](https://i.imgur.com/QZKNYjx.png) 

Truy cập vào file `simp.txt` vừa giải nén trên server:

![](https://i.imgur.com/S4VPRP2.png)

Vậy là ta đã thành công đọc được file ở `/etc/passwd` ở server.
