# -*- coding:utf-8 -*-
from re import IGNORECASE, search
from typing import Optional, Sequence

from linebot.v3.messaging.models import (
    Action,
    ButtonsTemplate,
    CarouselColumn,
    CarouselTemplate,
    ClipboardAction,
    Message,
    PostbackAction,
    TemplateMessage,
    TextMessage,
    URIAction,
)

from ..abs_bot import Bot
from ..line_bot_util import EMPTY_POSTBACK_ACTION, get_sender
from ..normal_util import list_to_regex, partition
from .contact import Contact, Individual, Organization
from .util import search_contacts_by_criteria, search_contacts_by_name


class ContactBot(Bot):
    __SENDER_NAME = "聯繫魔法師"
    __VALID_CONTACT_STR = [
        "touch",
        "contact",
        "connect",
        "聯繫",
        "聯絡",
        "聯繫方式",
        "聯絡方式",
        "連繫",
        "連絡",
        "連絡方式",
        "連絡方式",
    ]
    __CONTACT_REGEX = list_to_regex(__VALID_CONTACT_STR)

    @property
    def __sender_name(self) -> str:
        return self.__SENDER_NAME

    @property
    def __contact_regex(self):
        return self.__CONTACT_REGEX

    async def handle_text_message(
        self,
        payload: str,
        quote_token: Optional[str] = None,
    ) -> list[Message]:
        """處理文字訊息"""

        if payload.startswith("緊急"):
            return [
                TemplateMessage(
                    altText="緊急電話",
                    template=ButtonsTemplate(
                        altText="各種緊急電話",
                        text="\n\n".join(
                            [
                                "\n".join(
                                    [
                                        f"三峽校區電話：{Contact.SANXIA_NORMAL_PHONE}",
                                        f"三峽校區24H緊急行政電話：{Contact.SANXIA_24H_PHONE}",
                                        f"三峽校區24H急難救助電話：{Contact.SANXIA_EMERGENCY_PHONE}",
                                    ]
                                ),
                                "\n".join(
                                    [
                                        f"台北校區電話：{Contact.TAIPEI_NORMAL_PHONE}",
                                        f"台北校區24H急難救助電話：{Contact.TAIPEI_EMERGENCY_PHONE}",
                                    ]
                                ),
                            ]
                        ),
                        defaultAction=URIAction(
                            label="查看更多",
                            uri="https://new.ntpu.edu.tw/safety",
                        ),
                        actions=[
                            ClipboardAction(
                                label="複製三峽校區24H緊急行政電話",
                                clipboardText=Contact.SANXIA_24H_PHONE,
                            ),
                            ClipboardAction(
                                label="複製三峽校區24H急難救助電話",
                                clipboardText=Contact.SANXIA_EMERGENCY_PHONE,
                            ),
                            ClipboardAction(
                                label="複製台北校區24H急難救助電話",
                                clipboardText=Contact.TAIPEI_EMERGENCY_PHONE,
                            ),
                            URIAction(
                                label="查看更多",
                                uri="https://new.ntpu.edu.tw/safety",
                            ),
                        ],
                    ),
                    sender=get_sender(self.__sender_name),
                )
            ]

        if m := search(self.__contact_regex, payload, IGNORECASE):
            criteria = m.group()

            if contacts := search_contacts_by_name(criteria):
                return [
                    TemplateMessage(
                        altText="�����結果",
                        template=template,
                        sender=get_sender(self.__sender_name),
                    )
                    for template in self.__generate_contact_templates(contacts)
                ]

            if contacts := await search_contacts_by_criteria(criteria):
                return [
                    TemplateMessage(
                        altText="搜尋結果",
                        template=template,
                        sender=get_sender(self.__sender_name),
                    )
                    for template in self.__generate_contact_templates(contacts)
                ]

            return [
                TextMessage(
                    text=f"查無含有「{criteria}」的聯絡資料",
                    sender=get_sender(self.__sender_name),
                    quoteToken=quote_token,
                )
            ]

        return []

    async def handle_postback_event(self, payload: str) -> list[Message]:
        """處理回傳事件"""

        if payload.startswith("查看更多"):
            payload = payload.split(self.split_char)[1]

            if contacts := search_contacts_by_name(payload):
                return [
                    TemplateMessage(
                        altText="更多資訊",
                        template=template,
                        sender=get_sender(self.__sender_name),
                    )
                    for template in self.__generate_contact_templates(contacts, True)
                ]

        if payload.startswith("查看成員"):
            payload = payload.split(self.split_char)[1]

            if contacts := search_contacts_by_name(payload):
                if isinstance(contact := contacts[0], Organization):
                    return [
                        TemplateMessage(
                            altText="成員清單",
                            template=template,
                            sender=get_sender(self.__sender_name),
                        )
                        for template in self.__generate_contact_templates(
                            contact.members
                        )
                    ]

        if payload.startswith("查看資訊"):
            payload = payload.split(self.split_char)[1]

            if contacts := search_contacts_by_name(payload):
                individual_contacts = [c for c in contacts if isinstance(c, Individual)]
                if individual_contacts:
                    return [
                        TemplateMessage(
                            altText="更多資訊",
                            template=template,
                            sender=get_sender(self.__sender_name),
                        )
                        for template in self.__generate_contact_templates(
                            individual_contacts
                        )
                    ]

        return []

    def __generate_individual_carousel_column(
        self,
        individual: Individual,
        depth: bool = False,
    ) -> CarouselColumn:
        """
        Generates a carousel column for an individual with their organization, title, extension, phone, email, and actions.

        Args:
            individual (Individual): The individual for whom the carousel column is generated.
            depth (bool, optional): Flag to indicate whether to include depth actions. Defaults to False.

        Returns:
            CarouselColumn: The generated carousel column.
        """

        texts = [f"{individual.organization} {individual.title}"]
        actions: list[Action] = []

        if extension := individual.extension:
            texts.append(f"分機號碼: {extension}")

        if not depth and (phone := individual.phone):
            actions.append(
                ClipboardAction(
                    label="複製電話(含分機)",
                    clipboardText=phone,
                )
            )

        if depth and (phone_url := individual.phone_url):
            actions.append(
                URIAction(
                    label=f"打電話給 {individual.name}"[:20],
                    uri=phone_url,
                )
            )

        if len(actions) == 0 and (extension := individual.extension):
            actions.append(
                ClipboardAction(
                    label="複製分機號碼",
                    clipboardText=extension,
                )
            )

        if email := individual.email:
            texts.append(f"電子郵件: {email}")

        if not depth and (email := individual.email):
            actions.append(
                ClipboardAction(
                    label="複製電子郵件",
                    clipboardText=email,
                )
            )

        if depth and (email_url := individual.email_url):
            actions.append(
                URIAction(
                    label=f"寄信給 {individual.name}"[:20],
                    uri=email_url,
                )
            )

        if not depth:
            actions.append(
                PostbackAction(
                    label="查看更多",
                    displayText=f"搜尋 {individual.name} 的更多資訊",
                    data=f"查��更多{self.split_char}{individual.name}",
                )
            )
        else:
            actions.append(
                PostbackAction(
                    label="授課課程",
                    displayText=f"搜尋 {individual.name} 的授課課程",
                    data=f"授課課程{self.split_char}{individual.name}",
                )
            )

        default_action = (
            URIAction(label="搜尋連結", uri=individual.search_url)
            if individual.search_url
            else None
        )

        return CarouselColumn(
            title=individual.name,
            text=text if len(text := "\n".join(texts)) <= 60 else text[:59] + "…",
            defaultAction=default_action,
            actions=actions,
        )

    def __generate_organization_carousel_column(
        self,
        organization: Organization,
    ) -> CarouselColumn:
        """
        Generates a carousel column for the organization with the specified information.

        Args:
            organization (Organization): The organization for which the carousel column is generated.

        Returns:
            CarouselColumn: The generated carousel column.
        """

        texts: list[str] = []
        actions: list[Action] = []

        if superior := organization.superior:
            texts.append(f"上級單位: {superior}")

        if website := organization.website:
            texts.append(f"網站網址: {website}")

            actions.append(
                URIAction(
                    label="查看網站",
                    uri=website,
                )
            )

        actions.append(
            PostbackAction(
                label="查看成員",
                displayText=f"搜尋 {organization.name} 的成員",
                data=f"查看成員{self.split_char}{organization.name}",
            )
        )

        default_action = (
            URIAction(label="搜尋連結", uri=organization.search_url)
            if organization.search_url
            else None
        )

        return CarouselColumn(
            title=organization.name,
            text=text if len(text := "\n".join(texts)) <= 60 else text[:59] + "…",
            defaultAction=default_action,
            actions=actions,
        )

    def __generate_contact_templates(
        self,
        contacts: Sequence[Contact],
        depth: bool = False,
    ) -> list[CarouselTemplate]:
        """
        Generate contact templates based on the provided contacts and depth flag.

        Parameters:
            contacts (Sequence[Contact]): The list of contacts to generate templates for.
            depth (bool, optional): Flag to indicate whether to include depth. Defaults to False.

        Returns:
            list[CarouselTemplate]: The list of generated carousel templates.
        """

        contacts = sorted(contacts, key=lambda c: isinstance(c, Organization))[:50]

        templates: list[CarouselTemplate] = []
        for contact_group in partition(contacts, 10):
            items: list[CarouselColumn] = []
            for contact in contact_group:
                if isinstance(contact, Individual):
                    items.append(
                        self.__generate_individual_carousel_column(contact, depth)
                    )

                if isinstance(contact, Organization):
                    items.append(self.__generate_organization_carousel_column(contact))

            max_action_cnt = max(len(i.actions) for i in items)
            for i in items:
                while len(i.actions) < max_action_cnt:
                    i.actions.append(EMPTY_POSTBACK_ACTION)

            templates.append(CarouselTemplate(columns=items))

        return templates


CONTACT_BOT = ContactBot()
