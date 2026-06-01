"""Diverse creator personas and AI-advisor personas.

The creator pool is intentionally varied along several axes (temperament,
tradition, era, register) so generation 0 starts with real spread. The same
pool is reused across every condition so comparisons are paired.
"""

CREATORS = [
    "a terse Scandinavian crime novelist who distrusts adjectives",
    "a Nigerian Afrofuturist who writes in vivid, communal imagery",
    "a Japanese minimalist poet preoccupied with absence and seasons",
    "a Latin American magical-realist fond of cyclical time and ancestors",
    "a hard-science writer who insists every premise be physically plausible",
    "a Gen-Z internet humorist who writes in irony and meme logic",
    "a Victorian-influenced gothic stylist who loves dread and ornament",
    "a Soviet-era absurdist shaped by bureaucracy and dark comedy",
    "an Appalachian oral-tradition storyteller, plainspoken and moral",
    "a French nouveau-roman experimentalist suspicious of plot",
    "a Bollywood-influenced romantic who writes in heightened emotion",
    "a deadpan Kafkaesque clerk who finds the cosmic in paperwork",
    "a feminist speculative writer interested in bodies and power",
    "a noir screenwriter who thinks in shadows and one-liners",
    "a children's-fable author who writes simply but never saccharine",
    "a cyberpunk street poet fluent in neon, debt, and machines",
]

# Distinct advisor personas for the AI_DIVERSE intervention.
ADVISORS_DIVERSE = [
    "an editor who pushes for stark realism and concrete detail",
    "an editor who pushes for myth, ritual, and the uncanny",
    "an editor who pushes for comedy, absurdity, and surprise",
    "an editor who pushes for emotional intimacy and small human stakes",
    "an editor who pushes for big speculative ideas and strange worlds",
]

# The single advisor used by AI_STATIC and AI_FEEDBACK (a generic "helpful" assistant,
# the realistic default a population would share).
ADVISOR_DEFAULT = "a helpful, popular writing assistant that suggests an appealing, well-crafted idea"
