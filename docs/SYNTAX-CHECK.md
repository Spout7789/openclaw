# Syntax Check Reference

## JavaScript (ES6+)

### ❌ NEVER DO:
```javascript
// Duplicate let in same scope
let x = 1;
let x = 2;  // ERROR

// Using undeclared variable
console.log(y);  // y not declared

// Mismatched brackets
function test() {
  if (x) {
    doSomething();
  // Missing closing }
```

### ✅ ALWAYS:
```javascript
// Use const by default, let if reassigning
const x = 1;
let y = 2;
y = 3;  // OK

// Use === not ==
if (x === y)

// Arrow functions
const fn = () => { return x; }

// Destructuring
const { a, b } = obj;
```

### COMMON PATTERNS TO CHECK:
1. `let x =` appearing twice in same function = ERROR
2. `{` and `}` matching count
3. `function` keyword consistency
4. `=>` consistency in arrow functions

## Python 3

### ❌ NEVER DO:
```python
# IndentationError - mixing tabs/spaces
def foo():
	return x  # tab
   bar()  # spaces

# NameError
print(x)  # x not defined

# SyntaxError
def foo()
    pass  # missing colon

# Duplicate key in dict (last wins, but suspicious)
d = {'a': 1, 'a': 2}
```

### ✅ ALWAYS:
```python
# Use f-strings
name = f"Hello {x}"

# Type hints (optional but recommended)
def foo(x: int) -> str:
    pass

# Context managers
with open('file') as f:
    pass
```

## Pre-Flight Syntax Checks

Before presenting code, verify:
1. No duplicate variable declarations
2. Brackets/braces match
3. No obvious typos in keywords
4. Indentation consistent (Python)
