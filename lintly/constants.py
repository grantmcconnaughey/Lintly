FAIL_ON_ANY = 'any'
FAIL_ON_NEW = 'new'

# Identifies that a comment came from Lintly. This is used to aid in automatically
# deleting old PR comments/reviews. This is valid Markdown that is hidden from
# users in GitHub and GitLab.
LINTLY_IDENTIFIER = '<!-- Automatically posted by Lintly -->'

# These constants define the actions that lintly might take against a PR concerning reviews, ie.
# not the commit status
ACTION_REVIEW_USE_CHECKS = 'use_checks'
ACTION_REVIEW_REQUEST_CHANGES = 'request_changes'
ACTION_REVIEW_APPROVE = 'approve'
ACTION_REVIEW_COMMENT = 'comment'
ACTION_REVIEW_DO_NOTHING = 'do_nothing'
