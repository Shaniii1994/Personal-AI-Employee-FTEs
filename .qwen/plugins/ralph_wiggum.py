"""
Ralph Wiggum Stop Hook Plugin for Claude Code

This plugin intercepts Claude's exit and checks if the task is complete.
If not complete, it re-injects the prompt to keep Claude working.

Installation:
1. Copy this file to: ~/.claude/plugins/ralph_wiggum.py
2. Or use the local .claude/plugins folder in your project

Usage:
    claude --plugin ralph_wiggum.py "Your task here"

Reference: https://github.com/anthropics/claude-code/tree/main/.claude/plugins/ralph-wiggum
"""

import os
import sys
from pathlib import Path
from datetime import datetime


class RalphWiggumPlugin:
    """
    Ralph Wiggum persistence plugin.
    
    Keeps Claude working until a task is marked complete.
    """
    
    name = "ralph_wiggum"
    version = "0.1.0"
    
    def __init__(self, config=None):
        """
        Initialize the plugin.
        
        Args:
            config: Plugin configuration dictionary
        """
        self.config = config or {}
        self.max_iterations = self.config.get('max_iterations', 10)
        self.iteration_count = 0
        self.vault_path = Path(self.config.get('vault_path', 'AI_Employee_Vault'))
        
        # Completion patterns to detect
        self.completion_patterns = [
            '<promise>TASK_COMPLETE</promise>',
            '<promise>COMPLETE</promise>',
            'TASK_COMPLETE',
            '[Task Complete]',
            'Task completed successfully',
        ]
    
    def should_continue(self, output: str) -> bool:
        """
        Check if Claude should continue working.
        
        Args:
            output: Claude's output
            
        Returns:
            True if should continue, False if complete
        """
        self.iteration_count += 1
        
        # Check max iterations
        if self.iteration_count >= self.max_iterations:
            print(f"\n[Ralph Wiggum] Max iterations ({self.max_iterations}) reached")
            return False
        
        # Check for completion patterns
        output_lower = output.lower()
        for pattern in self.completion_patterns:
            if pattern.lower() in output_lower:
                print(f"\n[Ralph Wiggum] Task completion detected")
                return False
        
        # Check if task file moved to Done
        done_folder = self.vault_path / 'Done'
        if done_folder.exists():
            # Count files modified in last minute
            recent_done = [
                f for f in done_folder.iterdir()
                if f.is_file() and datetime.now().timestamp() - f.stat().st_mtime < 60
            ]
            if recent_done:
                print(f"\n[Ralph Wiggum] Task completion detected (file moved to Done)")
                return False
        
        # Continue working
        print(f"\n[Ralph Wiggum] Task not complete, continuing... (iteration {self.iteration_count}/{self.max_iterations})")
        return True
    
    def get_continuation_prompt(self, original_prompt: str, output: str) -> str:
        """
        Generate a continuation prompt.
        
        Args:
            original_prompt: The original task prompt
            output: Claude's previous output
            
        Returns:
            New prompt to continue work
        """
        return f"""[Ralph Wiggum Loop - Iteration {self.iteration_count + 1}]

Continue working on the task. Your previous output was:

---
{output[:2000]}  # Truncate to avoid token limits
---

Keep working until the task is complete. Remember to:
1. Follow the Company Handbook rules
2. Create plans for complex tasks
3. Request approval when needed
4. Move completed items to /Done

Original task:
{original_prompt}
"""
    
    def on_exit_attempt(self, context: dict) -> dict:
        """
        Called when Claude tries to exit.
        
        Args:
            context: Current context including output and prompt
            
        Returns:
            Modified context or empty dict to allow exit
        """
        output = context.get('output', '')
        
        if self.should_continue(output):
            # Block exit and provide continuation prompt
            return {
                'continue': True,
                'prompt': self.get_continuation_prompt(
                    context.get('original_prompt', ''),
                    output
                )
            }
        
        # Allow exit
        return {'continue': False}


# Hook registration
def register_hook(hooks):
    """Register the Ralph Wiggum hook with Claude Code."""
    
    plugin = RalphWiggumPlugin()
    
    @hooks.register('before_exit')
    def check_task_complete(context):
        """Check if task is complete before allowing exit."""
        result = plugin.on_exit_attempt(context)
        
        if result.get('continue'):
            # Block exit and inject continuation prompt
            print(result['prompt'])
            return {
                'block': True,
                'additional_prompt': result['prompt']
            }
        
        return {'block': False}


# Simple CLI for testing
if __name__ == '__main__':
    print("Ralph Wiggum Plugin loaded")
    print(f"Max iterations: {RalphWiggumPlugin().max_iterations}")
    print(f"Vault path: {RalphWiggumPlugin().vault_path}")
    print("\nThis plugin should be loaded by Claude Code automatically.")
    print("To test: claude --plugin ralph_wiggum.py \"Your task\"")
