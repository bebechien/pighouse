<?php
// video_test.html 용 json video list 만드는 파일

function ListIn($dir, $prefix = '') {
  $dir = rtrim($dir, '\\/');
  $result = array();

    foreach (scandir($dir) as $f) {
      if ($f !== '.' and $f !== '..') {
        if (is_dir("$dir/$f")) {
          $result = array_merge($result, ListIn("$dir/$f", "$prefix$f/"));
        } else {
          $ext = pathinfo($f, PATHINFO_EXTENSION);
          if(preg_match("[mp4|mkv|m3u8]i", $ext, $matches)) {
            $result[] = $prefix.$f;
          }
        }
      }
    }
  return $result;
}

header('Content-type: application/json');
echo json_encode(ListIn("data1", "data1/"));
?>
