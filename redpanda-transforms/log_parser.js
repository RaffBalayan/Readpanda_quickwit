function parseLog(logLine) {
  const pattern = /^(\S+) (\S+) \S+ \[([^]]+)\] "([A-Z]+) (\S+) HTTP\/\d\.\d" (\d+) (\d+) "([^"]+)" "([^"]+)"$/;
  const matches = logLine.match(pattern);

  if (!matches) return null;

  return {
    host: matches[1],
    user: matches[2],
    timestamp: matches[3],
    method: matches[4],
    path: matches[5],
    status: parseInt(matches[6]),
    size: parseInt(matches[7]),
    referer: matches[8],
    agent: matches[9],
  };
}

function process(msg) {
  const parsed = parseLog(msg.value.toString());

  if (parsed) {
    return {
      ...msg,
      value: JSON.stringify(parsed),
    };
  }

  return msg;
}