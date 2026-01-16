# Browser Testing Patterns

Detailed testing scenarios for common UI patterns using Cursor browser tools.

---

## Testing Workflow

Every testing session follows this pattern:

```
1. Navigate to page
2. Snapshot for element references
3. Interact with elements
4. Re-snapshot after state changes
5. Verify expected state
6. Screenshot if visual verification needed
```

**Key principle:** Always re-snapshot after interactions that change page state. The element references from the previous snapshot may be stale.

---

## Form Testing

### Basic Form Submission

```
Scenario: User submits a valid form

1. Navigate to form page
2. Snapshot to get form element refs
3. Type into each required field
4. Click submit button
5. Wait for submission (loading state)
6. Snapshot to verify success state
7. Check for success message or redirect
```

### Form Validation Errors

```
Scenario: User submits with invalid data

1. Navigate to form page
2. Snapshot
3. Leave required field empty OR enter invalid data
4. Click submit button
5. Snapshot
6. Verify error message appears next to field
7. Verify form did NOT submit (no redirect, no success message)
```

### Form Field Interactions

```
Scenario: Testing individual field behavior

1. Navigate to form
2. Snapshot
3. Click into field (focus)
4. Snapshot - verify focus state styling
5. Type invalid value
6. Click out of field (blur)
7. Snapshot - verify inline validation error
8. Click back into field
9. Type valid value
10. Click out
11. Snapshot - verify error cleared
```

### Form with Async Validation

```
Scenario: Field that validates against server (e.g., username availability)

1. Navigate to form
2. Snapshot
3. Type value that triggers async check
4. Wait for validation request to complete
5. Snapshot - verify validation result displayed
```

---

## Modal/Dialog Testing

### Open and Close Cycle

```
Scenario: Modal opens and closes correctly

1. Navigate to page with modal trigger
2. Snapshot
3. Click trigger button
4. Wait for modal animation
5. Snapshot - verify modal is visible
6. Click backdrop OR close button
7. Wait for close animation
8. Snapshot - verify modal is gone
```

### Modal with Form

```
Scenario: Submit form inside modal

1. Open modal (as above)
2. Snapshot to get form elements inside modal
3. Fill form fields
4. Click submit
5. Wait for submission
6. Snapshot - verify either:
   - Modal closed with success
   - Success message inside modal
   - Form errors if validation failed
```

### Modal Escape Key

```
Scenario: Modal closes on Escape

1. Open modal
2. Snapshot - verify open
3. Press Escape key
4. Wait for animation
5. Snapshot - verify closed
```

---

## List/Table Testing

### List Rendering

```
Scenario: List displays items correctly

1. Navigate to list page
2. Snapshot
3. Verify expected number of items visible
4. Verify item content matches expected data
```

### Empty State

```
Scenario: List shows empty state when no items

1. Navigate to list (with no data)
2. Snapshot
3. Verify empty state message/illustration displayed
4. Verify "Add" or "Create" CTA is visible
```

### CRUD Operations

```
Scenario: Create new item

1. Navigate to list
2. Snapshot - note current item count
3. Click "Add" button
4. Complete add flow (form or inline)
5. Snapshot
6. Verify new item appears in list
7. Verify item count increased by 1
```

```
Scenario: Edit existing item

1. Navigate to list
2. Snapshot
3. Click edit on specific item
4. Modify content
5. Save changes
6. Snapshot
7. Verify item shows updated content
```

```
Scenario: Delete item

1. Navigate to list
2. Snapshot - note current item count
3. Click delete on specific item
4. Confirm deletion (if confirmation dialog)
5. Snapshot
6. Verify item no longer in list
7. Verify item count decreased by 1
```

### List Loading State

```
Scenario: List shows loading skeleton

1. Navigate to list (before data loads)
2. Snapshot immediately
3. Verify skeleton/loading state visible
4. Wait for data
5. Snapshot
6. Verify actual items replaced skeleton
```

---

## Navigation Testing

### Route Navigation

```
Scenario: Navigating between pages

1. Start at home page
2. Snapshot
3. Click navigation link
4. Wait for page load
5. Snapshot
6. Verify correct page content loaded
7. Verify active nav state shows current page
```

### Back Navigation

```
Scenario: Browser back button works

1. Navigate to page A
2. Navigate to page B
3. Snapshot - verify on page B
4. Navigate back
5. Snapshot - verify returned to page A
```

### Deep Links

```
Scenario: Direct URL access works

1. Navigate directly to deep URL (e.g., /settings/account)
2. Snapshot
3. Verify correct page loaded
4. Verify auth redirect if protected route
```

### Mobile Navigation

```
Scenario: Mobile menu works

1. Resize browser to mobile viewport (< 768px)
2. Navigate to page
3. Snapshot
4. Click hamburger/menu button
5. Snapshot - verify mobile menu open
6. Click nav item
7. Wait for navigation
8. Snapshot - verify menu closed, correct page loaded
```

---

## Authentication Testing

### Login Flow

```
Scenario: User logs in successfully

1. Navigate to /login
2. Snapshot
3. Enter valid credentials
4. Click submit
5. Wait for redirect
6. Snapshot
7. Verify redirected to dashboard/home
8. Verify user session indicator visible
```

### Login Validation

```
Scenario: Invalid credentials show error

1. Navigate to /login
2. Enter invalid credentials
3. Click submit
4. Wait for response
5. Snapshot
6. Verify error message displayed
7. Verify still on login page
```

### Protected Routes

```
Scenario: Unauthenticated user redirected

1. Clear session (if possible)
2. Navigate directly to protected route
3. Snapshot
4. Verify redirected to login
5. Verify return URL preserved (optional)
```

---

## Error State Testing

### API Error Handling

```
Scenario: API returns error

1. Navigate to page that makes API call
2. (Trigger error condition if possible)
3. Snapshot
4. Verify error message displayed
5. Verify retry option available (if applicable)
6. Verify page doesn't crash
```

### Network Error

```
Scenario: Network request fails

1. Navigate to page
2. (Simulate offline or slow network if possible)
3. Attempt action that requires network
4. Snapshot
5. Verify graceful error handling
6. Verify user can retry
```

---

## Mobile Viewport Testing

### Responsive Layout

```
Scenario: Page adapts to mobile viewport

1. Resize browser to 375x667 (iPhone SE)
2. Navigate to page
3. Snapshot
4. Verify:
   - No horizontal scroll
   - Touch targets at least 44px
   - Text readable without zoom
   - Key actions accessible
```

### Touch Interactions

```
Scenario: Touch-specific interactions work

1. Resize to mobile viewport
2. Navigate to page with touch interactions
3. Test swipe gestures (if applicable)
4. Test tap vs long-press (if applicable)
5. Verify touch feedback visible
```

---

## State Persistence Testing

### Page Refresh

```
Scenario: State persists across refresh

1. Navigate to page
2. Make changes (fill form, toggle setting, etc.)
3. Refresh page
4. Snapshot
5. Verify state persisted (or intentionally reset)
```

### LocalStorage/Cookie State

```
Scenario: User preferences persist

1. Navigate to settings
2. Change a preference
3. Snapshot - verify change applied
4. Navigate away
5. Navigate back OR refresh
6. Snapshot
7. Verify preference still set
```

---

## Testing Checklist Template

Use this checklist for each feature:

```markdown
## [Feature Name] Testing

### Happy Path
- [ ] Primary use case works end-to-end
- [ ] Success feedback shown to user
- [ ] Data persisted correctly

### Validation
- [ ] Required fields enforced
- [ ] Invalid input shows error
- [ ] Errors clear when corrected

### Edge Cases
- [ ] Empty state handled
- [ ] Long text/content handled
- [ ] Special characters handled

### Error Handling
- [ ] API errors show user-friendly message
- [ ] Network errors handled gracefully
- [ ] User can recover/retry

### Mobile
- [ ] Layout works on 375px viewport
- [ ] Touch targets adequate
- [ ] No horizontal scroll

### Accessibility
- [ ] Keyboard navigation works
- [ ] Focus states visible
- [ ] Error messages announced
```
