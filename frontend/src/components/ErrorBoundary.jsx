import { Component } from "react";

export default class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, err: null };
  }

  static getDerivedStateFromError(err) {
    return { hasError: true, err };
  }

  componentDidCatch(err, info) {
    console.error("Route error", err, info);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="p-8">
          <h1 className="text-2xl font-bold mb-2">Something went wrong</h1>
          <p className="mb-4 text-sm opacity-80">{String(this.state.err || "")}</p>
          <a className="btn btn-primary" href="/settings/channels">Go to Channels</a>
        </div>
      );
    }
    return this.props.children;
  }
}

