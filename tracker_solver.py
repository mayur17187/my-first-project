import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import os

# ==========================================
# PART 1: SETUP / CREATE DUMMY DATA
# (Delete this part if you have the real cones.csv file)
# ==========================================
if not os.path.exists('cones.csv'):
    print("cones.csv not found. Creating dummy data...")
    # Create two circles of cones to simulate a track
    theta = np.linspace(0, 2*np.pi, 50, endpoint=False)
    
    # Inner loop (Blue)
    r_blue = 10 + np.random.normal(0, 0.5, 50) # Radius 10 with noise
    bx = r_blue * np.cos(theta)
    by = r_blue * np.sin(theta)
    
    # Outer loop (Yellow)
    r_yellow = 16 + np.random.normal(0, 0.5, 50) # Radius 16 with noise
    yx = r_yellow * np.cos(theta)
    yy = r_yellow * np.sin(theta)
    
    # Shuffle the data to mimic "unordered" input
    data = []
    for x, y in zip(bx, by):
        data.append([x, y, 'blue'])
    for x, y in zip(yx, yy):
        data.append([x, y, 'yellow'])
    
    df_mock = pd.DataFrame(data, columns=['x', 'y', 'color'])
    df_mock = df_mock.sample(frac=1).reset_index(drop=True) # Shuffle rows
    df_mock.to_csv('cones.csv', index=False)

# ==========================================
# PART 2: THE SOLUTION LOGIC
# ==========================================

def solve_track():
    # 1. Load Data
    try:
        df = pd.read_csv('cones.csv')
    except FileNotFoundError:
        print("Error: cones.csv not found!")
        return

    # 2. Separate Cones by Color
    blue_cones = df[df['color'] == 'blue'].copy()
    yellow_cones = df[df['color'] == 'yellow'].copy()

    # 3. Estimate Overall Track Center
    # We take the average of ALL cone positions
    center_x = df['x'].mean()
    center_y = df['y'].mean()

    # 4. Sort Cones Angularly
    # We calculate the angle of each cone relative to the center using arctan2
    # This helps us "connect the dots" in the correct order
    
    def get_angle(x, y, cx, cy):
        return np.arctan2(y - cy, x - cx)

    blue_cones['angle'] = blue_cones.apply(lambda row: get_angle(row['x'], row['y'], center_x, center_y), axis=1)
    yellow_cones['angle'] = yellow_cones.apply(lambda row: get_angle(row['x'], row['y'], center_x, center_y), axis=1)

    # Sort both dataframes by angle so indices align
    blue_sorted = blue_cones.sort_values('angle').reset_index(drop=True)
    yellow_sorted = yellow_cones.sort_values('angle').reset_index(drop=True)

    # Note: This assumes equal number of blue and yellow cones. 
    # If counts differ in the real file, you might need to interpolate, 
    # but for this level of assignment, simple angular sorting is usually expected.

    # 5. Compute Midpoints (The Centerline)
    mid_x = (blue_sorted['x'] + yellow_sorted['x']) / 2
    mid_y = (blue_sorted['y'] + yellow_sorted['y']) / 2
    
    # Close the loop for the centerline (connect last point to first)
    mid_x = pd.concat([mid_x, mid_x.iloc[[0]]], ignore_index=True)
    mid_y = pd.concat([mid_y, mid_y.iloc[[0]]], ignore_index=True)

    # ==========================================
    # PART 3: VISUALIZATION & ANIMATION
    # ==========================================
    
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_title("Race Track Reconstruction & Particle Animation")
    ax.set_aspect('equal') # Important so the track doesn't look squashed
    
    # Plot static elements
    ax.scatter(blue_cones['x'], blue_cones['y'], c='blue', label='Blue Cones')
    ax.scatter(yellow_cones['x'], yellow_cones['y'], c='gold', label='Yellow Cones')
    ax.plot(mid_x, mid_y, 'r--', alpha=0.5, label='Centerline') # Dashed red line
    ax.scatter(center_x, center_y, c='green', marker='x', s=100, label='Track Center')

    # Setup the particle (a red dot)
    particle, = ax.plot([], [], 'ro', markersize=10, label='Car')
    
    ax.legend()

    # Animation update function
    def update(frame):
        # frame is the index of the point on the centerline
        x = mid_x.iloc[frame]
        y = mid_y.iloc[frame]
        particle.set_data([x], [y]) # Pass as lists/arrays
        return particle,

    # Create Animation
    # frames=len(mid_x) means it will step through every point calculated
    # interval=50 means 50 milliseconds per frame
    ani = animation.FuncAnimation(fig, update, frames=len(mid_x), interval=50, blit=True)

    # ==========================================
    # PART 4: EXPORT
    # ==========================================
    print("Saving animation... (this might take a moment)")
    
    # To save as MP4, we need the ffmpeg writer. 
    # Ensure ffmpeg is installed on Ubuntu: sudo apt install ffmpeg
    try:
        writer = animation.FFMpegWriter(fps=20, metadata=dict(artist='Me'), bitrate=1800)
        ani.save('track_animation.mp4', writer=writer)
        print("Success! Saved as track_animation.mp4")
    except Exception as e:
        print(f"Could not save MP4 (Check if ffmpeg is installed). Error: {e}")
        print("Showing plot instead...")
    
    plt.show()

if __name__ == "__main__":
    solve_track()