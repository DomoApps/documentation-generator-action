# Product API Template

> **Note:** This is a template for generating API documentation from Swagger YAML files. Replace placeholders with actual values from the YAML input.

---

# mako API

> **Description:** Jupyter and AI Projects

---

## Create a new FileSet

**Method:** `POST`  
**Endpoint:** `/api/files/v1/filesets`

**Path Parameters:**

_None_

**Query Parameters:**

_None_

**Request Body Parameters:**

| Parameter    | Type    | Required | Description                                        |
|--------------|---------|----------|----------------------------------------------------|
| name         | string  | true     | The name for the file set.                         |
| description  | string  | false    | A description for the file set.                    |
| connector    | string  | false    | The connector that powers the file set.            |
| aiEnabled    | boolean | false    | Indicates whether AI features are enabled for the file set. |

<!--
type: tab
title: Javascript
-->

```javascript
let requestBody = {
  name: "Example FileSet",
  description: "A description for the FileSet",
  connector: "DOMO",
  aiEnabled: false
};

fetch('/api/files/v1/filesets', {
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

url = 'http://example.com/api/files/v1/filesets'
request_body = {
    "name": "Example FileSet",
    "description": "A description for the FileSet",
    "connector": "DOMO",
    "aiEnabled": False
}

response = requests.post(url, json=request_body)

if response.status_code == 201:
    print('Success:', response.json())
else:
    print('Failed:', response.status_code, response.json())
```

<!-- type: tab-end -->

---

**Response:**

```json
{
  "201": {
    "id": "e49f188e-be98-451d-ba0f-ada1157bb656",
    "name": "Policies (2025)",
    "description": "Location for all new and updated policies for FY2025",
    "aiEnabled": false,
    "indexStatus": null,
    "batchType": "INCREMENTAL",
    "connector": "DOMO",
    "created": "2025-07-28T20:17:43.958479Z",
    "createdBy": 27,
    "updated": "2025-07-28T20:17:43.958479Z",
    "updatedBy": 27,
    "owner": "27",
    "accountId": 0,
    "connectorContext": null,
    "permission": "OWNER",
    "size": 0,
    "fileCount": 0
  }
}
```

---

## Get a FileSet by ID

**Method:** `GET`  
**Endpoint:** `/api/files/v1/filesets/{fileSetId}`

**Path Parameters:**

| Parameter | Type   | Required | Description                      |
|-----------|--------|----------|----------------------------------|
| fileSetId | string | true     | The ID of the FileSet to retrieve.|

**Query Parameters:**

_None_

**Request Body Parameters:**

_None_

<!--
type: tab
title: Javascript
-->

```javascript
let fileSetId = "e49f188e-be98-451d-ba0f-ada1157bb656";

fetch(`/api/files/v1/filesets/${fileSetId}`, {
  method: 'GET',
  headers: {
    'Content-Type': 'application/json'
  }
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

file_set_id = "e49f188e-be98-451d-ba0f-ada1157bb656"
url = f'http://example.com/api/files/v1/filesets/{file_set_id}'

response = requests.get(url)

if response.status_code == 200:
    print('Success:', response.json())
else:
    print('Failed:', response.status_code, response.json())
```

<!-- type: tab-end -->

---

**Response:**

```json
{
  "200": {
    "id": "e49f188e-be98-451d-ba0f-ada1157bb656",
    "name": "Policies (2025)",
    "description": "Location for all new and updated policies for FY2025",
    "aiEnabled": false,
    "indexStatus": null,
    "batchType": "INCREMENTAL",
    "connector": "DOMO",
    "created": "2025-07-28T20:17:43.958479Z",
    "createdBy": 27,
    "updated": "2025-07-28T20:17:43.958479Z",
    "updatedBy": 27,
    "owner": "27",
    "accountId": 0,
    "connectorContext": null,
    "permission": "OWNER",
    "size": 0,
    "fileCount": 0
  }
}
```