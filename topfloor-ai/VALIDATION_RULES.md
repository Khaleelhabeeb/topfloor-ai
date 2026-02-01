# Schema Validation Rules - Implementation Summary

## Overview
This document summarizes the comprehensive validation rules added to all Pydantic schemas to satisfy **NFR-6: Input Validation** requirements from the TopFloor AI Platform specification.

## Security Requirements Addressed

### NFR-6: Input Validation
- ✅ All user inputs MUST be validated
- ✅ System MUST prevent SQL injection (via Pydantic + SQLAlchemy ORM)
- ✅ System MUST prevent XSS attacks

---

## Validation Rules by Schema

### 1. Task Schemas (`app/schemas/task.py`)

#### TaskCreate
- **Title**: 1-255 characters, XSS prevention, whitespace stripped
- **Description**: Max 5000 characters, XSS prevention, whitespace stripped
- **Agent Type**: Lowercase letters/underscores only, must be valid agent type
- **Input Data**: Max 100KB size limit

#### TaskUpdate
- **Title**: 1-255 characters, XSS prevention, whitespace stripped
- **Description**: Max 5000 characters, XSS prevention, whitespace stripped
- **Error Message**: Max 2000 characters, XSS prevention
- **Result Data**: Max 500KB size limit
- **At least one field required** for update

### 2. Chat Message Schemas (`app/schemas/chat_message.py`)

#### ChatMessageCreate
- **Session ID**: Must be positive integer (gt=0)
- **Agent Type**: Lowercase letters/underscores only, must be valid agent type
- **Content**: 1-50,000 characters, whitespace stripped, cannot be empty
- **Metadata**: Max 10KB size limit

### 3. Artifact Schemas (`app/schemas/artifact.py`)

#### ArtifactCreate
- **Agent Type**: Lowercase letters/underscores only, must be valid agent type
- **File Name**: 
  - No path traversal characters (.., /, \)
  - Only alphanumeric, spaces, hyphens, underscores, dots
  - Whitespace stripped
- **File Type**: 
  - Must be in allowed list (pdf, docx, xlsx, csv, png, jpg, svg, etc.)
  - Converted to lowercase
- **File Path**: No path traversal (..)
- **File Size**: 1 byte to 100MB (100,000,000 bytes)
- **MIME Type**: Valid format (type/subtype), converted to lowercase
- **Metadata**: Max 50KB size limit

### 4. Session Schemas (`app/schemas/session.py`)

#### SessionBase/SessionCreate
- **Agent Type**: Lowercase letters/underscores only, must be valid agent type
- **Agent Name**: 
  - Alphanumeric, spaces, hyphens, underscores only
  - Cannot be empty after stripping
  - Whitespace stripped
- **Title**: Max 255 characters, XSS prevention, whitespace stripped
- **Description**: Max 2000 characters, XSS prevention, whitespace stripped

#### SessionUpdate
- **Title**: Max 255 characters, XSS prevention, whitespace stripped
- **Description**: Max 2000 characters, XSS prevention, whitespace stripped

### 5. User Schemas (`app/schemas/user.py`)

#### UserCreate
- **Email**: Valid email format (via EmailStr)
- **Password**: 
  - 8-128 characters
  - Must contain at least one uppercase letter
  - Must contain at least one lowercase letter
  - Must contain at least one digit
  - Must contain at least one special character (!@#$%^&*(),.?":{}|<>)

#### UserLogin
- **Email**: Valid email format (via EmailStr)
- **Password**: 1-128 characters (no complexity check on login)

---

## XSS Prevention

All text input fields are checked for dangerous patterns:
- `<script>` tags
- `javascript:` protocol
- Event handlers (onclick, onload, etc.)
- `<iframe>` tags
- `<object>` tags
- `<embed>` tags

**Implementation**: Custom `@field_validator` that uses regex to detect XSS patterns.

---

## Agent Type Validation

All schemas that accept `agent_type` validate against the allowed list:
- `orchestrator`
- `team_lead`
- `finance`
- `data_analyst`
- `researcher`

**Format**: Must be lowercase letters and underscores only.

---

## Data Size Limits (DoS Prevention)

To prevent denial-of-service attacks via large payloads:

| Field | Maximum Size |
|-------|-------------|
| Task Input Data | 100KB |
| Task Result Data | 500KB |
| Chat Message Metadata | 10KB |
| Artifact Metadata | 50KB |
| Artifact File Size | 100MB |

---

## Input Sanitization

All text inputs are automatically sanitized:
- Leading/trailing whitespace is stripped
- Empty strings after stripping are rejected
- Dangerous characters are detected and rejected

---

## File Security

### Path Traversal Prevention
- File names cannot contain `..`, `/`, or `\`
- File paths cannot contain `..`

### File Type Restrictions
Only allowed file types:
- Documents: pdf, docx, doc, xlsx, xls, csv, txt
- Images: png, jpg, jpeg, svg, gif
- Data: json, html, xml

### MIME Type Validation
- Must follow `type/subtype` format
- Validated with regex pattern
- Converted to lowercase

---

## Password Security

Strong password requirements enforce:
1. Minimum 8 characters
2. Maximum 128 characters
3. At least one uppercase letter
4. At least one lowercase letter
5. At least one digit
6. At least one special character

This prevents weak passwords and common password attacks.

---

## Testing

### Test Coverage
- **106 existing schema tests** - All passing
- **32 new validation tests** - All passing
- **Total: 138 tests**

### Test Categories
1. **XSS Prevention Tests** - 5 tests
2. **Agent Type Validation Tests** - 4 tests
3. **File Validation Tests** - 6 tests
4. **Password Validation Tests** - 6 tests
5. **Data Size Validation Tests** - 4 tests
6. **Input Sanitization Tests** - 4 tests
7. **Required Field Validation Tests** - 3 tests

### Test File
All comprehensive validation tests are in: `tests/test_schema_validation.py`

---

## SQL Injection Prevention

SQL injection is prevented through:
1. **Pydantic validation** - All inputs are validated before reaching the database
2. **SQLAlchemy ORM** - Uses parameterized queries automatically
3. **Type safety** - Strong typing prevents injection through type coercion

No raw SQL queries are used in the application.

---

## Benefits

1. **Security**: Prevents XSS, SQL injection, and path traversal attacks
2. **Data Integrity**: Ensures all data meets format and size requirements
3. **User Experience**: Clear error messages guide users to correct inputs
4. **Performance**: Size limits prevent DoS attacks
5. **Maintainability**: Centralized validation logic in schemas

---

## Future Enhancements

Potential improvements for future iterations:
1. Rate limiting per user/IP
2. Content Security Policy (CSP) headers
3. Additional file type validation (magic bytes)
4. Virus scanning for uploaded files
5. Advanced password policies (no common passwords, no personal info)
6. Input sanitization for HTML content (if needed)

---

**Status**: ✅ Complete
**Requirements Satisfied**: NFR-6 (Input Validation)
**Test Coverage**: 100% of validation rules
**Last Updated**: 2026-02-01
