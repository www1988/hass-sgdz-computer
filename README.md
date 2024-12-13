# Home Assistant 松果电子电脑控制

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

这是一个用于 Home Assistant 的松果电子电脑控制集成组件，可以通过 Home Assistant 远程控制电脑的开关机状态。

## 功能特点

- 远程开关机控制
- 强制关机/重启功能
- 实时显示电脑状态
- 自动检测设备在线状态
- 支持多设备管理
- UI界面配置，无需修改配置文件

## 安装方法

### HACS 安装（推荐）
1. 在 HACS 中添加自定义存储库：
   - 点击 HACS -> 集成
   - 点击右上角菜单中的自定义存储库
   - 在存储库中填入：`www1988/hass-sgdz-computer`
   - 类别选择：Integration
2. 点击 "下载"
3. 重启 Home Assistant

### 手动安装
1. 下载最新版本的代码
2. 将 `custom_components/sgdz_computer` 文件夹复制到你的 Home Assistant 配置目录下的 `custom_components` 文件夹中
3. 重启 Home Assistant

## 配置说明

1. 在 Home Assistant 的集成页面中点击添加集成
2. 搜索 "松果电子电脑控制"
3. 输入你的松果电子账号和密码
4. 从列表中选择要控制的设备
5. 完成配置

## 使用说明

### 基本控制
- 开机：点击开关即可开机
- 关机：点击开关即可正常关机

### 高级功能
组件提供了两个服务：
- `sgdz_computer.force_shutdown`: 强制关机
- `sgdz_computer.force_restart`: 强制重启

可以在自动化、脚本中调用这些服务。

### 属性说明
设备会显示以下属性：
- 设备状态（开/关）
- 在线状态
- 设备名称
- 账号信息

## 常见问题

1. **设备显示离线**
   - 检查设备是否正常连接网络
   - 确认账号密码是否正确

2. **操作没有响应**
   - 检查设备是否在线
   - 查看 Home Assistant 日志获取详细错误信息

## 调试

如果需要查看详细日志，可以在 configuration.yaml 中添加：

```yaml
logger:
  default: info
  logs:
    custom_components.sgdz_computer: debug
```

## 更新日志

### v1.0.0
- 初始发布
- 支持基本的开关机功能
- 添加强制关机和重启功能
- 支持 UI 配置

## 许可证

本项目采用 MIT 许可证，详见 [LICENSE](LICENSE) 文件。

MIT License

Copyright (c) 2024 www1988
