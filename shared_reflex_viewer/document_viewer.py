import reflex as rx


class Viewer(rx.NoSSRComponent):

    library = "../public/viewer.js"
    tag = "Viewer"
    is_default = True

    name: rx.Var[str] = "apsViewer"
    access: rx.Var[str]
    expires: rx.Var[str]
    urn: rx.Var[str]
    width: rx.Var[str] = "100%"
    height: rx.Var[str] = "600px"
    position: rx.Var[str] = 'relative'


viewer = Viewer.create
