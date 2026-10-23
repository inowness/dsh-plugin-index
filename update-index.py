#!/usr/bin/env python3
"""Regenerate index.json from the npm registry.

Usage: python3 update-index.py
Fetches publish metadata for every listed package from registry.npmjs.org
(falling back to registry.npmmirror.com) and writes index.json in the
DeepSeek Harness plugin market index format 1.
"""
import json
import urllib.request
from datetime import datetime

REGISTRIES = [
    "https://registry.npmjs.org",
    "https://registry.npmmirror.com",
]

# name -> (title, description, author, homepage, repository, directory, category, labels, keywords)
# titles/descriptions are localized: {"en": ..., "zh": ...}
PLUGINS = {
    "@deepseek-ai/dsh-subagent-codex": {
        "title": {"en": "Codex Subagent", "zh": "Codex 子代理"},
        "description": {
            "en": "One-shot Codex subagent provider over the official app-server protocol.",
            "zh": "通过官方 app-server 协议调用一次性 Codex 子代理。",
        },
        "category": "subagent",
        "labels": ["official"],
        "keywords": ["codex", "subagent", "delegation", "sdk"],
    },
    "@deepseek-ai/dsh-subagent-claude-code": {
        "title": {"en": "Claude Code Subagent", "zh": "Claude Code 子代理"},
        "description": {
            "en": "One-shot Claude Code subagent provider over the official Agent SDK.",
            "zh": "通过官方 Agent SDK 调用一次性 Claude Code 子代理。",
        },
        "category": "subagent",
        "labels": ["official"],
        "keywords": ["claude", "subagent", "delegation", "sdk"],
    },
    "@deepseek-ai/dsh-tool-subagent": {
        "title": {"en": "Subagent Tool", "zh": "子代理工具"},
        "description": {
            "en": "Model-facing subagent delegation tool over the ctx.subagents seam.",
            "zh": "面向模型、基于 ctx.subagents 的子代理委派工具。",
        },
        "category": "subagent",
        "labels": ["official"],
        "keywords": ["subagent", "tool", "delegation"],
    },
    "@deepseek-ai/dsh-experimental-agent-team-profile": {
        "title": {"en": "Agent Teams", "zh": "Agent 团队"},
        "description": {
            "en": "Experimental profile bundle enabling Agent Teams over dsh-base.",
            "zh": "实验性 bundle：在 dsh-base 上启用 Agent Teams 多智能体团队协作。",
        },
        "category": "team",
        "labels": ["experimental"],
        "keywords": ["team", "multi-agent", "collaboration"],
    },
    "@deepseek-ai/dsh-experimental-auto-review": {
        "title": {"en": "Auto Review", "zh": "自动审查"},
        "description": {
            "en": "Per-tool LLM authorization review for the Auto permission preset.",
            "zh": "为 Auto 权限预设提供逐工具 LLM 授权审查。",
        },
        "category": "automation",
        "labels": ["experimental"],
        "keywords": ["review", "permissions", "approval", "llm"],
    },
    "@deepseek-ai/dsh-experimental-ralph-bundle": {
        "title": {"en": "Ralph", "zh": "Ralph"},
        "description": {
            "en": "Run explicitly requested repeated work with fresh agents.",
            "zh": "用全新 agent 循环执行明确要求的重复工作。",
        },
        "category": "automation",
        "labels": ["experimental"],
        "keywords": ["loop", "fresh-agent", "iteration"],
    },
    "@deepseek-ai/dsh-experimental-badge-skill-bundle": {
        "title": {"en": "Powered-by-DSH Badge", "zh": "DSH 徽章"},
        "description": {
            "en": "Offer the powered-by-DSH badge as a discoverable skill.",
            "zh": "把 powered-by-DSH 徽章作为可发现的技能提供。",
        },
        "category": "ui",
        "labels": ["experimental"],
        "keywords": ["badge", "skill", "attribution"],
    },
    "@deepseek-ai/dsh-experimental-cot-translation-bundle": {
        "title": {"en": "CoT Translation", "zh": "思考链翻译"},
        "description": {
            "en": "Experimental machine translation of expanded reasoning.",
            "zh": "实验性：对展开的推理（CoT）做机器翻译。",
        },
        "category": "ui",
        "labels": ["experimental"],
        "keywords": ["translation", "reasoning", "cot"],
    },
    "@deepseek-ai/dsh-experimental-inspector-profile": {
        "title": {"en": "Inspector", "zh": "检查器"},
        "description": {
            "en": "Optional Web bundle for raw Session logs and Chat node inspection.",
            "zh": "可选 Web bundle：查看原始会话日志与 Chat 节点。",
        },
        "category": "tools",
        "labels": ["experimental"],
        "keywords": ["inspector", "logs", "debug"],
    },
    "@deepseek-ai/dsh-experimental-plugin-market-bundle": {
        "title": {"en": "Plugin Market (Discover)", "zh": "插件市场（发现）"},
        "description": {
            "en": "Experimental custom plugin markets: a Discover tab that browses and installs bundles from plugin market indexes.",
            "zh": "实验性自定义插件市场：Discover 标签页，浏览并安装索引源中的 bundle。",
        },
        "category": "ui",
        "labels": ["experimental"],
        "keywords": ["market", "discover", "index"],
    },
    "@deepseek-ai/dsh-experimental-session-search": {
        "title": {"en": "Session Search", "zh": "会话搜索"},
        "description": {
            "en": "Give Agents tools to search and read earlier sessions from the current workspace.",
            "zh": "给 Agent 提供搜索和读取当前工作区历史会话的工具。",
        },
        "category": "tools",
        "labels": ["experimental"],
        "keywords": ["session", "search", "history"],
    },
    "@deepseek-ai/dsh-experimental-session-titles-bundle": {
        "title": {"en": "Session Titles", "zh": "会话标题"},
        "description": {
            "en": "Refresh session titles as new human prompts arrive.",
            "zh": "新消息到来时自动刷新会话标题。",
        },
        "category": "ui",
        "labels": ["experimental"],
        "keywords": ["session", "titles"],
    },
    "@deepseek-ai/dsh-experimental-terminal-bundle": {
        "title": {"en": "Persistent Terminal", "zh": "持久终端"},
        "description": {
            "en": "Keep shell processes alive across tool calls.",
            "zh": "让 shell 进程跨工具调用保持存活。",
        },
        "category": "tools",
        "labels": ["experimental"],
        "keywords": ["terminal", "shell", "persistent"],
    },
    "@deepseek-ai/dsh-experimental-tool-worktree": {
        "title": {"en": "Git Worktree Tool", "zh": "Git Worktree 工具"},
        "description": {
            "en": "Model tool that creates and enters a new Git worktree.",
            "zh": "模型工具：创建并进入新的 Git worktree。",
        },
        "category": "tools",
        "labels": ["experimental"],
        "keywords": ["git", "worktree", "branch"],
    },
    "@deepseek-ai/dsh-experimental-voice-input-bundle": {
        "title": {"en": "Voice Input", "zh": "语音输入"},
        "description": {
            "en": "Experimental voice input with local SenseVoice; downloads its runtime on first use.",
            "zh": "实验性语音输入（本地 SenseVoice），首次使用时下载运行时。",
        },
        "category": "ui",
        "labels": ["experimental"],
        "keywords": ["voice", "speech", "input"],
    },
}

AUTHOR = "DeepSeek"
REPO_URL = "https://github.com/deepseek-ai/deepseek-harness"
REPO_DIRECTORY_PREFIX = "packages/"
REPO_DIRECTORIES = {
    "@deepseek-ai/dsh-subagent-codex": "packages/subagent/subagent-codex",
    "@deepseek-ai/dsh-subagent-claude-code": "packages/subagent/subagent-claude-code",
    "@deepseek-ai/dsh-tool-subagent": "packages/subagent/tool-subagent",
    "@deepseek-ai/dsh-experimental-agent-team-profile": "packages/experimental/agent-team-profile",
    "@deepseek-ai/dsh-experimental-auto-review": "packages/experimental/auto-review",
    "@deepseek-ai/dsh-experimental-ralph-bundle": "packages/experimental/ralph-bundle",
    "@deepseek-ai/dsh-experimental-badge-skill-bundle": "packages/experimental/badge-skill-bundle",
    "@deepseek-ai/dsh-experimental-cot-translation-bundle": "packages/experimental/cot-translation-bundle",
    "@deepseek-ai/dsh-experimental-inspector-profile": "packages/experimental/inspector-profile",
    "@deepseek-ai/dsh-experimental-plugin-market-bundle": "packages/experimental/plugin-market-bundle",
    "@deepseek-ai/dsh-experimental-session-search": "packages/experimental/session-search",
    "@deepseek-ai/dsh-experimental-session-titles-bundle": "packages/experimental/session-titles-bundle",
    "@deepseek-ai/dsh-experimental-terminal-bundle": "packages/experimental/terminal-bundle",
    "@deepseek-ai/dsh-experimental-tool-worktree": "packages/experimental/tool-worktree",
    "@deepseek-ai/dsh-experimental-voice-input-bundle": "packages/experimental/voice-input-bundle",
}

CATEGORIES = {
    "subagent": {"en": "Subagents", "zh": "子代理"},
    "team": {"en": "Team Collaboration", "zh": "团队协作"},
    "ui": {"en": "Interface & Experience", "zh": "界面与体验"},
    "tools": {"en": "Developer Tools", "zh": "开发工具"},
    "automation": {"en": "Automation", "zh": "自动化"},
}

LABELS = {
    "official": {"en": "Official", "zh": "官方"},
    "experimental": {"en": "Experimental", "zh": "实验性"},
}


def fetch(url, timeout=60):
    req = urllib.request.Request(url, headers={"User-Agent": "dsh-plugin-index-updater/1.0", "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def npm_metadata(package):
    encoded = package.replace("/", "%2f")
    last_error = None
    for registry in REGISTRIES:
        try:
            return fetch(f"{registry}/{encoded}")
        except Exception as error:  # noqa: BLE001
            last_error = error
    raise RuntimeError(f"could not fetch {package}: {last_error}")


def to_unix_seconds(iso):
    return int(datetime.fromisoformat(iso.replace("Z", "+00:00")).timestamp())


def main():
    index = {
        "format": 1,
        "title": {"en": "DeepSeek Harness Plugin Index (community-hosted)", "zh": "DeepSeek Harness 插件索引（社区托管）"},
        "description": {
            "en": "Official @deepseek-ai plugin packages for DeepSeek Harness, listed by an independent community index.",
            "zh": "DeepSeek Harness 官方 @deepseek-ai 插件包，由独立社区索引收录。",
        },
        "metadata": {
            "categories": {
                cat_id: {"title": title}
                for cat_id, title in CATEGORIES.items()
            },
            "labels": {
                label_id: {"title": title}
                for label_id, title in LABELS.items()
            },
        },
        "plugins": [],
    }
    for package, meta in PLUGINS.items():
        doc = npm_metadata(package)
        times = doc.get("time", {})
        versions = []
        for version in doc.get("versions", {}).values():
            published = times.get(version.get("version"))
            if not published:
                continue
            versions.append({
                "version": version["version"],
                "publishTimestamp": to_unix_seconds(published),
                "source": {"type": "npm"},
            })
        versions.sort(key=lambda v: v["publishTimestamp"], reverse=True)
        index["plugins"].append({
            "name": package,
            "title": meta["title"],
            "description": meta["description"],
            "author": AUTHOR,
            "homepage": f"{REPO_URL}#readme",
            "repository": {
                "url": REPO_URL,
                "directory": REPO_DIRECTORIES[package],
            },
            "metadata": {
                "category": meta["category"],
                "keywords": meta["keywords"],
                "labels": meta["labels"],
            },
            "versions": versions,
        })
    index["plugins"].sort(key=lambda p: p["name"])
    with open("index.json", "w", encoding="utf-8") as out:
        json.dump(index, out, ensure_ascii=False, indent=2)
        out.write("\n")
    print(f"wrote index.json with {len(index['plugins'])} plugins, "
          f"{sum(len(p['versions']) for p in index['plugins'])} versions")


if __name__ == "__main__":
    main()
