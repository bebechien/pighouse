package main

import (
	"bufio"
	"bytes"
	"encoding/binary"
	"fmt"
	"os"
	"strings"
	"github.com/djimenez/iconv-go"
)

const STRLEN = 80
const STRUCT_SIZE = 3072

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
	id       int
	filename string
	owner    string
	title    string
	date     string
	readcnt  int
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
		// each entry starts with the filename which is typically "77 46" ("M." in ASCII CODE)
		//fmt.Println(entryBuf)

		var b bytes.Buffer
		b.Write(entryBuf)
		var singlebuf byte

		filename := string(bytes.Trim(b.Next(STRLEN), "\x00"))
		owner, _ := iconv.ConvertString(string(bytes.Trim(b.Next(STRLEN), "\x00")), "euc-kr", "utf-8")
		title, _ := iconv.ConvertString(string(bytes.Trim(b.Next(STRLEN), "\x00")), "euc-kr", "utf-8")
		b.Next(4) // skip fileheader.level
		singlebuf, _ = b.ReadByte()
		tm_year := int(singlebuf)
		singlebuf, _ = b.ReadByte()
		tm_mon := int(singlebuf)
		singlebuf, _ = b.ReadByte()
		tm_mday := int(singlebuf)
		b.Next(1) // skip fileheader.isdirectory
		readcnt := int(binary.LittleEndian.Uint16(b.Next(2)))

		date := fmt.Sprintf("%d/%d/%d", tm_year+1900, tm_mon+1, tm_mday)

		ArticleList = append(ArticleList, Article{idx, filename, owner, title, date, readcnt})
	}

	return ArticleList, err
}

const INDEX_HEADER = "<html><head><meta http-equiv=\"Content-Type\" content=\"text/html; charset=utf-8\"></head>" +
	"<body><table><tr><th>번호</th><th>글쓴이</th><th>날짜</th><th>조회수</th><th>제목</th></tr>\n"
const INDEX_FOOTER = "</table></body></html>"

func GenerateIdx(path string, list []Article) {
	file, err := os.Create(path + "/index.html")
	if err != nil {
		fmt.Println(err)
		return
	}
	w := bufio.NewWriter(file)

	fmt.Fprint(w, INDEX_HEADER)

	for _, item := range list {
		fmt.Fprintf(w, "<tr onclick=\"location.href=`%s.html`\"=><td>%d</td><td>%s</td><td>%s</td><td>%d</td><td>%s</td></tr>\n", item.filename, item.id, item.owner, item.date, item.readcnt, item.title)
	}

	fmt.Fprint(w, INDEX_FOOTER)
	w.Flush()
	file.Close()
}

const PAGE_HEADER = "<html><head><meta http-equiv=\"Content-Type\" content=\"text/html; charset=utf-8\"></head><body id=\"body\">\n"
const PAGE_FOOTER = "</body></html>"

func GeneratePages(src string, path string, list []Article) {
  idx := 0
	for _, item := range list {
		file, err := os.Create(path + "/" + item.filename + ".html")
		if err != nil {
			fmt.Println(err)
			return
		}
		w := bufio.NewWriter(file)

		prev_move := ""
		if idx > 0 {
			prev_move = "case \"KeyP\":window.location=\""+list[idx-1].filename+".html\";break;"
		}
		next_move := ""
		if idx < len(list)-1 {
			next_move = "case \"KeyN\":window.location=\""+list[idx+1].filename+".html\";break;"
		}

		fmt.Fprintf(w, PAGE_HEADER)
		fmt.Fprintf(w, "<script>window.addEventListener(\"keydown\", (event) => {switch(event.code) {" +
		"case \"KeyQ\":window.location=\"index.html\";break;" + prev_move + next_move +
		"}}, true);</script>\n")

		src_data, err := os.ReadFile(src + "/" + item.filename)
		if err != nil {
			fmt.Println(err)
			file.Close()
			return
		}

		text, _ := iconv.ConvertString(string(bytes.Trim(src_data, "\x00")), "euc-kr", "utf-8")
		fmt.Fprintf(w, "<pre>%s</pre>", text)

		fmt.Fprintf(w, PAGE_FOOTER)
		w.Flush()
		file.Close()

		idx++
	}
}

func FallbackDIR(path string) ([]Article, error) {
	var ArticleList []Article

	files, err := os.ReadDir(path + "/.")
	if err != nil {
		return ArticleList, err
	}

	idx := 0
	for _, file := range files {
		idx++

		src, err := os.ReadFile(path + "/" + file.Name())
		if err != nil {
			return ArticleList, err
		}
		text, _ := iconv.ConvertString(string(bytes.Trim(src, "\x00")), "euc-kr", "utf-8")
		lines := strings.Split(text, "\n")
		if len(lines) < 3 {
			fmt.Printf("skip possible broken file [%s]\n", file.Name())
			fmt.Println(text)
			idx--
			continue
		}

		owner := ""
		title := file.Name()
		date := ""
		if strings.HasPrefix(lines[0], "Posted By:") {
			// old loco bbs type
			owner = strings.Fields(lines[0])[2]
			title = lines[1][11:]
			date = lines[2][11:]
		} else if strings.HasPrefix(lines[0], "글쓴이:") {
			owner = strings.Fields(lines[0])[1]
			date = lines[1][10:]
			title = lines[2][10:]
		} else {
			fmt.Printf("skip unknown format file [%s]\n", file.Name())
			idx--
			continue
		}

		ArticleList = append(ArticleList, Article{idx, file.Name(), owner, title, date, 0})
	}

	return ArticleList, nil
}

func main() {
	if len(os.Args) != 3 {
		fmt.Printf("Usage: %s <path-to-board> <path-to-output>\n", os.Args[0])
		return
	}

	board := os.Args[1]
	outpath := os.Args[2]

	if err := os.MkdirAll(outpath, os.ModePerm); err != nil {
		fmt.Println(err)
		return
	}

	articles, err := ReadDIR(board)
	if os.IsNotExist(err) {
		articles, err = FallbackDIR(board)
	}
	if err != nil {
		fmt.Println(err)
		return
	}

	GenerateIdx(outpath, articles)
	GeneratePages(board, outpath, articles)
}
