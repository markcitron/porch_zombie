```python
# Pseudocode-style overview
while True:
    if in_patrol_mode:
        pan_head_slowly()
        scan = get_lidar_data()
        if detect_movement(scan):
            target = find_nearest_target(scan)
            switch_to_tracking_mode(target)
    elif in_tracking_mode:
        if target_still_present():
            update_head_position(target)
        else:
            switch_to_patrol_mode()
```
