# mako API

> **Version:** 0.0.0
>
> Jupyter and AI Projects

## Table of Contents

1. [Text Summarization](#text-summarization)
2. [Text-to-SQL](#text-to-sql)
3. [Text Generation](#text-generation)


---

## Text Summarization

**Method:** `POST`
**Endpoint:** `/api/ai/v1/text/summarize`

Generate a summary based on the given text input.

### Path Parameters

_None_

### Query Parameters

_None_

### Request Body

Text Summarization AI Service Request.

Prompt Templates
----------------

A prompt template is a string that contains placeholders for parameters that will be replaced with parameter values before the prompt
is submitted to the model.A default prompt template is set for each model configured for the Text Summarization AI Service. Individual requests can override the
default template by including the `promptTemplate` parameter.

### Prompt Template Parameters

The following request parameters are automatically injected into the prompt template if the associated placeholder is present:

* input
* system
Models with built-in support for system prompts and chat message history do not need to include *system* or
*chatContext* in the prompt template.Additional parameters can be provided in the `parameters` map as key-value pairs.

### Prompt Template Examples

* "${input}"
* "${system}\n${input}"

| Parameter             | Type            | Required | Description                                                                                                                                                            |
|-----------------------|-----------------|----------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `input`               | string          | ✓ Yes    | Text information to be summarized.                                                                                                                                     |
| `sessionId`           | string (uuid)   | No       | The AI session ID. If provided, this request will be associated with the specified AI Session.                                                                         |
| `promptTemplate`      | object          | No       | Optional ParameterizedPromptTemplate object (nullable)                                                                                                                 |
| `parameters`          | object          | No       | Custom parameters to inject into the prompt template if an associated placeholder is present.                                                                          |
| `model`               | string          | No       | The ID of the model to use for Text Summarization. The specified model must be configured for the Text Summarization AI Service by an Admin.                            |
| `modelConfiguration`  | object          | No       | Additional model-specific configuration parameter key-value pairs. e.g. temperature, max_tokens, etc.                                                                  |
| `system`              | string          | No       | The system message to use for the Text Summarization task. If not provided, the default system message will be used. If the model does not include built-in support for system prompts, this parameter may be included in the prompt template using the "${system}" placeholder. |
| `chunkingConfiguration` | object        | No       | Optional ChunkingConfiguration object (nullable)                                                                                                                       |
| `outputStyle`         | string          | No       | Determines the design, structuring and organization of the summarization output. Allowed values: `bulleted`, `numbered`, `paragraph`, `unknown`                        |
| `outputWordLength`    | object          | No       | Optional SizeBoundary object (nullable)                                                                                                                                |
| `temperature`         | number (double) | No       | Controls randomness in the model's output. Lower values make output more deterministic.                                                                                |
| `maxTokens`           | integer (int32) | No       | The maximum number of tokens to generate in the response.                                                                                                              |

### Request Example

<!--
type: tab
title: JavaScript
-->

```javascript
// Generate a realistic fetch/axios example using the request body example
// Use the actual endpoint path with any path parameters filled in
// Include proper headers (Content-Type: application/json if body exists)

fetch('/api/ai/v1/text/summarize', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    input: "San Francisco, officially the City and County of San Francisco, is a commercial, financial, and cultural center in Northern California. With a population of 808,437 residents as of 2022, San Francisco is the fourth most populous city in the U.S. state of California. The city covers a land area of 46.9 square miles (121 square kilometers) at the end of the San Francisco Peninsula, making it the second-most densely populated large U.S. city after New York City and the fifth-most densely populated U.S. county, behind only four New York City boroughs. Among the 92 U.S. cities proper with over 250,000 residents, San Francisco is ranked first by per capita income and sixth by aggregate income as of 2022."
  })
})
.then(response => response.json())
.then(data => console.log(data));
```

<!--
type: tab
title: Python
-->

```python
# Generate a realistic requests example using the request body example
# Use the actual endpoint path with any path parameters filled in
# Include proper headers if needed

import requests
import json

url = 'http://api/ai/v1/text/summarize'
headers = {'Content-Type': 'application/json'}
data = {
    "input": "San Francisco, officially the City and County of San Francisco, is a commercial, financial, and cultural center in Northern California. With a population of 808,437 residents as of 2022, San Francisco is the fourth most populous city in the U.S. state of California. The city covers a land area of 46.9 square miles (121 square kilometers) at the end of the San Francisco Peninsula, making it the second-most densely populated large U.S. city after New York City and the fifth-most densely populated U.S. county, behind only four New York City boroughs. Among the 92 U.S. cities proper with over 250,000 residents, San Francisco is ranked first by per capita income and sixth by aggregate income as of 2022."
}

response = requests.post(url, headers=headers, data=json.dumps(data))
print(response.json())
```

<!--
type: tab
title: cURL
-->

```bash
# Generate a realistic cURL command
# Use the actual endpoint path
# Include -H headers and -d data as appropriate

curl -X POST http://api/ai/v1/text/summarize \
-H "Content-Type: application/json" \
-d '{
  "input": "San Francisco, officially the City and County of San Francisco, is a commercial, financial, and cultural center in Northern California. With a population of 808,437 residents as of 2022, San Francisco is the fourth most populous city in the U.S. state of California. The city covers a land area of 46.9 square miles (121 square kilometers) at the end of the San Francisco Peninsula, making it the second-most densely populated large U.S. city after New York City and the fifth-most densely populated U.S. county, behind only four New York City boroughs. Among the 92 U.S. cities proper with over 250,000 residents, San Francisco is ranked first by per capita income and sixth by aggregate income as of 2022."
}'
```

<!-- type: tab-end -->

### Response

**Status:** `200`

```json
{
  "prompt": "Write a 5 to 10 words summary of the following text. ```...``` CONCISE SUMMARY:",
  "output": "Vibrant, densely populated commercial and cultural hub in Northern California.",
  "modelId": "domo.domo_ai.domogpt-summarize-v1:anthropic"
}
```

### Error Responses

| Status Code | Description |
|-------------|-------------|
| `403` | Forbidden |
| `409` | Conflict |

---

## Text-to-SQL

**Method:** `POST`  
**Endpoint:** `/api/ai/v1/text/sql`

Generate a SQL query based on the given text input and data source schema.

### Path Parameters

_None_

### Query Parameters

_None_

### Request Body

Text-to-SQL AI Service Request.

Prompt Templates  
----------------

A prompt template is a string that contains placeholders for parameters that will be replaced with parameter values before the prompt is submitted to the model. A default prompt template is set for each model configured for the Text-to-SQL AI Service. Individual requests can override the default template by including the `promptTemplate` parameter.

### Prompt Template Parameters

The following request parameters are automatically injected into the prompt template if the associated placeholder is present:

* input
* system
* dataSourceSchemas
* dialect
* commentToken
* escapeChar
Models with built-in support for system prompts and chat message history do not need to include *system* or *chatContext* in the prompt template. Additional parameters can be provided in the `parameters` map as key-value pairs.

### Prompt Template Examples

* "${input}"
* "${system}\n${input}"

| Parameter           | Type            | Required | Description                                                                                                                           |
|---------------------|-----------------|----------|---------------------------------------------------------------------------------------------------------------------------------------|
| `input`             | string          | ✔ Yes    | The input text.                                                                                                                       |
| `sessionId`         | string (uuid)   | No       | The AI session ID. If provided, this request will be associated with the specified AI Session.                                        |
| `dataSourceSchemas` | array           | No       | The data source schemas and metadata to be included in the Text-to-SQL task prompt to generate SQL.                                    |
| `promptTemplate`    | object          | No       | Optional ParameterizedPromptTemplate object (nullable)                                                                                |
| `parameters`        | object          | No       | Custom parameters to inject into the prompt template if an associated placeholder is present.                                         |
| `model`             | string          | No       | The ID of the model to use for Text-to-SQL. The specified model must be configured for the Text-to-SQL AI Service by an Admin.        |
| `modelConfiguration`| object          | No       | Additional model-specific configuration parameter key-value pairs. e.g. temperature, max_tokens, etc.                                  |
| `dialect`           | string          | No       | The SQL dialect to use in the Text-to-SQL task prompt. Defaults to MYSQL.                                                             |
| `commentToken`      | string          | No       | The comment token to use in the Text-to-SQL task prompt. Defaults to "#"                                                               |
| `escapeChar`        | string          | No       | The escape character to use in the Text-to-SQL task prompt. Defaults to "`"                                                           |
| `system`            | string          | No       | The system message to use for the Text-to-SQL task. If not provided, the default system will be used.                                 |
| `domoSupported`     | boolean         | No       | Whether the generated SQL should be compatible with Domo's query engine. Defaults to true                                             |
| `sqlRequestOptions` | array           | No       | Optional SQL request options to control the behavior of the Text-to-SQL AI Service.                                                   |
| `temperature`       | number (double) | No       | Controls randomness in the model's output. Lower values make output more deterministic.                                               |
| `maxTokens`         | integer (int32) | No       | The maximum number of tokens to generate in the response.                                                                             |

### Request Example

<!--
type: tab
title: JavaScript
-->

```javascript
const axios = require('axios');

async function textToSQL() {
  try {
    const response = await axios.post('https://your-api-domain.com/api/ai/v1/text/sql', {
      input: "What are my total sales by region?",
      dataSourceSchemas: [
        {
          dataSourceName: "Store Sales",
          columns: [
            { type: "STRING", name: "product" },
            { type: "LONG", name: "store" },
            { type: "LONG", name: "amount" },
            { type: "DATETIME", name: "timestamp'" },
            { type: "STRING", name: "region" }
          ]
        }
      ]
    }, {
      headers: {
        'Content-Type': 'application/json'
      }
    });
    console.log(response.data);
  } catch (error) {
    console.error(error);
  }
}

textToSQL();
```

<!--
type: tab
title: Python
-->

```python
import requests

def text_to_sql():
    url = 'https://your-api-domain.com/api/ai/v1/text/sql'
    headers = {'Content-Type': 'application/json'}
    data = {
        "input": "What are my total sales by region?",
        "dataSourceSchemas": [
            {
                "dataSourceName": "Store Sales",
                "columns": [
                    {"type": "STRING", "name": "product"},
                    {"type": "LONG", "name": "store"},
                    {"type": "LONG", "name": "amount"},
                    {"type": "DATETIME", "name": "timestamp'"},
                    {"type": "STRING", "name": "region"}
                ]
            }
        ]
    }
    
    response = requests.post(url, json=data, headers=headers)
    print(response.json())

text_to_sql()
```

<!--
type: tab
title: cURL
-->

```bash
curl -X POST https://your-api-domain.com/api/ai/v1/text/sql \
-H "Content-Type: application/json" \
-d '{
  "input": "What are my total sales by region?",
  "dataSourceSchemas": [
    {
      "dataSourceName": "Store Sales",
      "columns": [
        {"type": "STRING", "name": "product"},
        {"type": "LONG", "name": "store"},
        {"type": "LONG", "name": "amount"},
        {"type": "DATETIME", "name": "timestamp'"},
        {"type": "STRING", "name": "region"}
      ]
    }
  ]
}'
```

<!-- type: tab-end -->

### Response

**Status:** `200`

```json
{
  "prompt": "# MYSQL\n[{\"dataSourceName\":\"Store_Sales\",\"columns\":[{\"name\":\"product\",\"type\":\"STRING\"},{\"name\":\"store\",\"type\":\"LONG\"},{\"name\":\"amount\",\"type\":\"LONG\"},{\"name\":\"timestamp\",\"type\":\"DATETIME\"},{\"name\":\"region\",\"type\":\"STRING\"}]}]\n# Generate a query to answer the following:\n# What are my total sales by region?",
  "output": "SELECT region, SUM(amount) AS total_sales FROM `Store Sales` GROUP BY region",
  "modelId": "domo.domo_ai.domogpt-medium-v1.2:anthropic"
}
```

### Error Responses

| Status Code | Description                     |
|-------------|---------------------------------|
| `400`       | Invalid property in request     |
| `403`       | Forbidden                       |
| `409`       | Conflict                        |

---

## Text Generation

**Method:** `POST`
**Endpoint:** `/api/ai/v1/text/generation`

Generate text based on the given text input.

### Path Parameters

_None_

### Query Parameters

_None_

### Request Body

Text Generation AI Service Request.

Prompt Templates
----------------

A prompt template is a string that contains placeholders for parameters that will be replaced with parameter values before the prompt is submitted to the model. A default prompt template is set for each model configured for the Text Generation AI Service. Individual requests can override the default template by including the `promptTemplate` parameter.

### Prompt Template Parameters

The following request parameters are automatically injected into the prompt template if the associated placeholder is present:

* input
* system
Models with built-in support for system prompts and chat message history do not need to include *system* or *chatContext* in the prompt template. Additional parameters can be provided in the `parameters` map as key-value pairs.

### Prompt Template Examples

* "${input}"
* "${system}\n${input}"

| Parameter          | Type              | Required | Description                                                                                                                                 |
|--------------------|-------------------|----------|---------------------------------------------------------------------------------------------------------------------------------------------|
| `input`            | string            | ✓ Yes    | The input text.                                                                                                                             |
| `sessionId`        | string (uuid)     | No       | The AI session ID. If provided, this request will be associated with the specified AI Session.                                              |
| `promptTemplate`   | object            | No       | Optional ParameterizedPromptTemplate object (nullable)                                                                                      |
| `parameters`       | object            | No       | Custom parameters to inject into the prompt template if an associated placeholder is present.                                               |
| `model`            | string            | No       | The ID of the model to use for Text Generation. The specified model must be configured for the Text Generation                            AI Service by an Admin. |
| `modelConfiguration` | object          | No       | Additional model-specific configuration parameter key-value pairs. e.g. temperature, max_tokens, etc.                                       |
| `system`           | string            | No       | The system message to use for the Text Generation task. If not provided, the default system message will be                            used. If the model does not include built-in support for system prompts, this parameter may be included in the                            prompt template using the "${system}" placeholder.                      |
| `temperature`      | number (double)   | No       | Controls randomness in the model's output. Lower values make output more deterministic.                                                     |
| `maxTokens`        | integer (int32)   | No       | The maximum number of tokens to generate in the response.                                                                                   |

### Request Example

<!--
type: tab
title: JavaScript
-->

```javascript
// Generate a realistic fetch/axios example using the request body example
// Use the actual endpoint path with any path parameters filled in
// Include proper headers (Content-Type: application/json if body exists)
fetch('/api/ai/v1/text/generation', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    "input": "Why is the sky blue?"
  })
})
.then(response => response.json())
.then(data => console.log(data))
.catch(error => console.error('Error:', error));
```

<!--
type: tab
title: Python
-->

```python
# Generate a realistic requests example using the request body example
# Use the actual endpoint path with any path parameters filled in
# Include proper headers if needed
import requests

url = "http://localhost:5000/api/ai/v1/text/generation"
payload = {
    "input": "Why is the sky blue?"
}
headers = {
    "Content-Type": "application/json"
}

response = requests.post(url, json=payload, headers=headers)

print(response.json())
```

<!--
type: tab
title: cURL
-->

```bash
# Generate a realistic cURL command
# Use the actual endpoint path
# Include -H headers and -d data as appropriate
curl -X POST "http://localhost:5000/api/ai/v1/text/generation" \
-H "Content-Type: application/json" \
-d '{
  "input": "Why is the sky blue?"
}'
```

<!-- type: tab-end -->

### Response

**Status:** `200`

```json
{
  "prompt": "Why is the sky blue?",
  "output": "The sky is blue because of Rayleigh scattering.",
  "modelId": "domo.domo_ai.domogpt-small-v1:anthropic"
}
```

### Error Responses

| Status Code | Description |
|-------------|-------------|
| `403`       | Forbidden   |
| `409`       | Conflict    |

---

