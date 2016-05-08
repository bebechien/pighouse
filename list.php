// 간단히 외부 서버에 있는 txt 가져오는 방법
<?php
$txt = file_get_contents('http://remote.url/list.txt');
echo $txt;
?>

// video 폴더 밑에 있는 mp4 목록을 만드는 예제 (최신 파일 순으로 정렬)
<?php
function scan_dir($dir) {
    $ignored = array('.', '..', '.svn', '.htaccess');

    $files = array();    
    foreach (scandir($dir) as $file) {
        if (in_array($file, $ignored)) continue;
        $files[$file] = filemtime($dir . '/' . $file);
    }

    arsort($files);
    $files = array_keys($files);

    return ($files) ? $files : false;
}

function file_list($d,$x) {
  foreach(scan_dir($d) as $f)if(is_file($d.'/'.$f)&&(($x)?ereg($x.'$',$f):1))$l[]=$f;
  return $l;
}

function listup($d, $prefix) {
  $list = file_list($d, "mp4");
  foreach($list as $file) :
    if (!empty($prefix)) {
      print($prefix."http://server.url/".$d.rawurlencode($file)."\n");
    }
    else {
      print("http://server.url/".$d.rawurlencode($file)."\n");
    }
  endforeach;
}

listup("video/", "");
?>
