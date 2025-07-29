from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
import random

@register("astrbot_plugin_random_likes", "--sora--", "随机点赞数量插件", "1.0", "https://github.com/sora-yyds/astrbot_plugin_random_likes")
class RandomLikesPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.config = self.context.get_config()

    async def initialize(self):
        """插件初始化方法，设置默认配置"""
        default_config = {
            "min_likes": 1,
            "max_likes": 10,
            "enabled": True
        }
        
        for key, value in default_config.items():
            if self.config.get(key) is None:
                self.config.set(key, value)
        
        self.config.save()
        logger.info("随机点赞插件初始化完成")
    
    @filter.command("random_like")
    async def random_like(self, event: AstrMessageEvent):
        """生成随机点赞数量"""
        if not self.config.get("enabled", True):
            yield event.plain_result("插件已禁用")
            return
        
        min_val = self.config.get("min_likes", 1)
        max_val = self.config.get("max_likes", 10)
        
        likes = random.randint(min_val, max_val)
        user_name = event.get_sender_name()
        
        # 尝试执行真正的QQ点赞操作
        success = await self.perform_qq_like(event, likes)
        
        if success:
            yield event.plain_result(f"🎉 {user_name} 已获得 {likes} 个真实点赞！")
        else:
            yield event.plain_result(f"🎉 {user_name} 获得了 {likes} 个点赞！(模拟点赞)")

    @filter.command("set_range", ["{min}", "{max}"])
    async def set_range(self, event: AstrMessageEvent):
        """设置点赞数量范围 /set_range 最小值 最大值"""
        args = event.get_args()
        
        try:
            min_val = int(args.get("min", 1))
            max_val = int(args.get("max", 10))
            
            if min_val >= max_val:
                yield event.plain_result("❌ 最小值必须小于最大值")
                return
            
            if min_val < 0:
                yield event.plain_result("❌ 最小值不能小于0")
                return
            
            self.config.set("min_likes", min_val)
            self.config.set("max_likes", max_val)
            self.config.save()
            
            yield event.plain_result(f"✅ 已设置点赞范围: {min_val} - {max_val}")
            
        except ValueError:
            yield event.plain_result("❌ 请输入有效的数字")

    @filter.regex(r".*(点赞|👍|赞).*")
    async def keyword_like(self, event: AstrMessageEvent):
        """关键词触发快速点赞"""
        if not self.config.get("enabled", True):
            return
            
        likes = random.randint(1, 50)
        
        # 尝试执行真正的QQ点赞操作
        success = await self.perform_qq_like(event, likes)
        
        if success:
            yield event.plain_result(f"👍 已为你点赞 {likes} 次！")
        else:
            yield event.plain_result(f"👍 +{likes} (模拟点赞，若需真实点赞请加我为好友)")

    async def perform_qq_like(self, event: AstrMessageEvent, count: int) -> bool:
        """执行真正的QQ点赞操作"""
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
            logger.error(f"执行点赞操作时出错: {e}")
            return False

    @filter.command("like_status")
    async def like_status(self, event: AstrMessageEvent):
        """查看插件状态和配置"""
        min_val = self.config.get("min_likes", 1)
        max_val = self.config.get("max_likes", 10)
        enabled = self.config.get("enabled", True)
        
        status = "启用" if enabled else "禁用"
        
        status_msg = f"""
📊 随机点赞插件状态

状态: {status}
点赞范围: {min_val} - {max_val}

可用指令:
• /random_like - 生成随机点赞(尝试真实点赞)
• /set_range 最小值 最大值 - 设置范围
• /test_like 次数 - 测试点赞功能(1-10次)
• /like_status - 查看状态
• 发送包含"点赞"、"👍"、"赞"的消息触发快速点赞

注意: 真实点赞功能仅支持QQ平台，且需要机器人与用户为好友关系
        """.strip()
        
        yield event.plain_result(status_msg)

    @filter.command("test_like", ["{count}"])
    async def test_like(self, event: AstrMessageEvent):
        """测试点赞功能 /test_like 次数"""
        if not self.config.get("enabled", True):
            yield event.plain_result("插件已禁用")
            return
        
        args = event.get_args()
        try:
            count = int(args.get("count", 1))
            count = max(1, min(count, 10))  # 限制在1-10次之间
            
            user_name = event.get_sender_name()
            success = await self.perform_qq_like(event, count)
            
            if success:
                yield event.plain_result(f"✅ 成功为 {user_name} 点赞 {count} 次！")
            else:
                yield event.plain_result(f"❌ 点赞失败，可能是平台不支持或需要添加好友")
                
        except ValueError:
            yield event.plain_result("❌ 请输入有效的数字 (1-10)")

    async def terminate(self):
        """插件销毁方法"""
        logger.info("随机点赞插件已卸载")
