# -*- coding:utf-8 -*-
import random
from asyncio import sleep
from datetime import datetime
from enum import Enum, auto, unique
from typing import Optional

from sanic import Sanic

from .request import ID_REQUEST

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

MASTER_DEPARTMENT_CODE = {
    "法律學系碩士班一般生組": "51",
    "法律學系碩士班法律專業組": "52",
    "企業管理學系碩士班": "31",
    "金融與合作經營學系碩士班": "34",
    "會計學系碩士班": "32",
    "統計學系碩士班": "33",
    "國際企業研究所碩士班": "35",
    "資訊管理研究所": "36",
    "公共行政暨政策學系碩士班": "71",
    "財政學系碩士班": "72",
    "不動產與城鄉環境學系碩士班": "73",
    "都市計劃研究所碩士班": "74",
    "自然資源與環境管理研究所碩士班": "75",
    "經濟學系碩士班": "61",
    "社會工作學系碩士班": "63",
    "社會學系碩士班": "62",
    "犯罪學研究所": "64",
    "民俗藝術與文化資產研究所": "41",
    "中國文學系碩士班": "43",
    "歷史學系碩士班": "44",
    "通訊工程學系碩士班": "81",
    "電機工程學系碩士班": "82",
    "資訊工程學系碩士班": "83",
}


FULL_MASTER_DEPARTMENT_CODE = {
    "企業管理學系碩士班": "31",
    "會計學系碩士班": "32",
    "統計學系碩士班": "33",
    "金融與合作經營學系碩士班": "34",
    "國際企業研究所碩士班": "35",
    "資訊管理研究所": "36",
    "財務金融英語碩士學位學程": "37",
    "民俗藝術與文化資產研究所": "41",
    "古典文獻學研究所": "42",
    "中國文學系碩士班": "43",
    "歷史學系碩士班": "44",
    "法律學系碩士班一般生組": "51",
    "法律學系碩士班法律專業組": "52",
    "經濟學系碩士班": "61",
    "社會學系碩士班": "62",
    "社會工作學系碩士班": "63",
    "犯罪學研究所": "64",
    "公共行政暨政策學系碩士班": "71",
    "財政學系碩士班": "72",
    "不動產與城鄉環境學系碩士班": "73",
    "都市計劃研究所碩士班": "74",
    "自然資源與環境管理研究所碩士班": "75",
    "城市治理英語碩士學位學程": "76",
    "會計學系碩士在職專班": "77",
    "統計學系碩士在職專班": "78",
    "企業管理學系碩士在職專班": "79",
    "通訊工程學系碩士班": "81",
    "電機工程學系碩士班": "82",
    "資訊工程學系碩士班": "83",
    "智慧醫療管理英語碩士學位學程": "91",
}

PHD_DEPARTMENT_CODE = {
    "會計學系博士班": "32",
    "法律學系博士班": "51",
    "經濟學系博士班": "61",
    "公共行政暨政策學系博士班": "71",
    "不動產與城鄉環境學系博士班": "73",
    "都市計劃研究所博士班": "74",
    "自然資源與環境管理研究所博士班": "75",
    "電機資訊學院博士班": "76",
}

FULL_PHD_DEPARTMENT_CODE = {
    "會計學系博士班": "32",
    "法律學系博士班": "51",
    "經濟學系博士班": "61",
    "公共行政暨政策學系博士班": "71",
    "不動產與城鄉環境學系博士班": "73",
    "都市計劃研究所博士班": "74",
    "自然資源與環境管理研究所博士班": "75",
    "電機資訊學院博士班": "76",
}


# 科系代碼 -> 科系名稱
DEPARTMENT_NAME = {v: k for k, v in DEPARTMENT_CODE.items()}
MASTER_DEPARTMENT_NAME = {v: k for k, v in MASTER_DEPARTMENT_CODE.items()}
PHD_DEPARTMENT_NAME = {v: k for k, v in PHD_DEPARTMENT_CODE.items()}

# 科系代碼 -> 科系全名
FULL_DEPARTMENT_NAME = {v: k for k, v in FULL_DEPARTMENT_CODE.items()}
FULL_MASTER_DEPARTMENT_NAME = {v: k for k, v in FULL_MASTER_DEPARTMENT_CODE.items()}
FULL_PHD_DEPARTMENT_NAME = {v: k for k, v in FULL_PHD_DEPARTMENT_CODE.items()}


async def healthz(app: Sanic, force: bool = False) -> bool:
    """
    Perform a health check on a URL.

    Args:
        app (Sanic): The Sanic application.
        force (bool, optional): Whether to force the renew. Defaults to False.

    Returns:
        bool: True if the health check is successful, False otherwise.
    """

    if force:
        await app.cancel_task("load_student_dict", raise_exception=False)
        app.add_task(load_student_dict, name="load_student_dict")
        return True

    if not await ID_REQUEST.check_url():
        if await ID_REQUEST.change_base_url():
            await app.cancel_task("load_student_dict", raise_exception=False)
            app.add_task(load_student_dict, name="load_student_dict")

        return False

    return True


async def load_student_dict() -> None:
    """Updates the student dict for each department and year."""

    cur_year = datetime.now().year - 1911
    for year in range(cur_year, cur_year - 6, -1):
        for dep in DEPARTMENT_CODE.values():
            await sleep(random.uniform(10, 20))
            await ID_REQUEST.get_students_by_year_and_department(year, dep)


@unique
class Order(Enum):
    """Enumeration representing the order in which different items should be displayed or sorted."""

    ID = auto()
    NAME = auto()
    YEAR = auto()
    DEPARTMENT = auto()
    FULL_DEPARTMENT = auto()


def student_info_format(
    student_id: str,
    name: str,
    order: Optional[list[Order]] = None,
    space: int = 1,
) -> str:
    """
    Format the student information based on the given parameters and return the formatted string.

    Args:
        student_id (str): The ID of the student
        name (str): The name of the student. Defaults to None.
        order (list[Order], optional): The order of the information. Defaults to None.
        space (int, optional): The space between the formatted information. Defaults to 1.

    Returns:
        str: The formatted student information.
    """

    # Set default order if not provided
    if order is None:
        order = [Order.YEAR, Order.DEPARTMENT, Order.ID, Order.NAME]

    message = []
    is_over_99 = len(student_id) == 9
    is_master = student_id[0] == "7"
    is_phd = student_id[0] == "8"

    # Format the student information based on the order
    for o in order:
        match o:
            case Order.ID:
                message.append(student_id)

            case Order.NAME:
                message.append(name)

            case Order.YEAR:
                year = student_id[1 : is_over_99 + 3]
                message.append(year)

            case Order.DEPARTMENT:
                department = student_id[is_over_99 + 3 : is_over_99 + 5]
                if is_master:
                    message.append(MASTER_DEPARTMENT_NAME[department])
                    continue

                if is_phd:
                    message.append(PHD_DEPARTMENT_NAME[department])
                    continue

                if department == DEPARTMENT_CODE["社學"][0:2]:
                    department += student_id[is_over_99 + 5]

                message.append(DEPARTMENT_NAME[department] + "系")

            case Order.FULL_DEPARTMENT:
                department = student_id[is_over_99 + 3 : is_over_99 + 5]
                if is_master:
                    message.append(FULL_MASTER_DEPARTMENT_NAME[department])
                    continue

                if is_phd:
                    message.append(FULL_PHD_DEPARTMENT_NAME[department])
                    continue

                if department in [DEPARTMENT_CODE["法律"], DEPARTMENT_CODE["社學"][:2]]:
                    department += student_id[is_over_99 + 5]

                if department[0:2] == DEPARTMENT_CODE["法律"]:
                    message.append("法律系")
                    message.append(DEPARTMENT_NAME[department] + "組")

                else:
                    message.append(DEPARTMENT_NAME[department] + "系")

            case _:
                raise ValueError("Invalid Order")

    return (" " * space).join(message)


async def search_student_by_uid(uid: str) -> Optional[str]:
    """
    Async function to search for a student by ID.

    Args:
        uid (str): The unique identifier of the student.

    Returns:
        Optional[str]: The information of the student if found, otherwise None.
    """

    return await ID_REQUEST.get_student_by_uid(uid)


def search_students_by_name(name: str) -> list[tuple[str, str]]:
    """
    Searches for students by name.

    Args:
        name (str): The name of the student to search for.

    Returns:
        list: A list of tuples containing the names and IDs of the matching students.
    """

    return [
        (key, value)
        for key, value in ID_REQUEST.STUDENT_DICT.items()
        if set(name).issubset(value)
    ]


async def search_students_by_year_and_department(year: int, department: str) -> str:
    """
    Asynchronously search for students by year and department.

    Args:
        year (int): The year to search for.
        department (str): The department to search within.

    Returns:
        str: Information about the students found, including their IDs, names, and total count.
    """

    department_name = DEPARTMENT_NAME.get(department, "")
    department_type = "組" if department.startswith(DEPARTMENT_CODE["法律"]) else "系"

    if students := await ID_REQUEST.get_students_by_year_and_department(
        year, department
    ):
        students_info = "\n".join(
            [
                student_info_format(student_id, student_name, [Order.ID, Order.NAME], 3)
                for student_id, student_name in students.items()
            ]
        )

        students_info += f"\n\n{year}學年度{department_name}{department_type}共有{len(students)}位學生"

    else:
        students_info = f"{year}學年度{department_name}{department_type}好像沒有人耶OAO"

    return students_info
