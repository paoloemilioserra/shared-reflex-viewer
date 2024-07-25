from __future__ import annotations
import logging
import pathlib
import pprint
from copy import copy

import reflex as rx

import api.crud.objects
import autodesk.consulting.aps.data_management
from reflex_weave_mui import *
from reflex_weave_mui.icon import NAMES_MAP, ICON_NAMES
from reflex_weave_mui.tree import ResourceType
from components import styles
from components import utils


class TreeWeaveState(rx.State):
    resources: dict[str, list[ResourceType]] = {}
    project_id: str = '<xxxxx>'
    root_id: str = ''
    data: dict[str, ResourceType] = {}

    async def get_project_files_folder(self):
        if self.project_id == '':
            return
        with rx.session() as db:
            try:
                project = await api.crud.objects.project.get_item(db, acc_id=self.project_id)
                self.data = {
                    project.root_folder: ResourceType(
                        id=project.root_folder,
                        name='Project Files',
                        paretn=None,
                        is_folder=True,
                        is_loading=True,
                        children=[]
                    )
                }
            except:
                return

    def handle_on_node_select(self, oid):
        parent = self.data[oid]
        if parent.is_folder and parent.is_loading:
            for k, v in autodesk.consulting.aps.data_management.get_folder_maps(project_id=self.project_id, folder_id=oid).items():
                if k not in self.data:
                    data = {
                        k: ResourceType(
                            id=k,
                            name=v['name'],
                            parent=oid,
                            is_folder=True,
                            is_loading=True,
                            children=[]
                        )
                    }
                    self.data.update(data)
                    parent.children.append(k)
            for k, v in autodesk.consulting.aps.data_management.get_items_maps(project_id=self.project_id, folder_id=oid).items():
                if k not in self.data:
                    data = {
                        k: ResourceType(
                            id=k,
                            name=v['name'],
                            parent=oid,
                            is_folder=False,
                            is_loading=False,
                            children=[]
                        )
                    }
                    self.data.update(data)
                    parent.children.append(k)
            parent.is_loading = False
            # group the folders first and then the files and sort alphabetically
            sorted_children_ids = sorted([i for i in parent.children if self.data[i].is_folder], key=lambda d: self.data[d].name)
            sorted_children_ids.extend(sorted([i for i in parent.children if not self.data[i].is_folder], key=lambda d: self.data[d].name))
            parent.children = sorted_children_ids


def example(name: str, component: rx.Component) -> rx.Component:
    return stack(
        text(name),
        container(
            component,
        ),
        divider(orientation=divider.orientation.HORIZONTAL, variant=divider.variant.FULLWIDTH),
        spacing='0.5em'
    )


def render_tree():
    return tree(
        folder_tree=True,
        root_id='xxxxx',  # TreeWeaveState.root_id,
        data=TreeWeaveState.data,
        on_node_select=TreeWeaveState.handle_on_node_select,
    )


@rx.page(route='/tree', title='Recursive tree')
def index() -> rx.Component:
    return container(
        example(
            'Autodesk Docs folder tree',
            render_tree()
        ),
        example(
            'Root ID',
            text(TreeWeaveState.root_id)
        ),
        on_mount=TreeWeaveState.get_project_files_folder
    )
