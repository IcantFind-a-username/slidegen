import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
  createGenerationJob,
  getJobStatus,
  downloadPptx,
  STATUS_LABELS,
  isProcessing
} from './api/pptApi';

// Polling interval in milliseconds
const POLL_INTERVAL = 1000;

// Smooth progress animation config
const PROGRESS_ANIMATION_INTERVAL = 50; // Update every 50ms
const PROGRESS_INCREMENT = 0.005; // Increment by 0.5% each tick

function App() {
  // Form state
  const [prompt, setPrompt] = useState('');
  
  // Job state
  const [jobId, setJobId] = useState(null);
  const [jobStatus, setJobStatus] = useState(null);
  const [serverProgress, setServerProgress] = useState(0); // Actual progress from server
  const [displayProgress, setDisplayProgress] = useState(0); // Smoothly animated progress
  const [error, setError] = useState(null);
  
  // UI state
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  // Refs for intervals
  const pollingRef = useRef(null);
  const progressAnimationRef = useRef(null);

  // Stop all intervals
  const stopPolling = useCallback(() => {
    if (pollingRef.current) {
      clearInterval(pollingRef.current);
      pollingRef.current = null;
    }
  }, []);

  const stopProgressAnimation = useCallback(() => {
    if (progressAnimationRef.current) {
      clearInterval(progressAnimationRef.current);
      progressAnimationRef.current = null;
    }
  }, []);

  // Smooth progress animation - gradually approach server progress
  useEffect(() => {
    if (isProcessing(jobStatus)) {
      // Start smooth animation
      progressAnimationRef.current = setInterval(() => {
        setDisplayProgress(prev => {
          // Target is slightly ahead of server progress for smooth feel
          // But cap at 95% until actually done
          const target = Math.min(serverProgress + 0.05, 0.95);
          
          if (prev < target) {
            // Ease towards target
            const newProgress = prev + PROGRESS_INCREMENT;
            return Math.min(newProgress, target);
          }
          return prev;
        });
      }, PROGRESS_ANIMATION_INTERVAL);
      
      return () => stopProgressAnimation();
    } else if (jobStatus === 'done') {
      // Animate to 100%
      setDisplayProgress(1.0);
      stopProgressAnimation();
    }
  }, [jobStatus, serverProgress, stopProgressAnimation]);

  const pollJobStatus = useCallback(async (id) => {
    try {
      const status = await getJobStatus(id);
      setJobStatus(status.status);
      setServerProgress(status.progress || 0);
      
      if (status.status === 'failed') {
        setError(status.error || 'Generation failed. Please try again.');
        stopPolling();
        stopProgressAnimation();
      } else if (status.status === 'done') {
        stopPolling();
      }
    } catch (e) {
      console.error('Polling error:', e);
      setError('Connection error. Please try again.');
      stopPolling();
      stopProgressAnimation();
    }
  }, [stopPolling, stopProgressAnimation]);

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
    setServerProgress(0);
    setDisplayProgress(0);
    stopPolling();
    stopProgressAnimation();
    
    try {
      const response = await createGenerationJob({ prompt: prompt.trim() });
      setJobId(response.job_id);
      setJobStatus(response.status);
      startPolling(response.job_id);
    } catch (e) {
      setError('Failed to start generation. Please try again.');
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
    setServerProgress(0);
    setDisplayProgress(0);
    setError(null);
    stopPolling();
    stopProgressAnimation();
  };

  useEffect(() => {
    return () => {
      stopPolling();
      stopProgressAnimation();
    };
  }, [stopPolling, stopProgressAnimation]);

  const isJobActive = jobId && isProcessing(jobStatus);
  const isComplete = jobStatus === 'done';
  const isFailed = jobStatus === 'failed';
  const canSubmit = !isSubmitting && !isJobActive && prompt.trim().length > 0;

  // Get user-friendly status message
  const getStatusMessage = (status) => {
    switch (status) {
      case 'queued':
        return 'Starting...';
      case 'generating_json':
        return 'Creating content...';
      case 'rendering':
        return 'Building slides...';
      default:
        return STATUS_LABELS[status] || 'Processing...';
    }
  };

  return (
    <div className="app-container">
      {/* Header - Ultra Minimal */}
      <header className="header">
        <span className="header-eyebrow">Powered by AI</span>
        <h1>Create stunning<br />presentations.</h1>
      </header>

      {/* Main Card */}
      <main className="main-card">
        <form onSubmit={handleSubmit}>
          <div className="input-section">
            <textarea
              id="prompt"
              className="prompt-textarea"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Describe what you want to present..."
              disabled={isJobActive}
            />
          </div>

          <button
            type="submit"
            className="generate-btn"
            disabled={!canSubmit}
          >
            {isSubmitting ? (
              <>
                <span className="loading-spinner"></span>
                <span>Starting</span>
              </>
            ) : (
              <span>Generate</span>
            )}
          </button>
        </form>

        {/* Status Section - Only show when job is active */}
        {isJobActive && (
          <div className="status-section">
            <div className="progress-container">
              <div className="progress-bar">
                <div 
                  className="progress-fill" 
                  style={{ width: `${Math.max(displayProgress * 100, 2)}%` }}
                />
              </div>
              <div className="progress-text">
                <span>{getStatusMessage(jobStatus)}</span>
                <span className="progress-percent">{Math.round(displayProgress * 100)}%</span>
              </div>
            </div>
          </div>
        )}

        {/* Error State */}
        {isFailed && error && (
          <div className="status-section">
            <div className="error-message">
              <span className="error-icon">✕</span>
              <span>{error}</span>
            </div>
            <button className="new-btn" onClick={handleReset} style={{ marginTop: '1rem' }}>
              Try again
            </button>
          </div>
        )}

        {/* Success State */}
        {isComplete && (
          <div className="status-section">
            <div className="download-section">
              <div className="success-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                  <polyline points="20,6 9,17 4,12" />
                </svg>
              </div>
              <p className="success-text">Your presentation is ready!</p>
              
              <button className="download-btn" onClick={handleDownload}>
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4" />
                  <polyline points="7,10 12,15 17,10" />
                  <line x1="12" y1="15" x2="12" y2="3" />
                </svg>
                Download PPTX
              </button>
              
              <button className="new-btn" onClick={handleReset}>
                Create another
              </button>
            </div>
          </div>
        )}

        {/* General Error (not job-related) */}
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
