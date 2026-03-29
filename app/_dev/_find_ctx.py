html = open(r'c:\Users\glwex\Documents\GitHub\SWF-Next2D-Converter\Next2Flash STABLE\index.html','r',encoding='utf-8').read()
target = '<script src="./assets/js/next2d-tool.min.js">'
idx = html.find(target)
print(f"Found at {idx}")
start = max(0, idx - 200)
end = min(len(html), idx + len(target) + 20)
# Print char by char to avoid escaping issues
print("CONTEXT:")
print(html[start:end])
