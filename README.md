# dsh-plugin-index

**DeepSeek Harness 插件市场索引源（社区托管）** · A community-hosted [plugin market index](https://github.com/deepseek-ai/deepseek-harness) for DeepSeek Harness (DSH).

本仓库维护一份符合 DSH 插件市场 **format 1** 的 `index.json`，收录官方 [@deepseek-ai](https://www.npmjs.com/org/deepseek-ai) 发布的可安装插件包。索引中的版本号与发布时间与 npm registry 一致。

## 索引源地址（Index Source URL）

```
https://raw.githubusercontent.com/inowness/dsh-plugin-index/main/index.json
```

## 如何在 DSH 中使用

1. **启用插件市场**：打开 DeepSeek Harness，进入「插件 Plugins」页 →「实验插件 Experimental plugins」→ 打开 **Custom plugin markets（自定义插件市场）**（只需一次；也可以在 profile 的 bundles 中加入 `@deepseek-ai/dsh-experimental-plugin-market-bundle`）。
2. **添加索引源**：插件页会出现「已安装 / 发现 Discover」两个标签 → 切到「发现」→「索引源 Index sources」→ 添加上面的 raw URL。
3. **浏览与安装**：之后即可在 Discover 中搜索、筛选并安装索引里的插件（安装由插件管理器经 pnpm 完成，装进当前 profile）。

> DSH 的 Discover 会对索引内容做缓存（默认 10 分钟）；GitHub raw 走 CDN，更新 `index.json` 后可能需数分钟才能看到新版本。

## 收录内容

| 类别 | 插件 |
|---|---|
| 子代理 Subagents | `dsh-subagent-codex` · `dsh-subagent-claude-code` · `dsh-tool-subagent` |
| 团队协作 Team | `dsh-experimental-agent-team-profile` |
| 自动化 Automation | `dsh-experimental-auto-review` · `dsh-experimental-ralph-bundle` |
| 界面与体验 UI | `dsh-experimental-badge-skill-bundle` · `dsh-experimental-cot-translation-bundle` · `dsh-experimental-plugin-market-bundle` · `dsh-experimental-session-titles-bundle` · `dsh-experimental-voice-input-bundle` |
| 开发工具 Tools | `dsh-experimental-inspector-profile` · `dsh-experimental-session-search` · `dsh-experimental-terminal-bundle` · `dsh-experimental-tool-worktree` |

## 更新索引

```bash
python3 update-index.py   # 从 registry.npmjs.org 拉取最新发布信息，重写 index.json
```

`update-index.py` 会为每个包抓取 npm 元数据（`registry.npmjs.org` 失败时回退 `registry.npmmirror.com`），生成所有已发布版本的 `version` + `publishTimestamp`，并按 DSH format 1 输出。

## 说明与免责声明

- 本仓库只托管索引数据；插件本体是 DeepSeek 官方发布在 npm 的包，版权归其所有者。
- 索引内容只是「市场的声明」，实际安装结果以插件包自身的 manifest 为准；安装前请自行核实包名与版本。
- 索引中的 `source` 均为 npm，安装时走你本机 pnpm 配置的 registry（国内环境配置了 npmmirror 会自动走镜像）。

## License

本仓库的索引数据与脚本以 MIT 协议发布，见 [LICENSE](LICENSE)。
