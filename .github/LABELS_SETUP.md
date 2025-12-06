# Setting Up GitHub Labels

This guide explains how to set up the recommended labels for this repository.

## Automatic Setup (Recommended)

The easiest way to set up labels is using the GitHub CLI (`gh`):

### Prerequisites
- Install [GitHub CLI](https://cli.github.com/)
- Authenticate with `gh auth login`

### Using the Label Configuration

```bash
# Navigate to the repository directory
cd solakon-one-homeassistant

# Apply labels from the configuration file
# Note: This requires a tool like github-label-sync or manual creation
```

## Manual Setup

You can manually create labels through the GitHub web interface:

1. Go to your repository on GitHub
2. Click on **Issues** tab
3. Click on **Labels** (next to Milestones)
4. Click **New label** button
5. For each label in `.github/labels.yml`, create it with the specified:
   - Name
   - Description
   - Color (hex code without #)

## Using GitHub Label Sync Tool

For automated label synchronization, you can use [github-label-sync](https://github.com/Financial-Times/github-label-sync):

```bash
# Install the tool
npm install -g github-label-sync

# Sync labels (requires GitHub token)
github-label-sync --access-token YOUR_TOKEN solakon-de/solakon-one-homeassistant .github/labels.yml
```

## Recommended Labels

The `.github/labels.yml` file contains the following categories:

### Type Labels
- **bug** - Something isn't working (red)
- **feature** - New feature or request (blue)
- **enhancement** - Improvement to existing functionality (blue)
- **documentation** - Documentation improvements (blue)
- **question** - Further information requested (purple)

### Priority Labels
- **priority:high** - High priority (red)
- **priority:medium** - Medium priority (yellow)
- **priority:low** - Low priority (green)

### Status Labels
- **wontfix** - Won't be worked on
- **duplicate** - Already exists
- **good first issue** - Good for newcomers
- **help wanted** - Extra attention needed

### Release Management Labels (for Release Drafter)
- **breaking-change** - Breaking change
- **new-feature** - New feature
- **bugfix** - Bug fix
- **maintenance** - Maintenance task
- **ci** - CI/CD related
- **dependencies** - Dependency updates
- **refactor** - Code refactoring
- **performance** - Performance improvement

## Best Practices

1. **Apply labels consistently**: Use labels on all issues and PRs
2. **Use multiple labels**: Combine type, priority, and status labels as needed
3. **Update as needed**: Modify labels if requirements change
4. **Document usage**: Ensure team knows which labels to use when

## For Repository Maintainers

When triaging issues:
1. Add a **type label** (bug, feature, etc.)
2. Add a **priority label** if appropriate
3. Add **good first issue** for simple tasks suitable for new contributors
4. Use **breaking-change** label for PRs that break compatibility
5. Release Drafter will automatically categorize PRs based on labels

## Automation Benefits

With proper labels:
- Release Drafter automatically categorizes changelog entries
- Semantic version bumps are determined automatically
- Issues can be filtered and prioritized easily
- Contributors can find suitable issues to work on
