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

__author__ = "Paolo Emilio Serra - paolo.serra@autodesk.com"
__copyright__ = "2024"
__version__ = "1.0.0"

import logging
from typing import Any

import reflex as rx
import urllib
import aps
from shared_reflex_viewer import styles

from shared_reflex_viewer.document_viewer import viewer


token = aps.token


class State(rx.State):
    aps_token: str = rx.LocalStorage("{}", name="aps_token")
    urn: str = ''
    model: str = 'STR'

    models: list[tuple[str, str]] = [
        ('STR', 'dXJuOmFkc2sud2lwcHJvZDpmcy5maWxlOnZmLm1xNV9mVlJGUjV1SU1Cd29sUHNNLXc_dmVyc2lvbj0x'),
        ('MEP', 'dXJuOmFkc2sud2lwcHJvZDpmcy5maWxlOnZmLmh5MElubDV6VHA2dGEzUGxOUDlwTEE_dmVyc2lvbj0x')
    ]

    def login(self):
        global token
        fp = self.router.page.full_raw_path
        parsed = urllib.parse.urlparse(fp)
        if len(parsed.query) == 0:
            return
        code = urllib.parse.parse_qs(parsed.query).get("code", [""])[0]
        if len(code) > 0:
            if not aps.is_token_valid():
                token = aps.get_3_legged_token(("data:read",), code)
        self.aps_token = repr(token)

    @rx.var
    def access(self) -> str:
        global token
        return token.Access if token.Access is not None else ''

    @rx.var
    def expires(self) -> str:
        global token
        return str(token.Expires)

    def set_urn(self, e: str):
        self.urn = e


def create_viewer_old(urn: str) -> rx.Component:
    global token

    return rx.script(
        """
        var viewer;
        var md_ViewerDocument;
        var md_viewables;

        function DisplayViewer() {

            var options = {
                env: 'AutodeskProduction2',
                api: 'streamingV2',
                getAccessToken: function(onTokenReady) {
                    onTokenReady("%s", %s);
                }
            }

            <!-- This is called when the page is loaded-->
            Autodesk.Viewing.Initializer(options, function() {

                var htmlDiv = document.getElementById('apsViewer_old');
                viewer = new Autodesk.Viewing.GuiViewer3D(htmlDiv);
                var startedCode = viewer.start();

                if (startedCode > 0) {
                    console.error('Failed to create a Viewer: WebGL not supported.');
                    return;
                }

                console.log('Initialization complete, loading a model next...');

            });

            var documentId = 'urn:' + '%s'; // Add the string 'urn:' to the actual URN value
            Autodesk.Viewing.Document.load(documentId, onDocumentLoadSuccess, onDocumentLoadFailure);
        };

        function onDocumentLoadSuccess(viewerDocument) {

            var viewerapp = viewerDocument.getRoot();

            md_ViewerDocument=viewerDocument; // Hold the viewerDocument in a global variable so that we can access it within SelectViewable()
            md_viewables = viewerapp.search({'type':'geometry'});

            if (md_viewables.length === 0) {
                console.error('Document contains no viewables.');
                return;
            }

            viewer.loadDocumentNode(viewerDocument, md_viewables[0]);
        }

        function onDocumentLoadFailure() {
            console.error('Failed fetching manifest');
        }
        """
        % (token.Access, str(token.Expires), urn),
        on_ready=rx.call_script("DisplayViewer();"),
     )


def create_viewer() -> rx.Component:
    global token
    return viewer(
        name='apsViewer',
        access=State.access,
        expires=State.expires,
        urn=State.urn,
        width="100%",
        height="600px",
    )


def menu_button() -> rx.Component:
    """The menu button on the top right of the page.

    Returns:
        The menu button component.
    """
    return rx.chakra.box(
        rx.chakra.menu(
            rx.chakra.menu_button(
                rx.chakra.icon(
                    tag="hamburger",
                    size=40,
                    color=styles.dark_slate,
                    stroke_width=1,
                ),
            ),
            rx.chakra.menu_list(
                rx.chakra.menu_item(
                    rx.chakra.text('Log In'),
                    on_click=rx.redirect(aps.get_code_address(('data:read', )), external=False)
                ),
                rx.chakra.menu_divider(),
                rx.chakra.menu_item(
                    rx.chakra.text('Copyright Autodesk, Inc. © 2024'),
                ),
            ),
        ),
        position="fixed",
        right="1.5em",
        top="1.5em",
        z_index="500",
    )


def get_style_sheet() -> rx.Component:
    return rx.html('<link rel="stylesheet" href="https://developer.api.autodesk.com/modelderivative/v2/viewers/7.*/style.min.css" type="text/css">')


def index() -> rx.Component:
    global token
    return rx.chakra.vstack(
        rx.script(
            src="https://developer.api.autodesk.com/viewingservice/v2/viewers/three.min.js",
            strategy="beforeInteractive",
        ),
        rx.script(
            src="https://developer.api.autodesk.com/derivativeservice/v2/viewers/7.*/viewer3D.min.js",
            strategy="beforeInteractive",
        ),
        get_style_sheet(),
        rx.fragment(
            rx.chakra.heading("APS Viewer", font_size="2em"),
            rx.select.root(
                rx.select.trigger(placeholder='Select Model'),
                rx.select.content(
                    rx.select.group(
                        rx.foreach(
                            State.models,
                            lambda x: rx.select.item(x[0], value=x[1])
                        )
                    )
                ),
                on_change=State.set_urn,
            ),
            menu_button(),
        ),
        create_viewer(),
        on_mount=State.login,
    )


# Create app instance and add index page.
app = rx.App()
app.add_page(index, route='/', description='Autodesk Consulting', title='APS Viewer')
