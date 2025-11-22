# mako API

> **Version:** 0.0.0
>
> Jupyter and AI Projects

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

**Prompt Templates**

A prompt template is a string that contains placeholders for parameters that will be replaced with parameter values before the prompt is submitted to the model.A default prompt template is set for each model configured for the Text Summarization AI Service. Individual requests can override the default template by including the `promptTemplate` parameter.

**Prompt Template Parameters**

The following request parameters are automatically injected into the prompt template if the associated placeholder is present:

- input
- system Models with built-in support for system prompts and chat message history do not need to include *system* or *chatContext* in the prompt template.Additional parameters can be provided in the `parameters` map as key-value pairs.

**Prompt Template Examples**

- "${input}"
- "${system}\n${input}"

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `input` | string | ✔ Yes | Text information to be summarized. |
| `sessionId` | string (uuid) | No | The AI session ID. If provided, this request will be associated with the specified AI Session. |
| `promptTemplate` | [ParameterizedPromptTemplate](#schema-parameterizedprompttemplate-nullable) | No | Optional ParameterizedPromptTemplate object (nullable) |
| `parameters` | object | No | Custom parameters to inject into the prompt template if an associated placeholder is present. |
| `model` | string | No | The ID of the model to use for Text Summarization. The specified model must be configured for the Text Summarization AI Service by an Admin. |
| `modelConfiguration` | object | No | Additional model-specific configuration parameter key-value pairs. e.g. temperature, max_tokens, etc. |
| `system` | string | No | The system message to use for the Text Summarization task. If not provided, the default system message will be used. If the model does not include built-in support for system prompts, this parameter may be included in the prompt template using the "${system}" placeholder. |
| `chunkingConfiguration` | [ChunkingConfiguration](#schema-chunkingconfiguration-nullable) | No | Optional ChunkingConfiguration object (nullable) |
| `outputStyle` | string | No | Determines the design, structuring and organization of the summarization output. Allowed values: `bulleted`, `numbered`, `paragraph`, `unknown` |
| `outputWordLength` | [SizeBoundary](#schema-sizeboundary-nullable) | No | Optional SizeBoundary object (nullable) |
| `temperature` | number (double) | No | Controls randomness in the model's output. Lower values make output more deterministic. |
| `maxTokens` | integer (int32) | No | The maximum number of tokens to generate in the response. |

<details>
<summary><strong>ParameterizedPromptTemplate Object</strong></summary>

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `template` | string | No |  |


</details>

<details>
<summary><strong>ChunkingConfiguration Object</strong></summary>

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `maxChunkSize` | integer (int32) | No | This parameter prevents the chunks from exceeding a specific size. It is a limit on the number of words that each chunk can include. |
| `chunkOverlap` | integer (int32) | No | Dictates the overlap between consecutive chunks. It is the count of common characters between two adjacent chunks. |
| `separators` | array | No | It is a list of characters or Strings which can be used to start a new chunk when they appear in the original text. They are ordered from highest to lowest priority. Highest priority separator is used to split a new chunk first. If it is not present, we move to the next separator. |
| `separatorType` | string | No | Type of separator being used. |
| `disallowIntermediateChunks` | boolean | No | If set to true, only the original text will be chunked preventing further summarization of summaries if needed. |


</details>

<details>
<summary><strong>SizeBoundary Object</strong></summary>

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `min` | integer (int32) | No |  |
| `max` | integer (int32) | No |  |


</details>

### Request Example

<!--
type: tab
title: JavaScript
-->

```javascript
const axios = require('axios');

const data = {
  input: "San Francisco, officially the City and County of San Francisco, is a commercial, financial, and cultural center in Northern California. With a population of 808,437 residents as of 2022, San Francisco is the fourth most populous city in the U.S. state of California. The city covers a land area of 46.9 square miles (121 square kilometers) at the end of the San Francisco Peninsula, making it the second-most densely populated large U.S. city after New York City and the fifth-most densely populated U.S. county, behind only four New York City boroughs. Among the 92 U.S. cities proper with over 250,000 residents, San Francisco is ranked first by per capita income and sixth by aggregate income as of 2022."
};

axios.post('https://yourapiurl.com/api/ai/v1/text/summarize', data, {
  headers: {
    'Content-Type': 'application/json'
  }
})
.then(response => console.log(response.data))
.catch(error => console.error(error));
```

<!--
type: tab
title: Python
-->

```python
import requests

url = 'https://yourapiurl.com/api/ai/v1/text/summarize'
headers = {
    'Content-Type': 'application/json',
}
data = {
    "input": "San Francisco, officially the City and County of San Francisco, is a commercial, financial, and cultural center in Northern California. With a population of 808,437 residents as of 2022, San Francisco is the fourth most populous city in the U.S. state of California. The city covers a land area of 46.9 square miles (121 square kilometers) at the end of the San Francisco Peninsula, making it the second-most densely populated large U.S. city after New York City and the fifth-most densely populated U.S. county, behind only four New York City boroughs. Among the 92 U.S. cities proper with over 250,000 residents, San Francisco is ranked first by per capita income and sixth by aggregate income as of 2022."
}
response = requests.post(url, headers=headers, json=data)

print(response.json())
```

<!--
type: tab
title: cURL
-->

```bash
curl -X POST https://yourapiurl.com/api/ai/v1/text/summarize \
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

**Prompt Templates**

A prompt template is a string that contains placeholders for parameters that will be replaced with parameter values before the prompt is submitted to the model. A default prompt template is set for each model configured for the Text-to-SQL AI Service. Individual requests can override the default template by including the `promptTemplate` parameter.

**Prompt Template Parameters**

The following request parameters are automatically injected into the prompt template if the associated placeholder is present:

- input
- system
- dataSourceSchemas
- dialect
- commentToken
- escapeChar

Models with built-in support for system prompts and chat message history do not need to include *system* or *chatContext* in the prompt template. Additional parameters can be provided in the `parameters` map as key-value pairs.

**Prompt Template Examples**

- "${input}"
- "${system}\\n${input}"

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `input` | string | ✓ Yes | The input text. |
| `sessionId` | string (uuid) | No | The AI session ID. If provided, this request will be associated with the specified AI Session. |
| `dataSourceSchemas` | array | No | The data source schemas and metadata to be included in the Text-to-SQL task prompt to generate SQL. |
| `promptTemplate` | [ParameterizedPromptTemplate](#schema-parameterizedprompttemplate-nullable) | No | Optional ParameterizedPromptTemplate object (nullable). |
| `parameters` | object | No | Custom parameters to inject into the prompt template if an associated placeholder is present. |
| `model` | string | No | The ID of the model to use for Text-to-SQL. The specified model must be configured for the Text-to-SQL AI Service by an Admin. |
| `modelConfiguration` | object | No | Additional model-specific configuration parameter key-value pairs. e.g. temperature, max_tokens, etc. |
| `dialect` | string | No | The SQL dialect to use in the Text-to-SQL task prompt. Defaults to MYSQL. |
| `commentToken` | string | No | The comment token to use in the Text-to-SQL task prompt. Defaults to "#". |
| `escapeChar` | string | No | The escape character to use in the Text-to-SQL task prompt. Defaults to "`". |
| `system` | string | No | The system message to use for the Text-to-SQL task. If not provided, the default system will be used. If the model does not include built-in support for system prompts, this parameter may be included in the prompt template using the "${system}" placeholder. |
| `domoSupported` | boolean | No | Whether the generated SQL should be compatible with Domo's query engine. Defaults to true. |
| `sqlRequestOptions` | array | No | Optional SQL request options to control the behavior of the Text-to-SQL AI Service. |
| `temperature` | number (double) | No | Controls randomness in the model's output. Lower values make output more deterministic. |
| `maxTokens` | integer (int32) | No | The maximum number of tokens to generate in the response. |

<details>
<summary><strong>ParameterizedPromptTemplate Object</strong></summary>

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `template` | string | No |  |


</details>

### Request Example

<!--
type: tab
title: JavaScript
-->

```javascript
// Generate a realistic fetch/axios example using the request body example
// Use the actual endpoint path with any path parameters filled in
// Include proper headers (Content-Type: application/json if body exists)

const exampleRequest = async () => {
  const response = await fetch('/api/ai/v1/text/sql', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      input: "What are my total sales by region?",
      dataSourceSchemas: [
        {
          dataSourceName: "Store Sales",
          columns: [
            { type: "STRING", name: "product" },
            { type: "LONG", name: "store" },
            { type: "LONG", name: "amount" },
            { type: "DATETIME", name: "timestamp" },
            { type: "STRING", name: "region" }
          ]
        }
      ]
    })
  });

  const data = await response.json();
  console.log(data);
};

exampleRequest();

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

url = '/api/ai/v1/text/sql'
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
                {"type": "DATETIME", "name": "timestamp"},
                {"type": "STRING", "name": "region"}
            ]
        }
    ]
}

response = requests.post(url, headers=headers, json=data)
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

curl -X POST /api/ai/v1/text/sql \
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
        {"type": "DATETIME", "name": "timestamp"},
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

- **prompt**: The pre-processed input text and schema used for generating the SQL query.
- **output**: The generated SQL query.
- **modelId**: Identifier of the model used.

### Error Responses

| Status Code | Description |
|-------------|-------------|
| `400` | Invalid property in request |
| `403` | Forbidden |
| `409` | Conflict |

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

**Prompt Templates**

A prompt template is a string that contains placeholders for parameters that will be replaced with parameter values before the prompt is submitted to the model. A default prompt template is set for each model configured for the Text Generation AI Service. Individual requests can override the default template by including the `promptTemplate` parameter.

**Prompt Template Parameters**

The following request parameters are automatically injected into the prompt template if the associated placeholder is present:

- input
- system

Models with built-in support for system prompts and chat message history do not need to include *system* or *chatContext* in the prompt template. Additional parameters can be provided in the `parameters` map as key-value pairs.

**Prompt Template Examples**

- "${input}"
- "${system}\\n${input}"

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `input` | string | ✔ Yes | The input text. |
| `sessionId` | string (uuid) | No | The AI session ID. If provided, this request will be associated with the specified AI Session. |
| `promptTemplate` | [ParameterizedPromptTemplate](#schema-parameterizedprompttemplate-nullable) | No | Optional ParameterizedPromptTemplate object (nullable) |
| `parameters` | object | No | Custom parameters to inject into the prompt template if an associated placeholder is present. |
| `model` | string | No | The ID of the model to use for Text Generation. The specified model must be configured for the Text Generation AI Service by an Admin. |
| `modelConfiguration` | object | No | Additional model-specific configuration parameter key-value pairs. e.g. temperature, max_tokens, etc. |
| `system` | string | No | The system message to use for the Text Generation task. If not provided, the default system message will be used. If the model does not include built-in support for system prompts, this parameter may be included in the prompt template using the "${system}" placeholder. |
| `temperature` | number (double) | No | Controls randomness in the model's output. Lower values make output more deterministic. |
| `maxTokens` | integer (int32) | No | The maximum number of tokens to generate in the response. |

<details>
<summary><strong>ParameterizedPromptTemplate Object</strong></summary>

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `template` | string | No |  |

</details>

### Request Example

<!--
type: tab
title: JavaScript
-->

```javascript
// Generate a realistic fetch/axios example using the request body example
// Use the actual endpoint path with any path parameters filled in
// Include proper headers (Content-Type: application/json if body exists)
axios.post('https://api.example.com/api/ai/v1/text/generation', {
  input: 'Why is the sky blue?'
}, {
  headers: {
    'Content-Type': 'application/json',
  }
}).then(response => {
  console.log(response.data);
});
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

url = 'https://api.example.com/api/ai/v1/text/generation'
headers = {'Content-Type': 'application/json'}
data = {'input': 'Why is the sky blue?'}

response = requests.post(url, json=data, headers=headers)
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
curl -X POST https://api.example.com/api/ai/v1/text/generation \
  -H "Content-Type: application/json" \
  -d '{"input": "Why is the sky blue?"}'
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

- `prompt`: The original input text provided for generation.
- `output`: The generated text output by the model.
- `modelId`: The ID of the model used for text generation.

### Error Responses

| Status Code | Description |
|-------------|-------------|
| `403` | Forbidden |
| `409` | Conflict |

---

## Text-to-BeastMode

**Method:** `POST`  
**Endpoint:** `/api/ai/v1/text/beastmode`

Generate a Beast Mode calculation based on the given text input and data source schema.

### Path Parameters

_None_

### Query Parameters

_None_

### Request Body

Text-to-Beast-Mode AI Service Request.

**Prompt Templates**

A prompt template is a string that contains placeholders for parameters that will be replaced with parameter values before the prompt is submitted to the model.A default prompt template is set for each model configured for the Text-to-Beast-Mode AI Service. Individual requests can override the default template by including the `promptTemplate` parameter.

**Prompt Template Parameters**

The following request parameters are automatically injected into the prompt template if the associated placeholder is present:

- input
- system
- dataSourceSchema

Models with built-in support for system prompts and chat message history do not need to include *system* or *chatContext* in the prompt template.Additional parameters can be provided in the `parameters` map as key-value pairs.

**Prompt Template Examples**

- "${input}"
- "${system}\n${input}"

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `input` | string | ✓ Yes | The input text. |
| `sessionId` | string (uuid) | No | The AI session ID. If provided, this request will be associated with the specified AI Session. |
| `dataSourceSchema` | [AIDataSourceSchema](#schema-aidatasourceschema-nullable) | No | Optional AIDataSourceSchema object (nullable) |
| `promptTemplate` | [ParameterizedPromptTemplate](#schema-parameterizedprompttemplate-nullable) | No | Optional ParameterizedPromptTemplate object (nullable) |
| `parameters` | object | No | Custom parameters to inject into the prompt template if an associated placeholder is present. |
| `model` | string | No | The ID of the model to use for Text-to-Beast-Mode. The specified model must be configured for the Text-to-Beast-Mode AI Service by an Admin. |
| `modelConfiguration` | object | No | Additional model-specific configuration parameter key-value pairs. e.g. temperature, max_tokens, etc. |
| `system` | string | No | The system message to use for the Text-to-SQL task. If not provided, the default system will be used. If the model does not include built-in support for system prompts, this parameter may be included in the prompt template using the "${system}" placeholder. |
| `temperature` | number (double) | No | Controls randomness in the model's output. Lower values make output more deterministic. |
| `maxTokens` | integer (int32) | No | The maximum number of tokens to generate in the response. |
| `disableValidation` | boolean | No | Whether to disable validation of the generated Beast Mode calculation. |

<details> <summary><strong>AIDataSourceSchema Object</strong></summary>

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `dataSourceId` | string | No | The unique identifier for the data source. |
| `dataSourceName` | string | No | The name of the data source. |
| `description` | string | No | A description of the data source. |
| `columns` | array | No | The columns in the data source. |

</details>

<details> <summary><strong>ParameterizedPromptTemplate Object</strong></summary>

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `template` | string | No | |

</details>

### Request Example

<!-- type: tab title: JavaScript -->

```javascript
fetch('https://api.example.com/api/ai/v1/text/beastmode', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    input: "Count distinct products",
    dataSourceSchema: {
      dataSourceName: "Store Sales",
      columns: [
        { type: "STRING", name: "product" },
        { type: "LONG", name: "store" },
        { type: "LONG", name: "amount" },
        { type: "DATETIME", name: "timestamp" },
        { type: "STRING", name: "region" }
      ]
    }
  })
})
.then(response => response.json())
.then(data => console.log(data))
.catch(error => console.error('Error:', error));
```

<!-- type: tab title: Python -->

```python
import requests
import json

url = "https://api.example.com/api/ai/v1/text/beastmode"
headers = {
    "Content-Type": "application/json"
}
data = {
    "input": "Count distinct products",
    "dataSourceSchema": {
        "dataSourceName": "Store Sales",
        "columns": [
            {"type": "STRING", "name": "product"},
            {"type": "LONG", "name": "store"},
            {"type": "LONG", "name": "amount"},
            {"type": "DATETIME", "name": "timestamp"},
            {"type": "STRING", "name": "region"}
        ]
    }
}

response = requests.post(url, headers=headers, data=json.dumps(data))
print(response.json())
```

<!-- type: tab title: cURL -->

```bash
curl -X POST https://api.example.com/api/ai/v1/text/beastmode \
-H "Content-Type: application/json" \
-d '{
  "input": "Count distinct products",
  "dataSourceSchema": {
    "dataSourceName": "Store Sales",
    "columns": [
      { "type": "STRING", "name": "product" },
      { "type": "LONG", "name": "store" },
      { "type": "LONG", "name": "amount" },
      { "type": "DATETIME", "name": "timestamp" },
      { "type": "STRING", "name": "region" }
    ]
  }
}'
```

<!-- type: tab-end -->

### Response

**Status:** `200`

```json
{
  "prompt": "# MYSQL\n# {\"dataSourceName\":\"Store_Sales\",\"columns\":[{\"name\":\"product\",\"type\":\"STRING\"},{\"name\":\"store\",\"type\":\"LONG\"},{\"name\":\"amount\",\"type\":\"LONG\"},{\"name\":\"timestamp\",\"type\":\"DATETIME\"},{\"name\":\"region\",\"type\":\"STRING\"}]}\n# Generate a query to answer the following:\n# Count distinct products",
  "output": "COUNT(DISTINCT `product`)",
  "modelId": "domo.domo_ai.domogpt-medium-v1.2:anthropic"
}
```

**Response Fields:**

- **prompt**: The generated SQL state prompt for the AI model.
- **output**: The resulting SQL query for the Beast Mode calculation.
- **modelId**: The identifier of the AI model used for processing.

### Error Responses

| Status Code | Description |
|-------------|-------------|
| `403` | Forbidden |
| `409` | Conflict |

---

## Tool Calling

**Method:** `POST`  
**Endpoint:** `/api/ai/v1/messages/tools`

Process a tool calling request.

### Path Parameters

_None_

### Query Parameters

_None_

### Request Body

Request for making tool calls using AI.

| Parameter             | Type                       | Required | Description                                                       |
|-----------------------|----------------------------|----------|-------------------------------------------------------------------|
| `input`               | array                      | ✔ Yes    | The list of input messages to be processed by the AI.             |
| `sessionId`           | string (uuid)              | No       | The unique identifier for the AI session associated with this request. |
| `system`              | array                      | No       | System-level messages or configurations to guide the AI's response. |
| `model`               | string                     | No       | The identifier of the AI model to be used for generating a response. |
| `modelConfiguration`  | object                     | No       | Specific parameters or settings that configure the AI model behavior. |
| `temperature`         | number (double)            | No       | A parameter for controlling the randomness of the model's output. |
| `maxTokens`           | integer (int32)            | No       | The maximum number of tokens to generate in the response.         |
| `tools`               | array                      | No       | The list of tools the model can call.                             |
| `toolChoice`          | [ToolChoice](#schema-toolchoice-nullable) | No       | Optional ToolChoice object (nullable)                             |
| `validateSchema`      | boolean                    | No       | A flag to determine whether to validate the AI response against the provided schema. |

<details>
<summary><strong>ToolChoice Object</strong></summary>

| Parameter               | Type    | Required | Description |
|-------------------------|---------|----------|-------------|
| `type`                  | string  | No       |             |
| `name`                  | string  | No       |             |
| `allowParallelToolCalls`| boolean | No       |             |

</details>

### Request Example

<!--
type: tab
title: JavaScript
-->

```javascript
const fetch = require('node-fetch');

const requestBody = {
  input: [
    {
      role: 'USER',
      content: [
        {
          type: 'TEXT',
          text: 'Do you have any blue coats available?'
        }
      ]
    }
  ],
  tools: [
    {
      name: 'get_product_recommendations',
      description: 'Searches for products matching certain criteria in the database',
      parameters: {
        categories: ['coats & jackets'],
        colors: ['blue'],
        keywords: ['coat'],
        price_range: { min: 100, max: 200 },
        limit: 5,
        today: new Date().toISOString(),
        id: '550e8400-e29b-41d4-a716-446655440000'
      }
    }
  ],
  toolChoice: { type: 'AUTO' }
};

fetch('https://yourapi.com/api/ai/v1/messages/tools', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify(requestBody)
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
import requests
import datetime

url = 'https://yourapi.com/api/ai/v1/messages/tools'
headers = {'Content-Type': 'application/json'}
request_body = {
    "input": [
        {
            "role": "USER",
            "content": [
                {
                    "type": "TEXT",
                    "text": "Do you have any blue coats available?"
                }
            ]
        }
    ],
    "tools": [
        {
            "name": "get_product_recommendations",
            "description": "Searches for products matching certain criteria in the database",
            "parameters": {
                "categories": ["coats & jackets"],
                "colors": ["blue"],
                "keywords": ["coat"],
                "price_range": {"min": 100, "max": 200},
                "limit": 5,
                "today": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "id": "550e8400-e29b-41d4-a716-446655440000"
            }
        }
    ],
    "toolChoice": {"type": "AUTO"}
}

response = requests.post(url, headers=headers, json=request_body)
print(response.json())
```

<!--
type: tab
title: cURL
-->

```bash
curl -X POST 'https://yourapi.com/api/ai/v1/messages/tools' \
-H 'Content-Type: application/json' \
-d '{
  "input": [
    {
      "role": "USER",
      "content": [
        {
          "type": "TEXT",
          "text": "Do you have any blue coats available?"
        }
      ]
    }
  ],
  "tools": [
    {
      "name": "get_product_recommendations",
      "description": "Searches for products matching certain criteria in the database",
      "parameters": {
        "categories": ["coats & jackets"],
        "colors": ["blue"],
        "keywords": ["coat"],
        "price_range": {"min": 100, "max": 200},
        "limit": 5,
        "today": "2023-06-10T12:00:00Z",
        "id": "550e8400-e29b-41d4-a716-446655440000"
      }
    }
  ],
  "toolChoice": {"type": "AUTO"}
}'
```

<!-- type: tab-end -->

### Response

**Status:** `200`

```json
{
  "content": [
    {
      "type": "TEXT",
      "text": "Certainly! I'd be happy to help you find a blue coat. I'll use the product recommendation tool to search for that."
    },
    {
      "type": "TOOL_USE_REQUEST",
      "toolInput": {
        "categories": ["coats & jackets"],
        "colors": ["blue"],
        "keywords": ["coat"],
        "price_range": {"min": 100.0, "max": 200.0},
        "limit": 5,
        "today": "2023-06-10T12:00:00+00:00",
        "id": "550e8400-e29b-41d4-a716-446655440000"
      },
      "name": "get_product_recommendations",
      "toolCallId": "toolu_bdrk_01Tnc9RttRWSwvKHd5JA1sRk"
    }
  ],
  "modelId": "domo.domo_ai.domogpt-medium-v1.2:anthropic",
  "isCustomerModel": false,
  "sessionId": "526bb9ee-02d0-4717-a83d-946715b5fa82",
  "requestId": "c765dc33-9f3e-4f23-84e5-cf7aa2cd3f63",
  "stopReason": "TOOL_USE"
}
```

### Error Responses

| Status Code | Description |
|-------------|-------------|
| `403` | Forbidden |
| `409` | Conflict |

---

## Chat Messages

**Method:** `POST`  
**Endpoint:** `/api/ai/v1/messages/chat`

Process a chat messages request.

### Path Parameters

_None_

### Query Parameters

_None_

### Request Body

Request for interacting with the chat message AI service.

| Parameter            | Type             | Required | Description                                                              |
|----------------------|------------------|----------|--------------------------------------------------------------------------|
| `input`              | array            | ✓ Yes    | The list of input messages to be processed by the AI.                    |
| `sessionId`          | string (uuid)    | No       | The unique identifier for the AI session associated with this request.   |
| `system`             | array            | No       | System-level messages or configurations to guide the AI's response.       |
| `model`              | string           | No       | The identifier of the AI model to be used for generating a response.     |
| `modelConfiguration` | object           | No       | Specific parameters or settings that configure the AI model behavior.    |
| `temperature`        | number (double)  | No       | A parameter for controlling the randomness of the model's output.        |
| `maxTokens`          | integer (int32)  | No       | The maximum number of tokens to generate in the response.                |

### Request Example

<!--
type: tab
title: JavaScript
-->

```javascript
// JavaScript example using fetch
fetch('https://yourapi.com/api/ai/v1/messages/chat', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    input: [
      {
        role: 'USER',
        content: [
          {
            type: 'TEXT',
            text: 'Why is the sky blue?'
          }
        ]
      }
    ]
  }),
})
.then(response => response.json())
.then(data => console.log(data))
.catch((error) => console.error('Error:', error));
```

<!--
type: tab
title: Python
-->

```python
# Python example using requests
import requests
import json

url = 'https://yourapi.com/api/ai/v1/messages/chat'
headers = {
    'Content-Type': 'application/json'
}
data = {
    "input": [
        {
            "role": "USER",
            "content": [
                {
                    "type": "TEXT",
                    "text": "Why is the sky blue?"
                }
            ]
        }
    ]
}

response = requests.post(url, headers=headers, data=json.dumps(data))
print(response.json())
```

<!--
type: tab
title: cURL
-->

```bash
# cURL example
curl -X POST https://yourapi.com/api/ai/v1/messages/chat \
-H "Content-Type: application/json" \
-d '{
  "input": [
    {
      "role": "USER",
      "content": [
        {
          "type": "TEXT",
          "text": "Why is the sky blue?"
        }
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
  "content": [
    {
      "type": "TEXT",
      "text": "The sky appears blue due to a phenomenon called Rayleigh scattering."
    }
  ],
  "modelId": "domo.domo_ai.domogpt-medium-v1.2:anthropic",
  "isCustomerModel": false,
  "sessionId": "e1f6a485-7fb6-4f71-b41c-37d6cb5f6bd3",
  "requestId": "df2256fd-d133-4ea1-b958-295be09be7c1",
  "stopReason": "END_TURN"
}
```

- **content**: An array of content objects returned by the AI.
- **modelId**: The identifier of the model used for this response.
- **isCustomerModel**: A boolean indicating if a custom model was used.
- **sessionId**: The session identifier associated with this request.
- **requestId**: The unique request identifier.
- **stopReason**: The reason the response generation was stopped.

### Error Responses

| Status Code | Description |
|-------------|-------------|
| `403` | Forbidden |
| `409` | Conflict |

---

## Image to Text

**Method:** `POST`  
**Endpoint:** `/api/ai/v1/image/text`

Extract text from an image. By default, all text detected in the image is included. The system and input prompt may be modified in order to describe, classify or extract specific information from the image.

### Path Parameters

_None_

### Query Parameters

_None_

### Request Body

**Image to Text AI Service Request.**

**Prompt Templates**  
A prompt template is a string that contains placeholders for parameters that will be replaced with parameter values before the prompt is submitted to the model. A default prompt template is set for each model configured for the Image to Text AI Service. Individual requests can override the default template by including the `promptTemplate` parameter.

**Prompt Template Parameters**  
The following request parameters are automatically injected into the prompt template if the associated placeholder is present:

- input
- system

Models with built-in support for system prompts and chat message history do not need to include *system* or *chatContext* in the prompt template. Additional parameters can be provided in the `parameters` map as key-value pairs.

**Prompt Template Examples**

- "${input}"
- "${system}\n${input}"

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `input` | string | ✓ Yes | The input text prompt for analyzing the image. |
| `image` | [Image](#schema-image-nullable) | No | Optional Image object (nullable) |
| `sessionId` | string (uuid) | No | The AI session ID. If provided, this request will be associated with the specified AI Session. |
| `model` | string | No | The ID of the model to use for Image to Text processing. The specified model must be configured for the Image to Text AI Service by an Admin. |
| `system` | string | No | The system message to use for the Image to Text task. If not provided, the default system message will be used. If the model does not include built-in support for system prompts, this parameter may be included in the prompt template using the "${system}" placeholder. |
| `modelConfiguration` | object | No | Additional model-specific configuration parameter key-value pairs. e.g., temperature, max_tokens, etc. |
| `promptTemplate` | [ParameterizedPromptTemplate](#schema-parameterizedprompttemplate-nullable) | No | Optional ParameterizedPromptTemplate object (nullable) |
| `parameters` | object | No | Custom parameters to inject into the prompt template if an associated placeholder is present. |
| `maxTokens` | integer (int32) | No | The maximum number of tokens to generate in the response. |
| `temperature` | number (double) | No | Controls randomness in the model's output. Lower values make output more deterministic. |

<details>
<summary><strong>Image Object</strong></summary>

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `data` | string | No | The base64 encoded image data. |
| `type` | string | No | The image type, e.g., "base64". |
| `mediaType` | string | No | The media type of the image, e.g., "image/png". |

</details>

<details>
<summary><strong>ParameterizedPromptTemplate Object</strong></summary>

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `template` | string | No |  |

</details>

### Request Example

<!--
type: tab
title: JavaScript
-->

```javascript
fetch('/api/ai/v1/image/text', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        image: {
            data: "<base64 string>",
            type: "base64",
            mediaType: "image/png"
        }
    })
})
    .then(response => response.json())
    .then(data => console.log(data));
```

<!-- type: tab-end -->

<!--
type: tab
title: Python
-->

```python
import requests
import json

url = 'https://example.com/api/ai/v1/image/text'
headers = {'Content-Type': 'application/json'}
data = {
    "image": {
        "data": "<base64 string>",
        "type": "base64",
        "mediaType": "image/png"
    }
}

response = requests.post(url, headers=headers, data=json.dumps(data))
print(response.json())
```

<!-- type: tab-end -->

<!--
type: tab
title: cURL
-->

```bash
curl -X POST https://example.com/api/ai/v1/image/text \
     -H "Content-Type: application/json" \
     -d '{
           "image": {
             "data": "<base64 string>",
             "type": "base64",
             "mediaType": "image/png"
           }
         }'
```

<!-- type: tab-end -->

### Response

**Status:** `200`

```json
{
  "prompt": "What do you see in this image?",
  "output": "This image shows a small red square on a white background. The square appears to be a simple geometric shape with clean edges.",
  "model": "domo.domo_ai.domogpt-medium-v1.2:anthropic"
}
```

- **prompt**: The prompt used for analyzing the image.
- **output**: The description of the image as processed by the model.
- **model**: The model ID used for processing the request.


### Error Responses

| Status Code | Description |
|-------------|-------------|
| `403` | Forbidden |
| `409` | Conflict |

---

## Text Embeddings

**Method:** `POST`  
**Endpoint:** `/api/ai/v1/embedding/text`

Generate text embeddings based on the given text input.

### Path Parameters

_None_

### Query Parameters

_None_

### Request Body

Text Embedding AI Service Request.

| Parameter            | Type          | Required | Description                                                                           |
|----------------------|---------------|----------|---------------------------------------------------------------------------------------|
| `input`              | array         | No       | The input text to embed.                                                              |
| `model`              | string        | No       | The ID of the model to use for Text Embedding. The specified model must be configured for the Text Embedding AI Service by an Admin. |
| `dimensions`         | integer (int32)| No       | The number of dimensions for the output embeddings.                                   |
| `modelConfiguration` | object        | No       | Additional model-specific configuration parameter key-value pairs.                    |
| `requestId`          | string (uuid) | No       | A unique identifier for the request to help with tracking and troubleshooting.       |

### Request Example

<!--
type: tab
title: JavaScript
-->

```javascript
const url = 'https://example.com/api/ai/v1/embedding/text';
const requestBody = {
  input: ["This is a sample text for generating embeddings."],
  model: "example-model-id",
  dimensions: 128,
  modelConfiguration: { someParameter: "value" },
  requestId: "unique-request-id"
};

fetch(url, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify(requestBody)
})
  .then(response => response.json())
  .then(data => console.log(data))
  .catch(error => console.error('Error:', error));
```

<!-- type: tab-end -->

<!--
type: tab
title: Python
-->

```python
import requests
import json

url = 'https://example.com/api/ai/v1/embedding/text'
request_body = {
    "input": ["This is a sample text for generating embeddings."],
    "model": "example-model-id",
    "dimensions": 128,
    "modelConfiguration": {"someParameter": "value"},
    "requestId": "unique-request-id"
}

response = requests.post(url, headers={'Content-Type': 'application/json'}, data=json.dumps(request_body))
print(response.json())
```

<!-- type: tab-end -->

<!--
type: tab
title: cURL
-->

```bash
curl -X POST https://example.com/api/ai/v1/embedding/text \
     -H "Content-Type: application/json" \
     -d '{"input": ["This is a sample text for generating embeddings."], "model": "example-model-id", "dimensions": 128, "modelConfiguration": {"someParameter": "value"}, "requestId": "unique-request-id"}'
```

<!-- type: tab-end -->

### Response

**Status:** `200`

```json
{
  "embeddings": [
    [
      0.1,
      0.2,
      0.3,
      0.4,
      0.5
    ]
  ],
  "modelId": "domo.domo_ai.domo-embed-text-multilingual-v1:cohere"
}
```

- **embeddings**: An array of numeric values representing the computed embeddings for the input text.
- **modelId**: The identifier of the model used for generating the embeddings.

### Error Responses

| Status Code | Description |
|-------------|-------------|
| `403`       | Forbidden   |
| `409`       | Conflict    |

---

## Image Embeddings

**Method:** `POST`  
**Endpoint:** `/api/ai/v1/embedding/image`

Generate image embeddings based on the given image input.

### Path Parameters

_None_

### Query Parameters

_None_

### Request Body

Text Embedding AI Service Request.

| Parameter           | Type              | Required | Description                                                                                                            |
|---------------------|-------------------|----------|------------------------------------------------------------------------------------------------------------------------|
| `input`             | array             | No       | The input images to embed. Example format: base64 encoded images.                                                      |
| `model`             | string            | No       | The ID of the model to use for Image Embedding. The specified model must be configured for the Image Embedding AI Service by an Admin. |
| `dimensions`        | integer (int32)   | No       | The number of dimensions for the generated embeddings.                                                                 |
| `modelConfiguration`| object            | No       | Additional model-specific configuration parameter key-value pairs.                                                     |
| `requestId`         | string (uuid)     | No       | A unique identifier for the request.                                                                                   |

### Request Example

<!--
type: tab
title: JavaScript
-->

```javascript
fetch('/api/ai/v1/embedding/image', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    input: ["example-string"],
    model: "example-string",
    dimensions: 42,
    modelConfiguration: {},
    requestId: "1bafa48d-7180-49c6-8c4f-d0bb38dd4f00"
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
import requests

url = '/api/ai/v1/embedding/image'
headers = {
    'Content-Type': 'application/json'
}
data = {
    "input": ["example-string"],
    "model": "example-string",
    "dimensions": 42,
    "modelConfiguration": {},
    "requestId": "1bafa48d-7180-49c6-8c4f-d0bb38dd4f00"
}

response = requests.post(url, headers=headers, json=data)
print(response.json())
```

<!--
type: tab
title: cURL
-->

```bash
curl -X POST /api/ai/v1/embedding/image \
-H "Content-Type: application/json" \
-d '{
  "input": ["example-string"],
  "model": "example-string",
  "dimensions": 42,
  "modelConfiguration": {},
  "requestId": "1bafa48d-7180-49c6-8c4f-d0bb38dd4f00"
}'
```

<!-- type: tab-end -->

### Response

**Status:** `200`

```json
{
  "embeddings": [
    [
      0.1,
      0.2,
      0.3,
      0.4,
      0.5
    ]
  ],
  "modelId": "domo.domo_ai.domo-embed-text-multilingual-v1:cohere"
}
```

### Error Responses

| Status Code | Description |
|-------------|-------------|
| `403`       | Forbidden   |
| `409`       | Conflict    |

---

