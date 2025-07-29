from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
import random
import json
import os
from datetime import datetime, date

@register("astrbot_plugin_random_likes", "--sora--", "智能检测点赞关键词并自动随机点赞数", "1.0", "https://github.com/sora-yyds/astrbot_plugin_random_likes")
class RandomLikesPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.config = self.context.get_config()
        
        # 获取插件数据目录
        try:
            # 尝试通过context获取数据目录
            if hasattr(self.context, 'get_data_dir'):
                plugin_data_dir = self.context.get_data_dir()
                logger.info(f"通过context获取数据目录: {plugin_data_dir}")
            else:
                # 基于当前工作目录查找data目录
                current_dir = os.getcwd()
                logger.info(f"当前工作目录: {current_dir}")
                
                # 尝试常见的data目录路径
                possible_data_paths = [
                    os.path.join(current_dir, 'data'),  # 当前目录下的data
                    os.path.join(os.path.dirname(current_dir), 'data'),  # 上级目录的data
                ]
                
                # 查找存在的data目录
                data_dir = None
                for path in possible_data_paths:
                    if os.path.exists(path):
                        data_dir = path
                        break
                
                if data_dir:
                    plugin_data_dir = os.path.join(data_dir, 'plugin_data', 'astrbot_plugin_random_likes')
                else:
                    # 最终回退：在当前工作目录下创建
                    logger.warning("未找到data目录，在当前工作目录下创建plugin_data")
                    plugin_data_dir = os.path.join(current_dir, 'plugin_data', 'astrbot_plugin_random_likes')
                    
        except Exception as e:
            logger.warning(f"获取数据目录失败，使用默认路径: {e}")
            current_dir = os.getcwd()
            plugin_data_dir = os.path.join(current_dir, 'data', 'plugin_data', 'astrbot_plugin_random_likes')
        
        # 确保插件数据目录存在
        try:
            os.makedirs(plugin_data_dir, exist_ok=True)
            logger.info(f"插件数据目录: {plugin_data_dir}")
            logger.info(f"目录是否存在: {os.path.exists(plugin_data_dir)}")
        except Exception as e:
            logger.error(f"创建插件数据目录失败: {e}")
        
        # 点赞记录文件路径
        self.like_records_file = os.path.join(plugin_data_dir, 'like_records.json')
        # 本地配置文件路径（备用）
        self.local_config_file = os.path.join(plugin_data_dir, 'plugin_config.json')
        
        # 配置是否可用的标志
        self.config_available = False

    async def initialize(self):
        """插件初始化方法，设置默认配置"""
        try:
            logger.info("开始初始化随机点赞插件")

            # 检查配置系统是否可用
            self.config_available = self._test_config_system()
            logger.info(f"AstrBot配置系统可用: {self.config_available}")
            
            if not self.config_available:
                logger.warning("插件配置系统不可用，使用本地配置文件")
            
            default_config = {
                "min_likes": 1,
                "max_likes": 10,
                "enabled": True
            }
            
            logger.info(f"默认配置: {default_config}")
            
            # 使用安全的配置方法设置默认值
            for key, value in default_config.items():
                current_value = self.get_config_value(key)
                logger.info(f"检查配置项 {key}: 当前值={current_value}, 默认值={value}")
                if current_value is None:
                    logger.info(f"设置默认配置: {key} = {value}")
                    self.set_config_value(key, value)
            
            # 清理过期的点赞记录
            self.clean_old_records()
            
            logger.info("随机点赞插件初始化完成")
            
        except Exception as e:
            logger.error(f"插件初始化失败: {e}")
            logger.warning("使用默认配置运行插件")
    
    @filter.command("设置点赞范围")
    async def set_range(self, event: AstrMessageEvent):
        """设置点赞数量范围 /设置点赞范围 最小值 最大值 (仅管理员)"""
        # 检查是否为管理员
        if not self.is_admin(event):
            yield event.plain_result("❌ 此指令仅限管理员使用")
            return
            
        try:
            # 手动解析命令参数
            message_parts = event.message_str.strip().split()
            
            if len(message_parts) < 3:
                yield event.plain_result("❌ 请提供完整的参数: /设置点赞范围 最小值 最大值\n例如: /设置点赞范围 1 10")
                return
            
            min_val = int(message_parts[1])
            max_val = int(message_parts[2])
            
            if min_val >= max_val:
                yield event.plain_result("❌ 最小值必须小于最大值")
                return
            
            if min_val < 0:
                yield event.plain_result("❌ 最小值不能小于0")
                return
            
            if max_val > 20:
                yield event.plain_result("❌ 最大值不能超过20")
                return
            
            # 使用安全的配置设置方法
            success1 = self.set_config_value("min_likes", min_val)
            success2 = self.set_config_value("max_likes", max_val)
            
            if success1 and success2:
                yield event.plain_result(f"✅ 已设置点赞范围: {min_val} - {max_val}")
            else:
                yield event.plain_result("❌ 设置失败，配置保存出错")
            
        except ValueError:
            yield event.plain_result("❌ 请输入有效的数字\n格式: /设置点赞范围 最小值 最大值\n例如: /设置点赞范围 1 10")
        except IndexError:
            yield event.plain_result("❌ 参数不足，请使用格式: /设置点赞范围 最小值 最大值")
        except Exception as e:
            logger.error(f"设置范围时出错: {e}")
            yield event.plain_result("❌ 设置失败，请检查参数格式: /设置点赞范围 最小值 最大值")

    @filter.event_message_type(filter.EventMessageType.ALL)
    async def keyword_like(self, event: AstrMessageEvent):
        """关键词触发快速点赞"""
        if not self.get_config_value("enabled", True):
            return
        
        # 检查消息中是否包含点赞相关关键词
        message_text = event.message_str.lower()
        if not any(keyword in message_text for keyword in ["点赞"]):
            return
        
        # 获取用户ID
        user_id = event.get_sender_id()
        if not user_id:
            return
        
        # 检查今天是否已经点过赞
        if self.is_user_liked_today(user_id):
            yield event.plain_result("今天已经给你点过赞了哦，明天再来吧~")
            yield event.re
            return
            
        likes = random.randint(1, 10)
        
        # 尝试执行QQ点赞操作
        try:
            success = await self.perform_qq_like(event, likes)
            
            if success:
                # 记录点赞信息
                self.record_user_like(user_id, likes)
                yield event.plain_result(f"✨ 已为你点赞 {likes} 次~")
            else:
                yield event.plain_result(f"❌ 点赞失败，可能是平台不支持或需要添加好友")
                
        except Exception as e:
            if str(e) == "LIKE_LIMIT_REACHED":
                # 虽然达到上限，但仍然记录用户已点赞，避免重复尝试
                self.record_user_like(user_id, likes)
                yield event.plain_result("丛雨今天已经给你点过赞了哦，明天再来吧~")
            else:
                yield event.plain_result(f"❌ 点赞失败，可能是平台不支持或需要添加好友")

    async def perform_qq_like(self, event: AstrMessageEvent, count: int) -> bool:
        """执行QQ点赞操作"""
        try:
            # 获取平台信息
            platform_name = event.get_platform_name()
            
            # 只有QQ平台才支持点赞功能
            if platform_name.lower() not in ['qq', 'aiocqhttp', 'onebot']:
                logger.info(f"平台 {platform_name} 不支持点赞功能")
                return False
            
            # 获取发送者ID
            sender_id = event.get_sender_id()
            if not sender_id:
                logger.warning("无法获取发送者ID")
                return False
            
            # 获取平台适配器
            platform = self.context.get_platform(platform_name)
            if not platform:
                logger.warning(f"无法获取平台适配器: {platform_name}")
                return False
            
            # 尝试获取原始客户端对象
            if hasattr(platform, 'client') or hasattr(platform, 'bot'):
                client = getattr(platform, 'client', None) or getattr(platform, 'bot', None)
                
                # 尝试调用点赞API
                if hasattr(client, 'send_like'):
                    # OneBot v11 标准的点赞API
                    await client.send_like(user_id=int(sender_id), times=min(count, 10))  # QQ限制每日最多10次
                    logger.info(f"成功为用户 {sender_id} 点赞 {min(count, 10)} 次")
                    return True
                elif hasattr(client, 'call_api'):
                    # 通用API调用方式
                    await client.call_api('send_like', user_id=int(sender_id), times=min(count, 10))
                    logger.info(f"通过call_api为用户 {sender_id} 点赞 {min(count, 10)} 次")
                    return True
                else:
                    logger.warning("客户端不支持点赞API")
                    return False
            else:
                logger.warning("无法获取平台客户端对象")
                return False
                
        except Exception as e:
            error_msg = str(e)
            logger.error(f"执行点赞操作时出错: {e}")
            
            # 检查是否是点赞上限错误
            if any(keyword in error_msg for keyword in [
                "点赞数已达上限", 
                "retcode=1200", 
                "今日同一好友点赞数已达上限",
                "点赞失败 今日同一好友点赞数已达上限"
            ]):
                # 这是一个特殊情况，需要在调用方处理
                raise Exception("LIKE_LIMIT_REACHED")
            
            return False

    @filter.command("点赞状态")
    async def like_status(self, event: AstrMessageEvent):
        """查看插件状态和配置"""
        min_val = self.get_config_value("min_likes", 1)
        max_val = self.get_config_value("max_likes", 10)
        enabled = self.get_config_value("enabled", True)
        
        status = "启用" if enabled else "禁用"
        
        status_msg = f"""
📊 随机点赞插件状态

状态: {status}
点赞范围: {min_val} - {max_val}

可用指令:
• /设置点赞范围 最小值 最大值 - 设置点赞范围 (仅管理员) (例: /设置点赞范围 1 10)
• /点赞状态 - 查看状态
• /点赞统计 - 查看点赞统计
• 发送包含"点赞"的消息会自动触发点赞

注意: 
• 每人每天只能点赞一次
• 点赞功能仅支持QQ平台，且需要机器人与用户为好友关系

        """.strip()
        
        yield event.plain_result(status_msg)

    @filter.command("点赞统计")
    async def like_stats(self, event: AstrMessageEvent):
        """查看点赞统计信息"""
        try:
            records = self.load_like_records()
            today = date.today().isoformat()
            
            # 统计今日点赞数据
            today_likes = []
            total_users = len(records)
            
            for user_id, record in records.items():
                if record.get('date') == today:
                    today_likes.append(record['count'])
            
            today_count = len(today_likes)
            today_total_likes = sum(today_likes) if today_likes else 0
            
            # 检查当前用户是否已点赞
            current_user_id = event.get_sender_id()
            user_status = "已点赞" if self.is_user_liked_today(current_user_id) else "未点赞"
            
            stats_msg = f"""
📈 点赞统计信息

今日数据:
• 点赞人数: {today_count} 人
• 总点赞数: {today_total_likes} 次
• 当前状态: {user_status}

历史数据:
• 总用户数: {total_users} 人
• 记录保留: 最近7天

提示: 每人每天只能点赞一次
            """.strip()
            
            yield event.plain_result(stats_msg)
            
        except Exception as e:
            logger.error(f"获取点赞统计失败: {e}")
            yield event.plain_result("❌ 获取统计信息失败")

    async def terminate(self):
        """插件销毁方法"""
        logger.info("随机点赞插件已卸载")

    def load_like_records(self) -> dict:
        """加载点赞记录"""
        try:
            if os.path.exists(self.like_records_file):
                with open(self.like_records_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"加载点赞记录失败: {e}")
        return {}
    
    def save_like_records(self, records: dict):
        """保存点赞记录"""
        try:
            logger.info(f"正在保存点赞记录到: {self.like_records_file}")
            logger.debug(f"记录内容: {len(records)} 条记录")
            
            # 确保目录存在
            records_dir = os.path.dirname(self.like_records_file)
            if not os.path.exists(records_dir):
                os.makedirs(records_dir, exist_ok=True)
                logger.info(f"创建记录目录: {records_dir}")
            
            with open(self.like_records_file, 'w', encoding='utf-8') as f:
                json.dump(records, f, ensure_ascii=False, indent=2)
            
            # 验证文件是否成功保存
            if os.path.exists(self.like_records_file):
                file_size = os.path.getsize(self.like_records_file)
                logger.info(f"✅ 点赞记录保存成功: {self.like_records_file} (大小: {file_size} 字节)")
            else:
                logger.error(f"❌ 点赞记录保存失败，文件不存在: {self.like_records_file}")
                
        except Exception as e:
            logger.error(f"保存点赞记录失败: {e}")
            logger.error(f"目标路径: {self.like_records_file}")
            logger.error(f"记录目录: {os.path.dirname(self.like_records_file)}")
            logger.error(f"当前工作目录: {os.getcwd()}")
    
    def is_user_liked_today(self, user_id: str) -> bool:
        """检查用户今天是否已被点赞"""
        records = self.load_like_records()
        today = date.today().isoformat()
        return user_id in records and records[user_id].get('date') == today
    
    def record_user_like(self, user_id: str, count: int):
        """记录用户点赞信息"""
        records = self.load_like_records()
        today = date.today().isoformat()
        records[user_id] = {
            'date': today,
            'count': count,
            'timestamp': datetime.now().isoformat()
        }
        self.save_like_records(records)
    
    def clean_old_records(self):
        """清理过期的点赞记录（保留最近7天）"""
        try:
            records = self.load_like_records()
            today = date.today()
            cleaned_records = {}
            
            for user_id, record in records.items():
                try:
                    record_date = date.fromisoformat(record['date'])
                    # 保留最近7天的记录
                    if (today - record_date).days <= 7:
                        cleaned_records[user_id] = record
                except Exception:
                    continue
            
            if len(cleaned_records) != len(records):
                self.save_like_records(cleaned_records)
                logger.info(f"清理了 {len(records) - len(cleaned_records)} 条过期记录")
        except Exception as e:
            logger.error(f"清理过期记录失败: {e}")
    
    def get_config_value(self, key: str, default_value=None):
        """安全获取配置值"""
        try:
            # 首先尝试从 AstrBot 配置系统获取
            if self.config_available and self.config is not None:
                value = self.config.get(key)
                if value is not None:
                    return value
            
            # 如果 AstrBot 配置系统不可用，从本地配置文件获取
            local_config = self._load_local_config()
            if key in local_config:
                return local_config[key]
            
            return default_value
        except Exception as e:
            logger.error(f"获取配置项 {key} 失败: {e}")
            return default_value
    
    def set_config_value(self, key: str, value):
        """安全设置配置值"""
        try:
            success = False
            logger.info(f"正在设置配置项: {key} = {value}")
            
            # 首先尝试使用 AstrBot 配置系统
            if self.config_available and self.config is not None:
                try:
                    self.config.set(key, value)
                    self.config.save()
                    logger.info(f"✅ 通过 AstrBot 配置系统设置 {key} 成功")
                    success = True
                except Exception as e:
                    logger.warning(f"使用 AstrBot 配置系统设置 {key} 失败: {e}")
            
            # 同时保存到本地配置文件作为备份
            try:
                local_config = self._load_local_config()
                local_config[key] = value
                self._save_local_config(local_config)
                logger.info(f"✅ 通过本地配置文件设置 {key} 成功")
                success = True
            except Exception as e:
                logger.error(f"保存到本地配置文件失败: {e}")
            
            logger.info(f"配置设置结果: {key} = {value}, 成功: {success}")
            return success
        except Exception as e:
            logger.error(f"设置配置项 {key} 失败: {e}")
            return False
    
    def is_admin(self, event: AstrMessageEvent) -> bool:
        """检查用户是否为管理员"""
        try:
            # 首先检查事件对象是否有 is_admin 方法
            if hasattr(event, 'is_admin'):
                return event.is_admin()
            
            # 获取发送者ID
            sender_id = event.get_sender_id()
            if not sender_id:
                return False
            
            # 获取AstrBot全局配置（不是插件配置）
            try:
                # 尝试获取全局配置
                astr_config = self.context.get_context_config()
                if astr_config is None:
                    # 如果没有 get_context_config 方法，尝试其他方式
                    astr_config = self.context.config if hasattr(self.context, 'config') else None
                    if astr_config is None:
                        logger.warning("无法获取全局配置，使用默认管理员检查")
                        return False
            except Exception as e:
                logger.error(f"获取全局配置失败: {e}")
                return False
            
            # 尝试从不同的配置项中获取管理员列表
            admin_ids = []
            
            # 可能的管理员配置键名
            possible_admin_keys = [
                'admins',
                'admin_ids', 
                "admins_id",
                'administrators',
                'admin_list',
                'admin_users',
                'superusers'
            ]
            
            for key in possible_admin_keys:
                try:
                    admin_list = astr_config.get(key) if hasattr(astr_config, 'get') else None
                    if admin_list:
                        if isinstance(admin_list, list):
                            admin_ids.extend([str(admin_id) for admin_id in admin_list])
                        elif isinstance(admin_list, str):
                            admin_ids.append(admin_list)
                        break
                except Exception as e:
                    logger.debug(f"尝试获取配置键 {key} 失败: {e}")
                    continue
            
            # 检查发送者是否在管理员列表中
            return str(sender_id) in admin_ids
            
        except Exception as e:
            logger.error(f"检查管理员权限时出错: {e}")
            return False
    
    def _test_config_system(self) -> bool:
        """测试配置系统是否可用"""
        try:
            if self.config is None:
                return False
            
            # 检查必要的方法是否存在且可调用
            if not (hasattr(self.config, 'get') and callable(getattr(self.config, 'get', None))):
                return False
            if not (hasattr(self.config, 'set') and callable(getattr(self.config, 'set', None))):
                return False
            if not (hasattr(self.config, 'save') and callable(getattr(self.config, 'save', None))):
                return False
            
            # 尝试进行一个简单的操作
            test_key = "test_config_system"
            self.config.set(test_key, "test_value")
            value = self.config.get(test_key)
            if value != "test_value":
                return False
            
            return True
        except Exception as e:
            logger.debug(f"配置系统测试失败: {e}")
            return False
    
    def _load_local_config(self) -> dict:
        """加载本地配置文件"""
        try:
            if os.path.exists(self.local_config_file):
                with open(self.local_config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"加载本地配置失败: {e}")
        return {}
    
    def _save_local_config(self, config_data: dict):
        """保存本地配置文件"""
        try:
            logger.info(f"正在保存配置到: {self.local_config_file}")
            logger.info(f"配置内容: {config_data}")
            
            # 确保目录存在
            config_dir = os.path.dirname(self.local_config_file)
            if not os.path.exists(config_dir):
                os.makedirs(config_dir, exist_ok=True)
                logger.info(f"创建配置目录: {config_dir}")
            
            with open(self.local_config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, ensure_ascii=False, indent=2)
            
            # 验证文件是否成功保存
            if os.path.exists(self.local_config_file):
                file_size = os.path.getsize(self.local_config_file)
                logger.info(f"✅ 配置文件保存成功: {self.local_config_file} (大小: {file_size} 字节)")
            else:
                logger.error(f"❌ 配置文件保存失败，文件不存在: {self.local_config_file}")
                
        except Exception as e:
            logger.error(f"保存本地配置失败: {e}")
            logger.error(f"目标路径: {self.local_config_file}")
            logger.error(f"配置目录: {os.path.dirname(self.local_config_file)}")
            logger.error(f"当前工作目录: {os.getcwd()}")
