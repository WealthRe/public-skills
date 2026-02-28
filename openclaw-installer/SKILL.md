---
name: openclaw-installer
description: 通用的 OpenClaw 安装技能，用于在 Linux 系统上自动化安装和配置 OpenClaw。支持多种 Linux 发行版（RedHat/CentOS, Debian/Ubuntu, openEuler 等）和系统架构（x86_64, arm64 等）。提供完整的安装流程，包括依赖项安装、OpenClaw 安装、系统服务配置、对话插件配置和模型配置。使用场景：首次安装 OpenClaw、重新安装、系统迁移时的 OpenClaw 部署。
---

# OpenClaw Installer

## 概述

该技能提供了在 Linux 系统上自动化安装和配置 OpenClaw 的完整流程。它支持多种常见的 Linux 发行版和系统架构，并包含详细的错误处理和验证步骤，确保安装过程顺利完成。

## 安装流程

### 步骤 1: 系统信息检测

在开始安装之前，需要检测系统的基本信息：

1. 操作系统类型和版本
2. 系统架构（x86_64, arm64, etc.）
3. 包管理器类型（yum, dnf, apt-get, zypper 等）

### 步骤 2: 依赖项安装

安装 OpenClaw 需要以下依赖项：
- Node.js（最新兼容版本）
- Git（用于版本控制）
- 编译工具（cmake, gcc, gcc-c++, make）

#### 2.1 安装 Node.js

根据系统架构和操作系统类型，下载并安装最新兼容版本的 Node.js。对于大多数系统，推荐使用 Node.js 22.x 版本。

#### 2.2 安装其他依赖项

使用系统包管理器安装 git 和编译工具。

### 步骤 3: 安装 OpenClaw

使用 npm 全局安装 OpenClaw 包。为了加速安装过程，可以使用国内镜像源。

### 步骤 4: 系统服务配置

创建系统级别的 systemd 服务，以便 OpenClaw 能够在系统启动时自动运行，并在崩溃时自动重启。

### 步骤 5: 对话插件配置（可选）

配置对话插件（如飞书 channel）：
1. 飞书 channel 配置：
   - 需要输入 app_id 和 app_secret
   - 配置文件：~/.openclaw/openclaw.json
   - 支持多个飞书 channel 配置

### 步骤 6: 模型配置（可选）

配置模型服务（如阿里云 coding plan 模型）：
1. 阿里云百炼模型配置：
   - 需要输入 api_key 和 base_url
   - 支持配置多个模型
   - 配置文件：~/.openclaw/openclaw.json

### 步骤 7: 验证安装

验证 OpenClaw 是否成功安装并正常运行。

## 资源

### scripts/
包含安装过程中使用的 shell 脚本。

### references/
包含系统信息检测和依赖项安装的详细说明。

### assets/
包含 systemd 服务配置文件模板。
