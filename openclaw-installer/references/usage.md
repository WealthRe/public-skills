# OpenClaw 安装技能使用指南

## 概述

本技能提供了在 Linux 系统上自动化安装和配置 OpenClaw 的完整流程。它支持多种常见的 Linux 发行版和系统架构，并包含详细的错误处理和验证步骤。

## 使用方法

### 1. 直接执行安装脚本

最简单的使用方法是直接执行安装脚本：

```bash
cd /Users/wealthre/.claude/skills/openclaw-installer/scripts
chmod +x install_openclaw.sh
./install_openclaw.sh
```

### 2. 通过 SSH 在远程机器上执行

您也可以通过 SSH 在远程机器上执行安装脚本：

```bash
# 将脚本复制到远程机器
scp /Users/wealthre/.claude/skills/openclaw-installer/scripts/install_openclaw.sh root@<remote_host>:/tmp

# 登录远程机器并执行脚本
ssh root@<remote_host> "cd /tmp && chmod +x install_openclaw.sh && ./install_openclaw.sh"
```

### 3. 在本地机器上执行

如果您是在本地机器上安装 OpenClaw，可以直接运行以下命令：

```bash
curl -fsSL https://example.com/install_openclaw.sh | sudo bash
```

## 系统要求

### 支持的操作系统

- Ubuntu/Debian 系统（推荐使用最新 LTS 版本）
- RedHat/CentOS 7.x 及以上版本
- Fedora 系统
- openEuler 系统

### 支持的系统架构

- x86_64（64 位 Intel/AMD 架构）
- arm64（64 位 ARM 架构，如 Raspberry Pi 4、AWS Graviton 等）

## 安装过程

### 1. 系统信息检测

脚本会自动检测您的操作系统类型、版本和系统架构。

### 2. 依赖项安装

脚本会根据您的系统类型，使用适当的包管理器安装以下依赖项：
- Git（版本控制工具）
- CMake（编译工具）
- GCC/G++（C/C++ 编译器）
- Make（构建工具）

### 3. Node.js 安装

脚本会下载并安装最新版本的 Node.js（当前版本为 v22.12.0）。

### 4. OpenClaw 安装

脚本会使用 npm 全局安装 OpenClaw。

### 5. 系统服务配置

脚本会创建一个系统级别的 systemd 服务，以便 OpenClaw 能够在系统启动时自动运行，并在崩溃时自动重启。

### 6. 安装验证

脚本会验证 OpenClaw 是否成功安装并正常运行。

## 故障排除

### 1. 安装过程中出现的错误

如果在安装过程中出现错误，脚本会停止执行并显示详细的错误信息。您可以根据错误信息尝试以下解决方案：

- 检查网络连接是否正常
- 确保您有足够的权限执行安装脚本（需要 root 权限）
- 检查磁盘空间是否足够
- 查看系统日志以获取更多信息

### 2. 验证过程失败

如果验证过程失败，可能是以下原因导致的：
- OpenClaw 网关服务未能成功启动
- 网络端口被占用
- 防火墙阻止了访问

您可以使用以下命令检查服务状态：

```bash
systemctl status openclaw-gateway
```

## 卸载 OpenClaw

如果您需要卸载 OpenClaw，可以执行以下命令：

```bash
# 停止并禁用系统服务
systemctl stop openclaw-gateway
systemctl disable openclaw-gateway
rm -f /etc/systemd/system/openclaw-gateway.service
systemctl daemon-reload

# 卸载 OpenClaw 包
npm uninstall -g openclaw

# 卸载 Node.js
rm -rf /usr/local/nodejs
rm -f /usr/bin/node
rm -f /usr/bin/npm

# 卸载依赖项（根据系统类型）
# Ubuntu/Debian
apt-get remove -y git cmake gcc g++ make

# RedHat/CentOS
yum remove -y git cmake gcc gcc-c++ make

# Fedora
dnf remove -y git cmake gcc gcc-c++ make
```

## 注意事项

1. 请确保您有足够的权限执行安装脚本（需要 root 权限）。
2. 安装过程中会下载一些文件，需要确保网络连接正常。
3. 安装过程可能需要几分钟时间，具体时间取决于您的网络速度和系统性能。
4. 安装完成后，OpenClaw 网关服务会自动启动并在系统启动时自动运行。