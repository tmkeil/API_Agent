import { Component, type ErrorInfo, type ReactNode } from 'react'

interface Props {
  children: ReactNode
}

interface State {
  hasError: boolean
  error: Error | null
}

export default class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error('ErrorBoundary caught:', error, info.componentStack)
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-slate-100">
          <div className="bg-white shadow-lg rounded-lg p-8 w-full max-w-md border border-red-200">
            <h1 className="text-lg font-semibold text-red-700 mb-2">
              Unerwarteter Fehler
            </h1>
            <p className="text-sm text-slate-600 mb-4">
              {this.state.error?.message || 'Ein unbekannter Fehler ist aufgetreten.'}
            </p>
            <button
              onClick={() => {
                this.setState({ hasError: false, error: null })
                window.location.href = '/'
              }}
              className="bg-indigo-600 text-white px-4 py-2 rounded text-sm font-medium hover:bg-indigo-700 transition-colors"
            >
              Zur Startseite
            </button>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}
