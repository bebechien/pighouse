package main

import (
  "os"
  "fmt"
  "bytes"
  "bufio"
  iconv "github.com/djimenez/iconv-go"
)

const STRLEN = 80
const STRUCT_SIZE = 3072

const INDEX_HEADER = "<html><head><meta http-equiv=\"Content-Type\" content=\"text/html; charset=utf-8\"></head><body>"
const INDEX_FOOTER = "</body></html>"

//struct fileheader {             /* This structure is used to hold data in */
//	char filename[STRLEN] ;     /* the BOARDS and DIR files               */
//	char owner[STRLEN] ;
//	char title[STRLEN] ;
//	unsigned level;
//	unsigned char tm_year;	/* struct tm 구조 멤버와 동일하게 이름붙였음 */
//	unsigned char tm_mon;
//	unsigned char tm_mday;
//	unsigned char isdirectory; /* chopin */
//				   /* .BOARDS 파일에만 사용되는 플랙이고 */
//				   /* 보드이름이면 0 		*/
//				   /* 디렉토리 이름이면 1 	*/
//	unsigned short int readcnt;/* 조회수 */
//	unsigned char directory_zapped; /* 특정 디렉토리를 뉴에서 읽히지 
//					않도록 하는 플래그 
//					closed보드등에서 이용 */
//	/* dummy */
//	unsigned char dummy[217];
//	unsigned char accessed[MAXUSERS] ;
//};

type Article struct {
  id int
  filename string
  owner string
  title string
}

func ReadDIR(path string) ([]Article, error) {
  var ArticleList []Article

  file, err := os.Open(path + "/.DIR")
  if err != nil {
      return ArticleList, err
  }
  defer file.Close()

  entryBuf := make([]byte, STRUCT_SIZE)

  idx := 0
  for true {
    idx++

    _, err := file.Read(entryBuf)
    if err != nil {
      break
    }
    // each entry starts with the filename which is typically "77 46"
    //fmt.Println(entryBuf)

    var b bytes.Buffer
    b.Grow(64)
    b.Write(entryBuf)
    rdbuf := make([]byte, STRLEN)
    _, err = b.Read(rdbuf)
    if err != nil {
      break
    }
    filename := string(rdbuf)
    _, err = b.Read(rdbuf)
    if err != nil {
      break
    }
    owner := string(rdbuf)
    _, err = b.Read(rdbuf)
    if err != nil {
      break
    }
    title, _ := iconv.ConvertString(string(rdbuf), "euc-kr", "utf-8")

    ArticleList = append(ArticleList, Article{idx, filename, owner, title})
  }

  return ArticleList, err
}

func GenerateIdx(path string, list []Article) {
  file, err := os.Create(path + "/index.html")
  if err != nil {
    fmt.Println(err)
    return
  }
  defer file.Close()
  w := bufio.NewWriter(file)

  fmt.Fprint(w, INDEX_HEADER)

  for _, item := range list {
    fmt.Fprintf(w, "%d ", item.id)
    fmt.Fprintf(w, "%s, %s, %s<BR>", item.filename, item.owner, item.title)
    fmt.Fprintln(w)
  }

  fmt.Fprint(w, INDEX_FOOTER)
  w.Flush()
}

func main() {
  board := "/path/to/the/board"
  outpath := "/path/to/the/output"
  if err := os.MkdirAll(outpath, os.ModePerm); err != nil {
    fmt.Println(err)
    return
  }

  articles, err := ReadDIR(board)
  if err != nil {
    fmt.Println(err)
  }

  GenerateIdx(outpath, articles)
}
