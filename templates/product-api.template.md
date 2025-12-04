## {{SUMMARY}}

**Method:** `{{HTTP_METHOD}}`
**Endpoint:** `{{ENDPOINT_PATH}}`

{{DESCRIPTION}}

### Path Parameters

{{PATH_PARAMETERS_TABLE}}

### Query Parameters

{{QUERY_PARAMETERS_TABLE}}

### Request Body

{{REQUEST_BODY_DESCRIPTION}}

{{REQUEST_BODY_TABLE}}

{{NESTED_OBJECT_TABLES}}

### Request Example

<!--
type: tab
title: JavaScript
-->

```javascript
fetch('https://<instance>.domo.com{{ENDPOINT_PATH}}', {
  method: '{{HTTP_METHOD}}',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({{REQUEST_BODY_EXAMPLE}})
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

url = "https://<instance>.domo.com{{ENDPOINT_PATH}}"
headers = {
    "Content-Type": "application/json"
}
data = {{PYTHON_REQUEST_BODY}}

response = requests.post(url, headers=headers, json=data)
print(response.json())
```

<!--
type: tab
title: cURL
-->

```bash
curl -X {{HTTP_METHOD}} "https://<instance>.domo.com{{ENDPOINT_PATH}}" \
  -H "Content-Type: application/json" \
  -d '{{REQUEST_BODY_EXAMPLE}}'
```

<!-- type: tab-end -->

### Response

**Status:** `{{SUCCESS_STATUS_CODE}}`

```json
{{RESPONSE_EXAMPLE}}
```

{{RESPONSE_FIELD_DESCRIPTIONS}}

### Error Responses

{{ERROR_RESPONSES}}

---
