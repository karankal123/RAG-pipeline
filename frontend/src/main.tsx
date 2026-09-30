import React from 'react';
import ReactDOM from 'react-dom/client';
import './styles.css';

const apiBase = 'http://localhost:8000/api';

function App() {
  const [question, setQuestion] = React.useState('What is the applicant\'s monthly income?');
  const [answer, setAnswer] = React.useState('');
  const [loading, setLoading] = React.useState(false);

  const askQuestion = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${apiBase}/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question,
          application_id: 'APP-001',
          top_k: 5,
          retrieval_type: 'hybrid'
        })
      });

      const data = await response.json();
      setAnswer(data.answer || 'No answer');
    } catch (error) {
      setAnswer('The backend is not running or the request failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-shell">
      <header className="topbar">
        <h1>Loan Intelligence RAG</h1>
      </header>

      <main className="content">
        <section className="panel">
          <h2>Retrieval Playground</h2>
          <textarea
            rows={4}
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Ask a question about the loan package"
          />
          <button onClick={askQuestion} disabled={loading}>
            {loading ? 'Processing...' : 'Ask Question'}
          </button>
        </section>

        <section className="panel">
          <h2>Answer</h2>
          <p>{answer || 'No answer yet.'}</p>
        </section>
      </main>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
