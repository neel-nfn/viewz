import { Component } from "react";

export default class ErrorBoundary extends Component {
  constructor(props){ super(props); this.state = { hasError: false, err: null }; }
  static getDerivedStateFromError(error){ return { hasError: true, err: error }; }
  componentDidCatch(error, info){ /* no-op */ }
  render(){
    if(this.state.hasError){
      return (
        <div style={{padding:"2rem"}}>
          <h1 style={{fontSize:"1.25rem",fontWeight:600,marginBottom:"0.5rem"}}>Something went wrong.</h1>
          <p style={{opacity:0.8}}>Try refreshing the page. If this keeps happening, check console for details.</p>
        </div>
      );
    }
    return this.props.children;
  }
}
