# PATH_TRAVERSAL level 05 

Đây là một trang web chơi game flappy bird :), khi bấm start game thì ta sẽ chơi được game. Nhìn vào source code `index.php`:

```
<?php
    // error_reporting(0);
    if (!isset($_GET['game'])) {
        header('Location: /?game=fatty-bird-1.html');
    }
    $game = $_GET['game'];
?>

<!DOCTYPE html>
<html lang="en">
    <head>
        <?php include './views/header.html'; ?>
    </head>

    <body>
        <br><br>
        <p class="display-5 text-center">Goal: RCE me</p>

        <br>
        <div style="background-color: white; padding: 20px;">
            <?php include './views/' . $game; ?>
        </div>

    </body>

    <?php include './views/footer.html' ?>
</html>
```

So với các bài trước thì source code của bài này khá đơn giản, nhận vào một input bằng get param `game`:
```
$game = $_GET['game'];
```
Sau đó truyền nó vào câu `include`:
```
<?php include './views/' . $game; ?>
```

Chủ ý của anh lập trình viên là muốn lấy nội dung của các file game dạng HTML hiển thị lên trang.

## Vấn đề

Vấn đề ở đây, như các bạn hẳn đều nhận ra, dữ liệu lấy từ `$_GET['game']` là một untrust data được cung cấp bởi client, việc nối thẳng nó vào câu `include` có thể giúp một hacker đọc một file bất kì. Thay vì `?game=fatty-bird-1.html` thì một hacker có thể ghi là `?game=test.html`, lúc này file đang được đọc sẽ nằm ở:
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
![](https://i.imgur.com/nXgrxNt.png)

Nhưng mục tiêu ở đây là RCE, mình nghĩ một số bạn cũng sẽ nghĩ như mình, làm sao mà từ việc đọc một file có thể dẫn đến việc bị RCE được ta?

## Ý tưởng

Đoạn code khá ngắn, phần php đầu không có gì đặc biệt, nên mọi sự chú ý của mình dồn vào câu `include` kia. Để hack cái gì thì phải hiểu rõ nó, mình thử google để tìm hiểu về `include`:

![](https://i.imgur.com/OjZwV32.png)

Tác dụng của `include` là lấy nội dung của một file và **thực thi nó như code PHP**, có một điểm cần chú ý đó là `include` sẽ tự nhận dạng code php trong cặp dấu `<?php ?>`, không quan trọng đuôi hay định dạng file đó là gì, chỉ cần có cặp dấu trên thì các nội dung trong cặp dấu đó sẽ được thực thi như code php.

![](https://i.imgur.com/eaYHnMz.png)

Ok nhưng mà giờ làm sao để lợi dụng được điều này nhỉ. Mình bắt đầu nghĩ theo hướng liệu có nơi nào mà input của mình sẽ được ghi lại hay không, cuối cùng mình nhớ ra **Log**

Nhìn vào file `000-default.conf`:
```
<VirtualHost *:80>
  ServerAdmin webmaster@localhost
  DocumentRoot /var/www/html

  Alias "/upload/" "/usr/upload/"

  ErrorLog ${APACHE_LOG_DIR}/error.log
  CustomLog ${APACHE_LOG_DIR}/access.log combined
</VirtualHost>

```
Ta thấy server có setup để ghi log vào file tại đường dẫn `${APACHE_LOG_DIR}/access.log`, tìm hiểu thêm về file `access.log`:
![](https://i.imgur.com/UFymxMC.png)

Nôm na là file này sẽ ghi lại các thông tin về request gửi đến của ta như đường dẫn truy cập, IP, http method, user-agent, ...

Vậy ý tưởng của mình là ta sẽ gửi một request trong đó có một đoạn mã PHP ở bất cứ trường nào được server log lại (IP, http method, user-agent, resource, ...)

## Tấn công

Nhìn vào file Docker ta biết được vị trí của file `access.log` (trong thực tế thì đa phần vị trí file này có thể đoán được bằng fuzzing)

![](https://i.imgur.com/y3yma2f.png)

Giờ ta thử include file này:

![](https://i.imgur.com/eDl3XwH.png)

Nó chứa các truy cập của ta, ta thấy thông tin gồm các trường như http method, ip, user-agent, response code, ... Vậy giờ ta cần tiêm mã PHP vào một trong số các trường này trong request được gửi đi. Loại trừ đi các trường như response code, IP hay time line vì ta không thể chỉnh được thì còn lại các trường như HTTP method, resource, user-agent, cùng thử với phần user-agent xem sao:

![](https://i.imgur.com/DDaoBF2.png)

Kết quả:

![](https://i.imgur.com/CFMHMXp.png)

Mình đã dọn log để dễ nhìn hơn, chứ bình thường là nó rối mắt dữ lắm =)))

Đọc flag:

![](https://i.imgur.com/h9jSJm4.png)

Thật ra muốn đọc flag thì từ đầu có thể dùng path traversal để đọc cũng được, nhưng các anh muốn mình làm theo hướng này nên mình RCE rồi mới đọc flag :3

Vậy là ta đã xong bài lab!
