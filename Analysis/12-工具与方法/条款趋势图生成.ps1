Param(
  [string]$Trend = "reports/week/trend.json",
  [string]$Out42010 = "reports/week/trend-42010.png",
  [string]$Out25010 = "reports/week/trend-25010.png",
  [string]$Out15288 = "reports/week/trend-15288.png",
  [string]$Out12207 = "reports/week/trend-12207.png",
  [int]$Width = 700,
  [int]$Height = 300
)

$ErrorActionPreference = "Stop"
if (-not (Test-Path $Trend)) { throw "Trend file not found: $Trend" }

$points = Get-Content $Trend -Raw | ConvertFrom-Json
if ($points.Count -lt 2) { Write-Host "Not enough points to draw charts."; exit 0 }

$pts = if ($points.Count -gt 12) { $points[-12..-1] } else { $points }

function Draw-Series([object[]]$seriesPoints, [string]$fieldName, [string]$title, [string]$outPath) {
  Add-Type -AssemblyName System.Drawing
  $bmp = New-Object System.Drawing.Bitmap($Width, $Height)
  $g = [System.Drawing.Graphics]::FromImage($bmp)
  $g.SmoothingMode = 'AntiAlias'
  $g.Clear([System.Drawing.Color]::White)
  $left = 60; $right = 20; $top = 20; $bottom = 50
  $plotW = $Width - $left - $right
  $plotH = $Height - $top - $bottom
  $axisPen = New-Object System.Drawing.Pen([System.Drawing.Color]::Black,1)
  $g.DrawLine($axisPen, $left, $top, $left, $top+$plotH)
  $g.DrawLine($axisPen, $left, $top+$plotH, $left+$plotW, $top+$plotH)
  $font = New-Object System.Drawing.Font('Segoe UI',8)
  $brush = [System.Drawing.Brushes]::Black
  $allY = ($seriesPoints | ForEach-Object { [int]($_.$fieldName) })
  $yMin = [Math]::Min(0, ($allY | Measure-Object -Minimum).Minimum)
  $yMax = ($allY | Measure-Object -Maximum).Maximum
  if ($yMax -eq $yMin) { $yMax = $yMin + 1 }
  for ($i=0; $i -le 5; $i++) {
    $vy = $yMin + ($yMax - $yMin) * $i / 5
    $py = $top + $plotH - ($vy - $yMin) * $plotH / ($yMax - $yMin)
    $g.DrawLine($axisPen, $left-3, $py, $left, $py)
    $g.DrawString([string][int]$vy, $font, $brush, 5, $py-8)
  }
  for ($i=0; $i -lt $seriesPoints.Count; $i++) {
    $x = $left + $plotW * $i / ([Math]::Max(1, $seriesPoints.Count-1))
    $g.DrawLine($axisPen, $x, $top+$plotH, $x, $top+$plotH+3)
    $lbl = $seriesPoints[$i].date
    $g.DrawString($lbl, $font, $brush, $x-20, $top+$plotH+5)
  }
  $color = [System.Drawing.Color]::SteelBlue
  $pen = New-Object System.Drawing.Pen($color,2)
  $prev = $null
  for ($i=0; $i -lt $seriesPoints.Count; $i++) {
    $x = $left + $plotW * $i / ([Math]::Max(1, $seriesPoints.Count-1))
    $val = [int]$seriesPoints[$i].$fieldName
    $y = $top + $plotH - ($val - $yMin) * $plotH / ($yMax - $yMin)
    if ($prev -ne $null) { $g.DrawLine($pen, $prev.X, $prev.Y, $x, $y) }
    $g.FillEllipse((New-Object System.Drawing.SolidBrush($color)), $x-2, $y-2, 4, 4)
    $prev = @{ X = $x; Y = $y }
  }
  $titleFont = New-Object System.Drawing.Font('Segoe UI',10,[System.Drawing.FontStyle]::Bold)
  $g.DrawString($title, $titleFont, $brush, $left, 0)
  $dir = Split-Path $outPath -Parent
  if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir | Out-Null }
  $bmp.Save($outPath, [System.Drawing.Imaging.ImageFormat]::Png)
  $g.Dispose(); $bmp.Dispose()
}

Draw-Series -seriesPoints $pts -fieldName 'clauses42010' -title 'ISO/IEC/IEEE 42010 条款命中趋势（近12次）' -outPath $Out42010
Draw-Series -seriesPoints $pts -fieldName 'clauses25010' -title 'ISO/IEC 25010 条款命中趋势（近12次）' -outPath $Out25010
Draw-Series -seriesPoints $pts -fieldName 'clauses15288' -title 'ISO/IEC 15288 条款命中趋势（近12次）' -outPath $Out15288
Draw-Series -seriesPoints $pts -fieldName 'clauses12207' -title 'ISO/IEC/IEEE 12207 条款命中趋势（近12次）' -outPath $Out12207

Write-Host "Clause charts saved."
