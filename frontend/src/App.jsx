import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
  createGenerationJob,
  getJobStatus,
  downloadPptx,
  getRenderReport,
  STATUS_LABELS,
  isProcessing
} from './api/pptApi';

// Polling interval in milliseconds
const POLL_INTERVAL = 1500;

function App() {
  // Form state
  const [prompt, setPrompt] = useState('');
  
  // Job state
  const [jobId, setJobId] = useState(null);
  const [jobStatus, setJobStatus] = useState(null);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState(null);
  
  // UI state
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [report, setReport] = useState(null);
  const [showReport, setShowReport] = useState(false);
  
  // Polling ref
  const pollingRef = useRef(null);

  const stopPolling = useCallback(() => {
    if (pollingRef.current) {
      clearInterval(pollingRef.current);
      pollingRef.current = null;
    }
  }, []);

  const pollJobStatus = useCallback(async (id) => {
    try {
      const status = await getJobStatus(id);
      setJobStatus(status.status);
      setProgress(status.progress || 0);
      
      if (status.status === 'failed') {
        setError(status.error || 'Generation failed. Please try again.');
        stopPolling();
      } else if (status.status === 'done') {
        stopPolling();
        try {
          const reportData = await getRenderReport(id);
          setReport(reportData);
        } catch (e) {
          console.warn('Failed to fetch report:', e);
        }
      }
    } catch (e) {
      console.error('Polling error:', e);
      setError('Failed to fetch status: ' + e.message);
      stopPolling();
    }
  }, [stopPolling]);

  const startPolling = useCallback((id) => {
    pollJobStatus(id);
    pollingRef.current = setInterval(() => {
      pollJobStatus(id);
    }, POLL_INTERVAL);
  }, [pollJobStatus]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!prompt.trim()) {
      setError('Please enter a description for your presentation.');
      return;
    }
    
    setIsSubmitting(true);
    setError(null);
    setJobId(null);
    setJobStatus(null);
    setProgress(0);
    setReport(null);
    setShowReport(false);
    stopPolling();
    
    try {
      const response = await createGenerationJob({ prompt: prompt.trim() });
      setJobId(response.job_id);
      setJobStatus(response.status);
      startPolling(response.job_id);
    } catch (e) {
      setError('Failed to create job: ' + e.message);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDownload = () => {
    if (jobId) {
      downloadPptx(jobId);
    }
  };

  const handleReset = () => {
    setPrompt('');
    setJobId(null);
    setJobStatus(null);
    setProgress(0);
    setError(null);
    setReport(null);
    setShowReport(false);
    stopPolling();
  };

  useEffect(() => {
    return () => stopPolling();
  }, [stopPolling]);

  const isJobActive = jobId && isProcessing(jobStatus);
  const isComplete = jobStatus === 'done';
  const isFailed = jobStatus === 'failed';
  const canSubmit = !isSubmitting && !isJobActive && prompt.trim().length > 0;

  return (
    <div className="app-container">
      {/* Header */}
      <header className="header">
        <div className="header-logo">
          <div className="logo-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
              <rect x="3" y="3" width="18" height="18" rx="2" />
              <path d="M3 9h18" />
              <path d="M9 21V9" />
            </svg>
          </div>
        </div>
        <h1>SlideGen</h1>
        <p className="header-subtitle">AI-powered presentation generator</p>
      </header>

      {/* Main Card */}
      <main className="main-card">
        <form onSubmit={handleSubmit}>
          <div className="input-section">
            <label className="input-label" htmlFor="prompt">
              Describe your presentation
            </label>
            <textarea
              id="prompt"
              className="prompt-textarea"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Create a 10-slide presentation about the history of artificial intelligence, including key milestones, influential researchers, and future predictions..."
              disabled={isJobActive}
            />
            <div className="char-count">{prompt.length} characters</div>
          </div>

          <button
            type="submit"
            className="generate-btn"
            disabled={!canSubmit}
          >
            {isSubmitting ? (
              <>
                <span className="loading-spinner"></span>
                <span>Creating...</span>
              </>
            ) : (
              <span>Generate Presentation</span>
            )}
          </button>
        </form>

        {/* Status Section */}
        {jobId && (
          <div className="status-section">
            <div className="status-header">
              <span className={`status-badge ${jobStatus}`}>
                <span className="status-indicator"></span>
                {STATUS_LABELS[jobStatus] || jobStatus}
              </span>
              <span className="job-id">{jobId}</span>
            </div>

            {isJobActive && (
              <div className="progress-container">
                <div className="progress-bar">
                  <div 
                    className="progress-fill" 
                    style={{ width: `${Math.max(progress * 100, 3)}%` }}
                  />
                </div>
                <div className="progress-text">
                  <span>{STATUS_LABELS[jobStatus]}</span>
                  <span>{Math.round(progress * 100)}%</span>
                </div>
              </div>
            )}

            {isFailed && error && (
              <div className="error-message">
                <span className="error-icon">✕</span>
                <span>{error}</span>
              </div>
            )}

            {isComplete && (
              <div className="download-section">
                <div className="success-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <polyline points="20,6 9,17 4,12" />
                  </svg>
                </div>
                <p className="success-text">Your presentation is ready.</p>
                
                <button className="download-btn" onClick={handleDownload}>
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4" />
                    <polyline points="7,10 12,15 17,10" />
                    <line x1="12" y1="15" x2="12" y2="3" />
                  </svg>
                  Download PPTX
                </button>
                
                <button className="new-btn" onClick={handleReset}>
                  Create another presentation
                </button>

                {report && report.slides && report.slides.length > 0 && (
                  <div className="report-section">
                    <button 
                      className="report-toggle"
                      onClick={() => setShowReport(!showReport)}
                    >
                      <span>Render Report ({report.slides.length} items)</span>
                      <span className={`report-toggle-icon ${showReport ? 'open' : ''}`}>▼</span>
                    </button>
                    
                    {showReport && (
                      <div className="report-content">
                        {report.slides.map((slide, idx) => (
                          <div key={idx} className="report-slide">
                            <div className="report-slide-header">
                              <span>Slide {slide.slide_id}</span>
                              {slide.overflow_detected && (
                                <span className="overflow-badge">Overflow</span>
                              )}
                            </div>
                            {slide.actions && slide.actions.map((action, aIdx) => (
                              <div key={aIdx} className="report-action">
                                → {action.type}
                                {action.to_chars && ` (truncated to ${action.to_chars} chars)`}
                              </div>
                            ))}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {error && !jobId && (
          <div className="error-message" style={{ marginTop: '1rem' }}>
            <span className="error-icon">✕</span>
            <span>{error}</span>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;

