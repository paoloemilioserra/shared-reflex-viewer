import React from 'react';

const { Autodesk } = window;

class Viewer extends React.Component {
  constructor(props) {
    super(props);
    this.viewer = null;
    this.md_ViewerDocument = null;
    this.md_viewables = null;
  }

  componentDidMount() {
    this.initializeViewer();
  }

  initializeViewer = () => {
    var options = {
      env: 'AutodeskProduction2',
      api: 'streamingV2',
      getAccessToken: (onTokenReady) => {
        onTokenReady(this.props.access_token, this.props.expires);
      }
    };

    window.Autodesk.Viewing.Initializer(options, () => {
      var htmlDiv = document.getElementById(this.props.name);
      this.viewer = new window.Autodesk.Viewing.GuiViewer3D(htmlDiv);
      var startedCode = this.viewer.start();
      if (startedCode > 0) {
        console.error('Failed to create a Viewer: WebGL not supported.');
        return;
      }
      console.log('Initialization complete, loading a model next...');

      var documentId = 'urn:' + this.props.urn;
      Autodesk.Viewing.Document.load(documentId, this.onDocumentLoadSuccess, this.onDocumentLoadFailure);
    });
  };

  onDocumentLoadSuccess = (viewerDocument) => {
    var viewerapp = viewerDocument.getRoot();
    this.md_ViewerDocument = viewerDocument;
    this.md_viewables = viewerapp.search({ 'type': 'geometry' });
    if (this.md_viewables.length === 0) {
      console.error('Document contains no viewables.');
      return;
    }
    this.viewer.loadDocumentNode(viewerDocument, this.md_viewables[0]);
  };

  onDocumentLoadFailure = () => {
    console.error('Failed fetching manifest');
  };

  render() {
    const n = this.props.name;
    const w = this.props.width;
    const h = this.props.height;
    const p = this.props.position;
    return <div id={n} position={p} style={{width: w, height: h}}></div>;
  }
}

export default React.forwardRef((props, ref) => <Viewer {...props} innerRef={ref} />);