/**
 * API Helper Functions for SlideGen Backend
 * Backend Base URL: http://localhost:8000
 */

const API_BASE_URL = 'http://localhost:8000';

/**
 * Create a new PPT generation job
 * POST /generate
 * 
 * @param {Object} params - Generation parameters
 * @param {string} params.prompt - User's text prompt describing the PPT
 * @param {string} [params.template_id='default'] - Template ID to use
 * @param {string} [params.language='auto'] - Language setting
 * @param {string} [params.density='normal'] - Content density
 * @returns {Promise<{job_id: string, status: string}>}
 */
export async function createGenerationJob({
  prompt,
  template_id = 'default',
  language = 'auto',
  density = 'normal'
}) {
  const response = await fetch(`${API_BASE_URL}/generate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      prompt,
      template_id,
      language,
      density
    }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `HTTP Error: ${response.status}`);
  }

  return response.json();
}

/**
 * Poll job status
 * GET /jobs/{job_id}
 * 
 * @param {string} jobId - The job ID to check
 * @returns {Promise<{
 *   job_id: string,
 *   status: 'queued' | 'generating' | 'generating_json' | 'rendering' | 'done' | 'failed',
 *   progress: number,
 *   created_at: string,
 *   updated_at: string,
 *   error: string | null
 * }>}
 */
export async function getJobStatus(jobId) {
  const response = await fetch(`${API_BASE_URL}/jobs/${jobId}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `HTTP Error: ${response.status}`);
  }

  return response.json();
}

/**
 * Get download URL for the generated PPTX file
 * GET /jobs/{job_id}/download
 * 
 * @param {string} jobId - The job ID
 * @returns {string} - Download URL
 */
export function getDownloadUrl(jobId) {
  return `${API_BASE_URL}/jobs/${jobId}/download`;
}

/**
 * Download the generated PPTX file
 * Triggers a file download in the browser
 * 
 * @param {string} jobId - The job ID
 */
export async function downloadPptx(jobId) {
  const url = getDownloadUrl(jobId);
  
  const link = document.createElement('a');
  link.href = url;
  link.download = `presentation_${jobId}.pptx`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

/**
 * Get render report for a completed job
 * GET /jobs/{job_id}/report
 * 
 * @param {string} jobId - The job ID
 * @returns {Promise<{
 *   job_id: string,
 *   slides: Array<{
 *     slide_id: string,
 *     overflow_detected: boolean,
 *     actions: Array<{type: string, to_chars?: number}>
 *   }>
 * }>}
 */
export async function getRenderReport(jobId) {
  const response = await fetch(`${API_BASE_URL}/jobs/${jobId}/report`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `HTTP Error: ${response.status}`);
  }

  return response.json();
}

/**
 * Status display labels (English)
 */
export const STATUS_LABELS = {
  queued: 'Queued',
  generating: 'Generating content',
  generating_json: 'Creating structure',
  rendering: 'Rendering slides',
  done: 'Complete',
  failed: 'Failed'
};

/**
 * Check if status indicates job is still processing
 * @param {string} status 
 * @returns {boolean}
 */
export function isProcessing(status) {
  return ['queued', 'generating', 'generating_json', 'rendering'].includes(status);
}

