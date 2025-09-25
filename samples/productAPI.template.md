# Product API Template

> **Note:** This is a template for generating API documentation from Swagger YAML files. Replace placeholders with actual values from the YAML input.

---

# {{API_NAME}} API

> **Description:** {{API_DESCRIPTION}}

---

## {{ENDPOINT_NAME}}

**Method:** `{{HTTP_METHOD}}`  
**Endpoint:** `{{ENDPOINT_PATH}}`

**Path Parameters:**

{{#if PATH_PARAMETERS}}
| Parameter | Type | Required | Description |
| --------- | ------ | -------- | ----------- |
{{#each PATH_PARAMETERS}}
| {{name}} | {{type}} | {{required}} | {{description}} |
{{/each}}
{{else}}
_None_
{{/if}}

**Query Parameters:**

{{#if QUERY_PARAMETERS}}
| Parameter | Type | Required | Description |
| --------- | ------ | -------- | ----------- |
{{#each QUERY_PARAMETERS}}
| {{name}} | {{type}} | {{required}} | {{description}} |
{{/each}}
{{else}}
_None_
{{/if}}

**Request Body Parameters:**

{{#if REQUEST_BODY_PARAMETERS}}
| Parameter | Type | Required | Description |
| --------- | ------ | -------- | ----------- |
{{#each REQUEST_BODY_PARAMETERS}}
| {{name}} | {{type}} | {{required}} | {{description}} |
{{/each}}
{{else}}
_None_
{{/if}}

<!--
type: tab
title: Javascript
-->

```javascript
{
  JAVASCRIPT_CODE_EXAMPLE;
}
```

<!--
type: tab
title: Python
-->

```python
{PYTHON_CODE_EXAMPLE}
```

<!-- type: tab-end -->

---

**Response:**

```json
{{RESPONSE_EXAMPLE}}
```

---
