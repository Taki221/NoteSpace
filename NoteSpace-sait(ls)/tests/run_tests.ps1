param(
    [ValidateSet("all", "site", "dark", "http")]
    [string]$Suite = ""
)

# Определяет корень проекта и путь к файлу с результатами.
$projectRoot = Split-Path -Parent $PSScriptRoot
$resultsPath = Join-Path $PSScriptRoot "test-results.txt"
Set-Location $projectRoot

# Если набор не указан параметром, предлагает выбрать его в интерактивном меню.
if (-not $Suite) {
    Write-Host "Выберите набор тестов:"
    Write-Host "1. Все тесты"
    Write-Host "2. Светлая версия сайта"
    Write-Host "3. Тёмная версия сайта"
    Write-Host "4. HTTP-статусы"
    Write-Host "0. Выход"

    do {
        $choice = Read-Host "Введите номер"
        switch ($choice) {
            "1" { $Suite = "all" }
            "2" { $Suite = "site" }
            "3" { $Suite = "dark" }
            "4" { $Suite = "http" }
            "0" { exit 0 }
            default { Write-Host "Введите число от 0 до 4." }
        }
    } while (-not $Suite)
}

# Выбирает весь набор тестов или один конкретный файл.
switch ($Suite) {
    "all" {
        $testTargets = @(
            "tests\test_site.py",
            "tests\test_dark_theme.py",
            "tests\test_http_status.py"
        )
    }
    "site" {
        $testTargets = @("tests\test_site.py")
    }
    "dark" {
        $testTargets = @("tests\test_dark_theme.py")
    }
    "http" {
        $testTargets = @("tests\test_http_status.py")
    }
}

# Выводит результаты в терминал и перезаписывает ими файл с отчётом.
python -m pytest @testTargets -vv --durations=0 2>&1 |
    Tee-Object -FilePath $resultsPath

# Возвращает код завершения pytest, чтобы запуск корректно показывал успех или ошибку.
$pytestExitCode = $LASTEXITCODE

# Преобразует отчёт PowerShell в UTF-8, чтобы его можно было читать обычными редакторами.
$report = Get-Content -Path $resultsPath -Raw
Set-Content -Path $resultsPath -Value $report -Encoding UTF8

exit $pytestExitCode

#  для запуска: .\tests\run_tests.ps1