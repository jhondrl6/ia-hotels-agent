import sys

path = "/mnt/c/Users/Jhond/Github/iah-cli/modules/commercial_documents/v4_diagnostic_generator.py"

with open(path, "r", encoding="utf-8") as f:
    lines = f.readlines()

output = []
i = 0
while i < len(lines):
    line = lines[i]

    # Patch 1: After semrush status block, add GSC check
    if 'status.semrush_status_text = f"Error:' in line and "str(e)" in line:
        output.append(line)
        j = i + 1
        while j < len(lines) and lines[j].strip() == "":
            output.append(lines[j])
            j += 1
        if j < len(lines) and "return status" in lines[j]:
            gsc_block = '''        # --- GSC (FASE-D) ---
        try:
            from modules.analytics.google_search_console_client import GoogleSearchConsoleClient
            gsc = GoogleSearchConsoleClient()
            status.gsc_available = gsc.is_configured()
            if not status.gsc_available:
                if gsc._init_error:
                    status.gsc_error = gsc._init_error
                    status.gsc_status_text = f"No configurado ({gsc._init_error})"
                else:
                    status.gsc_status_text = "No configurado (agregue GSC_SITE_URL)"
        except Exception as e:
            status.gsc_error = str(e)
            status.gsc_status_text = f"Error: {str(e)}"

'''
            output.append(gsc_block)
        i = j
        continue

    # Patch 2: Add gsc_status_text after semrush_status_text
    if "data['semrush_status_text'] = analytics_status.semrush_status_for_template()" in line:
        output.append(line)
        output.append("        data['gsc_status_text'] = analytics_status.gsc_status_for_template()\n")
        i += 1
        continue

    # Patch 3: Add GSC to transparency section
    if "semrush = analytics_status.semrush_status_for_template()" in line:
        output.append(line)
        output.append("        gsc = analytics_status.gsc_status_for_template()\n")
        i += 1
        continue

    # Patch 4: Add GSC line in the transparency template
    if "- **Semrush SEO**: {semrush}" in line:
        output.append(line)
        output.append("- **Google Search Console**: {gsc}\n")
        i += 1
        continue

    output.append(line)
    i += 1

with open(path, "w", encoding="utf-8") as f:
    f.writelines(output)

print(f"Applied patches: {len(output)} lines written")
