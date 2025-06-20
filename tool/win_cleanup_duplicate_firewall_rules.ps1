# 清理Windows防火墙重复规则脚本（自动删除模式）

# 以管理员权限运行
if (-not ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host "请以管理员权限运行此脚本！" -ForegroundColor Red
    exit
}

# 获取所有启用的防火墙规则
$rules = Get-NetFirewallRule | Where-Object { $_.Enabled -eq "True" }

# 定义用于判断重复的关键属性
$ruleProperties = @("DisplayName", "Direction", "Action", "Protocol", "Profile")

# 临时存储规则的哈希表（用于去重）
$ruleMap = @{}

# 检测重复规则
Write-Host "正在检测重复的防火墙规则..." -ForegroundColor Yellow
foreach ($rule in $rules) {
    # 构建规则的唯一标识符（基于关键属性）
    $key = ($rule | Select-Object -Property $ruleProperties | Format-List | Out-String).Trim()

    if ($ruleMap.ContainsKey($key)) {
        Write-Host "检测到重复规则: $($rule.DisplayName)" -ForegroundColor Red
        $ruleMap[$key] += $rule
    } else {
        $ruleMap[$key] = @($rule)
    }
}

# 过滤出重复的规则组
$duplicateGroups = $ruleMap.Values | Where-Object { $_.Count -gt 1 }

if ($duplicateGroups.Count -eq 0) {
    Write-Host "未发现重复的防火墙规则。" -ForegroundColor Green
    exit
}

# 日志文件路径
$logFile = "FirewallCleanupLog.log"
Start-Transcript -Path $logFile

# 自动删除重复规则（保留每组的第一个规则）
Write-Host "`n开始自动删除重复规则..." -ForegroundColor Yellow
foreach ($group in $duplicateGroups) {
    # 保留第一个规则，删除其余规则
    $keepRule = $group[0]
    Write-Host "保留规则: $($keepRule.DisplayName)" -ForegroundColor Green

    for ($i = 1; $i -lt $group.Count; $i++) {
        $deleteRule = $group[$i]
        Write-Host "删除规则: $($deleteRule.DisplayName)" -ForegroundColor Red

        # 检查规则是否存在
        $ruleToDelete = Get-NetFirewallRule -Name $deleteRule.Name -ErrorAction SilentlyContinue
        if (-not $ruleToDelete) {
            Write-Host "规则已不存在: $($deleteRule.DisplayName)" -ForegroundColor Yellow
            continue
        }

        # 尝试删除规则并捕获异常
        try {
            Remove-NetFirewallRule -Name $deleteRule.Name -Confirm:$false -ErrorAction Stop
        } catch {
            Write-Host "删除失败: $($deleteRule.DisplayName)（错误详情: $_）" -ForegroundColor Red
        }
    }
}

Stop-Transcript
Write-Host "重复规则清理完成！日志已保存到: $logFile" -ForegroundColor Green
