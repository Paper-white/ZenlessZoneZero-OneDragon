from typing import List

from one_dragon.base.operation.operation_edge import node_from
from one_dragon.base.operation.operation_node import operation_node
from one_dragon.base.operation.operation_round_result import OperationRoundResult
from one_dragon.utils.i18_utils import gt
from zzz_od.application.zzz_application import ZApplication
from zzz_od.context.zzz_context import ZContext
from zzz_od.operation.back_to_normal_world import BackToNormalWorld
from zzz_od.operation.compendium.compendium_choose_tab import CompendiumChooseTab
from zzz_od.operation.compendium.open_compendium import OpenCompendium


class RiduWeeklyApp(ZApplication):

    def __init__(self, ctx: ZContext):
        ZApplication.__init__(
            self,
            ctx=ctx, app_id='ridu_weekly',
            op_name=gt('丽都周纪(领奖励)', 'ui'),
            run_record=ctx.ridu_weekly_record,
            retry_in_od=True,  # 传送落地有可能会歪 重试
        )

    @operation_node(name='快捷手册', is_start_node=True)
    def open_compendium(self) -> OperationRoundResult:
        op = OpenCompendium(self.ctx)
        return self.round_by_op_result(op.execute())

    @node_from(from_name='快捷手册')
    @operation_node(name='日常')
    def choose_train(self) -> OperationRoundResult:
        op = CompendiumChooseTab(self.ctx, tab_name='日常')
        return self.round_by_op_result(op.execute(), wait=1)

    @node_from(from_name='日常')
    @operation_node(name='丽都周纪')
    def click_schedule(self) -> OperationRoundResult:
        screen = self.screenshot()

        return self.round_by_find_and_click_area(screen, '丽都周纪', '丽都周纪',
                                                 success_wait=2, retry_wait=1)

    @node_from(from_name='丽都周纪')
    @operation_node(name='领取积分')
    def claim_score(self) -> OperationRoundResult:
        screen = self.screenshot()
        area = self.ctx.screen_loader.get_area('丽都周纪', '任务区域')

        result = self.round_by_ocr_and_click(screen, '100', area=area,
                                             color_range=[(150, 190, 0), (220, 255, 50)])

        if result.is_success:
            return self.round_wait(result.status, wait=1)

        return self.round_retry(result.status, wait=1)

    @node_from(from_name='领取积分', success=False)  # 没有100积分之后
    @operation_node(name='领取奖励')
    def confirm_schedule(self) -> OperationRoundResult:
        return self.round_by_click_area('丽都周纪', '领取奖励',
                                        success_wait=1, retry_wait=1)

    @node_from(from_name='领取奖励')
    @operation_node(name='完成后返回')
    def finish(self) -> OperationRoundResult:
        op = BackToNormalWorld(self.ctx)
        return self.round_by_op_result(op.execute())


def __debug():
    ctx = ZContext()
    ctx.init_by_config()
    app = RiduWeeklyApp(ctx)
    app.execute()


if __name__ == '__main__':
    __debug()