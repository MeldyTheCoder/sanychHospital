import typing
from typing import Callable, Any

import flet as ft
import pydantic

type RowAction = tuple[ft.Control | str, [Callable[[type[pydantic.BaseModel]], typing.Any]]]


class PydanticTable(ft.UserControl):
    def __init__(self,
                 columns_by_keys: dict[str, str],
                 dataset: list[pydantic.BaseModel],
                 displays: dict[str, Callable[[Any], str | int]] = None,
                 actions: list[RowAction] = None,
                 ):
        super().__init__()
        self._columns_by_keys = columns_by_keys
        self._displays = displays or {}
        self._actions = actions or []
        self._dataset: list[pydantic.BaseModel] = dataset

    def build(self):
        columns = [
            ft.DataColumn(
                label=ft.Text(
                    value=value,
                ),
                tooltip=value,
            ) for _, value in self._columns_by_keys.items()
        ]

        rows = [
            ft.DataRow(
                cells=[
                    ft.DataCell(
                        content=ft.Text(
                            value=getattr(item, key) if not self._displays.get(key) else self._displays[key](getattr(item, key))
                        )
                    ) for key in self._columns_by_keys.keys()
                ] + [
                    ft.DataCell(
                        content=ft.PopupMenuButton(
                            items=[
                                ft.PopupMenuItem(
                                    text=action[0],
                                    on_click=lambda *_, record=item, cb=action[1]: cb(record),
                                ) for action in self._actions
                            ]
                        )
                    ) if self._actions else ft.Container()
                ]
            ) for item in self._dataset
        ]

        if self._actions:
            columns.append(
                ft.DataColumn(
                    label=ft.Text("Действие"),
                    tooltip='Действие',
                )
            )

        table = ft.DataTable(
            columns=columns,
            rows=rows
        )
        self._content = table
        return self._content
