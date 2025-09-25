# Product API Template

> **Note:** This is a template for generating API documentation from Swagger YAML files. Replace placeholders with actual values from the YAML input.

---

# mako API

> **Description:** Jupyter and AI Projects

---

## Create a new FileSet

**Method:** `post`  
**Endpoint:** `/api/files/v1/filesets`

**Path Parameters:**

_None_

**Query Parameters:**

_None_

**Request Body Parameters:**

| Parameter   | Type   | Required | Description                   |
| ----------- | ------ | -------- | ----------------------------- |
| name        | string | true     | The name for the file set.    |
| description | string | false    | A description for the file set.|

<!--
type: tab
title: Javascript
-->

```javascript
fetch('/api/files/v1/filesets', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        name: 'My New FileSet',
        description: 'A description for my fileset',
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
import requests

url = '/api/files/v1/filesets'
data = {
    "name": "My New FileSet",
    "description": "A description for my fileset"
}

response = requests.post(url, json=data)
print(response.json())
```

<!-- type: tab-end -->

---

**Response:**

```json
{
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
```

---

## Get a FileSet by ID

**Method:** `get`  
**Endpoint:** `/api/files/v1/filesets/{fileSetId}`

**Path Parameters:**

| Parameter  | Type   | Required | Description                          |
| ---------- | ------ | -------- | ------------------------------------ |
| fileSetId  | string | true     | The ID of the FileSet to retrieve.   |

**Query Parameters:**

_None_

**Request Body Parameters:**

_None_

<!--
type: tab
title: Javascript
-->

```javascript
const fileSetId = 'e49f188e-be98-451d-ba0f-ada1157bb656';
fetch(`/api/files/v1/filesets/${fileSetId}`, {
    method: 'GET',
    headers: {
        'Accept': 'application/json',
    }
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
import requests

fileSetId = 'e49f188e-be98-451d-ba0f-ada1157bb656'
url = f'/api/files/v1/filesets/{fileSetId}'

response = requests.get(url)
print(response.json())
```

<!-- type: tab-end -->

---

**Response:**

```json
{
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
```

---

## List Files and Directories for a FileSet

**Method:** `post`  
**Endpoint:** `/api/files/v1/filesets/{fileSetId}/files/search`

**Path Parameters:**

| Parameter  | Type   | Required | Description                                |
| ---------- | ------ | -------- | ------------------------------------------ |
| fileSetId  | string | true     | The ID of the FileSet to search within.    |

**Query Parameters:**

| Parameter         | Type    | Required | Description                                                |
| ----------------- | ------- | -------- | ---------------------------------------------------------- |
| directoryPath     | string  | false    | The path to the directory within the FileSet, if applicable.|
| immediateChildren | boolean | false    | Whether to list only immediate children of the specified directory.|
| limit             | integer | false    | The maximum number of Files to return.                     |
| next              | string  | false    | The pagination token for the next set of results.          |

**Request Body Parameters:**

| Parameter  | Type  | Description                              |
| ---------- | ----- | ---------------------------------------- |
| fieldSort  | array | A list of field sort criteria to apply to the search. |
| filters    | array | A list of filters to apply to the search. |

<!--
type: tab
title: Javascript
-->

```javascript
const fileSetId = 'e49f188e-be98-451d-ba0f-ada1157bb656';
fetch(`/api/files/v1/filesets/${fileSetId}/files/search`, {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        fieldSort: [],
        filters: [],
    })
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
import requests

fileSetId = 'e49f188e-be98-451d-ba0f-ada1157bb656'
url = f'/api/files/v1/filesets/{fileSetId}/files/search'

data = {
    "fieldSort": [],
    "filters": []
}

response = requests.post(url, json=data)
print(response.json())
```

<!-- type: tab-end -->

---

**Response:**

```json
{
  "files": [
    {
      "id": "7150e608-c3a9-4b40-ac2d-eb182cc98c6f",
      "path": "sample/directory/path/PaidTimeOffPolicy.pdf",
      "name": "PaidTimeOffPolicy.pdf",
      "fileType": "DOCUMENT",
      "contentType": "application/pdf",
      "size": 69502,
      "hash": "ce0da94c741125c597cf3d54a3202cebdc16d7fe1074698219f724654595221c",
      "hashAlgorithm": "SHA_256_HEX",
      "downloadUrl": "",
      "created": "2025-07-28T21:47:39.814456Z",
      "createdBy": 27,
      "connectorKey": null,
      "indexStatus": null,
      "indexReason": null
    }
  ],
  "pageContext": {
    "next": "eyJpZCI6ImJiZjU3MDVkLWU1ZjQtNGRkMy1hMTUyLTgzNzdhNTYwYzY0YiIsInBhdGgiOiJzYW1wbGUvZGlyZWN0b3J5L3BhdGgiLCJuYW1lIjoicGF0aCIsInNpemUiOm51bGwsImNyZWF0ZWQiOiIyMDI1LTA3LTI5VDE4OjA3OjI2Ljc2MzE5M1oifQ=="
  }
}
```

---