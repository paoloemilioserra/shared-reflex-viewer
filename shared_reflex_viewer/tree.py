from reflex import Var
from reflex.vars import ComputedVar

from .base_component import WeaveMuiComponent
import reflex as rx
from typing import Union, Any, Optional, Literal
from reflex.utils import imports
from .icon import SvgIcon, ICONS_MAP
from .libraries import WeaveMUI
from .progress import circular_progress


class ResourceType(rx.Base):
    name: str = ''
    id: str = ''
    parent: str | None = None
    is_folder: bool = False
    is_loading: bool = False
    children: list[str] = []


class TreeView(rx.Component):
    library = WeaveMUI.tree_view  # '@weave-mui/tree-view@../local_modules/tree-view-1.0.10.tgz'

    lib_dependencies: list[str] = [
        WeaveMUI.enums,
        WeaveMUI.icons_weave,
        WeaveMUI.styled
        # '@weave-mui/enums@../local_modules/enums-1.0.6.tgz',
        # '@weave-mui/icons-weave@../local_modules/icons-weave-1.0.5.tgz',
        # '@weave-mui/styled@../local_modules/styled-1.0.5.tgz',
    ]

    tag = 'TreeView'

    # is_default = True

    striped_background: Optional[rx.Var[bool]] = None

    indicator: Optional[rx.Var[Literal['caret', 'operator']]] = None

    # The ref object that allows Tree View manipulation. Can be instantiated with useTreeViewApiRef().
    # api_ref: Optional[rx.Var[Any]] = None  # v7

    # If true, the tree view renders a checkbox at the left of its label that allows selecting it.
    # checkbox_selection: Optional[rx.Var[bool]] = None  # v7

    # Expanded item ids. Used when the item's expansion is not controlled.
    # default_expanded_items: Optional[rx.Var[list[str]]] = None  # v7

    default_expanded: Optional[rx.Var[list[str]]] = None  # v6

    default_expand_icon: Optional[rx.Var[rx.Component]] = None  # v6

    default_parent_icon: Optional[rx.Var[rx.Component]] = None  # v6

    # Selected item ids. (Uncontrolled) When multiSelect is true this takes an array of strings; when false (default) a string.
    # default_selected_items: Optional[rx.Var[list[Any]]] = None  # v7

    default_selected: Optional[rx.Var[list[str]]] = None

    disabled_items_focusable: Optional[rx.Var[bool]] = None

    disable_selection: Optional[rx.Var[bool]] = None

    # expanded_items: Optional[rx.Var[list[str]]] = None  # v7

    expanded: Optional[rx.Var[list[str]]] = None  # v6

    # expansion_trigger: Optional[rx.Var[Literal['content', 'iconContainer']]] = None  # v7

    id: Optional[rx.Var[str]] = None

    # Horizontal indentation between an item and its children. Examples: 24, "24px", "2rem", "2em".
    # item_children_indentation: Optional[rx.Var[Union[str, int]]] = None  # v7

    # If true, ctrl and shift will trigger multiselect.
    multi_select: Optional[rx.Var[bool]] = None

    # Callback fired when tree items are expanded/collapsed.
    # on_expanded_items_change: rx.EventHandler[lambda event, item_ids: [item_ids]]  # v7

    # Callback fired when a tree item is expanded or collapsed.
    # on_item_expansion_toggle: rx.EventHandler[lambda event, item_id, is_expanded: [item_id, is_expanded]]  # v7

    # Callback fired when tree items are focused.
    # on_item_focus: rx.EventHandler[lambda event, item_id, value: [item_id, value]]  # v7

    # Callback fired when a tree item is selected or deselected.
    # on_item_selection_toggle: rx.EventHandler[lambda event, item_id, is_selected: [item_id, is_selected]]  # v7

    # Callback fired when tree items are selected/deselected.
    # on_selected_items_change: rx.EventHandler[lambda event, item_ids: [item_ids]]  # v7

    on_node_focus: rx.EventHandler[lambda event, node_id, value: [node_id, value]]  # v6

    on_node_select: rx.EventHandler[lambda event, node_ids: [node_ids]]  # v6

    on_node_toggle: rx.EventHandler[lambda event, node_ids: [node_ids]]  # v6

    # Selected item ids. (Controlled) When multiSelect is true this takes an array of strings; when false (default) a string.
    # selected_items: Optional[rx.Var[Union[str, list[str]]]] = None  # v7

    # root_id: Optional[rx.Var[str]] = None  # custom added to support the creation of folder structures

    # data: Optional[rx.Var[dict[str, ResourceType]]] = None  # custom added to support the creation of folder structures

    selected: Optional[rx.Var[Any]] = None

    # The props used for each component slot.
    # slot_props: Optional[rx.Var[dict[str, Any]]] = None  # v7

    # Overridable component slots.
    # slots: Optional[rx.Var[dict[str, Any]]] = None  # v7

    # def _get_imports(self) -> imports.ImportDict:
    #     return {
    #         **super()._get_imports(),
    #         '@mui/x-tree-view': [
    #             rx.ImportVar(tag='useTreeView', is_default=False)
    #         ]
    #     }

    # def add_hooks(self) -> list[str | Var]:
    #     return [
    #         rx.Var.create('const apiRef = useTreeView;', _var_is_local=True, _var_is_string=False)
    #     ]

    # @classmethod
    # def create(cls, *children, **props):
    #     api_ref = props.pop('api_ref', rx.Var.create('useTreeView', _var_is_local=False, _var_is_string=False))
    #     return super().create(
    #         *children,
    #         api_ref=api_ref,
    #         **props
    #     )

    def add_hooks(self) -> list[str | Var]:
        root_id = f'const root_id = "{self.root_id}";'
        state_data = f'const stateData = {self.__getstate__()}.data;'
        root = Var.create_safe(
            f'const root = stateData[root_id];',
            _var_is_local=True,
            _var_is_string=False,
            _var_data=rx.vars.VarData(
                imports={
                    "@weave-mui/circular-progress": [
                        rx.utils.imports.ImportVar(tag="CircularProgress")
                    ],
                    "@weave-mui/icons-weave": [
                        rx.utils.imports.ImportVar(tag="FolderS"),
                        rx.utils.imports.ImportVar(tag="FileGenericS")
                    ],
                    "@weave-mui/tree-item": [
                        rx.utils.imports.ImportVar(tag="TreeItem"),
                    ],
                },
            ),
        )

        return [
            root_id,
            state_data,
            root,
            """            
const TreeRender = oid => {

    const data = stateData[oid];
    const labelIcon = data.is_folder ? <FolderS/> : <FileGenericS/>;
    const isChildren = data.children !== null;
    const isLoading = data.is_loading;

    if (isChildren) {
        if(isLoading){
            return (
            <TreeItem nodeId={data.id} labelText={data.name} labelIcon={labelIcon} guidelines>
                <CircularProgress variant={`indeterminate`} size={`XS`} sx={{"margin": "8px"}}/>
            </TreeItem>
            );
        }
    return (
        <TreeItem nodeId={data.id} labelText={data.name} labelIcon={labelIcon} guidelines>
            {data.children !== undefined && data.children.map((node, idx) => TreeRender(node))}
        </TreeItem>
        );
    }

    return <TreeItem nodeId={data.id} labelText={data.name} labelIcon={labelIcon} guidelines></TreeItem>
};

const RenderRootNode = node => {
    const isLoading = node.is_loading;
    if(isLoading) {
        return (
            <TreeItem nodeId={node.id} labelText={node.name} labelIcon={<FolderS/>} guidelines rootNode>
                <CircularProgress variant={`indeterminate`} size={`XS`} sx={{"margin": "8px"}}/>
            </TreeItem>
            );
       }
      return (
        <TreeItem nodeId={node.id} labelText={node.name} labelIcon={<FolderS/>} guidelines rootNode>
            {node.children !== undefined && node.children.map((c, idx) => TreeRender(c))}
        </TreeItem>
        );
}
"""
        ]

    @classmethod
    def create(cls, *children, **props):
        folder_tree: bool = props.pop('folder_tree', False)
        on_node_select = props.pop('on_node_select', None)
        multi_select = props.pop('multi_select', False)

        # cls.add_var(
        #     'root_id',
        #     type_=str,
        #     default_value=props.pop("root_id", "")
        # )
        # cls.add_var(
        #     'stateData',
        #     type_=dict[str, ResourceType],
        #     default_value=props.pop("data", {})
        # )

        if folder_tree:
            return super().create(
                rx.Var.create('RenderRootNode(root)', _var_is_string=False, _var_is_local=False),
                on_node_select=on_node_select,
                multi_select=multi_select,
                **props
            )
        return super().create(
            *children,
            **props
        )


class TreeItem(rx.Component):
    library = WeaveMUI.tree_item  # '@weave-mui/tree-item@../local_modules/tree-item-1.0.9.tgz'

    lib_dependencies: list[str] = [
        WeaveMUI.styled,
        WeaveMUI.typography
        # '@weave-mui/styled@../local_modules/styled-1.0.5.tgz',
        # '@weave-mui/typography@../local_modules/typography-1.0.7.tgz',
    ]

    tag = 'TreeItem'

    # prop that helps us to know which is the root element of the tree
    root_node: Optional[rx.Var[bool]] = None

    # When the prop is set to true, the guidelines will be displayed.
    guidelines: Optional[rx.Var[bool]] = None

    # prop to add an icon in the TreeItem content
    label_icon: Optional[rx.Component] = None

    # prop to add text to the TreeItem content
    label_text: rx.Var[Any] = None

    # The id of the item.
    node_id: rx.Var[str] = None

    # The component used to render the content of the item.
    content_component: Optional[rx.Var[rx.Component]] = None

    # Props applied to ContentComponent.
    content_props: Optional[rx.Var[dict[str, Any]]] = None

    # If true, the item is disabled.
    disabled: Optional[rx.Var[bool]] = None

    # The tree item label.
    label: Optional[rx.Var[rx.Component]] = None

    # on_focus

    # The props used for each component slot.
    slot_props: Optional[rx.Var[dict[str, Any]]] = None

    # Overridable component slots.
    slots: Optional[rx.Var[dict[str, rx.Component]]] = None

    @classmethod
    def create(cls, *children, **props):
        label_icon = props.pop('label_icon', None)
        if label_icon is not None:
            if isinstance(label_icon, str):
                try:
                    label_icon = ICONS_MAP[label_icon]
                except:
                    pass
            elif isinstance(label_icon, rx.Component):
                label_icon = label_icon
            elif isinstance(label_icon, rx.Var):
                try:
                    label_icon = ICONS_MAP[label_icon]
                except:
                    label_icon = None
            else:
                label_icon = None
        props['label_icon'] = label_icon
        return super().create(
            *children,
            **props
        )


class TreeSpace(rx.components.component.ComponentNamespace):
    __call__ = TreeView.create
    item = staticmethod(TreeItem.create)


tree = TreeSpace()


class FolderTreeState(rx.ComponentState):

    @classmethod
    def get_component(cls, *children, **props) -> rx.Component:
        on_node_select = props.pop('on_node_select', None)
        multi_select = props.pop('multi_select', False)

        return tree(
            folder_tree=True,
            on_node_select=on_node_select,
            multi_select=multi_select,
            **props
        )


folder_tree = FolderTreeState.create


