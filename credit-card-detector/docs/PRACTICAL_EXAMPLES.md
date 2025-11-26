# 📚 Practical Examples & Use Cases

Real-world examples of using the Credit Card Detector in various scenarios and applications.

## 📋 Table of Contents

1. [Web Application Integration](#-web-application-integration)
2. [Data Pipeline Processing](#-data-pipeline-processing)
3. [API Gateway Implementation](#-api-gateway-implementation)
4. [Batch Processing Large Datasets](#-batch-processing-large-datasets)
5. [Real-time Stream Processing](#-real-time-stream-processing)
6. [Compliance & Auditing](#-compliance--auditing)
7. [Monitoring & Alerting](#-monitoring--alerting)
8. [Multi-language Integration](#-multi-language-integration)
9. [Performance Optimization](#-performance-optimization)
10. [Error Handling & Resilience](#-error-handling--resilience)

## 🌐 Web Application Integration

### Flask Web App Example

```python
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)
DETECTOR_URL = "http://localhost:5000/scan"

@app.route('/api/process-text', methods=['POST'])
def process_text():
    """Process user-submitted text for credit card detection"""
    data = request.get_json()
    text = data.get('text', '')

    # Scan for credit cards
    response = requests.post(DETECTOR_URL, json={'text': text})
    detections = response.json()

    # Return safe version
    return jsonify({
        'original_length': len(text),
        'has_cards': len(detections['detections']) > 0,
        'card_count': len(detections['detections']),
        'safe_text': detections['redacted'],
        'detections': detections['detections']
    })

if __name__ == '__main__':
    app.run(debug=True, port=8000)
```

**Usage:**
```bash
# Start the detector
./start.sh basic

# Start the web app
python flask_app.py

# Test it
curl -X POST http://localhost:8000/api/process-text \
  -H "Content-Type: application/json" \
  -d '{"text": "Customer payment: Visa 4111111111111111"}'
```

### React Frontend Integration

```javascript
// API service for credit card detection
class CreditCardService {
    constructor(baseUrl = 'http://localhost:5000') {
        this.baseUrl = baseUrl;
    }

    async detectCards(text) {
        try {
            const response = await fetch(`${this.baseUrl}/scan`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ text })
            });

            const result = await response.json();
            return {
                success: true,
                hasCards: result.detections.length > 0,
                safeText: result.redacted,
                detections: result.detections
            };
        } catch (error) {
            return {
                success: false,
                error: error.message
            };
        }
    }
}

// React component usage
function TextInput() {
    const [text, setText] = useState('');
    const [result, setResult] = useState(null);
    const cardService = new CreditCardService();

    const handleDetect = async () => {
        const detection = await cardService.detectCards(text);
        setResult(detection);
    };

    return (
        <div>
            <textarea
                value={text}
                onChange={(e) => setText(e.target.value)}
                placeholder="Enter text to scan..."
            />
            <button onClick={handleDetect}>Detect Cards</button>

            {result && (
                <div>
                    <h3>Results:</h3>
                    <p>Cards Found: {result.hasCards ? 'Yes' : 'No'}</p>
                    <p>Safe Text: {result.safeText}</p>
                </div>
            )}
        </div>
    );
}
```

## 🔄 Data Pipeline Processing

### Apache Beam Pipeline Example

```python
import apache_beam as beam
import requests
import json

class DetectCreditCards(beam.DoFn):
    def __init__(self, detector_url='http://localhost:5000/scan'):
        self.detector_url = detector_url

    def process(self, element):
        try:
            response = requests.post(
                self.detector_url,
                json={'text': element['text']}
            )
            result = response.json()

            yield {
                'id': element['id'],
                'original_text': element['text'],
                'has_cards': len(result['detections']) > 0,
                'safe_text': result['redacted'],
                'card_count': len(result['detections']),
                'detections': result['detections'],
                'timestamp': element.get('timestamp')
            }
        except Exception as e:
            yield {
                'id': element['id'],
                'error': str(e),
                'original_text': element['text']
            }

def run_pipeline():
    with beam.Pipeline() as pipeline:
        # Sample data - in real scenario, this would come from your data source
        data = [
            {'id': 1, 'text': 'Payment: Visa 4111111111111111', 'timestamp': '2024-01-01T10:00:00Z'},
            {'id': 2, 'text': 'No payment info here', 'timestamp': '2024-01-01T10:01:00Z'},
            {'id': 3, 'text': 'MC: 5555555555554444 expires 12/25', 'timestamp': '2024-01-01T10:02:00Z'}
        ]

        results = (
            pipeline
            | 'CreateData' >> beam.Create(data)
            | 'DetectCards' >> beam.ParDo(DetectCreditCards())
            | 'LogResults' >> beam.Map(print)
        )

if __name__ == '__main__':
    run_pipeline()
```

### Airflow DAG Example

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.http.hooks.http import HttpHook
from datetime import datetime, timedelta
import json

def detect_credit_cards(**context):
    """Process text data for credit card detection"""
    http_hook = HttpHook(http_conn_id='credit_card_detector', method='POST')

    # Get data from previous task or database
    text_data = context['task_instance'].xcom_pull(task_ids='extract_data')

    results = []
    for item in text_data:
        try:
            response = http_hook.run(
                endpoint='/scan',
                data=json.dumps({'text': item['text']}),
                headers={'Content-Type': 'application/json'}
            )

            result = response.json()
            results.append({
                'id': item['id'],
                'has_cards': len(result['detections']) > 0,
                'safe_text': result['redacted'],
                'card_count': len(result['detections'])
            })
        except Exception as e:
            results.append({
                'id': item['id'],
                'error': str(e)
            })

    return results

default_args = {
    'owner': 'data-team',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

dag = DAG(
    'credit_card_detection_pipeline',
    default_args=default_args,
    description='Process text data for credit card detection',
    schedule_interval=timedelta(hours=1),
    catchup=False
)

# Define tasks
extract_data = PythonOperator(
    task_id='extract_data',
    python_callable=lambda: [
        {'id': 1, 'text': 'Customer payment: Visa 4111111111111111'},
        {'id': 2, 'text': 'Regular note without cards'}
    ],
    dag=dag
)

detect_cards = PythonOperator(
    task_id='detect_cards',
    python_callable=detect_credit_cards,
    dag=dag
)

store_results = PythonOperator(
    task_id='store_results',
    python_callable=lambda **context: print(context['task_instance'].xcom_pull(task_ids='detect_cards')),
    dag=dag
)

extract_data >> detect_cards >> store_results
```

## 🔌 API Gateway Implementation

### Kong Gateway Plugin Example

```python
# Custom Kong plugin for credit card detection
local plugin_handler = {}

function plugin_handler:access(conf)
    -- Get request body
    local cjson = require "cjson"
    local ngx = ngx
    local http = require "resty.http"

    -- Read request body
    ngx.req.read_body()
    local body = ngx.req.get_body_data()

    if not body then
        return
    end

    -- Try to parse as JSON
    local success, data = pcall(cjson.decode, body)
    if not success then
        return
    end

    -- Look for text fields to scan
    local text_fields = {}
    if conf.text_fields then
        for _, field in ipairs(conf.text_fields) do
            if data[field] then
                table.insert(text_fields, {
                    field = field,
                    text = data[field]
                })
            end
        end
    end

    -- Scan text for credit cards
    if #text_fields > 0 then
        local httpc = http.new()
        local res, err = httpc:request_uri("http://localhost:5000/scan", {
            method = "POST",
            body = cjson.encode({text = text_fields[1].text}),
            headers = {
                ["Content-Type"] = "application/json"
            }
        })

        if res and res.status == 200 then
            local scan_result = cjson.decode(res.body)

            -- Add detection results to headers
            ngx.header["X-Credit-Cards-Found"] = #scan_result.detections
            ngx.header["X-Text-Safe"] = scan_result.redacted

            -- Log detection
            ngx.log(ngx.INFO, "Credit cards detected: ", #scan_result.detections)
        end
    end
end

return plugin_handler
```

### Express.js Middleware

```javascript
const express = require('express');
const axios = require('axios');
const app = express();

app.use(express.json());

// Credit card detection middleware
const creditCardDetector = async (req, res, next) => {
    try {
        // Check if request has text data
        const textToScan = req.body.text ||
                           req.body.message ||
                           req.body.content ||
                           JSON.stringify(req.body);

        if (textToScan && textToScan.length > 10) {
            const response = await axios.post('http://localhost:5000/scan', {
                text: textToScan
            });

            const result = response.data;

            // Add detection info to request
            req.creditCardInfo = {
                hasCards: result.detections.length > 0,
                cardCount: result.detections.length,
                safeText: result.redacted,
                detections: result.detections
            };

            // Log detection
            if (result.detections.length > 0) {
                console.log(`Credit cards detected: ${result.detections.length}`);
            }
        }

        next();
    } catch (error) {
        console.error('Credit card detection error:', error.message);
        next(); // Continue even if detection fails
    }
};

// Apply middleware
app.use(creditCardDetector);

// Your routes
app.post('/api/messages', (req, res) => {
    if (req.creditCardInfo && req.creditCardInfo.hasCards) {
        return res.status(400).json({
            error: 'Message contains credit card information',
            safeText: req.creditCardInfo.safeText
        });
    }

    res.json({ message: 'Message processed successfully' });
});

app.listen(3000, () => {
    console.log('Server running on port 3000');
});
```

## 📊 Batch Processing Large Datasets

### Pandas Integration

```python
import pandas as pd
import requests
import concurrent.futures
import time
from tqdm import tqdm

def detect_credit_cards_batch(texts, detector_url='http://localhost:5000/scan', max_workers=5):
    """Process multiple texts in parallel"""
    results = []

    def process_text(text):
        try:
            response = requests.post(detector_url, json={'text': text}, timeout=30)
            return {
                'success': True,
                'result': response.json()
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    # Process in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_text, text): text for text in texts}

        for future in tqdm(concurrent.futures.as_completed(futures), total=len(texts)):
            text = futures[future]
            try:
                result = future.result()
                results.append({
                    'original_text': text,
                    **result
                })
            except Exception as e:
                results.append({
                    'original_text': text,
                    'success': False,
                    'error': str(e)
                })

    return results

# Example usage with DataFrame
def process_dataframe(df, text_column='content'):
    """Process DataFrame with credit card detection"""
    print(f"Processing {len(df)} records...")

    # Extract texts
    texts = df[text_column].tolist()

    # Detect credit cards
    start_time = time.time()
    results = detect_credit_cards_batch(texts)
    end_time = time.time()

    # Add results back to DataFrame
    df['has_cards'] = [r['result']['detections'] if r['success'] else [] for r in results]
    df['card_count'] = [len(r['result']['detections']) if r['success'] else 0 for r in results]
    df['safe_text'] = [r['result']['redacted'] if r['success'] else r['original_text'] for r in results]
    df['detection_error'] = [r.get('error') if not r['success'] else None for r in results]

    print(f"Processed {len(df)} records in {end_time - start_time:.2f} seconds")
    print(f"Cards found in {df['card_count'].sum()} instances")

    return df

# Usage example
if __name__ == "__main__":
    # Sample data
    data = {
        'id': [1, 2, 3, 4, 5],
        'content': [
            'Payment with Visa 4111111111111111',
            'No payment info here',
            'MC: 5555555555554444, phone: 555-123-4567',
            'Regular text message',
            'Amex 378282246310005 for purchase'
        ]
    }

    df = pd.DataFrame(data)

    # Start the detector first
    # ./start.sh production

    # Process the DataFrame
    processed_df = process_dataframe(df, 'content')

    # Save results
    processed_df.to_csv('processed_data.csv', index=False)
    print("Results saved to processed_data.csv")
```

### Apache Spark Integration

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import udf, col, lit
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, ArrayType
import requests
import json

def detect_credit_cards_spark(text):
    """UDF for credit card detection in Spark"""
    try:
        response = requests.post(
            'http://localhost:5000/scan',
            json={'text': text},
            timeout=10
        )
        result = response.json()
        return {
            'has_cards': len(result['detections']) > 0,
            'card_count': len(result['detections']),
            'safe_text': result['redacted'],
            'detections': json.dumps(result['detections'])
        }
    except Exception as e:
        return {
            'has_cards': False,
            'card_count': 0,
            'safe_text': text,
            'detections': json.dumps([]),
            'error': str(e)
        }

# Create Spark session
spark = SparkSession.builder \
    .appName("CreditCardDetection") \
    .getOrCreate()

# Register UDF
detect_udf = udf(detect_credit_cards_spark,
                 StructType([
                     StructField("has_cards", StringType(), False),
                     StructField("card_count", IntegerType(), False),
                     StructField("safe_text", StringType(), False),
                     StructField("detections", StringType(), False)
                 ]))

# Sample data
data = [
    (1, "Payment: Visa 4111111111111111"),
    (2, "No cards here"),
    (3, "MC: 5555555555554444"),
    (4, "Regular message"),
    (5, "Amex 378282246310005")
]

columns = ["id", "text"]
df = spark.createDataFrame(data, columns)

# Apply detection
result_df = df.withColumn("detection_result", detect_udf(col("text")))

# Extract individual fields
result_df = result_df.withColumn("has_cards", col("detection_result.has_cards")) \
                     .withColumn("card_count", col("detection_result.card_count")) \
                     .withColumn("safe_text", col("detection_result.safe_text")) \
                     .drop("detection_result")

# Show results
result_df.show(truncate=False)

# Save results
result_df.write.mode("overwrite").parquet("credit_card_detection_results")
```

## 🌊 Real-time Stream Processing

### Kafka Consumer Example

```python
from kafka import KafkaConsumer
import requests
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CreditCardStreamProcessor:
    def __init__(self, detector_url='http://localhost:5000/scan'):
        self.detector_url = detector_url

    def process_message(self, message):
        """Process individual message from Kafka"""
        try:
            # Parse message
            data = json.loads(message.value.decode('utf-8'))
            text = data.get('text', '')

            if not text:
                return None

            # Detect credit cards
            response = requests.post(
                self.detector_url,
                json={'text': text},
                timeout=5
            )

            result = response.json()

            # Enhanced message with detection results
            enhanced_data = {
                **data,
                'credit_cards_found': len(result['detections']),
                'safe_text': result['redacted'],
                'detections': result['detections'],
                'processed_at': json.dumps({"timestamp": time.time()})
            }

            if result['detections']:
                logger.warning(f"Credit cards detected in message: {len(result['detections'])}")

            return enhanced_data

        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return {
                'original_message': message.value.decode('utf-8'),
                'error': str(e),
                'processed_at': json.dumps({"timestamp": time.time()})
            }

    def start_consuming(self, kafka_servers, topic_name):
        """Start consuming messages from Kafka"""
        consumer = KafkaConsumer(
            topic_name,
            bootstrap_servers=kafka_servers,
            auto_offset_reset='earliest',
            value_deserializer=None  # We'll deserialize manually
        )

        logger.info(f"Started consuming from topic: {topic_name}")

        for message in consumer:
            processed = self.process_message(message)

            if processed:
                # Here you can send to another topic, database, etc.
                logger.info(f"Processed message: {message.offset}")

                # Example: Send to output topic
                # producer.send('processed_messages', value=processed)

    def start(self, kafka_servers='localhost:9092', topic_name='text_messages'):
        """Start the stream processor"""
        logger.info("Starting credit card stream processor...")

        # Ensure detector is running
        try:
            response = requests.get(f"{self.detector_url}/health")
            if response.status_code != 200:
                raise Exception("Detector not healthy")
        except Exception as e:
            logger.error(f"Credit card detector not available: {e}")
            return

        # Start consuming
        self.start_consuming(kafka_servers, topic_name)

if __name__ == "__main__":
    processor = CreditCardStreamProcessor()
    processor.start()
```

### WebSocket Integration

```python
import asyncio
import websockets
import json
import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CreditCardWebSocketServer:
    def __init__(self, detector_url='http://localhost:5000/scan'):
        self.detector_url = detector_url

    async def detect_credit_cards(self, text):
        """Detect credit cards in text"""
        try:
            # For async HTTP, use aiohttp
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.detector_url,
                    json={'text': text},
                    timeout=5
                ) as response:
                    return await response.json()
        except Exception as e:
            logger.error(f"Detection error: {e}")
            return {'detections': [], 'redacted': text}

    async def handle_client(self, websocket, path):
        """Handle WebSocket client connection"""
        logger.info(f"Client connected: {websocket.remote_address}")

        try:
            async for message in websocket:
                data = json.loads(message)
                text = data.get('text', '')

                if text:
                    # Detect credit cards
                    result = await self.detect_credit_cards(text)

                    # Send back result
                    response = {
                        'type': 'detection_result',
                        'has_cards': len(result['detections']) > 0,
                        'card_count': len(result['detections']),
                        'safe_text': result['redacted'],
                        'detections': result['detections']
                    }

                    await websocket.send(json.dumps(response))

        except websockets.exceptions.ConnectionClosed:
            logger.info("Client disconnected")
        except Exception as e:
            logger.error(f"Error handling client: {e}")

    async def start_server(self, host='localhost', port=8765):
        """Start the WebSocket server"""
        logger.info(f"Starting WebSocket server on {host}:{port}")

        async with websockets.serve(self.handle_client, host, port):
            await asyncio.Future()  # Run forever

if __name__ == "__main__":
    server = CreditCardWebSocketServer()
    asyncio.run(server.start_server())
```

## 🔍 Compliance & Auditing

### Audit Log Implementation

```python
import sqlite3
import json
import datetime
import hashlib

class CreditCardAuditLogger:
    def __init__(self, db_path='audit.db'):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Initialize audit database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                text_hash TEXT NOT NULL,
                has_cards BOOLEAN NOT NULL,
                card_count INTEGER NOT NULL,
                safe_text TEXT NOT NULL,
                detections TEXT NOT NULL,
                source TEXT,
                user_id TEXT,
                session_id TEXT
            )
        ''')

        conn.commit()
        conn.close()

    def log_detection(self, text, detection_result, source='unknown', user_id=None, session_id=None):
        """Log credit card detection result"""
        text_hash = hashlib.sha256(text.encode()).hexdigest()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO audit_log
            (timestamp, text_hash, has_cards, card_count, safe_text, detections, source, user_id, session_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.datetime.utcnow().isoformat(),
            text_hash,
            len(detection_result['detections']) > 0,
            len(detection_result['detections']),
            detection_result['redacted'],
            json.dumps(detection_result['detections']),
            source,
            user_id,
            session_id
        ))

        conn.commit()
        conn.close()

    def get_audit_report(self, start_date=None, end_date=None):
        """Generate audit report"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = "SELECT * FROM audit_log WHERE 1=1"
        params = []

        if start_date:
            query += " AND timestamp >= ?"
            params.append(start_date)

        if end_date:
            query += " AND timestamp <= ?"
            params.append(end_date)

        cursor.execute(query, params)
        rows = cursor.fetchall()

        conn.close()

        return rows

    def get_compliance_summary(self):
        """Get compliance summary statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Total scans
        cursor.execute("SELECT COUNT(*) FROM audit_log")
        total_scans = cursor.fetchone()[0]

        # Scans with cards
        cursor.execute("SELECT COUNT(*) FROM audit_log WHERE has_cards = 1")
        scans_with_cards = cursor.fetchone()[0]

        # Total cards detected
        cursor.execute("SELECT SUM(card_count) FROM audit_log")
        total_cards = cursor.fetchone()[0] or 0

        conn.close()

        return {
            'total_scans': total_scans,
            'scans_with_cards': scans_with_cards,
            'total_cards_detected': total_cards,
            'detection_rate': (scans_with_cards / total_scans * 100) if total_scans > 0 else 0
        }

# Usage with detection
audit_logger = CreditCardAuditLogger()

def detect_with_audit(text, source='api', user_id=None):
    """Detect cards with audit logging"""
    import requests

    # Detect cards
    response = requests.post('http://localhost:5000/scan', json={'text': text})
    result = response.json()

    # Log to audit
    audit_logger.log_detection(text, result, source, user_id)

    return result
```

### GDPR Compliance Example

```python
from datetime import datetime, timedelta
import requests
import sqlite3
import hashlib

class GDPRComplianceManager:
    def __init__(self, db_path='audit.db'):
        self.db_path = db_path

    def anonymize_old_data(self, days_old=365):
        """Anonymize audit data older than specified days"""
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Replace old text hashes with anonymized version
        cursor.execute('''
            UPDATE audit_log
            SET text_hash = 'ANONYMIZED',
                safe_text = 'ANONYMIZED',
                detections = '[]'
            WHERE timestamp < ? AND has_cards = 1
        ''', (cutoff_date.isoformat(),))

        conn.commit()
        conn.close()

    def export_user_data(self, user_id):
        """Export all data for a specific user (GDPR right to access)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM audit_log
            WHERE user_id = ?
            ORDER BY timestamp DESC
        ''', (user_id,))

        rows = cursor.fetchall()
        conn.close()

        return rows

    def delete_user_data(self, user_id):
        """Delete all data for a specific user (GDPR right to erasure)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Option 1: Complete deletion
        cursor.execute('DELETE FROM audit_log WHERE user_id = ?', (user_id,))

        # Option 2: Anonymization (keeps audit trail but removes personal info)
        # cursor.execute('''
        #     UPDATE audit_log
        #     SET user_id = 'ANONYMIZED',
        #         session_id = 'ANONYMIZED'
        #     WHERE user_id = ?
        # ''', (user_id,))

        conn.commit()
        conn.close()
```

## 📈 Performance Optimization

### Connection Pooling

```python
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import concurrent.futures

class OptimizedCreditCardDetector:
    def __init__(self, base_url='http://localhost:5000', pool_size=10):
        self.base_url = base_url
        self.session = self._create_session(pool_size)

    def _create_session(self, pool_size):
        """Create HTTP session with connection pooling"""
        session = requests.Session()

        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )

        # Configure adapter with connection pooling
        adapter = HTTPAdapter(
            pool_connections=pool_size,
            pool_maxsize=pool_size,
            max_retries=retry_strategy
        )

        session.mount("http://", adapter)
        session.mount("https://", adapter)

        return session

    def detect_batch_optimized(self, texts, max_workers=5):
        """Optimized batch detection with connection pooling"""
        results = []

        def detect_text(text):
            try:
                response = self.session.post(
                    f"{self.base_url}/scan",
                    json={'text': text},
                    timeout=30
                )
                return response.json()
            except Exception as e:
                return {'error': str(e), 'detections': [], 'redacted': text}

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(detect_text, text) for text in texts]

            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    results.append({'error': str(e), 'detections': [], 'redacted': ''})

        return results

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()

# Usage
with OptimizedCreditCardDetector() as detector:
    texts = ["text 1", "text 2", "text 3"] * 100
    results = detector.detect_batch_optimized(texts, max_workers=10)
```

### Caching Implementation

```python
import hashlib
import pickle
import os
from functools import wraps
import time

class CreditCardCache:
    def __init__(self, cache_dir='cache', ttl=3600):
        self.cache_dir = cache_dir
        self.ttl = ttl  # Time to live in seconds
        os.makedirs(cache_dir, exist_ok=True)

    def _get_cache_key(self, text):
        """Generate cache key from text"""
        return hashlib.sha256(text.encode()).hexdigest()

    def _get_cache_path(self, cache_key):
        """Get cache file path"""
        return os.path.join(self.cache_dir, f"{cache_key}.cache")

    def _is_cache_valid(self, cache_path):
        """Check if cache is still valid"""
        if not os.path.exists(cache_path):
            return False

        # Check file age
        file_age = time.time() - os.path.getmtime(cache_path)
        return file_age < self.ttl

    def get(self, text):
        """Get cached result if available and valid"""
        cache_key = self._get_cache_key(text)
        cache_path = self._get_cache_path(cache_key)

        if self._is_cache_valid(cache_path):
            try:
                with open(cache_path, 'rb') as f:
                    return pickle.load(f)
            except Exception:
                pass  # Cache corrupted, will be regenerated

        return None

    def set(self, text, result):
        """Cache detection result"""
        cache_key = self._get_cache_key(text)
        cache_path = self._get_cache_path(cache_key)

        try:
            with open(cache_path, 'wb') as f:
                pickle.dump(result, f)
        except Exception as e:
            print(f"Cache write error: {e}")

    def clear(self):
        """Clear all cached data"""
        import shutil
        if os.path.exists(self.cache_dir):
            shutil.rmtree(self.cache_dir)
            os.makedirs(self.cache_dir, exist_ok=True)

# Usage with caching
cache = CreditCardCache()

def detect_with_cache(text):
    """Detect credit cards with caching"""
    # Try cache first
    cached_result = cache.get(text)
    if cached_result:
        return cached_result

    # If not in cache, detect normally
    response = requests.post('http://localhost:5000/scan', json={'text': text})
    result = response.json()

    # Cache the result
    cache.set(text, result)

    return result
```

## 🛡️ Error Handling & Resilience

### Circuit Breaker Pattern

```python
import time
from enum import Enum

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitBreaker:
    def __init__(self, failure_threshold=5, timeout=60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED

    def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time > self.timeout:
                self.state = CircuitState.HALF_OPEN
            else:
                raise Exception("Circuit breaker is OPEN")

        try:
            result = func(*args, **kwargs)

            # Success: reset circuit breaker
            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.CLOSED
            self.failure_count = 0

            return result

        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()

            if self.failure_count >= self.failure_threshold:
                self.state = CircuitState.OPEN

            raise e

# Usage
circuit_breaker = CircuitBreaker(failure_threshold=3, timeout=30)

def safe_credit_card_detection(text):
    """Credit card detection with circuit breaker"""
    def detect():
        response = requests.post('http://localhost:5000/scan', json={'text': text})
        response.raise_for_status()
        return response.json()

    try:
        return circuit_breaker.call(detect)
    except Exception as e:
        # Return safe default when circuit is open
        return {
            'detections': [],
            'redacted': text,
            'error': f'Detection service unavailable: {str(e)}'
        }
```

### Retry with Exponential Backoff

```python
import time
import random

def retry_with_backoff(func, max_retries=3, base_delay=1, max_delay=60):
    """Execute function with exponential backoff retry"""
    for attempt in range(max_retries + 1):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries:
                raise e  # Re-raise if max retries exceeded

            # Calculate delay with exponential backoff and jitter
            delay = min(base_delay * (2 ** attempt) + random.uniform(0, 1), max_delay)

            print(f"Attempt {attempt + 1} failed, retrying in {delay:.2f}s: {e}")
            time.sleep(delay)

def detect_with_retry(text):
    """Credit card detection with retry logic"""
    def detect():
        response = requests.post('http://localhost:5000/scan', json={'text': text}, timeout=10)
        response.raise_for_status()
        return response.json()

    return retry_with_backoff(detect, max_retries=3, base_delay=1, max_delay=30)
```

---

## 🎉 Complete Examples Summary

This practical examples guide covers:

✅ **Web Integration**: Flask, React, API Gateway implementations
✅ **Data Processing**: Pandas, Spark, Airflow, Beam examples
✅ **Real-time Processing**: Kafka, WebSocket implementations
✅ **Compliance**: Audit logging, GDPR compliance features
✅ **Performance**: Connection pooling, caching optimization
✅ **Resilience**: Circuit breaker, retry patterns

**🚀 Start implementing these patterns in your applications today!**

For more examples and community contributions, check the [GitHub repository](https://github.com/bytechie/cc-detector).