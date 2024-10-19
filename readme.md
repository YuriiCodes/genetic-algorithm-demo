# Genetic Algorithm Scheduling System

This project implements a scheduling system using a **genetic algorithm** designed to generate optimal class schedules for university groups. It handles constraints like group sizes, lecturer availability, classroom capacities, and even/odd week sessions.

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [License](#license)

## Overview
The system uses a **genetic algorithm** to generate and optimize schedules for university courses. It accounts for several constraints, such as:
- Student groups with fixed sizes and subgroups
- Courses with specified lecture and practice hours
- Lecturer constraints (e.g., subjects they can teach, maximum hours per week)
- Classroom capacity and availability
- Scheduling for even and odd weeks

The algorithm ensures that the resulting schedule is as conflict-free as possible, minimizing gaps (or "windows") in the schedule while considering all specified constraints.

## Features
- **Genetic Algorithm Optimization**: Finds optimal schedules over multiple generations, ensuring high efficiency and adaptability.
- **Support for Even/Odd Weeks**: Includes sessions that are specific to even or odd weeks.
- **Constraint Handling**: Ensures compliance with constraints like room capacity, lecturer availability, and group size.
- **Adaptive Mutation and Population Reset**: Implements techniques to avoid getting stuck at local optima, promoting global optimization.
- **Dynamic Scheduling**: Easily generates new schedules based on different input datasets.
- **CSV-based Input**: Accepts inputs in CSV format for easy configuration and modification.

## Installation
1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/genetic-algorithm-scheduling.git
   cd genetic-algorithm-scheduling
   ```

2. **Set up the environment:**
   Ensure you have Python installed (version 3.8+ recommended). Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use 'venv\Scripts\activate'
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Prepare input files:**
   Place CSV files for groups, subjects, lecturers, and classrooms in the `inputs/` directory.

## Usage
1. **Configure CSV input files**:
   - `group.csv`: Contains group IDs, student numbers, and subgroups.
   - `subjects.csv`: Contains subject details including lecture and practice hours.
   - `lecturers.csv`: Lists lecturers and their constraints.
   - `classrooms.csv`: Details classroom capacities.

2. **Run the main script:**
   ```bash
   python main.py
   ```

3. The genetic algorithm will generate an optimal schedule, displaying the best fitness score for each generation.

### Example Output
The output will show the schedule for even and odd weeks, formatted by day and period:
```
Week: even
Monday
  Period 1: [Session(Group: 1, Subject: Mathematics, Lecturer: Dr. Smith, ...)]
  Period 2: ...

Week: odd
Monday
  Period 1: ...
```

## Configuration
You can adjust the parameters of the genetic algorithm in the `GeneticScheduler` class, including:
- `pop_size`: Population size
- `generations`: Number of generations to run
- `mutation_rate`: Initial mutation rate
- `reset_threshold`: Number of generations before population reset
