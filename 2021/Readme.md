# Porch Zombie 2021
For this years Porch Zombie, I am thinking more of a **Haunted Porch** concept.  To do this, I am planning on having multiple moving ghoulies, controlled by multiple Raspberry Pis.  

```dot
digraph G {
  Haunted_Porch_controller -> Zombie_1_Actuator
  Haunted_Porch_controller -> Zombie_2_Servos
  Zombie_1_Actuator -> up_down_actuator
  Zombie_1_Actuator -> front_back_actuator
  Zombie_1_Actuator -> circuit_trigger
  Zombie_2_Servos -> moving_hand_one
}
```

