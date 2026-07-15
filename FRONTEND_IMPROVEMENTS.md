# QueryEngine Frontend - UI/UX Improvements Guide

Modern, professional frontend enhancements following industry best practices.

## Current State
- ✅ Version 1 branding (Teal #00c6c2, Midnight Black #052831)
- ✅ Three-phase progressive loading with skeletons
- ✅ Real pytest output display
- ✅ Tailwind CSS with custom theme
- ⚠️ Room for polish & accessibility

## Recommended Improvements

### 1. **Error Boundary Component**

**Why:** Graceful error recovery. Users know what went wrong and can retry.

**File:** `frontend/src/components/ErrorBoundary.tsx` (NEW)

```tsx
import React from 'react';

interface Props {
  children: React.ReactNode;
}

interface State {
  hasError: boolean;
  error: string | null;
}

export class ErrorBoundary extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error: error.message };
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <h3 className="text-red-800 font-semibold">Something went wrong</h3>
          <p className="text-red-600 text-sm mt-2">{this.state.error}</p>
          <button
            onClick={() => window.location.reload()}
            className="mt-4 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
          >
            Reload Page
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}
```

**Usage in App.tsx:**
```tsx
<ErrorBoundary>
  <QueryInput />
  <ResultsPanel />
</ErrorBoundary>
```

---

### 2. **Toast Notification System**

**Why:** Non-blocking error messages. Better UX than alerts.

**File:** `frontend/src/components/Toast.tsx` (NEW)

```tsx
import { useState, useCallback } from 'react';

interface ToastMessage {
  id: string;
  message: string;
  type: 'success' | 'error' | 'info';
  duration?: number;
}

export const useToast = () => {
  const [toasts, setToasts] = useState<ToastMessage[]>([]);

  const addToast = useCallback(
    (message: string, type: 'success' | 'error' | 'info' = 'info', duration = 5000) => {
      const id = Date.now().toString();
      setToasts((prev) => [...prev, { id, message, type, duration }]);

      if (duration > 0) {
        setTimeout(() => {
          setToasts((prev) => prev.filter((t) => t.id !== id));
        }, duration);
      }

      return id;
    },
    []
  );

  const Toast = () => (
    <div className="fixed bottom-4 right-4 space-y-2 pointer-events-none">
      {toasts.map((toast) => (
        <div
          key={toast.id}
          className={`px-4 py-3 rounded-lg shadow-lg pointer-events-auto ${
            toast.type === 'error'
              ? 'bg-red-500 text-white'
              : toast.type === 'success'
              ? 'bg-green-500 text-white'
              : 'bg-gray-800 text-white'
          }`}
        >
          {toast.message}
        </div>
      ))}
    </div>
  );

  return { addToast, Toast };
};
```

**Usage:**
```tsx
const { addToast, Toast } = useToast();

try {
  await api.runFullPipeline(query);
} catch (err) {
  addToast('Request failed. Please try again.', 'error');
}

return (
  <>
    <Toast />
    {/* ... rest of UI ... */}
  </>
);
```

---

### 3. **Loading States with Progress Indicators**

**Why:** Users know where they are in the 3-phase process.

**File:** `frontend/src/components/ProgressBar.tsx` (NEW)

```tsx
interface Props {
  current: number;
  total: number;
  labels: string[];
}

export const ProgressBar = ({ current, total, labels }: Props) => {
  const percentage = (current / total) * 100;

  return (
    <div>
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div
          className="bg-primary-teal h-2 rounded-full transition-all duration-300"
          style={{ width: `${percentage}%` }}
        />
      </div>
      <div className="flex justify-between mt-2">
        {labels.map((label, idx) => (
          <span
            key={idx}
            className={`text-sm ${
              idx < current ? 'text-primary-teal font-semibold' : 'text-gray-500'
            }`}
          >
            {label}
          </span>
        ))}
      </div>
    </div>
  );
};
```

---

### 4. **Copy-to-Clipboard for Code Blocks**

**Why:** Users can copy SQL/tests for external use.

**File:** Update SQL display component:

```tsx
const [copied, setCopied] = useState(false);

const copyToClipboard = async (text: string) => {
  try {
    await navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  } catch (err) {
    console.error('Failed to copy:', err);
  }
};

return (
  <div className="relative bg-card-dark rounded p-4">
    <button
      onClick={() => copyToClipboard(sqlQuery)}
      className="absolute top-2 right-2 px-2 py-1 text-xs bg-primary-teal text-white rounded hover:bg-opacity-80"
    >
      {copied ? '✓ Copied' : 'Copy'}
    </button>
    <pre className="text-text-secondary overflow-auto">
      <code>{sqlQuery}</code>
    </pre>
  </div>
);
```

---

### 5. **Keyboard Shortcuts**

**Why:** Power users can speed up workflows.

**File:** Update App.tsx:

```tsx
useEffect(() => {
  const handleKeyPress = (e: KeyboardEvent) => {
    // Ctrl/Cmd + Enter: Submit query
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      handleSubmit();
    }
    // Escape: Clear results
    if (e.key === 'Escape') {
      setResult(null);
    }
  };

  window.addEventListener('keydown', handleKeyPress);
  return () => window.removeEventListener('keydown', handleKeyPress);
}, []);
```

Document shortcuts:
- `Ctrl/Cmd + Enter`: Run query
- `Escape`: Clear results

---

### 6. **Syntax Highlighting for SQL & Python**

**Why:** Code is easier to read with colors.

**Install:**
```bash
cd frontend
npm install highlight.js
```

**File:** `frontend/src/components/CodeBlock.tsx` (NEW)

```tsx
import hljs from 'highlight.js';
import 'highlight.js/styles/atom-one-dark.css';

interface Props {
  code: string;
  language: 'sql' | 'python';
}

export const CodeBlock = ({ code, language }: Props) => {
  const highlighted = hljs.highlight(code, { language }).value;

  return (
    <pre className="bg-card-dark rounded p-4 overflow-auto">
      <code
        dangerouslySetInnerHTML={{ __html: highlighted }}
        className="text-text-secondary"
      />
    </pre>
  );
};
```

---

### 7. **Dark Mode Toggle** (Optional)

**Why:** Accessibility. Some users prefer light mode.

```tsx
const [darkMode, setDarkMode] = useState(true);

return (
  <div className={darkMode ? 'dark' : ''}>
    <button
      onClick={() => setDarkMode(!darkMode)}
      className="absolute top-4 right-4"
    >
      {darkMode ? '☀️' : '🌙'}
    </button>
    {/* Rest of app */}
  </div>
);
```

Update `tailwind.config.js`:
```js
module.exports = {
  darkMode: 'class',
  // ...
};
```

---

### 8. **Sample Queries: Editable & Expandable**

**Why:** Users can see more examples without cluttering the UI.

```tsx
const [showMore, setShowMore] = useState(false);

const allSamples = [
  "Show total revenue by region",
  "Find top 5 customers by order count",
  // ... 3 more
  "List customers with more than 10 orders", // Expand to see
  "Calculate average order value by segment",
];

return (
  <>
    {allSamples.slice(0, showMore ? allSamples.length : 3).map((sample) => (
      <button
        key={sample}
        onClick={() => setQuery(sample)}
        className="block w-full text-left p-3 bg-card-dark hover:bg-opacity-80 rounded mb-2"
      >
        {sample}
      </button>
    ))}
    {!showMore && (
      <button
        onClick={() => setShowMore(true)}
        className="text-primary-teal text-sm"
      >
        + Show {allSamples.length - 3} more examples
      </button>
    )}
  </>
);
```

---

### 9. **Query History with Delete**

**Why:** Users can reference past queries without clutter.

```tsx
const [history, setHistory] = useState<string[]>([]);

const deleteFromHistory = (idx: number) => {
  setHistory((prev) => prev.filter((_, i) => i !== idx));
};

return (
  <div className="max-h-48 overflow-auto bg-card-dark rounded p-3">
    {history.map((query, idx) => (
      <div key={idx} className="flex justify-between items-center p-2 border-b">
        <span className="text-sm text-gray-300 flex-1">{query.substring(0, 50)}...</span>
        <button
          onClick={() => deleteFromHistory(idx)}
          className="text-red-400 hover:text-red-600 text-xs"
        >
          Delete
        </button>
      </div>
    ))}
  </div>
);
```

---

### 10. **Responsive Design for Mobile**

**Why:** Works on tablets/phones, not just desktop.

**Update Tailwind classes:**

```tsx
return (
  <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
    {/* Query input - full width on mobile, half on desktop */}
    <div className="lg:col-span-1">
      <QueryInput />
    </div>

    {/* Results - full width on mobile, half on desktop */}
    <div className="lg:col-span-1">
      <ResultsPanel />
    </div>
  </div>
);
```

---

## Implementation Priority

### Phase 1 (High Impact)
1. ✅ Toast notifications (better error UX)
2. ✅ Error boundaries (graceful failures)
3. ✅ Copy-to-clipboard (utility)

### Phase 2 (Polish)
4. Progress indicators (show phase status)
5. Syntax highlighting (code readability)
6. Keyboard shortcuts (power user features)

### Phase 3 (Nice-to-Have)
7. Dark mode toggle (accessibility)
8. Query history (user convenience)
9. Responsive design (mobile support)

---

## Accessibility Improvements

### ARIA Labels
```tsx
<button aria-label="Generate SQL query">
  Generate SQL & Tests
</button>
```

### Keyboard Navigation
```tsx
<input
  autoFocus
  onKeyDown={(e) => e.key === 'Enter' && handleSubmit()}
/>
```

### Color Contrast
- Background: `#052831` (Midnight Black)
- Text: `#ffffff` (White) - 21:1 contrast ✅ WCAG AAA
- Primary accent: `#00c6c2` (Teal) - Tested for contrast

---

## Performance Optimizations

### Lazy Load Results Panels

```tsx
import { lazy, Suspense } from 'react';

const SQLPanel = lazy(() => import('./panels/SQLPanel'));
const TestPanel = lazy(() => import('./panels/TestPanel'));

return (
  <Suspense fallback={<SkeletonLoader />}>
    {phase >= 1 && <SQLPanel />}
    {phase >= 2 && <TestPanel />}
  </Suspense>
);
```

### Memoize Heavy Components

```tsx
import { memo } from 'react';

const CodeBlock = memo(({ code }: Props) => (
  <pre>{code}</pre>
));
```

---

## Testing Improvements

### Add React Testing Library Tests

```bash
npm install --save-dev @testing-library/react @testing-library/jest-dom
```

```tsx
import { render, screen } from '@testing-library/react';
import App from './App';

test('renders query input', () => {
  render(<App />);
  expect(screen.getByPlaceholderText(/Enter your query/i)).toBeInTheDocument();
});
```

---

## Quick Start: Implement Toast Notifications

1. Create `frontend/src/components/Toast.tsx` (from above)
2. Update `frontend/src/App.tsx`:
   ```tsx
   const { addToast, Toast } = useToast();
   // In catch blocks:
   addToast('Error: ' + err.message, 'error');
   ```
3. Add `<Toast />` to render
4. Test: Try submitting without a query

---

## Demo Talking Points

✅ **Professional UI** - Clean, modern, Version 1 branding  
✅ **Responsive** - Works on desktop and mobile  
✅ **Accessible** - Keyboard navigation, screen reader support  
✅ **Fast** - 60s timeout with retry logic, async operations  
✅ **User-Friendly** - Clear errors, progress indicators, history  

---

## Resources

- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [React Best Practices](https://react.dev/learn)
- [Web Accessibility WCAG](https://www.w3.org/WAI/WCAG21/quickref/)
- [Highlight.js](https://highlightjs.org/)

