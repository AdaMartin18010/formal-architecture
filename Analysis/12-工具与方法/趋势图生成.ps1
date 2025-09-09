Param(
  [string]$Trend = "reports/week/trend.json",
  [string]$OutPng = "reports/week/trend.png",
  [int]$Width = 900,
  [int]$Height = 400
)

$ErrorActionPreference = "Stop"
if (-not (Test-Path $Trend)) { throw "Trend file not found: $Trend" }

$points = Get-Content $Trend -Raw | ConvertFrom-Json
if ($points.Count -lt 2) { Write-Host "Not enough points to draw chart."; exit 0 }

# Prepare data (last 12 points max)
$pts = if ($points.Count -gt 12) { $points[-12..-1] } else { $points }

# Series to plot
$seriesDefs = @(
  @{ name = 'courses'; color = 'Blue' },
  @{ name = 'standards'; color = 'Green' },
  @{ name = 'repo'; color = 'Red' }
)

# Y range
$allY = @()
foreach ($s in $seriesDefs) { $allY += ($pts | ForEach-Object { [int]($_.$($s.name)) }) }
$yMin = [Math]::Min(0, ($allY | Measure-Object -Minimum).Minimum)
$yMax = ($allY | Measure-Object -Maximum).Maximum
if ($yMax -eq $yMin) { $yMax = $yMin + 1 }

# Drawing
Add-Type -AssemblyName System.Drawing
$bmp = New-Object System.Drawing.Bitmap($Width, $Height)
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.SmoothingMode = 'AntiAlias'
$g.Clear([System.Drawing.Color]::White)

# Margins
$left = 70; $right = 20; $top = 20; $bottom = 60
$plotW = $Width - $left - $right
$plotH = $Height - $top - $bottom

# Axes
$axisPen = New-Object System.Drawing.Pen([System.Drawing.Color]::Black,1)
$g.DrawLine($axisPen, $left, $top, $left, $top+$plotH)
$g.DrawLine($axisPen, $left, $top+$plotH, $left+$plotW, $top+$plotH)

# Y ticks (5)
$font = New-Object System.Drawing.Font('Segoe UI',8)
$brush = [System.Drawing.Brushes]::Black
for ($i=0; $i -le 5; $i++) {
  $vy = $yMin + ($yMax - $yMin) * $i / 5
  $py = $top + $plotH - ($vy - $yMin) * $plotH / ($yMax - $yMin)
  $g.DrawLine($axisPen, $left-3, $py, $left, $py)
  $g.DrawString([string][int]$vy, $font, $brush, 5, $py-8)
}

# X labels
for ($i=0; $i -lt $pts.Count; $i++) {
  $x = $left + $plotW * $i / ([Math]::Max(1, $pts.Count-1))
  $g.DrawLine($axisPen, $x, $top+$plotH, $x, $top+$plotH+3)
  $lbl = $pts[$i].date
  $g.DrawString($lbl, $font, $brush, $x-20, $top+$plotH+5)
}

# Plot series
foreach ($s in $seriesDefs) {
  $color = [System.Drawing.Color]::$($s.color)
  $pen = New-Object System.Drawing.Pen($color,2)
  $prev = $null
  for ($i=0; $i -lt $pts.Count; $i++) {
    $x = $left + $plotW * $i / ([Math]::Max(1, $pts.Count-1))
    $val = [int]$pts[$i].$($s.name)
    $y = $top + $plotH - ($val - $yMin) * $plotH / ($yMax - $yMin)
    if ($prev -ne $null) { $g.DrawLine($pen, $prev.X, $prev.Y, $x, $y) }
    $g.FillEllipse((New-Object System.Drawing.SolidBrush($color)), $x-2, $y-2, 4, 4)
    $prev = @{ X = $x; Y = $y }
  }
}

# Legend
$legendX = $left + 10; $legendY = $top + 10; $dy=16
for ($j=0; $j -lt $seriesDefs.Count; $j++) {
  $c = [System.Drawing.Color]::$($seriesDefs[$j].color)
  $g.FillRectangle((New-Object System.Drawing.SolidBrush($c)), $legendX, $legendY+$j*$dy, 10,10)
  $g.DrawString($seriesDefs[$j].name, $font, $brush, $legendX+15, $legendY+$j*$dy-2)
}

# Title
$titleFont = New-Object System.Drawing.Font('Segoe UI',10,[System.Drawing.FontStyle]::Bold)
$g.DrawString('对齐统计趋势（近12次）', $titleFont, $brush, $left, 0)

# Save
$dir = Split-Path $OutPng -Parent
if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir | Out-Null }
$bmp.Save($OutPng, [System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose(); $bmp.Dispose()

Write-Host "Trend chart saved to $OutPng"
