import React from 'react';


class Viewer extends React.Component {
  constructor(props) {
    super(props);
    this.viewer = null;
    this.md_ViewerDocument = null;
    this.md_viewables = null;
    // this.state = {urn: props.urn, access: props.access, expires: props.expires}
  }

  componentDidMount() {
      this.initializeViewer();
  }

  componentWillUnmount() {
    this.setState({urn: '', access: '', expires: ''});
    if (this.viewer != null){
        this.viewer.finish();
        this.viewer = null;
        this.md_ViewerDocument = null;
        this.md_viewables = null;
        Autodesk.Viewing.shutdown();
    }
  }

  componentDidUpdate(prevProps) {
    if (!this.viewer) {
        if (this.props.urn !== '') {
            this.initializeViewer();
        }
      return;
    }
    const { urn, access, expires } = this.props;
    if (prevProps.urn !== urn || prevProps.access != access || prevProps.expires != expires) {
      this.changeDocument();
      return;
    }
  }

  initializeViewer = () => {
    var options = {
          env: 'AutodeskProduction2',
          api: 'streamingV2',
          getAccessToken: (onTokenReady) => {
            onTokenReady(this.props.access, this.props.expires);
          }
        };

    Autodesk.Viewing.Initializer(options, () => {
      if (this.props.urn === '') {
        return;
      }
      var htmlDiv = document.getElementById(this.props.name);
      this.viewer = new Autodesk.Viewing.GuiViewer3D(htmlDiv);
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

  changeDocument = (e) => {
    if (this.md_ViewerDocument !== null){
        if(this.md_ViewerDocument.getRoot().urn(false) !== this.props.urn) {
            var documentId = 'urn:' + this.props.urn;
            this.md_ViewerDocument = documentId;
            Autodesk.Viewing.Document.load(documentId, this.onDocumentLoadSuccess, this.onDocumentLoadFailure);
            this.viewer.run();
        }
    } else {
       this.initializeViewer();
    }
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
