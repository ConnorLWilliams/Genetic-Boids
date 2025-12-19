# Genetic-Boids
A modified version of the classic Boids where there are predator and prey boids. As prey are hunted by predators they are subject to evolutionary pressure.

I am working to make a web-app version of this, along with adding evolution to the predators.

I am also working to speed up the animations.

2 Separate Modes for Running passed as command line args (default real-time)

1. Real Time
- ex. python3 world.py real_time centering_factor speed_pref
- See boids move and update in real time args following real_time are gene names to plot up to 6 (slower with more plots)

2. Fast Sim
- ex. python3 world.py fast_sim 3000
- Have the simulation run without showing boids, get a plot of all evolved genes after it returns. arg following fast_sim is the number of world ticks to simulate

Example of what a real_time run looks like:
<img width="1593" height="857" alt="Boid_Sim_Third_Example" src="https://github.com/user-attachments/assets/7d24e1d7-4460-40c2-a63f-b39110ab4920" />

Example of what a fast_sim returns:
<img width="1912" height="2000" alt="boids_fastmode_example" src="https://github.com/user-attachments/assets/d1e756c5-eb4f-4530-a0f6-0d5fc2c1b8fb" />
