import React, { useState } from 'react';
import './App.css';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from 'chart.js';
import { Bar, Pie } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

// 🔹 Auto-detect backend URL
// 🔹 Fully dynamic API URL
const API_URL = 'http://localhost:8000';
console.log("Backend URL:", API_URL);


interface QueryResult {
  success: boolean;
  result?: any;
  error?: string;
}

const SAMPLE_QUERIES = [
  "How many total users do we have?",
  "What's our monthly recurring revenue?",
  "Show me user signups by month",
  "What's our customer churn rate?",
  "Which features are most popular?",
];

function App() {
  const [query, setQuery] = useState('');
  const [result, setResult] = useState<QueryResult | null>(null);
  const [loading, setLoading] = useState(false);

  // 🔹 Query history
  const [queryHistory, setQueryHistory] = useState<string[]>([]);

  const handleQuery = async () => {
    if (!query.trim()) return;

    setLoading(true);
    setResult(null);

    try {
      const response = await fetch(`${API_URL}/api/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question: query }),
      });

      const data = await response.json();

      if (data.success) {
        const firstDataPoint = data.result.data[0];
        const value = Object.values(firstDataPoint)[0] as string;
        const label = Object.keys(firstDataPoint)[0].replace('_', ' ').toUpperCase();

        const resultType = data.result.data.length > 1 ? 'table' : 'metric';

        setResult({
          success: true,
          result: {
            type: resultType,
            value: value,
            label: label,
            insight: data.result.insights,
            sql_query: data.result.sql_query,
            data: data.result.data
          }
        });

        // 🔹 Keep last 5 queries
        setQueryHistory(prev => [query, ...prev.slice(0, 4)]);
      } else {
        setResult({
          success: false,
          error: data.error || 'Query failed'
        });
      }
    } catch (error) {
      setResult({
        success: false,
        error: 'Failed to connect to backend. Make sure the API server is running.'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSampleQuery = (sampleQuery: string) => {
    setQuery(sampleQuery);
    setQueryHistory(prev => [sampleQuery, ...prev.slice(0, 4)]);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleQuery();
    }
  };

  // 🔹 CSV Export
  const exportToCSV = () => {
    if (!result?.result?.data) return;

    const data = result.result.data;
    const keys = Object.keys(data[0]);
    const csv = [
      keys.join(','),
      ...data.map((row: any) => keys.map(k => row[k]).join(','))
    ].join('\n');

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'analytics-data.csv';
    a.click();
  };

  // 🔥 Chart Rendering
  const renderChart = () => {
    if (!result?.result?.data || result.result.data.length <= 1) return null;

    const data = result.result.data;
    const keys = Object.keys(data[0]);

    const labels = data.map((item: any) => Object.values(item)[0] as string);
    const values = data.map((item: any) => parseFloat(Object.values(item)[1] as string));

    const chartData = {
      labels,
      datasets: [
        {
          label: keys[1].replace(/_/g, ' ').toUpperCase(),
          data: values,
          backgroundColor: [
            'rgba(102, 126, 234, 0.8)',
            'rgba(118, 75, 162, 0.8)',
            'rgba(237, 100, 166, 0.8)',
            'rgba(255, 154, 158, 0.8)',
          ],
          borderColor: [
            'rgba(102, 126, 234, 1)',
            'rgba(118, 75, 162, 1)',
            'rgba(237, 100, 166, 1)',
            'rgba(255, 154, 158, 1)',
          ],
          borderWidth: 2,
        },
      ],
    };

    const options = {
      responsive: true,
      plugins: {
        legend: {
          position: 'top' as const,
        },
      },
    };

    return labels.length <= 5 ? (
      <div style={{
        maxWidth: '500px',
        margin: '20px auto',
        background: 'white',
        padding: '20px',
        borderRadius: '8px'
      }}>
        <Pie data={chartData} options={options} />
      </div>
    ) : (
      <div style={{
        maxWidth: '500px',
        margin: '20px auto',
        background: 'white',
        padding: '20px',
        borderRadius: '8px'
      }}>
        <Bar data={chartData} options={options} />
      </div>
    );
  };

  // 🔹 Data Table
  const renderDataTable = () => {
    if (!result?.result?.data || result.result.data.length <= 1) return null;

    const data = result.result.data;
    const keys = Object.keys(data[0]);

    return (
      <div style={{ margin: '20px 0', overflowX: 'auto' }}>
        <table style={{
          width: '100%',
          borderCollapse: 'collapse',
          background: 'white',
          borderRadius: '8px',
          overflow: 'hidden'
        }}>
          <thead>
            <tr style={{ background: '#667eea', color: 'white' }}>
              {keys.map((key, idx) => (
                <th key={idx} style={{
                  padding: '12px',
                  textAlign: 'left',
                  textTransform: 'uppercase',
                  fontSize: '0.9rem'
                }}>
                  {key.replace(/_/g, ' ')}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.map((row: any, idx: number) => (
              <tr key={idx} style={{
                borderBottom: '1px solid #eee',
                background: idx % 2 === 0 ? 'white' : '#f9f9f9'
              }}>
                {keys.map((key, keyIdx) => (
                  <td key={keyIdx} style={{ padding: '12px', color: '#333' }}>
                    {row[key]}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  };

  return (
    <div className="App">
      <div style={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        padding: '20px'
      }}>
        <div style={{
          maxWidth: '800px',
          margin: '0 auto',
          background: 'white',
          borderRadius: '12px',
          padding: '30px',
          boxShadow: '0 10px 30px rgba(0,0,0,0.2)'
        }}>
          <div style={{ textAlign: 'center', marginBottom: '30px' }}>
            <h1 style={{ color: '#333', fontSize: '2.5rem', marginBottom: '10px', fontWeight: '600' }}>
              🚀 SaaS Analytics Assistant
            </h1>
            <p style={{ color: '#666', fontSize: '1.1rem', margin: '0' }}>
              Ask questions about your business data in natural language
            </p>
          </div>

          {/* Sample Queries */}
          <div style={{ marginBottom: '20px' }}>
            <h3 style={{ color: '#555', fontSize: '1.1rem', marginBottom: '10px' }}>
              Try these sample queries:
            </h3>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px' }}>
              {SAMPLE_QUERIES.map((sampleQuery, index) => (
                <button
                  key={index}
                  onClick={() => handleSampleQuery(sampleQuery)}
                  style={{
                    background: '#f0f2f5',
                    border: '1px solid #ddd',
                    borderRadius: '20px',
                    padding: '8px 16px',
                    fontSize: '0.9rem',
                    cursor: 'pointer',
                    transition: 'all 0.2s',
                    color: '#555'
                  }}
                >
                  {sampleQuery}
                </button>
              ))}
            </div>
          </div>

          {/* Query History */}
          {queryHistory.length > 0 && (
            <div style={{ marginTop: '20px', marginBottom: '20px' }}>
              <h3 style={{ color: '#555', fontSize: '1rem' }}>Recent Queries:</h3>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                {queryHistory.map((q, idx) => (
                  <button key={idx} onClick={() => setQuery(q)} style={{
                    background: '#fff3e0',
                    border: '1px solid #ffb74d',
                    borderRadius: '15px',
                    padding: '6px 12px',
                    fontSize: '0.85rem'
                  }}>
                    {q.slice(0, 30)}...
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Query Input */}
          <div style={{ marginBottom: '20px' }}>
            <textarea
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask about your SaaS metrics..."
              style={{
                width: '100%',
                minHeight: '80px',
                padding: '15px',
                border: '2px solid #e1e5e9',
                borderRadius: '8px',
                fontSize: '1rem',
                resize: 'vertical'
              }}
            />
          </div>

          {/* Query Button */}
          <div style={{ textAlign: 'center', marginBottom: '30px' }}>
            <button
              onClick={handleQuery}
              disabled={loading || !query.trim()}
              style={{
                background: loading || !query.trim()
                  ? '#ccc'
                  : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                color: 'white',
                border: 'none',
                padding: '12px 30px',
                borderRadius: '25px',
                fontSize: '1.1rem',
                fontWeight: '600',
                cursor: loading || !query.trim() ? 'not-allowed' : 'pointer',
                transition: 'all 0.2s',
                minWidth: '150px'
              }}
            >
              {loading ? '🔍 Analyzing...' : '🧠 Ask Your Data'}
            </button>
          </div>

          {/* Results Display */}
          {result && (
            <div style={{
              background: result.success ? '#f8f9ff' : '#fff3f3',
              border: `2px solid ${result.success ? '#e3f2fd' : '#ffebee'}`,
              borderRadius: '8px',
              padding: '20px',
              marginTop: '20px'
            }}>
              {result.success ? (
                <div>
                  <h3 style={{ color: '#2e7d32' }}>✅ Analysis Complete</h3>

                  {result.result.type === 'metric' && (
                    <div style={{
                      textAlign: 'center',
                      background: 'white',
                      borderRadius: '8px',
                      padding: '20px',
                      margin: '15px 0'
                    }}>
                      <div style={{
                        fontSize: '3rem',
                        fontWeight: 'bold',
                        color: '#1976d2',
                        marginBottom: '10px'
                      }}>
                        {result.result.value}
                      </div>
                      <div style={{ fontSize: '1.2rem', color: '#555' }}>
                        {result.result.label}
                      </div>
                    </div>
                  )}

                  {result.result.type === 'table' && result.result.data.length > 1 && renderChart()}

                  {/* CSV Export */}
                  {result.result.data.length > 1 && (
                    <div style={{ textAlign: 'right', marginBottom: '10px' }}>
                      <button onClick={exportToCSV} style={{
                        background: '#4caf50',
                        color: 'white',
                        border: 'none',
                        padding: '10px 20px',
                        borderRadius: '6px',
                        cursor: 'pointer'
                      }}>
                        Download CSV
                      </button>
                    </div>
                  )}

                  {result.result.type === 'table' && result.result.data.length > 1 && renderDataTable()}

                  <div style={{
                    background: 'rgba(33, 150, 243, 0.1)',
                    borderRadius: '6px',
                    padding: '12px',
                    color: '#1565c0',
                    fontStyle: 'italic'
                  }}>
                    💡 {result.result.insight}
                  </div>

                  {result.result.sql_query && (
                    <div style={{
                      background: '#f5f5f5',
                      borderRadius: '6px',
                      padding: '12px',
                      margin: '10px 0',
                      fontSize: '0.9rem',
                      fontFamily: 'monospace',
                      color: '#666'
                    }}>
                      <strong>Generated SQL:</strong> {result.result.sql_query}
                    </div>
                  )}
                </div>
              ) : (
                <p style={{ color: '#d32f2f' }}>❌ {result.error}</p>
              )}
            </div>
          )}

          {/* Footer */}
          <div style={{
            textAlign: 'center',
            marginTop: '40px',
            padding: '20px 0',
            borderTop: '1px solid #eee',
            color: '#888',
            fontSize: '0.9rem'
          }}>
            🔥 Built with React + FastAPI + Gemini Pro | Currently showing demo data
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
