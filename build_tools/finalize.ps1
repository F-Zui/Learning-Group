# 只做一件事：用 Word 更新目录域，然后保存 docx
$ErrorActionPreference = "Stop"
$doc_path = "D:\文档\学习中转\c++\算法竞赛模板手册.docx"

$w = New-Object -ComObject Word.Application
$w.Visible = $false
$w.DisplayAlerts = 0
$doc = $w.Documents.Open($doc_path, $false, $false)

for ($i = 1; $i -le $doc.TablesOfContents.Count; $i++) {
    $doc.TablesOfContents.Item($i).Update()
}
$doc.Repaginate()
$doc.Save()
$doc.Close($false)
$w.Quit()
Write-Output "toc updated"
