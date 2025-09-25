# FileSets API (BETA)

> **BETA:** This API is currently in BETA and is subject to change. Endpoints, request/response formats, and functionality may change without notice.

This API reference documents the endpoints for managing FileSets and Files in Domo. These endpoints allow you to upload, download, query, and manage Files and FileSets programmatically.

---

## Get File by Path

**Method:** `GET`  
**Endpoint:** `/api/files/v1/filesets/{filesetId}/path?path={filePath}`

**Path Parameters:**

- `filesetId` (String, required): The ID of the FileSet.

**Query Parameters:**

- `path` (String, required): The path to the File within the FileSet.

<!--
type: tab
title: Javascript
-->

```js
fetch(
  'https://{instance}.domo.com/api/files/v1/filesets/{filesetId}/path?path={filePath}',
  {
    method: 'GET',
    headers: {
      'X-DOMO-Developer-Token': '<your-token-here>',
      'Content-Type': 'application/json',
    },
  },
)
  .then((response) => response.json())
  .then((result) => console.log(result))
  .catch((error) => console.error(`Error: ${error}`));
```

<!--
type: tab
title: Python
-->

```python
import httpx

headers = {
    'X-DOMO-Developer-Token': '<your-token-here>',
    'Content-Type': 'application/json',
}
url = 'https://{instance}.domo.com/api/files/v1/filesets/{filesetId}/path?path={filePath}'

with httpx.Client() as client:
    response = client.get(url, headers=headers)
    print(response.json())
```

<!-- type: tab-end -->

**Response:**

```json
{
  "id": "00000000-0000-0000-0000-000000000001",
  "path": "rules.txt",
  "name": "rules.txt",
  "fileType": "TEXT",
  "contentType": "text/plain",
  "size": 12345,
  "hash": "fakehash00000000000000000000000000000000000000000000000000000000000001",
  "hashAlgorithm": "SHA_256_HEX",
  "downloadUrl": null,
  "created": "2025-01-01T00:00:00.000Z",
  "createdBy": 111111111,
  "connectorKey": null,
  "indexStatus": null,
  "indexReason": null
}
```

---

## Get File by Id

**Method:** `GET`  
**Endpoint:** `/api/files/v1/filesets/{filesetId}/files/{fileId}`

**Path Parameters:**

- `filesetId` (String, required): The ID of the FileSet.
- `fileId` (String, required): The ID of the file.

<!--
type: tab
title: Javascript
-->

```js
fetch(
  'https://{instance}.domo.com/api/files/v1/filesets/{filesetId}/files/{fileId}',
  {
    method: 'GET',
    headers: {
      'X-DOMO-Developer-Token': '<your-token-here>',
      'Content-Type': 'application/json',
    },
  },
)
  .then((response) => response.json())
  .then((result) => console.log(result))
  .catch((error) => console.error(`Error: ${error}`));
```

<!--
type: tab
title: Python
-->

```python
import httpx

headers = {
    'X-DOMO-Developer-Token': '<your-token-here>',
    'Content-Type': 'application/json',
}
url = 'https://{instance}.domo.com/api/files/v1/filesets/{filesetId}/files/{fileId}'

with httpx.Client() as client:
    response = client.get(url, headers=headers)
    print(response.json())
```

<!-- type: tab-end -->

**Response:**

```json
{
  "id": "00000000-0000-0000-0000-000000000002",
  "path": "rules.txt",
  "name": "rules.txt",
  "fileType": "TEXT",
  "contentType": "text/plain",
  "size": 12345,
  "hash": "fakehash00000000000000000000000000000000000000000000000000000000000002",
  "hashAlgorithm": "SHA_256_HEX",
  "downloadUrl": "https://instance-name.domo.com/api/files/v1/filesets/00000000-0000-0000-0000-000000000010/files/00000000-0000-0000-0000-000000000002/download",
  "created": "2025-01-01T00:00:00.000Z",
  "createdBy": 111111111,
  "connectorKey": null,
  "indexStatus": null,
  "indexReason": null
}
```

---

## Download File by Id

**Method:** `GET`  
**Endpoint:** `/api/files/v1/filesets/{filesetId}/files/{fileId}/download`

**Path Parameters:**

- `filesetId` (String, required): The ID of the FileSet.
- `fileId` (String, required): The ID of the file.

<!--
type: tab
title: Javascript
-->

```js
fetch(
  'https://{instance}.domo.com/api/files/v1/filesets/{filesetId}/files/{fileId}/download',
  {
    method: 'GET',
    headers: {
      'X-DOMO-Developer-Token': '<your-token-here>',
      'Content-Type': 'application/json',
    },
  },
)
  .then((response) => response.blob()) // Use .blob() for file downloads
  .then((blob) => {
    // Example: create a download link
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'filename.ext'; // Set desired file name
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);
  })
  .catch((error) => console.error(`Error: ${error}`));
```

<!--
type: tab
title: Python
-->

```python
import httpx

headers = {
    'X-DOMO-Developer-Token': '<your-token-here>',
    'Content-Type': 'application/json',
}
url = 'https://{instance}.domo.com/api/files/v1/filesets/{filesetId}/files/{fileId}/download'

with httpx.Client() as client:
    response = client.get(url, headers=headers)
    with open('filename.ext', 'wb') as f:
        f.write(response.content)
    print('File downloaded as filename.ext')
```

<!-- type: tab-end -->

**Response:**

- Returns the FileSet contents as a download (binary/text stream).

---

## Query Files

**Method:** `POST`  
**Endpoint:** `/api/files/v1/filesets/{filesetId}/query`

**Description:** Queries the Files and directories within a FileSet using a search query.

**Path Parameters:**

| Parameter | Type   | Required | Description           |
| --------- | ------ | -------- | --------------------- |
| filesetId | String | Yes      | The ID of the FileSet |

**Request Body Parameters:**

| Parameter     | Type    | Required | Description                          |
| ------------- | ------- | -------- | ------------------------------------ |
| query         | String  | Yes      | Text to search for in Files          |
| directoryPath | String  | No       | Limit search to a specific directory |
| topK          | Integer | No       | Maximum number of results to return  |

<!--
type: tab
title: Javascript
-->

```js
// Example: Search for text in documents, limited to 5 results
fetch(`https://{instance}.domo.com/api/files/v1/filesets/${filesetId}/query`, {
  method: 'POST',
  headers: {
    'X-DOMO-Developer-Token': '<your-token-here>',
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    query: 'quarterly sales data', // Text to search for in files
    directoryPath: 'reports/quarterly', // Optional: Limit search to specific directory
    topK: 5, // Optional: Maximum number of results to return
  }),
})
  .then((response) => response.json())
  .then((result) => {
    console.log(`Found ${result.matches.length} matching files:`);
    result.matches.forEach((match) => {
      console.log(`- ${match.node.name} (Score: ${match.score})`);
    });
  })
  .catch((error) => console.error(`Error: ${error}`));
```

<!--
type: tab
title: Python
-->

```python
import httpx

headers = {
    'X-DOMO-Developer-Token': '<your-token-here>',
    'Content-Type': 'application/json',
}
url = 'https://{instance}.domo.com/api/files/v1/filesets/{filesetId}/query'
data = {
    'query': 'quarterly sales data',     # Text to search for in files
    'directoryPath': 'reports/quarterly', # Optional: Limit search to specific directory
    'topK': 5,                           # Optional: Maximum number of results to return
}

with httpx.Client() as client:
    response = client.post(url, headers=headers, json=data)
    result = response.json()

    print(f"Found {len(result['matches'])} matching files:")
    for match in result['matches']:
        print(f"- {match['node']['name']} (Score: {match['score']})")
```

<!-- type: tab-end -->

**Response:**

```json
{
  "matches": [
    {
      "id": "00000000-0000-0000-0000-000000000003",
      "node": {
        "id": "00000000-0000-0000-0000-000000000003",
        "path": "reports/quarterly/Q2-2024-sales.pdf",
        "name": "Q2-2024-sales.pdf",
        "fileType": "FILE",
        "contentType": "application/pdf",
        "size": 12345,
        "created": 1718826000000,
        "type": "TEXT"
      },
      "score": 0.89
    },
    {
      "id": "00000000-0000-0000-0000-000000000004",
      "node": {
        "id": "00000000-0000-0000-0000-000000000004",
        "path": "reports/quarterly/Q1-2024-sales.pdf",
        "name": "Q1-2024-sales.pdf",
        "fileType": "FILE",
        "contentType": "application/pdf",
        "size": 10245,
        "created": 1712066400000,
        "type": "TEXT"
      },
      "score": 0.76
    }
  ]
}
```

---

## Upload File

**Method:** `POST`  
**Endpoint:** `/api/files/v1/filesets/{filesetId}/files`

**Path Parameters:**

- `filesetId` (String, required): The ID of the FileSet.

<!--
type: tab
title: Javascript
-->

```js
// Prepare the file and metadata for upload
const formdata = new FormData();
formdata.append('file', fileInput.files[0], 'rules.txt');
formdata.append('createFileRequest', JSON.stringify({ directoryPath: '' }));

const requestOptions = {
  method: 'POST',
  headers: {
    'X-DOMO-Developer-Token': '<your-token-here>',
    // Note: Do not set Content-Type header; browser will set it automatically for FormData
  },
  body: formdata,
  redirect: 'follow',
};

fetch(
  'https://{instance}.domo.com/api/files/v1/filesets/{filesetId}/files',
  requestOptions,
)
  .then((response) => response.json())
  .then((result) => console.log(result))
  .catch((error) => console.error(`Error: ${error}`));
```

<!--
type: tab
title: Python
-->

```python
import httpx

headers = {
    'X-DOMO-Developer-Token': '<your-token-here>',
}
url = 'https://{instance}.domo.com/api/files/v1/filesets/{filesetId}/files'

with open('rules.txt', 'rb') as file_obj:
    files = {
        'file': ('rules.txt', file_obj, 'text/plain'),
        'createFileRequest': (None, '{"directoryPath": ""}', 'application/json'),
    }
    with httpx.Client() as client:
        response = client.post(url, headers=headers, files=files)
        print(response.json())
```

<!-- type: tab-end -->

**Response:**

```json
{
  "id": "00000000-0000-0000-0000-000000000004",
  "path": "fab-rules.txt",
  "name": "fab-rules.txt",
  "fileType": "TEXT",
  "contentType": "text/plain",
  "size": 12345,
  "created": "2025-01-01T00:00:00.000Z",
  "createdBy": 111111111
}
```

---

## Search Files in FileSet

**Method:** `POST`  
**Endpoint:** `/api/files/v1/filesets/{filesetId}/files/search`

**Description:** Lists Files and directories within a FileSet, optionally filtered by directory path or other criteria.

**Path Parameters:**

| Parameter | Type   | Required | Description           |
| --------- | ------ | -------- | --------------------- |
| filesetId | String | Yes      | The ID of the FileSet |

**Query Parameters:**

| Parameter         | Type    | Required | Default | Description                                           |
| ----------------- | ------- | -------- | ------- | ----------------------------------------------------- |
| directoryPath     | String  | No       | null    | Filter Files by specific directory path               |
| immediateChildren | Boolean | No       | false   | If true, returns only immediate children of directory |
| limit             | Integer | No       | 100     | Maximum number of results                             |
| next              | String  | No       | null    | Pagination token for fetching next set of results     |

**Request Body Parameters:**

| Parameter   | Type  | Required | Description                                              |
| ----------- | ----- | -------- | -------------------------------------------------------- |
| fieldSort   | Array | No       | Sort options for results. Array of FieldSort Objects.    |
| filters     | Array | No       | Filter criteria for the search. Array of Filter Objects. |
| dateFilters | Array | No       | Date-based filter criteria. Array of DateFilter Objects. |

**FieldSort Object Properties:**

| Property | Type   | Description                     |
| -------- | ------ | ------------------------------- |
| field    | String | Field name to sort by           |
| order    | String | Sort direction: 'ASC' or 'DESC' |

**DateFilter Object Properties:**

| Property | Type    | Description                                  |
| -------- | ------- | -------------------------------------------- |
| field    | String  | Field name for date filter (e.g., 'created') |
| start    | String  | Start timestamp as ISO string                |
| end      | String  | End timestamp as ISO string                  |
| not      | Boolean | If true, inverts the date filter match       |

> **Note:** The Filter, FieldSort, and DateFilter objects have the same structure as in the Search FileSets endpoint.

<!--
type: tab
title: Javascript
-->

```js
// Example 1: List all files in FileSet
fetch(
  `https://{instance}.domo.com/api/files/v1/filesets/${filesetId}/files/search`,
  {
    method: 'POST',
    headers: {
      'X-DOMO-Developer-Token': '<your-token-here>',
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({}),
  },
)
  .then((response) => response.json())
  .then((result) => console.log(result.files))
  .catch((error) => console.error(`Error: ${error}`));

// Example 2: Advanced search with directory path and filters
fetch(
  `https://{instance}.domo.com/api/files/v1/filesets/${filesetId}/files/search?directoryPath=reports&limit=20`,
  {
    method: 'POST',
    headers: {
      'X-DOMO-Developer-Token': '<your-token-here>',
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      // Sort by file name in ascending order
      fieldSort: [
        {
          field: 'name',
          order: 'ASC',
        },
      ],
      // Filter files by name
      filters: [
        {
          field: 'name',
          value: ['.pdf'],
          operator: 'LIKE',
          not: false,
        },
      ],
      // Filter files created in past 30 days
      dateFilters: [
        {
          field: 'created',
          start: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(), // 30 days ago as ISO string
          end: new Date().toISOString(), // Current time as ISO string
        },
      ],
    }),
  },
)
  .then((response) => response.json())
  .then((result) => console.log(result.files))
  .catch((error) => console.error(`Error: ${error}`));
```

<!--
type: tab
title: Python
-->

```python
import httpx
import time

headers = {
    'X-DOMO-Developer-Token': '<your-token-here>',
    'Content-Type': 'application/json',
}

# Example 1: List all files in FileSet
url = f'https://{{instance}}.domo.com/api/files/v1/filesets/{filesetId}/files/search'
data = {}

with httpx.Client() as client:
    response = client.post(url, headers=headers, json=data)
    print(response.json())

# Example 2: Advanced search with directory path and filters
url = f'https://{{instance}}.domo.com/api/files/v1/filesets/{filesetId}/files/search?directoryPath=reports&limit=20'
from datetime import datetime, timedelta

current_time = datetime.now()
thirty_days_ago = current_time - timedelta(days=30)

data = {
    # Sort by file name in ascending order
    "fieldSort": [
        {
            "field": "name",
            "order": "ASC"
        }
    ],
    # Filter files by name
    "filters": [
        {
            "field": "name",
            "value": [".pdf"],
            "operator": "LIKE",
            "not": False
        }
    ],
    # Filter files created in past 30 days
    "dateFilters": [
        {
            "field": "created",
            "start": thirty_days_ago.isoformat(),  # ISO format string
            "end": current_time.isoformat()        # ISO format string
        }
    ]
}

with httpx.Client() as client:
    response = client.post(url, headers=headers, json=data)
    print(response.json())
```

<!-- type: tab-end -->

**Response:**

```json
{
  "files": [
    {
      "id": "00000000-0000-0000-0000-000000000001",
      "path": "reports/quarterly-report.pdf",
      "name": "quarterly-report.pdf",
      "fileType": "FILE",
      "contentType": "application/pdf",
      "size": 234567,
      "hash": "hash123456789abcdef",
      "hashAlgorithm": "SHA_256_HEX",
      "downloadUrl": "https://instance.domo.com/api/files/v1/filesets/00000000-0000-0000-0000-000000000010/files/00000000-0000-0000-0000-000000000001/download",
      "created": "2024-06-15T00:00:00.000Z",
      "createdBy": 111111111
    },
    {
      "id": "00000000-0000-0000-0000-000000000002",
      "path": "reports/annual-report.pdf",
      "name": "annual-report.pdf",
      "fileType": "FILE",
      "contentType": "application/pdf",
      "size": 456789,
      "hash": "hash987654321fedcba",
      "hashAlgorithm": "SHA_256_HEX",
      "downloadUrl": "https://instance.domo.com/api/files/v1/filesets/00000000-0000-0000-0000-000000000010/files/00000000-0000-0000-0000-000000000002/download",
      "created": "2024-06-10T00:00:00.000Z",
      "createdBy": 111111111
    }
  ],
  "pageContext": {
    "next": "eyJpZCI6IjEyMzQ1Njc4OTAifQ=="
  }
}
```

---

## Delete Files by Path

**Method:** `DELETE`  
**Endpoint:** `/api/files/v1/filesets/{filesetId}/path?path={filePath}`

**Path Parameters:**

- `filesetId` (String, required): The ID of the FileSet.

**Query Parameters:**

- `path` (String, required): The path to the File within the FileSet.

<!--
type: tab
title: Javascript
-->

```js
fetch(
  'https://{instance}.domo.com/api/files/v1/filesets/{filesetId}/path?path=rules.txt',
  {
    method: 'DELETE',
    headers: {
      'X-DOMO-Developer-Token': '<your-token-here>',
      'Content-Type': 'application/json',
    },
  },
)
  .then((response) => response.json())
  .then((result) => console.log(result))
  .catch((error) => console.error(`Error: ${error}`));
```

<!--
type: tab
title: Python
-->

```python
import httpx

headers = {
    'X-DOMO-Developer-Token': '<your-token-here>',
    'Content-Type': 'application/json',
}
url = 'https://{instance}.domo.com/api/files/v1/filesets/{filesetId}/path?path=rules.txt'

with httpx.Client() as client:
    response = client.delete(url, headers=headers)
    print(response.json())
```

<!-- type: tab-end -->

**Response:**

```json
{
  "status": "success",
  "message": "File deleted successfully."
}
```

---

## Delete File by Id

**Method:** `DELETE`  
**Endpoint:** `/api/files/v1/filesets/{filesetId}/files/{fileId}`

**Path Parameters:**

- `filesetId` (String, required): The ID of the FileSet.
- `fileId` (String, required): The ID of the File.

<!--
type: tab
title: Javascript
-->

```js
fetch(
  'https://{instance}.domo.com/api/files/v1/filesets/{filesetId}/files/{fileId}',
  {
    method: 'DELETE',
    headers: {
      'X-DOMO-Developer-Token': '<your-token-here>',
      'Content-Type': 'application/json',
    },
  },
)
  .then((response) => response.json())
  .then((result) => console.log(result))
  .catch((error) => console.error(`Error: ${error}`));
```

<!--
type: tab
title: Python
-->

```python
import httpx

headers = {
    'X-DOMO-Developer-Token': '<your-token-here>',
    'Content-Type': 'application/json',
}
url = 'https://{instance}.domo.com/api/files/v1/filesets/{filesetId}/files/{fileId}'

with httpx.Client() as client:
    response = client.delete(url, headers=headers)
    print(response.json())
```

<!-- type: tab-end -->

**Response:**

```json
{
  "status": "success",
  "message": "File deleted successfully."
}
```

---

## Search FileSets

**Method:** `POST`  
**Endpoint:** `/api/files/v1/filesets/search`

**Description:** Searches for FileSets in your Domo instance using filters and criteria.

**Query Parameters:**

| Parameter | Type    | Required | Default | Description                         |
| --------- | ------- | -------- | ------- | ----------------------------------- |
| limit     | Integer | No       | 100     | Maximum number of results to return |
| offset    | Integer | No       | 0       | Pagination offset                   |

**Request Body Parameters:**

| Parameter   | Type  | Required | Description                                              |
| ----------- | ----- | -------- | -------------------------------------------------------- |
| fieldSort   | Array | No       | Sort options for results. Array of FieldSort Objects.    |
| filters     | Array | No       | Filter criteria for the search. Array of Filter Objects. |
| dateFilters | Array | No       | Date-based filter criteria. Array of DateFilter Objects. |

**Filter Object Properties:**

| Property | Type    | Description                                                                                                                   |
| -------- | ------- | ----------------------------------------------------------------------------------------------------------------------------- |
| field    | String  | Field name to filter on (e.g., 'name', 'description')                                                                         |
| value    | Array   | Values to match against                                                                                                       |
| not      | Boolean | If true, inverts the filter match                                                                                             |
| operator | String  | Operation type: 'EQUALS', 'GREATER_THAN', 'LESS_THAN', 'LESS_THAN_OR_EQUAL', 'GREATER_THAN_OR_EQUAL', 'IN', 'IS_NULL', 'LIKE' |

**FieldSort Object Properties:**

| Property | Type   | Description                     |
| -------- | ------ | ------------------------------- |
| field    | String | Field name to sort by           |
| order    | String | Sort direction: 'ASC' or 'DESC' |

**DateFilter Object Properties:**

| Property | Type    | Description                                  |
| -------- | ------- | -------------------------------------------- |
| field    | String  | Field name for date filter (e.g., 'created') |
| start    | String  | Start timestamp as ISO string                |
| end      | String  | End timestamp as ISO string                  |
| not      | Boolean | If true, inverts the date filter match       |

> **Note:** To list all FileSets, send an empty object as the body. To filter, provide filter parameters in the body.

<!--
type: tab
title: Javascript
-->

```js
// Example 1: List all FileSets (empty search)
fetch(
  'https://{instance}.domo.com/api/files/v1/filesets/search?limit=50&offset=0',
  {
    method: 'POST',
    headers: {
      'X-DOMO-Developer-Token': '<your-token-here>',
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({}),
  },
)
  .then((response) => response.json())
  .then((result) => console.log(result.fileSets))
  .catch((error) => console.error(`Error: ${error}`));

// Example 2: Advanced search with filters and sorting
fetch('https://{instance}.domo.com/api/files/v1/filesets/search', {
  method: 'POST',
  headers: {
    'X-DOMO-Developer-Token': '<your-token-here>',
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    // Sort by name in ascending order
    fieldSort: [
      {
        field: 'name',
        order: 'ASC',
      },
    ],
    // Filter FileSet by name containing "Marketing"
    filters: [
      {
        field: 'name',
        value: ['Marketing'],
        operator: 'LIKE',
        not: false,
      },
    ],
    // Filter FileSet created between two dates
    dateFilters: [
      {
        field: 'created',
        start: new Date('2024-06-01').toISOString(), // June 1, 2024 as ISO string
        end: new Date('2024-06-30').toISOString(), // June 30, 2024 as ISO string
      },
    ],
  }),
})
  .then((response) => response.json())
  .then((result) => console.log(result.fileSets))
  .catch((error) => console.error(`Error: ${error}`));
```

<!--
type: tab
title: Python
-->

```python
import httpx

headers = {
    'X-DOMO-Developer-Token': '<your-token-here>',
    'Content-Type': 'application/json',
}

# Example 1: List all FileSets (empty search)
url = 'https://{instance}.domo.com/api/files/v1/filesets/search?limit=50&offset=0'
data = {}

with httpx.Client() as client:
    response = client.post(url, headers=headers, json=data)
    print(response.json())

# Example 2: Advanced search with filters and sorting
url = 'https://{instance}.domo.com/api/files/v1/filesets/search'
data = {
    # Sort by name in ascending order
    "fieldSort": [
        {
            "field": "name",
            "order": "ASC"
        }
    ],
    # Filter FileSet by name containing "Marketing"
    "filters": [
        {
            "field": "name",
            "value": ["Marketing"],
            "operator": "LIKE",
            "not": False
        }
    ],
    # Filter FileSet created between two dates
    "dateFilters": [
        {
            "field": "created",
            "start": "2024-06-01T00:00:00Z",  # June 1, 2024 as ISO string
            "end": "2024-06-30T23:59:59Z"     # June 30, 2024 as ISO string
        }
    ]
}

with httpx.Client() as client:
    response = client.post(url, headers=headers, json=data)
    print(response.json())
```

<!-- type: tab-end -->

**Response:**

```json
{
  "fileSets": [
    {
      "id": "00000000-0000-0000-0000-000000000010",
      "name": "Marketing Assets",
      "description": "Contains marketing assets for campaigns",
      "created": "2024-06-15T00:00:00.000Z",
      "createdBy": 111111111,
      "updated": "2024-06-20T00:00:00.000Z",
      "updatedBy": 111111111,
      "owner": "111111111",
      "permission": "OWNER",
      "fileCount": 25
    },
    {
      "id": "00000000-0000-0000-0000-000000000011",
      "name": "Marketing Reports",
      "description": "Marketing analysis and reports",
      "created": "2024-06-10T00:00:00.000Z",
      "createdBy": 111111111,
      "updated": "2024-06-18T00:00:00.000Z",
      "updatedBy": 111111111,
      "owner": "111111111",
      "permission": "OWNER",
      "fileCount": 12
    }
  ],
  "pageContext": {
    "offset": 0,
    "limit": 50,
    "total": 2
  }
}

with httpx.Client() as client:
    response = client.post(url, headers=headers, json=data)
    print(response.json())
```

<!-- type: tab-end -->

**Response:**

```json
{
  "id": "6fbf49f2-b1eb-4dd9-b1ea-4a477480965b",
  "name": "Unstructured",
  "description": "",
  "aiEnabled": true,
  "indexStatus": null,
  "batchType": "INCREMENTAL",
  "connector": "DOMO",
  "created": "2025-04-19T22:52:23.470150Z",
  "createdBy": 403368057,
  "updated": "2025-06-17T20:14:13.298781Z",
  "updatedBy": 403368057,
  "owner": "403368057",
  "accountId": 0,
  "connectorContext": null,
  "permission": "OWNER",
  "size": 730812,
  "fileCount": 2
}
```

---

## Create FileSet

**Method:** `POST`  
**Endpoint:** `/api/files/v1/filesets`

**Request Body Parameters:**

| Parameter        | Type    | Required | Description                                                            |
| ---------------- | ------- | -------- | ---------------------------------------------------------------------- |
| name             | String  | Yes      | The name of the FileSet                                                |
| accountId        | Integer | No       | The account ID to associate (nullable)                                 |
| connectorContext | Object  | No       | Connector context for the FileSet (nullable). ConnectorContext Object. |
| description      | String  | No       | Description for the FileSet                                            |

**ConnectorContext Object Properties:**

| Property     | Type   | Required | Description                                |
| ------------ | ------ | -------- | ------------------------------------------ |
| connector    | String | Yes      | The connector key                          |
| relativePath | String | No       | Relative path for the connector (nullable) |

<!--
type: tab
title: Javascript
-->

```js
fetch('https://{instance}.domo.com/api/files/v1/filesets', {
  method: 'POST',
  headers: {
    'X-DOMO-Developer-Token': '<your-token-here>',
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    name: 'Sample FileSet',
    description: 'A sample FileSet for demonstration purposes.',
    // accountId: 12345, // Optional
    // connectorContext: { connector: 'S3', relativePath: 'bucket/path' }, // Optional
  }),
})
  .then((response) => response.json())
  .then((result) => console.log(result))
  .catch((error) => console.error(`Error: ${error}`));
```

<!--
type: tab
title: Python
-->

```python
import httpx

headers = {
    'X-DOMO-Developer-Token': '<your-token-here>',
    'Content-Type': 'application/json',
}
url = 'https://{instance}.domo.com/api/files/v1/filesets'
data = {
    "name": "Sample FileSet",
    "description": "A sample FileSet for demonstration purposes.",
    # "accountId": 12345, # Optional
    # "connectorContext": {"connector": "S3", "relativePath": "bucket/path"}, # Optional
}

with httpx.Client() as client:
    response = client.post(url, headers=headers, json=data)
    print(response.json())
```

<!-- type: tab-end -->

**Response:**

```json
{
  "id": "00000000-0000-0000-0000-000000000012",
  "name": "Sample FileSet",
  "description": "A sample FileSet for demonstration purposes.",
  "created": "2025-01-01T00:00:00.000Z",
  "createdBy": 111111111
}
```

---

## Get FileSet by Id

**Method:** `GET`
**Endpoint:** `/api/files/v1/filesets/{filesetId}`

**Path Parameters:**

- `filesetId` (String, required): The ID of the FileSet.

<!--
type: tab
title: Javascript
-->

```js
fetch('https://{instance}.domo.com/api/files/v1/filesets/{filesetId}', {
  method: 'GET',
  headers: {
    'X-DOMO-Developer-Token': '<your-token-here>',
    'Content-Type': 'application/json',
  },
})
  .then((response) => response.json())
  .then((result) => console.log(result))
  .catch((error) => console.error(`Error: ${error}`));
```

<!--
type: tab
title: Python
-->

```python
import httpx

headers = {
    'X-DOMO-Developer-Token': '<your-token-here>',
    'Content-Type': 'application/json',
}
url = 'https://{instance}.domo.com/api/files/v1/filesets/{filesetId}'

with httpx.Client() as client:
    response = client.get(url, headers=headers)
    print(response.json())
```

<!-- type: tab-end -->

**Response:**

```json
{
  "id": "00000000-0000-0000-0000-000000000013",
  "name": "Sample FileSet",
  "description": "A sample FileSet for demonstration purposes.",
  "created": "2025-01-01T00:00:00.000Z",
  "createdBy": 111111111
}
```

## Update FileSet by Id

**Method:** `POST`  
**Endpoint:** `/api/files/v1/filesets/{filesetId}`

**Path Parameters:**

- `filesetId` (String, required): The ID of the FileSet.

**Request Body Parameters:**

| Parameter   | Type   | Required | Description                     |
| ----------- | ------ | -------- | ------------------------------- |
| name        | String | No       | The new name for the FileSet    |
| description | String | No       | The new description for FileSet |

<!--
type: tab
title: Javascript
-->

```js
fetch('https://{instance}.domo.com/api/files/v1/filesets/{filesetId}', {
  method: 'POST',
  headers: {
    'X-DOMO-Developer-Token': '<your-token-here>',
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    name: 'Updated FileSet Name', // Optional: New name for the FileSet
    description: 'Updated description.', // Optional: New description
  }),
})
  .then((response) => response.json())
  .then((result) => console.log(result))
  .catch((error) => console.error(`Error: ${error}`));
```

<!--
type: tab
title: Python
-->

```python
import httpx

headers = {
    'X-DOMO-Developer-Token': '<your-token-here>',
    'Content-Type': 'application/json',
}
url = 'https://{instance}.domo.com/api/files/v1/filesets/{filesetId}'
data = {
    "name": "Updated FileSet Name",  # Optional: New name for the FileSet
    "description": "Updated description."  # Optional: New description
}

with httpx.Client() as client:
    response = client.post(url, headers=headers, json=data)
    print(response.json())
```

<!-- type: tab-end -->

**Response:**

```json
{
  "id": "00000000-0000-0000-0000-000000000014",
  "name": "Sample FileSet",
  "description": "A sample FileSet for demonstration purposes.",
  "created": "2025-01-01T00:00:00.000Z",
  "createdBy": 111111111
}
```

---

## Delete FileSet by Id

**Method:** `DELETE`  
**Endpoint:** `/api/files/v1/filesets/{filesetId}`

**Path Parameters:**

- `filesetId` (String, required): The ID of the FileSet.

<!--
type: tab
title: Javascript
-->

```js
fetch('https://{instance}.domo.com/api/files/v1/filesets/{filesetId}', {
  method: 'DELETE',
  headers: {
    'X-DOMO-Developer-Token': '<your-token-here>',
    'Content-Type': 'application/json',
  },
})
  .then((response) => response.json())
  .then((result) => console.log(result))
  .catch((error) => console.error(`Error: ${error}`));
```

<!--
type: tab
title: Python
-->

```python
import httpx

headers = {
    'X-DOMO-Developer-Token': '<your-token-here>',
    'Content-Type': 'application/json',
}
url = 'https://{instance}.domo.com/api/files/v1/filesets/{filesetId}'

with httpx.Client() as client:
    response = client.delete(url, headers=headers)
    print(response.json())
```

<!-- type: tab-end -->

**Response:**

```json
{
  "status": "success",
  "message": "FileSet deleted successfully."
}
```
