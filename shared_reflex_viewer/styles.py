# coding: utf-8
# Author: paolo.serra@autodesk.com
# Copyright (c) 2024 Autodesk, Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License").
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.  See the License for the specific language governing
# permissions and limitations under the License.

__author__ = 'Paolo Emilio Serra - paolo.serra@autodesk.com'
__copyright__ = '2024'
__version__ = '1.0.0'


import reflex as rx

black = 'rgb(0, 0, 0)'
white = 'rgb(255, 255, 255)'
light_slate = 'rgb(204, 204, 204)'
dark_slate = 'rgb(102, 102, 102)'
clay = 'rgb(215, 78, 38)'
plant = 'rgb(43, 194, 117)'
iris = 'rgb(95, 96, 255)'
gold = 'rgb(255, 194, 26)'

# FONT
font_element = "Artifakt"
font_title = "Artifakt Legend"

fonts = [
    {'font-family': 'Artifakt',
     'font-style': 'normal',
     'font-weight': 300,
     'src': ['url( https://swc.autodesk.com/pharmacopeia/fonts/ArtifaktElement/v1.0/WOFF2/Artifakt%20Element%20Light.woff2) format("woff2")',
             'url( https://swc.autodesk.com/pharmacopeia/fonts/ArtifaktElement/v1.0/WOFF/Artifakt%20Element%20Light.woff) format("woff")',
             'url( https://swc.autodesk.com/pharmacopeia/fonts/ArtifaktElement/v1.0/TTF/Artifakt%20Element%20Light.ttf) format("truetype")',
             'url( https://swc.autodesk.com/pharmacopeia/fonts/ArtifaktElement/v1.0/WOFF2/Artifakt%20Element%20Bold.woff2) format("woff2")',
             'url( https://swc.autodesk.com/pharmacopeia/fonts/ArtifaktElement/v1.0/WOFF/Artifakt%20Element%20Bold.woff) format("woff")',
             'url( https://swc.autodesk.com/pharmacopeia/fonts/ArtifaktElement/v1.0/TTF/Artifakt%20Element%20Bold.ttf) format("truetype")'
             ]
     }
]


border_radius = "0.375rem"
box_shadow = f"0px 0px 0px 1px {light_slate}"
border = f"1px solid {light_slate}"
text_color = "black"
accent_text_color = f"{iris}"
accent_color = f"linear-gradient(45deg, rgba(255, 255, 255, 1) 10%, {iris} 200%)"
hover = {"_hover": {"bg": accent_color}}
hover_accent_color = {"_hover": {"color": accent_color}}
hover_accent_bg = {"_hover": {"bg": accent_color}}
content_width_vw = "90vw"
sidebar_width = "20em"

template_page_style = {"padding_top": "5em", "padding_x": ["auto", "2em"], "flex": "1", '@font-face': fonts, 'font-family': font_element}

template_content_style = {
    "align_items": "flex-start",
    "box_shadow": box_shadow,
    "border_radius": border_radius,
    "padding": "1em",
    "margin_bottom": "2em",
    '@font-face': fonts,
    'font-family': font_element,
}

link_style = {
    "color": text_color,
    "text_decoration": "none",
    **hover,
}

overlapping_button_style = {
    "background_color": "white",
    "border": border,
    "border_radius": border_radius,
}

base_style = {
    rx.chakra.MenuButton: {
        "width": "3em",
        "height": "3em",
        **overlapping_button_style,
    },
    rx.chakra.MenuItem: hover,
}

markdown_style = {
    "code": lambda text: rx.code(text, color="#1F1944", bg="#EAE4FD"),
    "a": lambda text, **props: rx.link(
        text,
        **props,
        font_weight="bold",
        color="#03030B",
        text_decoration="underline",
        text_decoration_color="#AD9BF8",
        _hover={
            "color": "#AD9BF8",
            "text_decoration": "underline",
            "text_decoration_color": "#03030B",
        },
    ),
}

