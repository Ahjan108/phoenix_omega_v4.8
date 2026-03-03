"""Regenerate all 12 CANONICAL.txt files with proper format."""

from pathlib import Path

# File data: path -> [(atom_data), ...]
# Each atom is: (role_prefix, band, mechanism_depth, cost_type, cost_intensity, identity_stage, prose_text)

files_data = {
    'atoms/corporate_managers/courage/shame/CANONICAL.txt': [
        ('RECOGNITION v01', 2, 1, 'internal', 2, 'pre_awareness', """Linda watches her hands shake as she types the email about the new strategic direction. Her hands know something her mind hasn't admitted yet: she's not sure about this direction. She's afraid she's leading them wrong. The email is professional. The confidence is performed. Her body knows the truth. She's a leader who doesn't fully trust her own judgment anymore. It started small — a decision that didn't land as planned. Then another. Now she's standing in front of these people she's supposed to lead, and there's a disconnect between the Linda they see and the Linda who lives inside here. The Linda who feels like she's faking it. Like everyone will eventually see that she doesn't deserve this title."""),
        ('RECOGNITION v02', 2, 1, 'internal', 2, 'pre_awareness', """Priya's stomach flips when her boss mentions "your growth potential in leadership." It sounds like praise. Priya hears something else: you're not there yet. You're not enough. The same voice that's been running for years. She smiles and thanks her boss. Inside, she's doing the math: what am I missing? What competency gap is he politely not naming? She's good at her job. Excellent, if she's honest. But she's not excellent enough to silence the voice that tells her she's overreaching. That she doesn't have whatever mysterious thing the truly senior people have. She goes back to her desk knowing she'll push harder. Work later. Try to close the gap she's invented. Shame is a motor. It makes her work. It never makes her confident."""),
        ('RECOGNITION v03', 3, 1, 'internal', 3, 'pre_awareness', """Dave doesn't volunteer in the meeting when his expertise could help. He listens to someone else describe the problem wrong. He could correct it. Should correct it. The shame is louder than the obligation. He stayed quiet in a meeting last month. Got called out, gently, by his boss: "Your perspective would have been valuable there." That's all it took. Now Dave is quiet more. Better to add nothing than to risk being perceived as arrogant or wrong. He's trading usefulness for safety. He knows it. The knowledge adds another layer of shame. He's becoming useless because he's too ashamed to contribute. He's in a meeting full of his own competence that he's decided to hide."""),
        ('RECOGNITION v04', 3, 1, 'internal', 3, 'pre_awareness', """Sandra got feedback in her review: "Brilliant work, but sometimes seems hesitant." That feedback has metastasized. She now interprets all her uncertainty as a visible flaw. Something people can see. A stamp on her forehead that says "not confident." When she presents, she's hyperaware of her own hesitation. She tries to compensate with overstatement. That feels false too. So she shrinks. She's started second-guessing proposals before she even presents them. "They won't like this. I'm not good at this. Someone else could do this better." The voice is ancient. The voice has her name on it. It's her own voice now."""),
        ('RECOGNITION v05', 4, 2, 'identity', 4, 'pre_awareness', """Kenji is in a room where he's supposed to lead but doesn't feel like a leader. He feels like a child who got lucky. There's a belief underneath everything now: people will eventually see that I was miscast. That I don't belong in this role. The belief is so basic, so foundational, that Kenji doesn't even question it. He works to try to prove it wrong. Works constantly. Works in ways that are starting to damage him. He's not managing from integrity anymore. He's managing from avoidance of exposure. Every interaction is a risk that someone will see the truth: he's not qualified. He's not capable. He's faking it. And the most shame-inducing part is knowing that his competence is real. He's delivered results. Yet the shame is louder. It reinterprets evidence. It says his success is accident or deception. Not genuine."""),
        # ... continue with remaining atoms for this file
    ],
}

# For now, let me just handle the first one manually and then do the rest programmatically
EOF

python3 << 'EOF'
# For efficiency, I'll create the remaining 11 files using the exact format needed
# Rather than creating the data structure above, I'll regenerate each file directly

# The files and their persona/topic/engine paths:
file_configs = [
    ('atoms/corporate_managers/courage/shame/CANONICAL.txt', 'corporate_managers/courage/shame'),
    ('atoms/corporate_managers/courage/spiral/CANONICAL.txt', 'corporate_managers/courage/spiral'),
    ('atoms/corporate_managers/financial_stress/overwhelm/CANONICAL.txt', 'corporate_managers/financial_stress/overwhelm'),
    ('atoms/corporate_managers/financial_stress/shame/CANONICAL.txt', 'corporate_managers/financial_stress/shame'),
    ('atoms/corporate_managers/financial_stress/spiral/CANONICAL.txt', 'corporate_managers/financial_stress/spiral'),
    ('atoms/gen_x_sandwich/courage/false_alarm/CANONICAL.txt', 'gen_x_sandwich/courage/false_alarm'),
    ('atoms/gen_x_sandwich/courage/shame/CANONICAL.txt', 'gen_x_sandwich/courage/shame'),
    ('atoms/gen_x_sandwich/courage/spiral/CANONICAL.txt', 'gen_x_sandwich/courage/spiral'),
    ('atoms/gen_x_sandwich/financial_stress/overwhelm/CANONICAL.txt', 'gen_x_sandwich/financial_stress/overwhelm'),
    ('atoms/gen_x_sandwich/financial_stress/shame/CANONICAL.txt', 'gen_x_sandwich/financial_stress/shame'),
    ('atoms/gen_x_sandwich/financial_stress/spiral/CANONICAL.txt', 'gen_x_sandwich/financial_stress/spiral'),
]

import re
from pathlib import Path

for file_path, path_prefix in file_configs:
    p = Path(file_path)
    if p.exists():
        # Read existing content
        content = p.read_text()
        
        # Add path: line to each atom
        # Pattern: metadata section that doesn't have path:
        def add_path_line(match):
            pre_dashes = match.group(1)  # ##ROLE v##\n---\n
            metadata = match.group(2)    # existing metadata lines
            post_prose = match.group(3)  # \nprosetext
            
            # Check if path: already exists
            if 'path:' in metadata:
                return match.group(0)  # Already has path
            
            # Add path: line before the closing ---
            lines = metadata.rstrip().split('\n')
            lines.append(f'path: {path_prefix}')
            new_metadata = '\n'.join(lines)
            
            return pre_dashes + new_metadata + post_prose
        
        # Find all atom blocks and add path lines
        pattern = r'(##\s+[A-Z_]+\s+v\d+\s*\n---\n)(.*?)(\n[^\-])'
        new_content = re.sub(pattern, add_path_line, content, flags=re.MULTILINE | re.DOTALL)
        
        p.write_text(new_content)
        print(f'✓ Updated {file_path} with path lines')
    else:
        print(f'✗ File not found: {file_path}')

print('\nAll files updated with path lines.')
EOF
