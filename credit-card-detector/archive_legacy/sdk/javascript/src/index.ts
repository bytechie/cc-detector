/**
 * Credit Card Detector JavaScript SDK
 *
 * A comprehensive TypeScript/JavaScript client for the Credit Card Detector API
 * with support for modern JavaScript features and type safety.
 */

import axios, { AxiosInstance, AxiosResponse } from 'axios';

// Types
export interface Detection {
  start: number;
  end: number;
  raw: string;
  number: string;
  valid: boolean;
  confidence: number;
  cardType?: string;
  skillSource?: string;
}

export interface ScanOptions {
  includeMetadata?: boolean;
  confidenceThreshold?: number;
}

export interface ScanResult {
  detections: Detection[];
  redacted: string;
  stats: {
    totalDetections: number;
    processingTimeMs: number;
    confidenceScore: number;
  };
}

export interface BatchScanOptions {
  parallel?: boolean;
  maxWorkers?: number;
}

export interface BatchScanResult {
  results: Array<{
    index: number;
    text: string;
    detections: Detection[];
    redacted: string;
    error?: string;
  }>;
  summary: {
    totalTexts: number;
    totalDetections: number;
    processingTimeMs: number;
  };
}

export interface EnhancedScanOptions {
  useAllSkills?: boolean;
  includeExternal?: boolean;
  resourceAware?: boolean;
  maxProcessingTime?: number;
}

export interface TrainingExample {
  input: string;
  expectedDetections?: Detection[];
}

export interface TrainingOptions {
  qualityThreshold?: number;
  autoDeploy?: boolean;
}

export interface SkillInfo {
  name: string;
  description: string;
  dependencies: string[];
  testCasesCount: number;
  performance: {
    f1Score: number;
    precision: number;
    recall: number;
    lastUpdated: number;
  };
  qualityScore: number;
  qualityGrade: string;
}

export interface FeedbackOptions {
  expectedDetections?: Detection[];
  context?: Record<string, any>;
}

export interface ResourceMetrics {
  cpuPercent: number;
  memoryPercent: number;
  memoryAvailableMb: number;
  activeThreads: number;
  timestamp: number;
}

export interface HealthCheck {
  status: 'ok' | 'degraded' | 'error';
  service: string;
  timestamp: string;
  dependencies: Record<string, any>;
}

export interface ClientConfig {
  apiKey?: string;
  baseUrl: string;
  timeout?: number;
  maxRetries?: number;
  retryDelay?: number;
  enableLogging?: boolean;
}

export class CreditCardDetectorError extends Error {
  constructor(
    message: string,
    public code?: string,
    public details?: Record<string, any>
  ) {
    super(message);
    this.name = 'CreditCardDetectorError';
  }
}

export class RateLimitError extends CreditCardDetectorError {
  constructor(message: string, details?: Record<string, any>) {
    super(message, 'RATE_LIMIT_EXCEEDED', details);
    this.name = 'RateLimitError';
  }
}

export class AuthenticationError extends CreditCardDetectorError {
  constructor(message: string, details?: Record<string, any>) {
    super(message, 'AUTHENTICATION_ERROR', details);
    this.name = 'AuthenticationError';
  }
}

/**
 * Main Credit Card Detector client class
 */
export class CreditCardDetector {
  private client: AxiosInstance;
  private config: ClientConfig;

  constructor(config: ClientConfig = { baseUrl: 'http://localhost:5000' }) {
    this.config = {
      timeout: 30000,
      maxRetries: 3,
      retryDelay: 1000,
      enableLogging: false,
      ...config
    };

    this.client = axios.create({
      baseURL: this.config.baseUrl,
      timeout: this.config.timeout,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
  }

  private setupInterceptors(): void {
    // Request interceptor for logging and error handling
    this.client.interceptors.request.use(
      (config) => {
        if (this.config.apiKey) {
          config.headers = {
            ...config.headers,
            'X-API-Key': this.config.apiKey,
          };
        }

        if (this.config.enableLogging) {
          console.log(`[Request] ${config.method?.toUpperCase()} ${config.url}`, {
            data: config.data,
            headers: config.headers,
          });
        }

        return config;
      },
      (error) => {
        if (this.config.enableLogging) {
          console.error('[Request Error]', error);
        }
        return Promise.reject(error);
      }
    );

    // Response interceptor for error handling and retries
    this.client.interceptors.response.use(
      (response) => {
        if (this.config.enableLogging) {
          console.log(`[Response] ${response.status} ${response.config.url}`, {
            status: response.status,
            headers: response.headers,
          });
        }

        return response;
      },
      async (error) => {
        const originalRequest = error.config;

        // Don't retry if we've already retried the max number of times
        if (!originalRequest || originalRequest._retryCount >= this.config.maxRetries) {
          return this.handleErrorResponse(error);
        }

        // Don't retry certain types of errors
        if (!this.shouldRetry(error)) {
          return this.handleErrorResponse(error);
        }

        // Increment retry count
        originalRequest._retryCount = originalRequest._retryCount || 0;
        originalRequest._retryCount++;

        // Add delay for retry
        await new Promise(resolve => setTimeout(resolve, this.config.retryDelay));

        return this.client(originalRequest);
      }
    );
  }

  private shouldRetry(error: any): boolean {
    if (!error.response) {
      // Network errors might be retryable
      return true;
    }

    const { status, config } = error.response;

    // Don't retry client errors (4xx) except for specific cases
    if (status >= 400 && status < 500) {
      return status === 429; // Rate limit errors
    }

    // Don't retry non-idempotent requests
    if (config.method && ['post', 'put', 'delete'].includes(config.method.toLowerCase())) {
      return false;
    }

    return true;
  }

  private handleErrorResponse(error: any): never {
    if (!error.response) {
      throw new CreditCardDetectorError(
        error.message || 'Network error',
        'NETWORK_ERROR'
      );
    }

    const { status, data } = error.response;

    if (status === 401) {
      throw new AuthenticationError(
        data?.error?.message || 'Authentication failed',
        data?.error?.details
      );
    }

    if (status === 429) {
      throw new RateLimitError(
        data?.error?.message || 'Rate limit exceeded',
        data?.error?.details
      );
    }

    const message = data?.error?.message || `HTTP ${status}: ${error.response.statusText}`;
    const code = data?.error?.code || 'HTTP_ERROR';

    throw new CreditCardDetectorError(message, code, data?.error?.details);
  }

  /**
   * Scan text for credit card numbers
   */
  async scan(text: string, options: ScanOptions = {}): Promise<ScanResult> {
    try {
      const data: any = { text };

      if (options.includeMetadata || options.confidenceThreshold !== undefined) {
        data.options = {};
        if (options.includeMetadata) {
          data.options.includeMetadata = options.includeMetadata;
        }
        if (options.confidenceThreshold !== undefined) {
          data.options.confidenceThreshold = options.confidenceThreshold;
        }
      }

      const response: AxiosResponse<ScanResult> = await this.client.post('/scan', data);
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  /**
   * Scan multiple texts for credit card numbers
   */
  async scanBatch(texts: string[], options: BatchScanOptions = {}): Promise<BatchScanResult> {
    try {
      const data = {
        texts,
        options: {
          parallel: options.parallel !== false,
          maxWorkers: options.maxWorkers || 4,
          ...options,
        },
      };

      const response: AxiosResponse<BatchScanResult> = await this.client.post('/scan-batch', data);
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  /**
   * Enhanced scan with all adaptive skills and optimization
   */
  async scanEnhanced(text: string, options: EnhancedScanOptions = {}): Promise<ScanResult> {
    try {
      const data = {
        text,
        options: {
          useAllSkills: true,
          includeExternal: true,
          resourceAware: true,
          ...options,
        },
      };

      const response: AxiosResponse<ScanResult> = await this.client.post('/scan-enhanced', data);
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  /**
   * Train new adaptive skills from examples
   */
  async trainSkill(
    examples: TrainingExample[],
    description?: string,
    options: TrainingOptions = {}
  ): Promise<any> {
    try {
      const data: any = {
        examples,
      };

      if (description) {
        data.description = description;
      }

      if (options.qualityThreshold !== undefined || !options.autoDeploy) {
        data.options = {};
        if (options.qualityThreshold !== undefined) {
          data.options.qualityThreshold = options.qualityThreshold;
        }
        if (!options.autoDeploy) {
          data.options.autoDeploy = false;
        }
      }

      const response = await this.client.post('/train', data);
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  /**
   * List all available adaptive skills
   */
  async listSkills(): Promise<{ totalSkills: number; skills: SkillInfo[] }> {
    try {
      const response = await this.client.get('/skills');
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  /**
   * Get performance metrics for all skills
   */
  async getSkillPerformance(): Promise<any> {
    try {
      const response = await this.client.get('/skill-performance');
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  /**
   * Submit feedback to improve skill performance
   */
  async submitFeedback(
    inputText: string,
    skillName: string,
    feedbackType: 'false_positive' | 'false_negative' | 'correct',
    options: FeedbackOptions = {}
  ): Promise<any> {
    try {
      const data: any = {
        input_text: inputText,
        skill_name: skillName,
        feedback_type: feedbackType,
      };

      if (options.expectedDetections) {
        data.expected_detections = options.expectedDetections;
      }
      if (options.context) {
        data.context = options.context;
      }

      const response = await this.client.post('/feedback', data);
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  /**
   * Get current system resource usage
   */
  async getResources(): Promise<{ current: ResourceMetrics; average5Min: ResourceMetrics }> {
    try {
      const response = await this.client.get('/resource-monitor');
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  /**
   * Get comprehensive health status
   */
  async getHealth(): Promise<HealthCheck> {
    try {
      const response = await this.client.get('/health');
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  /**
   * Benchmark different processing strategies
   */
  async benchmark(texts: string[], iterations: number = 1): Promise<any> {
    try {
      const data = {
        texts,
        iterations,
      };

      const response = await this.client.post('/benchmark-processing', data);
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  /**
   * Close the client and cleanup resources
   */
  close(): void {
    // No explicit cleanup needed for axios client
    if (this.config.enableLogging) {
      console.log('[CreditCardDetector] Client closed');
    }
  }
}

/**
 * Convenience function for quick usage
 */
export async function quickScan(
  text: string,
  config?: Partial<ClientConfig>
): Promise<ScanResult> {
  const detector = new CreditCardDetector(config);
  try {
    const result = await detector.scan(text);
    detector.close();
    return result;
  } catch (error) {
    detector.close();
    throw error;
  }
}

/**
 * Rate limiter for API calls
 */
export class RateLimiter {
  private maxRequests: number;
  private windowMs: number;
  private requests: number[] = [];

  constructor(maxRequests: number, windowMs: number) {
    this.maxRequests = maxRequests;
    this.windowMs = windowMs;
  }

  async waitIfNeeded(): Promise<void> {
    const now = Date.now();

    // Remove old requests outside the window
    this.requests = this.requests.filter(time => now - time < this.windowMs);

    if (this.requests.length >= this.maxRequests) {
      const oldestRequest = this.requests[0];
      const waitTime = this.windowMs - (now - oldestRequest);

      if (waitTime > 0) {
        await new Promise(resolve => setTimeout(resolve, waitTime));
      }
    }

    this.requests.push(now);
  }
}

// Export all types and classes
export * from './types';
export * from './utils';