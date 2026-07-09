<?php
// 设置页面编码
header('Content-Type: text/html; charset=utf-8');

// 从Linux系统环境变量中读取管理员凭证，提高安全性
// 在Linux系统中，可以通过以下命令设置环境变量：
// export RP_ADMIN_USERNAME='your_username'
// export RP_ADMIN_PASSWORD='your_secure_password'
$ADMIN_USERNAME = getenv('RP_ADMIN_USERNAME');
$ADMIN_PASSWORD = getenv('RP_ADMIN_PASSWORD');

// 如果环境变量未设置，使用默认值（仅用于开发和测试环境）
// 生产环境中应该要求设置环境变量
if (empty($ADMIN_USERNAME)) {
    $ADMIN_USERNAME = 'Admin_JiaoLuo';
}
if (empty($ADMIN_PASSWORD)) {
    $ADMIN_PASSWORD = 'ASHGAGiog5459549$agbo#agbLBZMGadoga';
}

// 文件存储目录
$UPLOAD_DIR = './uploads/';
$UPDATE_INFO_FILE = './update_info.json';

// 确保上传目录存在
if (!is_dir($UPLOAD_DIR)) {
    mkdir($UPLOAD_DIR, 0777, true);
}

// 登录状态检查
$is_logged_in = isset($_SESSION['admin_logged_in']) && $_SESSION['admin_logged_in'] === true;

// 启动会话
if (!session_id()) {
    session_start();
}

// 处理登录请求
if (isset($_POST['login'])) {
    $username = isset($_POST['username']) ? $_POST['username'] : '';
    $password = isset($_POST['password']) ? $_POST['password'] : '';
    
    if ($username === $ADMIN_USERNAME && $password === $ADMIN_PASSWORD) {
        $_SESSION['admin_logged_in'] = true;
        $is_logged_in = true;
    } else {
        $login_error = '用户名或密码错误';
    }
}

// 处理登出请求
if (isset($_GET['action']) && $_GET['action'] === 'logout') {
    $_SESSION['admin_logged_in'] = false;
    session_destroy();
    $is_logged_in = false;
}

// 处理上传更新包
$upload_success = false;
$upload_error = '';

if ($is_logged_in && isset($_POST['upload_update'])) {
    // 检查是否有文件上传
    if (isset($_FILES['update_package']) && $_FILES['update_package']['error'] === UPLOAD_ERR_OK) {
        $file_name = $_FILES['update_package']['name'];
        $file_tmp = $_FILES['update_package']['tmp_name'];
        $file_size = $_FILES['update_package']['size'];
        $file_type = $_FILES['update_package']['type'];
        
        // 获取文件扩展名
        $file_ext = strtolower(pathinfo($file_name, PATHINFO_EXTENSION));
        
        // 允许的文件类型（可以根据需要修改）
        $allowed_extensions = array('zip', 'rar', '7z', 'exe', 'msi');
        
        if (in_array($file_ext, $allowed_extensions)) {
            // 生成唯一的文件名
            $unique_file_name = 'update_' . date('YmdHis') . '.' . $file_ext;
            $target_path = $UPLOAD_DIR . $unique_file_name;
            
            if (move_uploaded_file($file_tmp, $target_path)) {
                // 获取版本信息和更新日志
                $version = isset($_POST['version']) ? $_POST['version'] : '';
                $update_log = isset($_POST['update_log']) ? $_POST['update_log'] : '';
                $force_update = isset($_POST['force_update']) ? true : false;
                
                // 计算文件哈希值（用于验证文件完整性）
                $file_hash = hash_file('sha256', $target_path);
                
                // 保存更新信息
                $update_info = array(
                    'version' => $version,
                    'file_name' => $unique_file_name,
                    'file_size' => $file_size,
                    'file_hash' => $file_hash,
                    'update_log' => $update_log,
                    'force_update' => $force_update,
                    'release_date' => date('Y-m-d H:i:s')
                );
                
                // 读取现有更新信息（如果有）
                $all_updates = array();
                if (file_exists($UPDATE_INFO_FILE)) {
                    $all_updates = json_decode(file_get_contents($UPDATE_INFO_FILE), true);
                    if (!is_array($all_updates)) {
                        $all_updates = array();
                    }
                }
                
                // 添加新的更新信息
                array_unshift($all_updates, $update_info);
                
                // 只保留最近5个版本的信息
                if (count($all_updates) > 5) {
                    $all_updates = array_slice($all_updates, 0, 5);
                }
                
                // 保存更新信息到文件
                if (file_put_contents($UPDATE_INFO_FILE, json_encode($all_updates, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT))) {
                    $upload_success = true;
                } else {
                    $upload_error = '保存更新信息失败';
                }
            } else {
                $upload_error = '文件上传失败';
            }
        } else {
            $upload_error = '不支持的文件类型';
        }
    } else {
        $upload_error = '请选择要上传的文件';
    }
}

// 获取当前更新信息
$current_update = null;
$all_updates = array();
if (file_exists($UPDATE_INFO_FILE)) {
    $all_updates = json_decode(file_get_contents($UPDATE_INFO_FILE), true);
    if (is_array($all_updates) && !empty($all_updates)) {
        $current_update = $all_updates[0];
    }
}

// 如果未登录，显示登录页面
if (!$is_logged_in):
?>
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>管理员登录 - 资源包转换工具更新服务器</title>
    <style>
        body {
            font-family: 'Microsoft YaHei', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 400px;
            margin: 50px auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .login-container {
            background-color: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }
        h1 {
            text-align: center;
            color: #4CAF50;
        }
        .form-group {
            margin-bottom: 15px;
        }
        .form-group label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        .form-group input {
            width: 100%;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
            box-sizing: border-box;
        }
        .btn {
            width: 100%;
            background-color: #4CAF50;
            color: white;
            padding: 10px;
            border: none;
            border-radius: 4px;
            font-size: 16px;
            cursor: pointer;
        }
        .btn:hover {
            background-color: #45a049;
        }
        .error {
            color: red;
            text-align: center;
            margin-bottom: 15px;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <h1>管理员登录</h1>
        <?php if (isset($login_error)): ?>
            <div class="error"><?php echo $login_error; ?></div>
        <?php endif; ?>
        <form method="post" action="admin_post_login.php">
            <div class="form-group">
                <label for="username">用户名：</label>
                <input type="text" id="username" name="username" required>
            </div>
            <div class="form-group">
                <label for="password">密码：</label>
                <input type="password" id="password" name="password" required>
            </div>
            <button type="submit" name="login" class="btn">登录</button>
        </form>
    </div>
</body>
</html>
<?php
// 如果已登录，显示管理页面
else:
?>
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>更新管理 - 资源包转换工具更新服务器</title>
    <style>
        body {
            font-family: 'Microsoft YaHei', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background-color: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }
        h1 {
            color: #4CAF50;
            text-align: center;
            margin-top: 0;
        }
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 1px solid #eee;
        }
        .btn {
            display: inline-block;
            background-color: #4CAF50;
            color: white;
            padding: 8px 16px;
            text-decoration: none;
            border-radius: 4px;
            font-weight: bold;
            border: none;
            cursor: pointer;
        }
        .btn:hover {
            background-color: #45a049;
        }
        .btn-danger {
            background-color: #f44336;
        }
        .btn-danger:hover {
            background-color: #d32f2f;
        }
        .form-group {
            margin-bottom: 15px;
        }
        .form-group label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        .form-group input[type="text"],
        .form-group textarea {
            width: 100%;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
            box-sizing: border-box;
        }
        .form-group textarea {
            height: 150px;
            resize: vertical;
        }
        .success {
            color: green;
            text-align: center;
            margin-bottom: 15px;
            padding: 10px;
            background-color: #e8f5e9;
            border-radius: 4px;
        }
        .error {
            color: red;
            text-align: center;
            margin-bottom: 15px;
            padding: 10px;
            background-color: #ffebee;
            border-radius: 4px;
        }
        .update-info {
            margin-top: 30px;
            padding: 20px;
            background-color: #f9f9f9;
            border-radius: 8px;
        }
        .update-info h2 {
            margin-top: 0;
            color: #4CAF50;
        }
        .update-list {
            list-style-type: none;
            padding: 0;
        }
        .update-item {
            padding: 15px;
            border-bottom: 1px solid #eee;
        }
        .update-item:last-child {
            border-bottom: none;
        }
        .update-item .version {
            font-weight: bold;
            color: #4CAF50;
        }
        .update-item .date {
            color: #777;
            font-size: 0.9em;
        }
        .update-item .log {
            margin-top: 10px;
            white-space: pre-wrap;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>更新管理</h1>
            <a href="admin_post_login.php?action=logout" class="btn btn-danger">退出登录</a>
        </div>
        
        <?php if ($upload_success): ?>
            <div class="success">更新包上传成功！</div>
        <?php elseif ($upload_error): ?>
            <div class="error"><?php echo $upload_error; ?></div>
        <?php endif; ?>
        
        <form method="post" enctype="multipart/form-data" action="admin_post_login.php">
            <div class="form-group">
                <label for="version">版本号：</label>
                <input type="text" id="version" name="version" placeholder="例如：1.0.1" required>
            </div>
            
            <div class="form-group">
                <label for="update_package">更新包文件：</label>
                <input type="file" id="update_package" name="update_package" required>
            </div>
            
            <div class="form-group">
                <label for="update_log">更新日志：</label>
                <textarea id="update_log" name="update_log" placeholder="请输入更新内容..." required></textarea>
            </div>
            
            <div class="form-group">
                <label>
                    <input type="checkbox" name="force_update"> 强制更新
                </label>
            </div>
            
            <button type="submit" name="upload_update" class="btn">上传更新包</button>
        </form>
        
        <div class="update-info">
            <h2>当前更新信息</h2>
            <?php if ($current_update): ?>
                <div class="update-item">
                    <div class="version">版本：<?php echo $current_update['version']; ?></div>
                    <div class="date">发布日期：<?php echo $current_update['release_date']; ?></div>
                    <div class="log">更新日志：
                        <?php echo nl2br($current_update['update_log']); ?>
                    </div>
                    <div>文件大小：<?php echo round($current_update['file_size'] / 1024 / 1024, 2); ?> MB</div>
                    <div>文件哈希：<?php echo $current_update['file_hash']; ?></div>
                    <div>强制更新：<?php echo $current_update['force_update'] ? '是' : '否'; ?></div>
                </div>
            <?php else:
                echo '<p>暂无更新信息</p>';
            endif; ?>
        </div>
        
        <?php if (count($all_updates) > 1): ?>
            <div class="update-info">
                <h2>历史更新记录</h2>
                <ul class="update-list">
                    <?php for ($i = 1; $i < count($all_updates); $i++):
                        $update = $all_updates[$i];
                    ?>
                        <li class="update-item">
                            <div class="version">版本：<?php echo $update['version']; ?></div>
                            <div class="date">发布日期：<?php echo $update['release_date']; ?></div>
                        </li>
                    <?php endfor; ?>
                </ul>
            </div>
        <?php endif; ?>
    </div>
</body>
</html>
<?php endif; ?>