
# SheetFlow Sheet Management

## Overview

This project is an HTTP server built with **Python**, **FastAPI**, and **Pydantic**, managing spreadsheets with type-safe operations. 
It supports creating sheets, updating cell values, resolving lookups, and retrieving sheets. Cyclic references in lookups are not allowed, ensuring robust functionality, enforces strict type validation and prevents circular references to maintain data integrity..

---

## Features

1. **Create a Spreadsheet**  
   Define a schema for columns and types (`boolean`, `int`, `double`, `string`) and get a unique sheet ID.

2. **Set Cell Values**  
   Update a specific cell with a type-validated value or use the `lookup(columnName, rowIndex)` function to reference another cell.

3. **Retrieve a Sheet**  
   Get the full sheet structure by its ID, with resolved lookup values.

4. **Cycle Prevention**  
   Detects and prevents cycles in lookup references.

5. **Advanced Lookup Structure**  
   The system supports extended lookup chains, enabling dynamic connections between cells. For example:

   - Cell `(A,1)` references `lookup(B,1)`.
   - Cell `(B,1)` references `lookup(C,1)`.

   If you set `(C,1)` to `10`, the values of `(A,1)`, `(B,1)`, and `(C,1)` will all resolve to `10`.

   When `(C,1)` is updated to `lookup(D,1)`, the entire lookup chain remains functional. If you then set `(D,1)` to `20`, this change propagates through the chain, updating `(A,1)`, `(B,1)` and `(C,1)` to `20`.

   This ensures lookups are dynamically resolved and stay consistent, even as dependencies evolve.
---

## API Endpoints

### 1. **Create a Sheet**
`POST /sheet`  
Request:
   ```json
   {
     "columns": [
       { "name": "A", "type": "boolean" },
       { "name": "B", "type": "int" }
     ]
   }
   ```
Response:
   ```json
   "unique-sheet-id"
   ```

### 2. **Set a Cell**
`POST /cells/?sheet_id={sheetId}`  
Request:
   ```json
   { "column": "A", "row": 1, "value": "true" }
   ```

### 3. **Get a Sheet**
`GET /cells/?sheet_id={sheetId}`  
Response:
   ```json
    { 
        "('D', '1')": "8",
        "('B', '3')": "11",
        "('A', '2')": "4"
    }
   ```

---

## Setup and Testing

### Docker execution
1. Build docker image:
   ```bash
   cd to cloned project
   docker build -t sheetflow .
   ```
2. Run docker container:
   ```bash
   docker run -d -p 8000:8000 sheetflow 
   ```
---
### Local execution - prerequisites
- **Python 3.8+**, **FastAPI**, **Pydantic**, **pytest**

### Installation
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the server:
   ```bash
   uvicorn app.main:app --reload
   ```

### Testing
Run tests with **pytest**:
```bash
pytest tests/
```

---