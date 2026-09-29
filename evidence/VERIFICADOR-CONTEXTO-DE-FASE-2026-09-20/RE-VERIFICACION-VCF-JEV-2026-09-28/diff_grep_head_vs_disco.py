import subprocess, io, sys

PAT = "`" + ".opencode"
PROC = subprocess.run(["git", "ls-files", "-z"], stdout=subprocess.PIPE)
md = [p.decode() for p in PROC.stdout.split(b"\x00") if p and p.endswith(b".md")]

disk = {}
for p in md:
    with io.open(p, "r", encoding="utf-8", errors="strict") as fh:
        disk[p] = fh.read().count(PAT)

res = subprocess.run(["git", "grep", "-c", "-F", PAT, "HEAD", "--", "*.md"],
                     stdout=subprocess.PIPE, stderr=subprocess.PIPE)
head = {}
for line in res.stdout.decode("utf-8", errors="replace").splitlines():
    parts = line.split(":")
    # formato: HEAD:<path>:<count>
    path = ":".join(parts[1:-1])
    head[path] = int(parts[-1])

out = io.open(sys.argv[1], "w", encoding="utf-8", newline="\n")
out.write("== patron: %r   (lineas-con-coincidencia en HEAD vs OCURRENCIAS en disco)\n" % PAT)
out.write("== HEAD (git grep -c): archivos=%d suma-lineas=%d\n" % (len(head), sum(head.values())))
out.write("== disco (str.count) : archivos=%d suma-ocurrencias=%d\n\n" % (len(disk), sum(disk.values())))

only_head = sorted(set(head) - set(disk))
only_disk = sorted(set(disk) - set(head))
out.write("== archivos que HEAD ve y el listado de ls-files NO (%d):\n" % len(only_head))
for p in only_head:
    out.write("   HEAD-lineas=%d  %s\n" % (head[p], p))
out.write("\n== archivos que el listado ve y HEAD no (%d):\n" % len(only_disk))
for p in only_disk:
    out.write("   disco-ocur=%d  %s\n" % (disk[p], p))
out.write("\n== coincidencia de nombres pero lineas(HEAD) > ocurrencias(disco):\n")
bad = 0
for p in sorted(set(head) & set(disk)):
    if head[p] > disk[p]:
        out.write("   HEAD-lineas=%d  disco-ocur=%d  %s\n" % (head[p], disk[p], p))
        bad += 1
out.write("   total=%d\n" % bad)
out.close()
sys.stdout.write("HEAD-sum=%d files=%d | DISK-sum=%d files=%d | onlyHEAD=%d onlyDISK=%d head>disk=%d\n"
                 % (sum(head.values()), len(head), sum(disk.values()), len(disk),
                    len(only_head), len(only_disk), bad))
