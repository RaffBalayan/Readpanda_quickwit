# quickwit/start.sh
#!/bin/sh
quickwit index create --index-config /quickwit/config.yaml
exec quickwit run