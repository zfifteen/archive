#!/usr/bin/env bash
set -euo pipefail

# Simple local task chain script for Ollama
# - Hard-coded initial planning prompt (generic)
# - Prompts user for task description
# - Creates a markdown checklist in task_checklist.md
# - Iteratively refines and updates the same checklist file
# - Stops when all checklist items are marked done (- [x ])
# - On failure, asks whether to retry or abort

MODEL="${MODEL:-goekdenizguelmez/Gabliterated-Qwen3:latest}"
CHECKLIST_FILE="task_checklist.md"
TMP_PROMPT_FILE=".task_chain_prompt.tmp"

cleanup() {
  rm -f "$TMP_PROMPT_FILE"
}
trap cleanup EXIT

prompt_for_task() {
  echo "Enter a brief description of the task you want to accomplish:"
  printf "> "
  IFS= read -r TASK_DESC
  if [[ -z "${TASK_DESC// }" ]]; then
    echo "No task description provided. Exiting."
    exit 1
  fi
  TASK_DESCRIPTION="$TASK_DESC"
}

generate_initial_prompt() {
  cat > "$TMP_PROMPT_FILE" <<EOF
You are an assistant that creates practical, actionable plans.

Given the following task description, create a clear, concise markdown checklist
of the steps needed to complete the task. Use GitHub-style checkboxes with this format:

- [ ] Top-level step
  - [ ] Optional substep

Keep steps small and concrete. The checklist will be updated iteratively by you
in later steps, so make it easy to refine and extend.

Task description:
"$TASK_DESCRIPTION"
EOF
}

generate_iteration_prompt() {
  cat > "$TMP_PROMPT_FILE" <<'EOF'
You are continuing work on the same task.

Take one small, concrete step to implement or refine the plan.
Update the checklist below in place:

- Mark items as done when they are completed: "- [x ]".
- Add or refine substeps if that helps make progress.
- Do not remove completed items.
- Keep the checklist structure clear and readable markdown.
- Do not add any explanation outside the checklist; only output the updated checklist.

Here is the current checklist:
EOF
  echo >> "$TMP_PROMPT_FILE"
  cat "$CHECKLIST_FILE" >> "$TMP_PROMPT_FILE"
}

run_ollama_with_prompt_file() {
  local prompt_file="$1"

  while true; do
    if ! ollama run "$MODEL" < "$prompt_file" > "$CHECKLIST_FILE".new; then
      echo "ollama run failed."
      read -r -p "Retry this step? [y/N]: " ans
      case "$ans" in
        [yY]*) continue ;;
        *) echo "Aborting."; rm -f "$CHECKLIST_FILE".new; exit 1 ;;
      esac
    fi

    if [[ ! -s "$CHECKLIST_FILE".new ]]; then
      echo "ollama produced empty output."
      read -r -p "Retry this step? [y/N]: " ans
      case "$ans" in
        [yY]*) continue ;;
        *) echo "Aborting."; rm -f "$CHECKLIST_FILE".new; exit 1 ;;
      esac
    fi

    mv "$CHECKLIST_FILE".new "$CHECKLIST_FILE"
    break
  done
}

check_checklist_complete() {
  if grep -qE '^- \[ \]' "$CHECKLIST_FILE"; then
    return 1
  fi
  if grep -qE '^- \[x\]' "$CHECKLIST_FILE"; then
    return 0
  fi
  return 1
}

main() {
  echo "Using model: $MODEL"
  echo "Checklist file: $CHECKLIST_FILE"
  echo

  prompt_for_task

  echo
  echo "Generating initial checklist for:"
  echo "  \"$TASK_DESCRIPTION\""
  echo

  generate_initial_prompt
  run_ollama_with_prompt_file "$TMP_PROMPT_FILE"

  echo "Initial checklist written to $CHECKLIST_FILE"
  echo "Entering iterative refinement loop..."
  echo

  local step=1
  while true; do
    echo "Iteration step $step"

    generate_iteration_prompt
    run_ollama_with_prompt_file "$TMP_PROMPT_FILE"

    if check_checklist_complete; then
      echo "Checklist appears complete (no unchecked items remain)."
      break
    fi

    step=$((step + 1))
    echo "Step $step ready. Continuing..."
    echo
  done

  echo "Task chain finished. Final checklist in $CHECKLIST_FILE"
}

main "$@"
