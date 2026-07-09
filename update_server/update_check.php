<?php
// 设置页面编码
header('Content-Type: application/json; charset=utf-8');

// 允许跨域请求
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');

// 更新信息文件路径
$UPDATE_INFO_FILE = './update_info.json';

// 检查文件是否存在
if (!file_exists($UPDATE_INFO_FILE)) {
    echo json_encode(array(
        'status' => 'error',
        'message' => '更新信息文件不存在'
    ));
    exit;
}

// 读取更新信息
$update_data = file_get_contents($UPDATE_INFO_FILE);
$updates = json_decode($update_data, true);

// 检查数据是否有效
if (!is_array($updates) || empty($updates)) {
    echo json_encode(array(
        'status' => 'error',
        'message' => '更新信息无效'
    ));
    exit;
}

// 获取最新的更新信息
$latest_update = $updates[0];

// 构造返回数据
$response = array(
    'status' => 'success',
    'has_update' => true,
    'version' => $latest_update['version'],
    'file_name' => $latest_update['file_name'],
    'file_size' => $latest_update['file_size'],
    'file_hash' => $latest_update['file_hash'],
    'update_log' => $latest_update['update_log'],
    'force_update' => $latest_update['force_update'],
    'release_date' => $latest_update['release_date'],
    'download_url' => './uploads/' . $latest_update['file_name']
);

// 返回JSON数据
echo json_encode($response, JSON_UNESCAPED_UNICODE);
?>