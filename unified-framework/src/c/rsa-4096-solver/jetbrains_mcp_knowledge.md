# JetBrains MCP (Model Context Protocol) Tools Knowledge Export

## Overview

The JetBrains MCP server provides AI assistants with direct access to IDE functionality through a standardized protocol. These tools enable intelligent code navigation, refactoring, analysis, and execution within JetBrains IDEs.

## Core Concepts

### Project Path Parameter
Most tools accept an optional `projectPath` parameter:
- **Always pass it when known** - reduces ambiguity and improves performance
- If unknown, you can use the current working directory
- The tool will attempt to infer it if not provided

### Line and Column Numbering
- **1-based indexing** - lines and columns start at 1, not 0
- Used in tools like `get_symbol_info` and `get_file_problems`

### File Paths
- Paths are typically **relative to project root**
- Some tools accept absolute paths, but relative is preferred
- Use forward slashes on all platforms

---

## Tool Categories

### 1. PROJECT STRUCTURE TOOLS

#### `get_project_modules`
**Purpose:** List all modules in the project with their types
**Parameters:**
- `projectPath` (optional)
**Returns:** Module names and types
**Use when:** Understanding project structure, multi-module projects

#### `get_project_dependencies`
**Purpose:** Get all libraries/dependencies defined in the project
**Parameters:**
- `projectPath` (optional)
**Returns:** Library names
**Use when:** Understanding dependencies, troubleshooting missing libraries

#### `get_repositories`
**Purpose:** List VCS (Version Control System) roots in the project
**Parameters:**
- `projectPath` (optional)
**Returns:** Repository paths
**Use when:** Working with multi-repository projects, git operations

---

### 2. FILE NAVIGATION TOOLS

#### `find_files_by_name_keyword` ⭐ FASTEST
**Purpose:** Search files by name substring (case-insensitive)
**Parameters:**
- `nameKeyword` (required) - substring to search for
- `fileCountLimit` (optional) - max results
- `timeout` (optional) - milliseconds
- `projectPath` (optional)
**Returns:** List of matching file paths
**Performance:** Uses indexes - MUCH faster than glob
**Limitations:** Searches names only, not full paths
**Use when:** You know part of the filename

#### `find_files_by_glob`
**Purpose:** Search files by glob pattern
**Parameters:**
- `globPattern` (required) - e.g., "src/**/*.java"
- `subDirectoryRelativePath` (optional) - limit to subdirectory
- `addExcluded` (optional) - include ignored files
- `fileCountLimit` (optional)
- `timeout` (optional)
- `projectPath` (optional)
**Returns:** List of matching file paths
**Use when:** Pattern-based searches, all files of a type

#### `list_directory_tree`
**Purpose:** Get tree representation like `tree` utility
**Parameters:**
- `directoryPath` (required) - relative to project root
- `maxDepth` (optional) - recursion depth
- `timeout` (optional)
- `projectPath` (optional)
**Returns:** Pseudo-graphic tree representation
**Best practice:** PREFER this over `ls` or `dir` commands

#### `get_all_open_file_paths`
**Purpose:** Get paths of currently open editor files
**Parameters:**
- `projectPath` (optional)
**Returns:** Active editor file path and other open files
**Use when:** Understanding user's current context

---

### 3. FILE READING TOOLS

#### `get_file_text_by_path`
**Purpose:** Read file contents by project-relative path
**Parameters:**
- `pathInProject` (required)
- `maxLinesCount` (optional) - limit lines
- `truncateMode` (optional) - "START", "MIDDLE", "END", "NONE"
- `projectPath` (optional)
**Returns:** File text content
**Notes:**
- Binary files return error
- Large files truncated with marker: `<<<...content truncated...>>>`

---

### 4. FILE MODIFICATION TOOLS

#### `replace_text_in_file` ⭐ MOST EFFICIENT
**Purpose:** Find and replace text in files
**Parameters:**
- `pathInProject` (required)
- `oldText` (required) - text to replace
- `newText` (required) - replacement text
- `replaceAll` (optional, default true) - replace all occurrences
- `caseSensitive` (optional, default true)
- `projectPath` (optional)
**Returns:** "ok" on success, error messages on failure
**Best practice:** Most efficient for targeted changes
**Note:** Automatically saves the file

#### `create_new_file`
**Purpose:** Create new file with optional content
**Parameters:**
- `pathInProject` (required)
- `text` (optional) - initial content
- `overwrite` (optional) - overwrite if exists
- `projectPath` (optional)
**Returns:** Success confirmation
**Note:** Creates parent directories automatically

#### `reformat_file`
**Purpose:** Apply IDE code formatting rules
**Parameters:**
- `path` (required) - relative to project root
- `projectPath` (optional)
**Use when:** Ensuring code style compliance

---

### 5. CODE SEARCH TOOLS

#### `search_in_files_by_text` ⭐ FAST
**Purpose:** Search for text substring across all project files
**Parameters:**
- `searchText` (required)
- `directoryToSearch` (optional) - relative to project root
- `fileMask` (optional) - e.g., "*.java"
- `caseSensitive` (optional)
- `maxUsageCount` (optional)
- `timeout` (optional)
- `projectPath` (optional)
**Returns:** Occurrences with `||markers||` around matches
**Best practice:** MUCH faster than command-line grep
**Example result:** `some text ||substring|| text`

#### `search_in_files_by_regex`
**Purpose:** Search with regex patterns across files
**Parameters:** Same as `search_in_files_by_text` but:
- `regexPattern` (required) - regex to search for
**Returns:** Occurrences with `||markers||`
**Use when:** Complex pattern matching needed

---

### 6. CODE INTELLIGENCE TOOLS

#### `get_symbol_info`
**Purpose:** Get Quick Documentation for symbol at position
**Parameters:**
- `filePath` (required) - relative to project root
- `line` (required) - 1-based line number
- `column` (required) - 1-based column number
- `projectPath` (optional)
**Returns:**
- Symbol name, signature, type
- Documentation
- Declaration code (if available)
**Use when:** Understanding symbol semantics, declarations

#### `get_file_problems`
**Purpose:** Analyze file for errors and warnings (IDE inspections)
**Parameters:**
- `filePath` (required) - relative to project root
- `errorsOnly` (optional) - only errors, or include warnings
- `timeout` (optional)
- `projectPath` (optional)
**Returns:** List of problems with severity, description, location
**Note:** Lines and columns are 1-based
**Use when:** Finding code issues, syntax errors

---

### 7. REFACTORING TOOLS

#### `rename_refactoring` ⭐ INTELLIGENT
**Purpose:** Rename symbol across entire project
**Parameters:**
- `pathInProject` (required)
- `symbolName` (required) - exact, case-sensitive current name
- `newName` (required) - new name
- `projectPath` (optional)
**Returns:** Success message or error
**Key advantage:** Context-aware, updates ALL references project-wide
**Best practice:** ALWAYS use this instead of text search-replace for symbols

---

### 8. EXECUTION TOOLS

#### `execute_terminal_command`
**Purpose:** Run shell commands in IDE terminal
**Parameters:**
- `command` (required) - shell command
- `timeout` (optional) - milliseconds
- `executeInShell` (optional) - use user's shell (bash/zsh)
- `reuseExistingTerminalWindow` (optional) - avoid multiple terminals
- `maxLinesCount` (optional)
- `truncateMode` (optional)
- `projectPath` (optional)
**Returns:** Terminal output (truncated if > 2000 lines)
**Features:**
- Checks if process running before collecting output
- Timeout notification if exceeded
- User confirmation required unless "Brave Mode" enabled

#### `execute_run_configuration`
**Purpose:** Run a specific run configuration
**Parameters:**
- `configurationName` (required)
- `timeout` (optional) - milliseconds
- `maxLinesCount` (optional)
- `truncateMode` (optional)
- `projectPath` (optional)
**Returns:** Exit code, output, success status
**Use when:** Running pre-configured tasks, tests, builds

#### `get_run_configurations`
**Purpose:** List available run configurations
**Parameters:**
- `projectPath` (optional)
**Returns:**
- Configuration names
- Command line info
- Working directory
- Environment variables
**Use when:** Discovering how to run the application/tests

---

### 9. EDITOR TOOLS

#### `open_file_in_editor`
**Purpose:** Open file in JetBrains IDE editor
**Parameters:**
- `filePath` (required) - absolute or relative to project root
- `projectPath` (optional)
**Use when:** Directing user attention to specific files

---

## Best Practices

### Performance Optimization

1. **File Search Priority:**
   ```
   1st: find_files_by_name_keyword (fastest - uses indexes)
   2nd: search_in_files_by_text (fast - IntelliJ search engine)
   3rd: find_files_by_glob (slower - recursive)
   ```

2. **Always pass `projectPath`** when known to reduce ambiguity

3. **Use search tools instead of command-line:**
   - ✅ `search_in_files_by_text`
   - ❌ `grep` command
   - ✅ `find_files_by_name_keyword`
   - ❌ `find` command

### Refactoring Safety

1. **For renaming symbols:**
   - ✅ Use `rename_refactoring` (context-aware)
   - ❌ Use `replace_text_in_file` (dumb text replacement)

2. **Rename refactoring advantages:**
   - Updates all references project-wide
   - Understands scope and context
   - Prevents broken references
   - Language-aware

### File Operations

1. **Reading files:**
   - Use `get_file_text_by_path` (native IDE access)
   - Specify `truncateMode` for large files
   - Handle binary file errors gracefully

2. **Modifying files:**
   - `replace_text_in_file` for targeted changes
   - File saves automatically
   - Returns clear error messages

3. **Creating files:**
   - `create_new_file` creates parent directories
   - Set `overwrite` flag if replacing existing

### Code Intelligence

1. **Understanding symbols:**
   - Use `get_symbol_info` with exact line/column (1-based)
   - Provides declaration, docs, type info
   - Works across language boundaries

2. **Finding issues:**
   - `get_file_problems` uses IDE's inspection engine
   - Filter with `errorsOnly` for critical issues
   - Returns precise locations (1-based)

### Terminal Execution

1. **Command execution:**
   - Set reasonable timeouts (default often insufficient)
   - Use `executeInShell=true` for shell scripts
   - Reuse terminal windows to avoid clutter
   - Output limited to 2000 lines (truncated)

2. **Run configurations:**
   - Discover with `get_run_configurations`
   - Execute with `execute_run_configuration`
   - Includes environment setup automatically

---

## Common Patterns

### Pattern: Navigate to Definition
```
1. search_in_files_by_text to find usages
2. get_symbol_info at specific location
3. open_file_in_editor to show user
```

### Pattern: Safe Refactoring
```
1. search_in_files_by_text to preview impact
2. rename_refactoring to perform change
3. get_file_problems to verify no new errors
```

### Pattern: Understand Project Structure
```
1. list_directory_tree for overview
2. get_project_modules for module structure
3. get_project_dependencies for external deps
```

### Pattern: Fix Compilation Errors
```
1. get_file_problems(errorsOnly=true) to find errors
2. get_symbol_info at error locations for context
3. replace_text_in_file or rename_refactoring to fix
4. reformat_file for clean code
```

### Pattern: Run and Debug
```
1. get_run_configurations to see options
2. execute_run_configuration to run
3. get_file_problems if failures occur
4. execute_terminal_command for ad-hoc testing
```

---

## Error Handling

### Common Error Messages

- **"project dir not found"** → Check projectPath parameter
- **"file not found"** → Verify path is relative to project root
- **"no occurrences found"** → Text doesn't exist (for replace operations)
- **"could not get document"** → File access issues (binary, permissions)
- **Timeout errors** → Increase timeout parameter

### Graceful Degradation

1. If MCP tool fails → Fall back to standard tools (Read, Edit, Bash)
2. If search times out → Narrow scope with directoryToSearch
3. If symbol info unavailable → Use search to find definition manually

---

## Integration Tips for Grok

### Context Awareness
- Use `get_all_open_file_paths` to understand user focus
- Use `get_repositories` to understand multi-repo projects
- Use `list_directory_tree` before making assumptions

### Speed Optimization
- Prefer MCP tools over bash commands (faster, better context)
- Use specific search tools based on query type
- Cache project structure information when possible

### User Experience
- `open_file_in_editor` to direct attention
- `reformat_file` after code changes for consistency
- `get_file_problems` to validate changes

### Safety
- Always use `rename_refactoring` for symbols
- Verify changes with `get_file_problems` after modifications
- Use `get_symbol_info` to understand impact before changes

---

## Limitations

1. **Only files in project directory** - no external files/libraries
2. **Binary files unsupported** for text operations
3. **Output truncation** at 2000 lines for commands
4. **User confirmation** may be required for terminal commands
5. **1-based indexing** for lines/columns (not 0-based)

---

## Summary Decision Tree

**Need to find a file?**
- Know partial name? → `find_files_by_name_keyword`
- Need pattern match? → `find_files_by_glob`

**Need to search code?**
- Simple text? → `search_in_files_by_text`
- Complex pattern? → `search_in_files_by_regex`

**Need to modify code?**
- Rename symbol? → `rename_refactoring`
- Replace text? → `replace_text_in_file`
- New file? → `create_new_file`

**Need to understand code?**
- What is this symbol? → `get_symbol_info`
- What's wrong with this file? → `get_file_problems`
- What's in this directory? → `list_directory_tree`

**Need to run code?**
- Existing config? → `execute_run_configuration`
- Custom command? → `execute_terminal_command`
- What can I run? → `get_run_configurations`

---

## Version Notes

This knowledge export reflects the JetBrains MCP server capabilities as integrated into Claude Code. Tool availability and behavior may vary across different IDE versions and MCP server implementations.

For the latest capabilities, check the actual tool definitions and parameter schemas.
