// 간단히 외부 서버에 있는 txt 가져오는 방법
<?php
$txt = file_get_contents('http://remote.url/list.txt');
echo $txt;
?>

// video 폴더 밑에 있는 동영상 목록을 만드는 예제 (정렬 옵션 추가)
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
  $imp = implode('|', $x);
  foreach(scan_dir($d, $sort_type) as $f) if(is_file($d.'/'.$f) && preg_match('/^.*\.('.$imp.')$/i', $f)) $l[]=$f;
  return $l;
}

function listup($d, $prefix, $sort_type) {
  $video_ext = array("mp4", "m4v", "mkv", "avi", "ts");
  $list = file_list($d, $video_ext, $sort_type);
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

// video 폴더를 recursive하게 탐색해 동영상 목록을 만드는 예제 (정렬 옵션 추가)
<?php
function scan_video($prefix, $dir, $sort_type = '', $contains='', $parent = '') {
  $dir = rtrim($dir, '\\/');
  $ignored = array('.', '..', '.svn', '.htaccess');

  $files = array();    
  foreach (scandir($dir) as $file) {
    if (in_array($file, $ignored)) continue;
    if (is_dir("$dir/$file")) scan_video($prefix, "$dir/$file", $sort_type, $contains, "$parent$file/");
    else $files[$file] = filemtime($dir . '/' . $file);
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

  $video_ext = array("mp4", "m4v", "mkv", "avi", "ts");
  $imp = implode('|', $video_ext);

  foreach ($files as $file) {
    $add_list = true;
    if (!empty($contains) && !preg_match('/'.$contains.'/i', $file)) $add_list=false;
    if(preg_match('/^.*\.('.$imp.')$/i', $file) && $add_list) {
      $path = implode("/", array_map("rawurlencode", explode("/", $dir."/".$file)));
      if (!empty($prefix)) {
        print($prefix."http://server.url/".$path."\n");
      }
      else {
        print("http://server.url/".$path."\n");
      }
    }
  }
}

// sort by name
scan_video("", "video");

// oldest to latest
scan_video("", "video", "oldest");
// latest to oldest
scan_video("", "video", "latest");

// contains specific word in a filename
scan_video("", "video", "", "x265");

?>
