$projectRoot = Split-Path -Parent $PSScriptRoot
$resultsPath = Join-Path $PSScriptRoot "test-results.txt"
Set-Location $projectRoot

Write-Host "1. Все тесты"
Write-Host "2. Светлая версия сайта"
Write-Host "3. Тёмная версия сайта"
Write-Host "4. HTTP-статусы"
Write-Host "0. Выход"

$choice = Read-Host "Введите номер"

switch ($choice) {
    "1" {
        $testFiles = @(
            "tests\test_site.py",
            "tests\test_dark_theme.py",
            "tests\test_http_status.py"
        )
    }
    "2" { $testFiles = @("tests\test_site.py") }
    "3" { $testFiles = @("tests\test_dark_theme.py") }
    "4" { $testFiles = @("tests\test_http_status.py") }
    "0" { exit 0 }
    default {
        Write-Host "Неверный номер. Запустите файл ещё раз и выберите число от 0 до 4."
        exit 1
    }
}

python -m pytest @testFiles -vv --durations=0 2>&1 |
    Tee-Object -FilePath $resultsPath

$pytestExitCode = $LASTEXITCODE
$report = Get-Content -Path $resultsPath -Raw
Set-Content -Path $resultsPath -Value $report -Encoding UTF8

exit $pytestExitCode



# Первый запуск из папки NoteSpace-sait(ls): установи зависимости:
# py -m pip install pytest requests selenium

# Запуск фронтенд-тестов из папки NoteSpace-sait(ls):
# .\tests\run_tests.ps1
