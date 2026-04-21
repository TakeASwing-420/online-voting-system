## Online Voting System (UDP, Python)

This repository implements a modular UDP-based real-time voting system:

- **Server** receives votes from clients and keeps live aggregated results.
- **Client** sends votes and receives updated vote totals immediately.

## Project structure

```text
online_voting/
  __init__.py
  protocol.py      # Message encoding/decoding + validation
  voting_store.py  # In-memory vote aggregation logic
  server.py        # UDP server implementation
  client.py        # UDP client implementation
run_server.py      # Server entry point
run_client.py      # Client entry point
```

## Run the server

```bash
python run_server.py --host 127.0.0.1 --port 9999 --candidates Alice Bob Charlie
```

## Run a client

```bash
python run_client.py --host 127.0.0.1 --port 9999 --voter-id voter-1

# Optional: increase wait time for slower networks
python run_client.py --host 127.0.0.1 --port 9999 --voter-id voter-1 --timeout 5
```

Then select a candidate in the client prompt to cast/update your vote.
