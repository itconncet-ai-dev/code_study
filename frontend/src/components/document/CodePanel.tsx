import { useRef, useEffect } from 'react'
import Editor from '@monaco-editor/react'
import type { editor } from 'monaco-editor'

interface CodePanelProps {
  code: string
  language: string
  highlightedLines?: number[]
  onScroll?: (scrollTop: number) => void
}

/**
 * CodePanel component displays syntax-highlighted code with line numbers.
 * Features:
 * - Monaco Editor for professional syntax highlighting
 * - Line numbers displayed by default
 * - Read-only mode (no editing)
 * - Optional line highlighting for synchronized scrolling
 * - Scroll event callback for synchronization with ExplanationPanel
 */
export function CodePanel({ code, language, highlightedLines = [], onScroll }: CodePanelProps) {
  const editorRef = useRef<editor.IStandaloneCodeEditor | null>(null)

  /**
   * Handle editor mount
   */
  function handleEditorDidMount(editor: editor.IStandaloneCodeEditor) {
    editorRef.current = editor

    // Setup scroll listener for synchronization
    if (onScroll) {
      editor.onDidScrollChange((e) => {
        onScroll(e.scrollTop)
      })
    }
  }

  /**
   * Apply line highlighting decorations when highlighted lines change
   */
  useEffect(() => {
    if (!editorRef.current || highlightedLines.length === 0) {
      return
    }

    const decorations = highlightedLines.map((lineNumber) => ({
      range: {
        startLineNumber: lineNumber,
        startColumn: 1,
        endLineNumber: lineNumber,
        endColumn: 1,
      },
      options: {
        isWholeLine: true,
        className: 'highlighted-line',
        glyphMarginClassName: 'highlighted-line-glyph',
      },
    }))

    const decorationIds = editorRef.current.deltaDecorations([], decorations)

    return () => {
      if (editorRef.current) {
        editorRef.current.deltaDecorations(decorationIds, [])
      }
    }
  }, [highlightedLines])

  return (
    <div className="h-full flex flex-col bg-white border-r border-gray-200">
      <div className="px-4 py-3 bg-gray-50 border-b border-gray-200">
        <h2 className="text-sm font-semibold text-gray-700">코드</h2>
      </div>
      <div className="flex-1 overflow-hidden">
        <Editor
          height="100%"
          language={language}
          value={code}
          theme="vs-light"
          onMount={handleEditorDidMount}
          options={{
            readOnly: true,
            minimap: { enabled: false },
            scrollBeyondLastLine: false,
            lineNumbers: 'on',
            glyphMargin: true,
            folding: false,
            lineDecorationsWidth: 10,
            lineNumbersMinChars: 3,
            renderLineHighlight: 'none',
            scrollbar: {
              vertical: 'visible',
              horizontal: 'visible',
              useShadows: false,
              verticalScrollbarSize: 10,
              horizontalScrollbarSize: 10,
            },
            fontSize: 14,
            fontFamily: '"Fira Code", "Consolas", "Monaco", monospace',
          }}
        />
      </div>
    </div>
  )
}
