// 간단히 외부 서버에 있는 txt 가져오는 방법
<?php
$txt = file_get_contents('http://remote.url/list.txt');
echo $txt;
?>

// video 폴더 밑에 있는 mp4 목록을 만드는 예제 (정렬 옵션 추가)
<?php
function scan_dir($dir, $sort_type) {
  $ignored = array('.', '..', '.svn', '.htaccess');

  $files = array();    
  foreach (scandir($dir) as $file) {
    if (in_array($file, $ignored)) continue;
    $files[$file] = filemtime($dir . '/' . $file);
  }

  if (empty($sort_type)) {
    $files = array_keys($files);
  }
  else {
    if($sort_type == "oldest") {
      asort($files);
    }
    else if($sort_type == "latest") {
      arsort($files);
    }
    $files = array_keys($files);
  }

  return ($files) ? $files : false;
}

function file_list($d,$x, $sort_type) {
  foreach(scan_dir($d, $sort_type) as $f)if(is_file($d.'/'.$f)&&(($x)?ereg($x.'$',$f):1))$l[]=$f;
  return $l;
}

function listup($d, $prefix, $sort_type) {
  $list = file_list($d, "mp4", $sort_type);
  foreach($list as $file) :
    if (!empty($prefix)) {
      print($prefix."http://server.url/".$d.rawurlencode($file)."\n");
    }
    else {
      print("http://server.url/".$d.rawurlencode($file)."\n");
    }
  endforeach;
}

// sort by name
listup("video/", "", "");

// oldest to latest
listup("video/", "", "oldest");
// latest to oldest
listup("video/", "", "latest");

?>
