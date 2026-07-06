# check_results.json 数据结构说明

本文件定义 `scripts/report_generator.py --input` 所接受的 JSON 数据格式。合规审查人员在完成检查清单后，按此格式整理结果即可直接生成报告。

## 整体结构

```json
{
  "app_info": { ... },
  "check_results": [ ... ]
}
```

## app_info（APP基本信息）

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `app_name` | string | ✅ | APP名称 |
| `package_name` | string | ✅ | 包名（Android）/ Bundle ID（iOS） |
| `version` | string | ✅ | APP版本号 |
| `platform` | string | 否 | 平台，默认"Android" |
| `company` | string | 否 | 运营公司名称 |
| `review_date` | string | 否 | 审查日期（YYYY-MM-DD），默认当天 |
| `review_scope` | string | 否 | 审查范围说明 |
| `material_status` | object | 否 | 材料完整性校验结果（来自 material_validator.py 输出） |
| `apk_analysis` | object | 否 | APK 分析结果（来自 apk_analyzer.py --output，或通过 --apk-analysis 单独传入） |

## check_results（检查结果数组）

每项对应一个检查项，字段如下：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `module` | string | ✅ | 模块编号，如 "M1"、"M2" |
| `item_id` | string | ✅ | 检查项编号，如 "M1-1"、"M2-3" |
| `item_name` | string | ✅ | 检查项名称 |
| `status` | string | ✅ | 合规状态：`compliant` / `warning` / `non_compliant` / `not_applicable` |
| `risk_level` | string | ✅ | 风险等级：`high` / `medium` / `low` |
| `finding` | string | ✅ | 事实发现（合规事实查明结果） |
| `legal_basis` | string | ✅ | 法规依据（含法律名称、条款、锚点编号） |
| `recommendation` | string | ✅ | 整改建议 |
| `method` | string | 否 | 审查方法标识：`[文本]` / `[技术]` / `[一致性]` |
| `consistency_issue` | boolean | 否 | 是否存在声明与事实不一致（阶段二专用） |
| `anchor_id` | string | 否 | 对应条文锚点编号（如 "A001"），用于 MCP 核验追溯 |

## 完整示例

```json
{
  "app_info": {
    "app_name": "示例购物APP",
    "package_name": "com.example.shop",
    "version": "3.2.1",
    "platform": "Android",
    "company": "示例科技有限公司",
    "review_date": "2026-07-06",
    "review_scope": "新版本上线前全量合规审查"
  },
  "check_results": [
    {
      "module": "M1",
      "item_id": "M1-1",
      "item_name": "隐私政策完整性",
      "status": "compliant",
      "risk_level": "low",
      "finding": "隐私政策包含法定必备10项内容，版本日期清晰，可在线查看",
      "legal_basis": "个保法§17；认定方法§1 [A001]",
      "recommendation": "无",
      "method": "[文本]",
      "anchor_id": "A001"
    },
    {
      "module": "M4",
      "item_id": "M4-2",
      "item_name": "权限申请同步告知目的",
      "status": "non_compliant",
      "risk_level": "high",
      "finding": "申请位置权限时弹窗仅写"需要使用位置信息"，未说明具体目的和使用场景",
      "legal_basis": "个保法§17；认定方法§2 [A037]",
      "recommendation": "权限申请弹窗须逐一说明权限使用目的，如"用于根据您的位置推荐附近门店"",
      "method": "[一致性]",
      "consistency_issue": true,
      "anchor_id": "A037"
    }
  ]
}
```

## 通过 APK 分析报告增强

`report_generator.py` 支持 `--apk-analysis` 参数，可直接传入 `scripts/apk_analyzer.py` 输出的 JSON 报告。报告中的权限清单、SDK 列表将自动与 `check_results` 中的一致性核验发现交叉引用，生成一致性核验专节。

## 数据来源

- **app_info**：由审查人员填写，或从 APK 分析结果中提取
- **check_results**：审查人员对照 `references/checklist-full.md` 逐项审查后填写
- **apk_analysis**：运行 `scripts/apk_analyzer.py --output apk_report.json` 生成
- **material_status**：运行 `scripts/material_validator.py --output validation_report.json` 生成
