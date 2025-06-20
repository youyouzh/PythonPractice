# ����Windows����ǽ�ظ�����ű����Զ�ɾ��ģʽ��

# �Թ���ԱȨ������
if (-not ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host "���Թ���ԱȨ�����д˽ű���" -ForegroundColor Red
    exit
}

# ��ȡ�������õķ���ǽ����
$rules = Get-NetFirewallRule | Where-Object { $_.Enabled -eq "True" }

# ���������ж��ظ��Ĺؼ�����
$ruleProperties = @("DisplayName", "Direction", "Action", "Protocol", "Profile")

# ��ʱ�洢����Ĺ�ϣ������ȥ�أ�
$ruleMap = @{}

# ����ظ�����
Write-Host "���ڼ���ظ��ķ���ǽ����..." -ForegroundColor Yellow
foreach ($rule in $rules) {
    # ���������Ψһ��ʶ�������ڹؼ����ԣ�
    $key = ($rule | Select-Object -Property $ruleProperties | Format-List | Out-String).Trim()

    if ($ruleMap.ContainsKey($key)) {
        Write-Host "��⵽�ظ�����: $($rule.DisplayName)" -ForegroundColor Red
        $ruleMap[$key] += $rule
    } else {
        $ruleMap[$key] = @($rule)
    }
}

# ���˳��ظ��Ĺ�����
$duplicateGroups = $ruleMap.Values | Where-Object { $_.Count -gt 1 }

if ($duplicateGroups.Count -eq 0) {
    Write-Host "δ�����ظ��ķ���ǽ����" -ForegroundColor Green
    exit
}

# ��־�ļ�·��
$logFile = "FirewallCleanupLog.log"
Start-Transcript -Path $logFile

# �Զ�ɾ���ظ����򣨱���ÿ��ĵ�һ������
Write-Host "`n��ʼ�Զ�ɾ���ظ�����..." -ForegroundColor Yellow
foreach ($group in $duplicateGroups) {
    # ������һ������ɾ���������
    $keepRule = $group[0]
    Write-Host "��������: $($keepRule.DisplayName)" -ForegroundColor Green

    for ($i = 1; $i -lt $group.Count; $i++) {
        $deleteRule = $group[$i]
        Write-Host "ɾ������: $($deleteRule.DisplayName)" -ForegroundColor Red

        # �������Ƿ����
        $ruleToDelete = Get-NetFirewallRule -Name $deleteRule.Name -ErrorAction SilentlyContinue
        if (-not $ruleToDelete) {
            Write-Host "�����Ѳ�����: $($deleteRule.DisplayName)" -ForegroundColor Yellow
            continue
        }

        # ����ɾ�����򲢲����쳣
        try {
            Remove-NetFirewallRule -Name $deleteRule.Name -Confirm:$false -ErrorAction Stop
        } catch {
            Write-Host "ɾ��ʧ��: $($deleteRule.DisplayName)����������: $_��" -ForegroundColor Red
        }
    }
}

Stop-Transcript
Write-Host "�ظ�����������ɣ���־�ѱ��浽: $logFile" -ForegroundColor Green
