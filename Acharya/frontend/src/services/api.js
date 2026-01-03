/**
 * API Service for Acharya
 * Connects the React frontend to the Python FastAPI backend
 */

const API_BASE_URL = 'http://localhost:8000';

/**
 * Start content generation for a topic
 * @param {string} topic - The topic to generate content for
 * @param {string} userId - Optional user ID
 * @returns {Promise<{session_id: string, status: string, message: string}>}
 */
export async function startGeneration(topic, userId = 'default_user') {
    const response = await fetch(`${API_BASE_URL}/api/generate`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ topic, user_id: userId }),
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to start content generation');
    }

    return response.json();
}

/**
 * Get the status and results of content generation
 * @param {string} sessionId - The session ID returned from startGeneration
 * @returns {Promise<{session_id: string, status: string, topic: string, subtopics: string[], content: object[], error: string|null}>}
 */
export async function getGenerationStatus(sessionId) {
    const response = await fetch(`${API_BASE_URL}/api/status/${sessionId}`);

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to get generation status');
    }

    return response.json();
}

/**
 * Get generation progress
 * @param {string} sessionId - The session ID
 * @returns {Promise<{status: string, progress: string, subtopics_count: number}>}
 */
export async function getProgress(sessionId) {
    const response = await fetch(`${API_BASE_URL}/api/progress/${sessionId}`);

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to get progress');
    }

    return response.json();
}

/**
 * Poll for content generation completion
 * @param {string} sessionId - The session ID
 * @param {function} onProgress - Callback for progress updates
 * @param {number} interval - Polling interval in ms (default: 3000)
 * @param {number} timeout - Max wait time in ms (default: 1200000 = 20 minutes)
 * @returns {Promise<{subtopics: string[], content: object[]}>}
 */
export async function pollForCompletion(sessionId, onProgress = null, interval = 3000, timeout = 1200000) {
    const startTime = Date.now();

    while (Date.now() - startTime < timeout) {
        const status = await getGenerationStatus(sessionId);

        if (onProgress) {
            onProgress(status);
        }

        if (status.status === 'completed') {
            return {
                subtopics: status.subtopics,
                content: status.content,
            };
        }

        if (status.status === 'error') {
            throw new Error(status.error || 'Content generation failed');
        }

        // Wait before polling again
        await new Promise((resolve) => setTimeout(resolve, interval));
    }

    throw new Error('Content generation timed out');
}

/**
 * Generate content for a topic (combined function)
 * @param {string} topic - The topic to generate content for
 * @param {function} onProgress - Callback for progress updates
 * @returns {Promise<{subtopics: string[], content: object[]}>}
 */
export async function generateContent(topic, onProgress = null) {
    // Start generation
    const { session_id } = await startGeneration(topic);

    // Poll for completion
    return pollForCompletion(session_id, onProgress);
}

/**
 * Health check for the API
 * @returns {Promise<boolean>}
 */
export async function healthCheck() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        return response.ok;
    } catch {
        return false;
    }
}

export default {
    startGeneration,
    getGenerationStatus,
    getProgress,
    pollForCompletion,
    generateContent,
    healthCheck,
};
