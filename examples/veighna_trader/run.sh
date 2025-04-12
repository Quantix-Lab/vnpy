#!/bin/bash
# VeighNa量化交易平台启动脚本

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_ROOT=$(cd "$(dirname "$0")/../.." && pwd)
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)

# 显示欢迎信息
echo -e "${BLUE}=====================================${NC}"
echo -e "${BLUE}   VeighNa量化交易平台启动程序   ${NC}"
echo -e "${BLUE}=====================================${NC}"

# 检查是否已激活虚拟环境
check_venv() {
    if [[ -z "$VIRTUAL_ENV" ]]; then
        echo -e "${YELLOW}未检测到激活的虚拟环境。${NC}"

        # 检查本地虚拟环境是否存在
        if [[ -d "$PROJECT_ROOT/.venv" ]]; then
            echo -e "${GREEN}发现本地虚拟环境，正在激活...${NC}"
            source "$PROJECT_ROOT/.venv/bin/activate" || {
                echo -e "${RED}激活虚拟环境失败！${NC}"
                exit 1
            }
            return 0
        fi

        echo -e "${YELLOW}未找到虚拟环境，是否创建新的虚拟环境？(y/n)${NC}"
        read -r response
        if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
            echo -e "${GREEN}正在创建虚拟环境...${NC}"
            python -m venv "$PROJECT_ROOT/.venv" || {
                echo -e "${RED}创建虚拟环境失败！${NC}"
                exit 1
            }
            source "$PROJECT_ROOT/.venv/bin/activate" || {
                echo -e "${RED}激活虚拟环境失败！${NC}"
                exit 1
            }
            echo -e "${GREEN}虚拟环境创建并激活成功。${NC}"

            echo -e "${YELLOW}是否安装依赖项？(y/n)${NC}"
            read -r install_deps
            if [[ "$install_deps" =~ ^([yY][eE][sS]|[yY])$ ]]; then
                # 安装依赖
                echo -e "${GREEN}正在安装核心依赖...${NC}"
                pip install -e "$PROJECT_ROOT" || {
                    echo -e "${RED}安装VeighNa核心失败！${NC}"
                    exit 1
                }

                echo -e "${GREEN}正在安装富途接口...${NC}"
                pip install -e "$PROJECT_ROOT/vnpy_futu" || {
                    echo -e "${RED}安装富途接口失败！${NC}"
                    exit 1
                }

                echo -e "${GREEN}正在安装应用模块...${NC}"
                pip install -e "$PROJECT_ROOT/vnpy_ctastrategy" || echo -e "${YELLOW}安装CTA策略模块失败，但继续执行。${NC}"
                pip install -e "$PROJECT_ROOT/vnpy_ctabacktester" || echo -e "${YELLOW}安装CTA回测模块失败，但继续执行。${NC}"
                pip install -e "$PROJECT_ROOT/vnpy_datamanager" || echo -e "${YELLOW}安装数据管理模块失败，但继续执行。${NC}"

                echo -e "${GREEN}依赖安装完成！${NC}"
            fi
        else
            echo -e "${RED}未创建虚拟环境，无法继续。${NC}"
            exit 1
        fi
    else
        echo -e "${GREEN}已激活虚拟环境: $VIRTUAL_ENV${NC}"
    fi
}

# 检查Qt环境变量
check_qt_env() {
    if [[ "$(uname)" == "Darwin" ]]; then
        if [[ -z "$QT_MAC_WANTS_LAYER" ]]; then
            echo -e "${YELLOW}设置macOS上的Qt环境变量以提升性能...${NC}"
            export QT_MAC_WANTS_LAYER=1
        fi
    fi
}

# 检查并处理依赖项
check_dependencies() {
    echo -e "${BLUE}检查关键依赖...${NC}"

    # 检查vnpy_futu
    if python -c "import vnpy_futu" &>/dev/null; then
        echo -e "${GREEN}vnpy_futu 已安装${NC}"
    else
        echo -e "${YELLOW}vnpy_futu 未安装，尝试安装...${NC}"
        pip install -e "$PROJECT_ROOT/vnpy_futu" || {
            echo -e "${RED}安装富途接口失败！${NC}"
            exit 1
        }
    fi

    # 检查PySide6
    if python -c "import PySide6" &>/dev/null; then
        echo -e "${GREEN}PySide6 已安装${NC}"
    else
        echo -e "${YELLOW}PySide6 未安装，尝试安装...${NC}"
        pip install PySide6==6.5.0 || {
            echo -e "${RED}安装PySide6失败！${NC}"
            exit 1
        }
    fi
}

# 启动程序
start_application() {
    echo -e "${BLUE}启动VeighNa量化交易平台...${NC}"

    # 切换到脚本目录
    cd "$SCRIPT_DIR" || {
        echo -e "${RED}无法进入脚本目录！${NC}"
        exit 1
    }

    # 启动应用
    python run.py

    # 捕获退出状态
    exit_status=$?
    if [[ $exit_status -ne 0 ]]; then
        echo -e "${RED}应用异常退出，退出代码: $exit_status${NC}"
        echo -e "${YELLOW}查看以上输出获取更多错误信息。${NC}"
    fi

    echo -e "${BLUE}=====================================${NC}"
    echo -e "${BLUE}   VeighNa量化交易平台已关闭   ${NC}"
    echo -e "${BLUE}=====================================${NC}"
}

# 主函数
main() {
    check_venv
    check_qt_env
    check_dependencies
    start_application
}

# 执行主函数
main