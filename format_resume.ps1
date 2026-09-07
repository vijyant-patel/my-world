$docPath = "C:\Users\Harendra\Downloads\Bharat_Yadav_Same_Format_ATS_Resume.docx"
$backupPath = "C:\Users\Harendra\Downloads\Bharat_Yadav_Same_Format_ATS_Resume_Backup.docx"
Copy-Item $docPath $backupPath -Force

$word = New-Object -ComObject Word.Application
$word.Visible = $false
try {
    $doc = $word.Documents.Open($docPath)
    
    # 1. Set Margins to 0.75 inch (54 points)
    $doc.PageSetup.TopMargin = 54
    $doc.PageSetup.BottomMargin = 54
    $doc.PageSetup.LeftMargin = 54
    $doc.PageSetup.RightMargin = 54

    # 2. Set all text to standard ATS-friendly font: Arial, 11pt, Black
    $doc.Content.Font.Name = "Arial"
    $doc.Content.Font.Size = 11
    
    # 3. Standardize Paragraph Spacing
    $doc.Content.ParagraphFormat.SpaceBefore = 0
    $doc.Content.ParagraphFormat.SpaceAfter = 4
    $doc.Content.ParagraphFormat.LineSpacingRule = 0 # wdLineSpaceSingle
    
    # 4. Make Headings standout
    $headings = @("EDUCATION", "EXPERIENCE", "SKILLS", "SUMMARY", "PROJECTS", "ACHIEVEMENTS", "CERTIFICATIONS", "WORK EXPERIENCE", "PROFESSIONAL EXPERIENCE", "TECHNICAL SKILLS")
    foreach ($para in $doc.Paragraphs) {
        $text = $para.Range.Text.Trim().ToUpper()
        
        # Remove trailing carriage returns/bells
        $text = $text -replace "[\r\n\a]", ""
        
        foreach ($h in $headings) {
            if ($text -eq $h) {
                $para.Range.Font.Size = 14
                $para.Range.Font.Bold = 1
                $para.Range.Font.ColorIndex = 1 # wdBlack
                $para.Range.ParagraphFormat.SpaceBefore = 12
                $para.Range.ParagraphFormat.SpaceAfter = 6
                # Bottom border = -3 (wdBorderBottom)
                $para.Range.Borders.Item(-3).LineStyle = 1 # wdLineStyleSingle
                $para.Range.Borders.Item(-3).LineWidth = 4 # 0.50 pt
            }
        }
    }

    $doc.Save()
    $doc.Close()
    Write-Host "Success formatting document."
} catch {
    Write-Host "Error: $_"
} finally {
    $word.Quit()
    [System.Runtime.Interopservices.Marshal]::ReleaseComObject($word) | Out-Null
}
