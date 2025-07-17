import numpy as np
import matplotlib.pyplot as plt
import panel as pn
pn.extension()  # required to enable widgets & plotting

# Function to generate and plot sine wave
def plot_sine(freq=1.0, amp=1.0):
    x = np.linspace(0, 2 * np.pi, 400)
    y = amp * np.sin(freq * x)
    
    plt.figure(figsize=(6, 3))
    plt.plot(x, y)
    plt.title(f"Sine Wave | Frequency: {freq}, Amplitude: {amp}")
    plt.xlabel("x")
    plt.ylabel("y")
    plt.grid(True)
    
    return pn.pane.Matplotlib(plt.gcf(), tight=True)

# Sliders for interactivity
freq_slider = pn.widgets.FloatSlider(name='Frequency', start=0.1, end=10.0, step=0.1, value=1.0)
amp_slider = pn.widgets.FloatSlider(name='Amplitude', start=0.1, end=5.0, step=0.1, value=1.0)

# Bind sliders to plotting function
interactive_plot = pn.bind(plot_sine, freq=freq_slider, amp=amp_slider)

# Layout
app = pn.Column(
    "# 🎵 Sine Wave Explorer",
    "Adjust the sliders to visualize different sine waves.",
    freq_slider,
    amp_slider,
    interactive_plot
)

app.servable()  # used when served with panel serve
