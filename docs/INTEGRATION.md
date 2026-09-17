# Hooking Quiddity to a live client

## Recommended stack (2026 private servers)

1. Asheron's Call client + ThwargLauncher
2. Decal 2.9.8.3
3. Virindi Bundle (VTank + VVS)
4. Utility Belt (beta if you want Lua)

Quiddity runs on the same Windows box, reading a snapshot file and writing a command queue.

## Sensor path A — file snapshot (simplest)

Have a UB Lua script or external dumper write:

```
%USERPROFILE%\Documents\Decal Plugins\UtilityBelt\quiddity\world.json
```

Point Quiddity at it:

```
set QUIDDITY_WORLD=C:\Users\you\Documents\Decal Plugins\UtilityBelt\quiddity\world.json
python3 -m quiddity.cli where
```

Minimum useful fields: `character.name`, `character.position`, `selected`, `inventory[]`.

Useful in-game dumps you can parse into that file:

- `/vt propertydump` — selected item raw properties
- `/ub id` — object id helpers
- Utility Belt inventory expressions / `/ub` inventory commands
- Mag-Tools inventory views

## Sensor path B — Utility Belt TCP

UB Networking defaults:

- host `127.0.0.1`
- port `42163`

UB's TCP server is designed for multi-client command broadcast (`/ub bc`, `/ub bct`), not a rich object query API. Treat it as an actuator. For state, keep using the file snapshot.

## Actuator path — command queue

```
python3 -m quiddity.cli run data/sample_routines/buff_cycle.yaml --emit ./command_queue.txt
```

Lines look like:

```
/vt opt set enablebuffing true
/vt nav load holtburg_lifestone
/ub use Mana Scarab
```

## Meta / nav reuse

Do not rewrite working VTank content. Wrap it:

```yaml
name: wrap_existing_meta
steps:
  - vt: "meta load MyQuest"
  - vt: "opt set enablemeta true"
  - vt: "opt set enablecombat true"
```

## Server rules

VTank's own license forbids using it contrary to the Asheron's Call Code of Conduct. Private servers vary. Quiddity will emit commands; it will not hide them. Keep a human in the loop unless the server you play on allows otherwise.

## Next implementation steps

1. UB Lua: on selection change and every 2s, serialize inventory + coords to world.json.
2. Replace CommandQueueActuator with a localhost POST that a Decal plugin executes via DispatchChatCommand.
3. Import ACE weenie + recipe tables into data/ for full catalog coverage.
4. Optional: ACE.Mods.WebAPI if you run the server.
