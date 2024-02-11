# -*- coding:utf-8 -*-
import asyncio
import random
import time
from enum import Enum, auto, unique
from typing import List

from sanic import Sanic

import ntpu_linebot.id.request as id_request

# 科系名稱 -> 科系代碼
DEPARTMENT_CODE = {
    "法律": "71",
    "法學": "712",
    "司法": "714",
    "財法": "716",
    "公行": "72",
    "經濟": "73",
    "社學": "742",
    "社工": "744",
    "財政": "75",
    "不動": "76",
    "會計": "77",
    "統計": "78",
    "企管": "79",
    "金融": "80",
    "中文": "81",
    "應外": "82",
    "歷史": "83",
    "休運": "84",
    "資工": "85",
    "通訊": "86",
    "電機": "87",
}

# 科系全名 -> 科系代碼
FULL_DEPARTMENT_CODE = {
    "法律學系": "71",
    "法學組": "712",
    "司法組": "714",
    "財經法組": "716",
    "公共行政暨政策學系": "72",
    "經濟學系": "73",
    "社會學系": "742",
    "社會工作學系": "744",
    "財政學系": "75",
    "不動產與城鄉環境學系": "76",
    "會計學系": "77",
    "統計學系": "78",
    "企業管理學系": "79",
    "金融與合作經營學系": "80",
    "中國文學系": "81",
    "應用外語學系": "82",
    "歷史學系": "83",
    "休閒運動管理學系": "84",
    "資訊工程學系": "85",
    "通訊工程學系": "86",
    "電機工程學系": "87",
}

# 科系代碼 -> 科系名稱
DEPARTMENT_NAME = {v: k for k, v in DEPARTMENT_CODE.items()}

# 科系代碼 -> 科系全名
FULL_DEPARTMENT_NAME = {v: k for k, v in FULL_DEPARTMENT_CODE.items()}


# 學生資訊排序
@unique
class Order(Enum):
    """輸出項目排序"""

    ID = auto()
    NAME = auto()
    YEAR = auto()
    DEPARTMENT = auto()
    FULL_DEPARTMENT = auto()


def student_info_format(
    student_id: str,
    name: str | None = None,
    order: List[Order] | None = None,
    space: int = 1,
) -> str:
    """學生資訊格式化"""

    if name is None:
        name = id_request.get_student_by_id(student_id)

    if not name:
        return ""

    if order is None:
        order = [Order.YEAR, Order.DEPARTMENT, Order.ID, Order.NAME]

    message = []
    over_99 = len(student_id) == 9

    for o in order:
        if o == Order.ID:
            message.append(student_id)
        elif o == Order.NAME:
            message.append(name)
        elif o == Order.YEAR:
            year = student_id[1 : over_99 + 3]
            message.append(year)
        elif o == Order.DEPARTMENT:
            department = student_id[over_99 + 3 : over_99 + 5]
            if department == DEPARTMENT_CODE["社學"][0:2]:
                department += student_id[over_99 + 5]

            message.append(DEPARTMENT_NAME[department] + "系")
        elif o == Order.FULL_DEPARTMENT:
            department = student_id[over_99 + 3 : over_99 + 5]
            if department in [
                DEPARTMENT_CODE["法律"],
                DEPARTMENT_CODE["社學"][0:2],
            ]:
                department += student_id[over_99 + 5]

            if department[0:2] == DEPARTMENT_CODE["法律"]:
                message.append("法律系")
                message.append(DEPARTMENT_NAME[department] + "組")
            else:
                message.append(DEPARTMENT_NAME[department] + "系")
        else:
            raise ValueError("Invalid order")

    return (" " * space).join(message)


def healthz(app: Sanic) -> bool:
    """網址健康檢查"""

    if not id_request.base_url:
        if not id_request.check_url():
            return False

        app.add_task(renew_student_list())

    return True


async def renew_student_list() -> None:
    """更新學生名單"""

    cur_year = time.localtime(time.time()).tm_year - 1911

    for year in range(cur_year - 5, cur_year + 1):
        for dep in DEPARTMENT_CODE.values():
            id_request.get_students_by_year_and_department(str(year), str(dep))
            await asyncio.sleep(random.uniform(5, 15))
